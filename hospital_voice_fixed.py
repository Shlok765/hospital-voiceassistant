import win32com.client
import pythoncom
import os
import time

class HospitalVoiceBot:
    def __init__(self, data_file="hospital_data.txt"):
        pythoncom.CoInitialize()
        # TTS
        self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
        voices = self.speaker.GetVoices()
        if voices.Count > 0:
            self.speaker.Voice = voices.Item(0)
        self.speaker.Rate = 1   # -10 to 10
        self.speaker.Volume = 100  # 0 to 100
        # Recognition
        try:
            self.recognizer = win32com.client.Dispatch("SAPI.SpSharedRecognizer")
            self.context = self.recognizer.CreateRecoContext()
            self.grammar = self.context.CreateGrammar()
            self.grammar.DictationSetState(0)  # start off
            self.event_handler = ContextEvents(self.context)
            self.event_handler.on_recognition = self.on_recognition
            self.sapi_available = True
            print("SAPI initialized")
        except Exception as e:
            print(f"SAPI init failed: {e}")
            self.sapi_available = False
            self.recognizer = None
            self.context = None
            self.grammar = None
            self.event_handler = None
        # Knowledge base
        self.data_file = data_file
        self.knowledge_base = self.load_knowledge_base()
        # State
        self.last_recognition = ""
        self.is_listening = False
        self.consecutive_no_input = 0
        self.max_no_input = 2  # after 2 consecutive no-input, we will speak a prompt but not loop endlessly

    def load_knowledge_base(self):
        kb = {}
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if ':' in line:
                            k, v = line.split(':', 1)
                            kb[k.strip().lower()] = v.strip()
                print(f"Loaded {len(kb)} entries")
            else:
                print(f"Data file not found, using default")
                kb = {"default": "I'm sorry, I didn't understand your question. Please try rephrasing or ask about visiting hours, doctor availability, appointment booking, insurance, or hospital facilities."}
        except Exception as e:
            print(f"Error loading KB: {e}")
            kb = {"default": "I'm sorry, I didn't understand your question. Please try rephrasing or ask about visiting hours, doctor availability, appointment booking, insurance, or hospital facilities."}
        return kb

    def get_response(self, user_input):
        ui = user_input.lower().strip()
        if ui in self.knowledge_base:
            return self.knowledge_base[ui]
        for k, v in self.knowledge_base.items():
            if k in ui and k != "default":
                return v
        return self.knowledge_base.get("default", "I'm sorry, I didn't understand your question.")

    def speak_text(self, text):
        try:
            print(f"Bot: {text}")
            self.speaker.Speak(text)
            time.sleep(0.5)
        except Exception as e:
            print(f"TTS error: {e}")
            # Fallback to print only
            print(f"Bot (TEXT ONLY): {text}")

    def on_recognition(self, streamNumber, streamPosition, recognitionType, result):
        try:
            result_obj = win32com.client.Dispatch(result)
            text = result_obj.PhraseInfo.GetText()
            print(f"You said: {text}")
            self.last_recognition = text.lower()
        except Exception as e:
            print(f"Recognition callback error: {e}")

    def listen_for_speech(self, timeout=6):
        if not self.sapi_available:
            print("SAPI not available, using manual input")
            return input("You: ").lower().strip()
        self.last_recognition = ""
        try:
            self.grammar.DictationSetState(1)  # turn on dictation
            start = time.time()
            while time.time() - start < timeout:
                if self.last_recognition:
                    break
                time.sleep(0.1)
            self.grammar.DictationSetState(0)  # turn off
            if self.last_recognition:
                result = self.last_recognition
                self.last_recognition = ""
                return result
            else:
                return None
        except Exception as e:
            print(f"Listen error: {e}")
            try:
                self.grammar.DictationSetState(0)
            except:
                pass
            return None

    def run_conversation(self):
        # If too many consecutive no-input, we will still listen but not speak the repeat message endlessly
        user_input = self.listen_for_speech(timeout=7)
        if user_input:
            self.consecutive_no_input = 0
            response = self.get_response(user_input)
            self.speak_text(response)
            # Check exit
            if any(word in user_input for word in ["goodbye", "bye", "exit", "quit"]):
                return False
        else:
            self.consecutive_no_input += 1
            if self.consecutive_no_input < self.max_no_input:
                self.speak_text("I didn't catch that. Could you please repeat?")
            else:
                # After max attempts, just listen again without speaking to avoid spam
                print("(Waiting for input...)")
        return True

    def run_continuous(self):
        print("Hospital Voice Bot ready! Speak or say 'quit' to exit.")
        self.speak_text("Hello! Welcome to City Hospital Reception. How can I assist you today.")
        self.is_listening = True
        while self.is_listening:
            try:
                cont = self.run_conversation()
                if not cont:
                    break
                time.sleep(0.5)
            except KeyboardInterrupt:
                print("\nStopping...")
                self.is_listening = False
                break
            except Exception as e:
                print(f"Loop error: {e}")
                self.speak_text("I'm experiencing technical difficulties. Please try again.")
        self.speak_text("Thank you for calling City Hospital. Have a great day!")
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
        bot.run_continuous()
    except Exception as e:
        print(f"Failed to start bot: {e}")
    finally:
        try:
            pythoncom.CoUninitialize()
        except:
            pass

if __name__ == "__main__":
    main()