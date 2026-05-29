import win32com.client
import pythoncom
import json
import os
import time

class HospitalVoiceBot:
    def __init__(self, data_file="hospital_data.txt"):
        # Initialize COM for SAPI
        pythoncom.CoInitialize()

        # Initialize SAPI for text-to-speech
        self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
        # Configure TTS engine
        voices = self.speaker.GetVoices()
        if voices.Count > 0:
            self.speaker.Voice = voices.Item(0)  # Use first voice
        self.speaker.Rate = 1  # Speed of speech (-10 to 10)
        self.speaker.Volume = 100  # Volume (0 to 100)

        # Initialize SAPI for speech recognition
        try:
            self.recognizer = win32com.client.Dispatch("SAPI.SpSharedRecognizer")
            self.context = self.recognizer.CreateRecoContext()
            self.grammar = self.context.CreateGrammar()
            self.grammar.DictationSetState(0)  # Start with dictation off

            # Set up event handlers for recognition
            self.event_handler = ContextEvents(self.context)
            self.event_handler.on_recognition = self.on_recognition

            self.sapi_available = True
            print("SAPI speech recognition initialized successfully")
        except Exception as e:
            print(f"SAPI speech recognition not available: {e}")
            self.sapi_available = False
            self.recognizer = None
            self.context = None
            self.grammar = None
            self.event_handler = None

        # Load knowledge base
        self.data_file = data_file
        self.knowledge_base = self.load_knowledge_base()

        # State variables
        self.last_recognition = ""
        self.is_listening = False
        self.consecutive_errors = 0
        self.max_consecutive_errors = 3

    def load_knowledge_base(self):
        """Load hospital data from text file"""
        knowledge_base = {}
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if ':' in line:
                            key, value = line.split(':', 1)
                            knowledge_base[key.strip().lower()] = value.strip()
                print(f"Loaded {len(knowledge_base)} entries from {self.data_file}")
            else:
                print(f"Data file {self.data_file} not found. Using default responses.")
                knowledge_base = {
                    "default": "I'm sorry, I didn't understand your question. Please try rephrasing or ask about visiting hours, doctor availability, appointment booking, insurance, or hospital facilities."
                }
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            knowledge_base = {
                "default": "I'm sorry, I didn't understand your question. Please try rephrasing or ask about visiting hours, doctor availability, appointment booking, insurance, or hospital facilities."
            }
        return knowledge_base

    def get_response(self, user_input):
        """Get response based on user input"""
        user_input = user_input.lower().strip()

        # Check for exact matches first
        if user_input in self.knowledge_base:
            return self.knowledge_base[user_input]

        # Check for partial matches
        for key, response in self.knowledge_base.items():
            if key in user_input and key != "default":
                return response

        # Return default response if no match found
        return self.knowledge_base.get("default", "I'm sorry, I didn't understand your question.")

    def speak_text(self, text):
        """Convert text to speech using SAPI"""
        try:
            print(f"Bot: {text}")
            self.speaker.Speak(text)
            # Wait a bit for speech to finish
            time.sleep(0.5)
            self.consecutive_errors = 0  # Reset error counter on success
        except Exception as e:
            print(f"Error in text-to-speech: {e}")
            self.consecutive_errors += 1
            # Try to reinitialize speaker once if we haven't exceeded max errors
            if self.consecutive_errors < self.max_consecutive_errors:
                try:
                    print("Attempting to recover TTS engine...")
                    self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
                    voices = self.speaker.GetVoices()
                    if voices.Count > 0:
                        self.speaker.Voice = voices.Item(0)
                    self.speaker.Rate = 1
                    self.speaker.Volume = 100
                    self.speaker.Speak(text)
                    time.sleep(0.5)
                    self.consecutive_errors = 0  # Reset on successful recovery
                except Exception as e2:
                    print(f"Failed to recover TTS: {e2}")
                    if self.consecutive_errors >= self.max_consecutive_errors:
                        print("Too many consecutive TTS errors, switching to text-only mode temporarily")
                        # Don't speak, just print
                        print(f"Bot (TEXT ONLY): {text}")
            else:
                print(f"Bot (TEXT ONLY): {text}")

    def on_recognition(self, streamNumber, streamPosition, recognitionType, result):
        """Callback for when speech is recognized"""
        try:
            result_obj = win32com.client.Dispatch(result)
            text = result_obj.PhraseInfo.GetText()
            print(f"You said: {text}")
            self.last_recognition = text.lower()
            self.consecutive_errors = 0  # Reset error counter on successful recognition
        except Exception as e:
            print(f"Error in recognition callback: {e}")
            self.consecutive_errors += 1

    def listen_for_speech(self, timeout=7):
        """Listen for speech input using SAPI"""
        if not self.sapi_available:
            # Fallback to manual input if SAPI not available
            print("SAPI not available, using manual input:")
            return input("You: ").lower().strip()

        # Reset last recognition
        self.last_recognition = ""

        try:
            # Turn on dictation
            self.grammar.DictationSetState(1)

            # Wait for recognition or timeout
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.last_recognition:
                    break
                time.sleep(0.1)

            # Turn off dictation
            self.grammar.DictationSetState(0)

            if self.last_recognition:
                result = self.last_recognition
                self.last_recognition = ""  # Reset for next time
                return result
            else:
                return None
        except Exception as e:
            print(f"Error during listening: {e}")
            self.consecutive_errors += 1
            try:
                self.grammar.DictationSetState(0)  # Ensure dictation is off
            except:
                pass
            return None

    def run_conversation(self):
        """Run a single conversation cycle"""
        # Check for too many consecutive errors
        if self.consecutive_errors >= self.max_consecutive_errors:
            print("Too many consecutive errors. Waiting before continuing...")
            time.sleep(2)
            self.consecutive_errors = 0  # Reset after waiting

        # Listen for user input
        user_input = self.listen_for_speech()

        if user_input:
            # Get response from knowledge base
            response = self.get_response(user_input)
            # Speak the response
            self.speak_text(response)

            # Check for exit command
            if any(word in user_input for word in ["goodbye", "bye", "exit", "quit"]):
                return False
        else:
            # If no input understood, ask to repeat
            self.speak_text("I didn't catch that. Could you please repeat?")

        return True

    def run_continuous(self):
        """Run continuous voice conversation"""
        print("Hospital Voice Bot is ready!")
        print("Speak your questions or type 'quit' to exit.")
        self.speak_text("Hello! Welcome to City Hospital Reception. How can I assist you today.")

        self.is_listening = True
        while self.is_listening:
            try:
                should_continue = self.run_conversation()
                if not should_continue:
                    break
                time.sleep(0.5)  # Small delay between conversations
            except KeyboardInterrupt:
                print("\nStopping voice bot...")
                self.is_listening = False
                break
            except Exception as e:
                print(f"Error in conversation loop: {e}")
                self.consecutive_errors += 1
                self.speak_text("I'm experiencing technical difficulties. Please try again.")

        self.speak_text("Thank you for calling City Hospital. Have a great day!")

        # Clean up
        try:
            pythoncom.CoUninitialize()
        except:
            pass

# Event handler class for SAPI recognition
class ContextEvents:
    def __init__(self, context):
        self.context = context
        self.on_recognition = None

    def OnRecognition(self, streamNumber, streamPosition, recognitionType, result):
        if self.on_recognition:
            self.on_recognition(streamNumber, streamPosition, recognitionType, result)

def main():
    """Main function to run the hospital voice bot"""
    bot = HospitalVoiceBot("hospital_data.txt")

    try:
        bot.run_continuous()
    except Exception as e:
        print(f"Failed to start voice bot: {e}")
    finally:
        try:
            pythoncom.CoUninitialize()
        except:
            pass

if __name__ == "__main__":
    main()