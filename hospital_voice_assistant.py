
import speech_recognition as sr
import os
import time


class HospitalVoiceAssistant:

    def __init__(self, data_file="hospital_data.txt"):

        # SPEECH RECOGNITION
        self.recognizer = sr.Recognizer()

        self.microphone = sr.Microphone()

        # LOAD KNOWLEDGE BASE
        self.data_file = data_file

        self.knowledge_base = self.load_knowledge_base()

        # COMMANDS
        self.commands = {

            ("appointment", "book", "schedule"):
                "You can book appointments from 9 AM to 5 PM.",

            ("doctor", "physician", "specialist"):
                "Doctors are available Monday to Saturday.",

            ("emergency", "ambulance", "accident"):
                "Emergency services are available twenty four hours.",

            ("insurance", "policy", "claim"):
                "We accept all major insurance providers.",

            ("pharmacy", "medicine", "medical store"):
                "Our pharmacy is open from 8 AM to 10 PM.",

            ("bye", "goodbye", "exit", "quit"):
                "Thank you for visiting City Hospital. Have a nice day."
        }

    # LOAD KNOWLEDGE BASE
    def load_knowledge_base(self):

        kb = {}

        try:

            if os.path.exists(self.data_file):

                with open(self.data_file, "r", encoding="utf-8") as file:

                    for line in file:

                        line = line.strip()

                        if ":" in line:

                            key, value = line.split(":", 1)

                            kb[key.strip().lower()] = value.strip()

                print(f"Loaded {len(kb)} entries from knowledge base")

            else:

                print("Knowledge base file not found")

                kb = {
                    "default": "Sorry, I did not understand that."
                }

        except Exception as e:

            print("Error loading knowledge base:", e)

            kb = {
                "default": "Sorry, I did not understand that."
            }

        return kb

    # SPEAK FUNCTION
     
    # SPEAK FUNCTION
    def speak(self, text):

        try:

            print("Bot:", text)

            safe_text = text.replace("'", "")

            command = (
                'powershell -c "Add-Type -AssemblyName System.Speech;'
                '$voice = New-Object System.Speech.Synthesis.SpeechSynthesizer;'
                f'$voice.Speak(\'{safe_text}\')"'
            )

            os.system(command)

        except Exception as e:

            print("Voice Error:", e)



    # LISTEN FUNCTION
    def listen(self):

        with self.microphone as source:

            print("Listening...")

            self.recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

            try:

                audio = self.recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=6
                )

                print("Recognizing...")

                text = self.recognizer.recognize_google(audio)

                text = text.lower()

                print("You said:", text)

                return text

            except sr.WaitTimeoutError:

                print("No speech detected")

                return None

            except sr.UnknownValueError:

                print("Could not understand audio")

                return None

            except sr.RequestError as e:

                print("Speech service error:", e)

                return None

            except Exception as e:

                print("Listening error:", e)

                return None

    # RESPONSE FUNCTION
    def get_response(self, user_input):

        user_input = user_input.lower()

        # COMMAND MATCHING
        for keywords, response in self.commands.items():

            if any(word in user_input for word in keywords):

                return response

        # KNOWLEDGE BASE MATCHING
        for key, value in self.knowledge_base.items():

            if key in user_input:

                return value

        return self.knowledge_base.get(
            "default",
            "Sorry, I did not understand that."
        )

    # MAIN LOOP
    def run(self):

        print("Hospital Voice Assistant Started")

        self.speak(
            "Hello! Welcome to City Hospital. How can I help you today?"
        )

        while True:

            user_input = self.listen()

            if not user_input:
                continue

            response = self.get_response(user_input)

            self.speak(response)

            # EXIT CONDITION
            if any(word in user_input for word in [
                "bye",
                "goodbye",
                "exit",
                "quit"
            ]):
                break

            time.sleep(0.3)


# MAIN
if __name__ == "__main__":

    bot = HospitalVoiceAssistant()

    bot.run()
