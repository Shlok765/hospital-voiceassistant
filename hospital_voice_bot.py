import win32com.client
import pythoncom
import os
import time

class HospitalVoiceBot:
    def __init__(self, data_file="hospital_data.txt"):
        pythoncom.CoInitialize()
        # Initialize TTS
        self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
        voices = self.speaker.GetVoices()
        if voices.Count > 0:
            self.speaker.Voice = voices.Item(0)
        self.speaker.Rate = 1
        self.speaker.Volume = 100
        # Initialize Speech Recognition
        try:
            self.recognizer = win32com.client.Dispatch("SAPI.SpSharedRecognizer")
            self.context = self.recognizer.CreateRecoContext()
            self.grammar = self.context.CreateGrammar()
            self.grammar.DictationSetState(0)  # Start with dictation off
            self.event_handler = ContextEvents(self.context)
            self.event_handler.on_recognition = self.on_recognition
            self.sapi_available = True
            print("SAPI Speech Recognition initialized")
        except Exception as e:
            print(f"SAPI Speech Recognition not available: {e}")
            self.sapi_available = False
            self.recognizer = None
            self.context = None
            self.grammar = None
            self.event_handler = None
        # Load knowledge base
        self.data_file = data_file
        self.knowledge_base = self.load_knowledge_base()
        # State
        self.last_recognition = ""
        self.is_running = False

    def load_knowledge_base(self):
        kb = {}
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if ':' in line:
                            key, value = line.split(':', 1)
                            kb[key.strip().lower()] = value.strip()
                print(f"Loaded {len(kb)} entries from {self.data_file}")
            else:
                print(f"Data file {self.data_file} not found. Using default responses.")
                kb = {"default": "I'm sorry, I didn't understand your question. Please try rephrasing or ask about visiting hours, doctor availability, appointment booking, insurance, or hospital facilities."}
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            kb = {"default": "I'm sorry, I didn't understand your question. Please try rephrasing or ask about visiting hours, doctor availability, appointment booking, insurance, or hospital facilities."}
        return kb

    def get_response(self, user_input):
        user_input = user_input.lower().strip()
        if user_input in self.knowledge_base:
            return self.knowledge_base[user_input]
        for key, response in self.knowledge_base.items():
            if key in user_input and key != "default":
                return response
        return self.knowledge_base.get("default", "I'm sorry, I didn't understand your question.")

    def speak_text(self, text):
        try:
            print(f"Bot: {text}")
            self.speaker.Speak(text)
            time.sleep(0.5)  # Allow time for speech to finish
        except Exception as e:
            print(f"TTS error: {e}")
            # Fallback to text-only output
            print(f"Bot (TEXT ONLY): {text}")

    def on_recognition(self, streamNumber, streamPosition, recognitionType, result):
        try:
            result_obj = win32com.client.Dispatch(result)
            text = result_obj.PhraseInfo.GetText()
            print(f"You said: {text}")
            self.last_recognition = text.lower()
        except Exception as e:
            print(f"Recognition error: {e}")

    def listen_for_speech(self, timeout=8):
        if not self.sapi_available:
            # Fallback to manual input if SAPI not available
            print("SAPI not available, using manual input:")
            return input("You: ").lower().strip()
        self.last_recognition = ""
        try:
            # Turn on dictation mode
            self.grammar.DictationSetState(1)
            start_time = time.time()
            # Wait for recognition or timeout
            while time.time() - start_time < timeout:
                if self.last_recognition:
                    break
                time.sleep(0.1)
            # Turn off dictation mode
            self.grammar.DictationSetState(0)
            if self.last_recognition:
                result = self.last_recognition
                self.last_recognition = ""  # Reset for next time
                return result
            else:
                return None
        except Exception as e:
            print(f"Error during listening: {e}")
            try:
                self.grammar.DictationSetState(0)  # Ensure dictation is off
            except:
                pass
            return None

    def run(self):
        """Main conversation loop"""
        print("Hospital Voice Bot is ready!")
        print("Speak your questions or say 'quit' to exit.")
        self.speak_text("Hello! Welcome to City Hospital Reception. How can I assist you today.")
        self.is_running = True
        while self.is_running:
            try:
                # Listen for user input
                user_input = self.listen_for_speech(timeout=8)
                if user_input:
                    # Get response from knowledge base
                    response = self.get_response(user_input)
                    # Speak the response
                    self.speak_text(response)
                    # Check for exit command
                    if any(word in user_input for word in ["goodbye", "bye", "exit", "quit"]):
                        break
                else:
                    # No input detected within timeout - just continue listening
                    # We don't speak here to avoid spamming the user
                    pass
                time.sleep(0.3)  # Small delay to prevent excessive CPU usage
            except KeyboardInterrupt:
                print("\nReceived interrupt signal, stopping...")
                break
            except Exception as e:
                print(f"Error in conversation loop: {e}")
                self.speak_text("I'm experiencing technical difficulties. Please try again.")
        # Final goodbye
        self.speak_text("Thank you for calling City Hospital. Have a great day!")
        # Clean up
        try:
            pythoncom.CoUninitialize()
        except:
            pass

class ContextEvents:
    def __init__(self, context):
        self.context = context
        self.on_recognition = None
    def OnRecognition(self, streamNumber, streamPosition, recognitionType, result):
        if self.on_recognition:
            self.on_recognition(streamNumber, streamPosition, recognitionType, result)

def main():
    bot = HospitalVoiceBot("hospital_data.txt")
    try:
        bot.run()
    except Exception as e:
        print(f"Failed to start voice bot: {e}")
    finally:
        try:
            pythoncom.CoUninitialize()
        except:
            pass

if __name__ == "__main__":
    main()