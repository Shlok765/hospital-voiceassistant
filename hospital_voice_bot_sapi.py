import win32com.client
import pythoncom
import json
import os
import time

class HospitalVoiceBotSAPI:
    def __init__(self, data_file="hospital_data.txt"):
        # Initialize COM for SAPI
        pythoncom.CoInitialize()

        # Initialize SAPI for text-to-speech
        self.speaker = win32com.client.Dispatch("SAPI.SpVoice")

        # Initialize SAPI for speech recognition
        self.recognizer = win32com.client.Dispatch("SAPI.SpSharedRecognizer")
        self.context = self.recognizer.CreateRecoContext()
        self.grammar = self.context.CreateGrammar()

        # Load knowledge base
        self.data_file = data_file
        self.knowledge_base = self.load_knowledge_base()
        self.is_listening = False

        # Set up event handlers for recognition
        self.event_handler = ContextEvents(self.context)
        self.event_handler.on_recognition = self.on_recognition

        # Reset recognition state
        self.last_recognition = ""
        self.recognition_event = None

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
        except Exception as e:
            print(f"Error in text-to-speech: {e}")

    def on_recognition(self, streamNumber, streamPosition, recognitionType, result):
        """Callback for when speech is recognized"""
        try:
            result_obj = win32com.client.Dispatch(result)
            text = result_obj.PhraseInfo.GetText()
            print(f"You said: {text}")
            self.last_recognition = text.lower()
            # Signal that we have recognition
            if self.recognition_event:
                self.recognition_event.set()
        except Exception as e:
            print(f"Error in recognition callback: {e}")

    def listen_for_speech(self, timeout=5):
        """Listen for speech input using SAPI"""
        # Reset last recognition
        self.last_recognition = ""
        # Create an event to wait for recognition
        self.recognition_event = pythoncom.PyEvent()
        self.recognition_event = type('Event', (object,), {'is_set': lambda: False, 'set': lambda: None})()
        self.recognition_event.is_set = lambda: bool(self.last_recognition)
        self.recognition_event.set = lambda: setattr(self, '_event_set', True)

        # Start listening
        self.grammar.DictationSetState(1)  # Turn on dictation

        try:
            # Wait for recognition or timeout
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.last_recognition:
                    break
                time.sleep(0.1)

            # Turn off dictation
            self.grammar.DictationSetState(0)

            if self.last_recognition:
                return self.last_recognition
            else:
                return None
        except Exception as e:
            print(f"Error during listening: {e}")
            self.grammar.DictationSetState(0)  # Ensure dictation is off
            return None

    def run_conversation(self):
        """Run a single conversation cycle"""
        # Listen for user input
        user_input = self.listen_for_speech()

        if user_input:
            # Get response from knowledge base
            response = self.get_response(user_input)
            # Speak the response
            self.speak_text(response)
        else:
            # If no input understood, ask to repeat
            self.speak_text("I didn't catch that. Could you please repeat?")

    def run_continuous(self):
        """Run continuous voice conversation"""
        print("Hospital Voice Bot is ready! Say 'hello' to start or 'goodbye' to exit.")
        self.speak_text("Hello! Welcome to City Hospital Reception. How can I assist you today.")

        self.is_listening = True
        while self.is_listening:
            try:
                self.run_conversation()
                time.sleep(0.5)  # Small delay between conversations
            except KeyboardInterrupt:
                print("\nStopping voice bot...")
                self.is_listening = False
                break
            except Exception as e:
                print(f"Error in conversation loop: {e}")
                self.speak_text("I'm experiencing technical difficulties. Please try again.")

        self.speak_text("Thank you for calling City Hospital. Have a great day!")

        # Clean up
        pythoncom.CoUninitialize()

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
    bot = HospitalVoiceBotSAPI("hospital_data.txt")

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