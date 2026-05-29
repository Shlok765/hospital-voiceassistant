import json
import os
import time

class HospitalTextBot:
    def __init__(self, data_file="hospital_data.txt"):
        # Load knowledge base
        self.data_file = data_file
        self.knowledge_base = self.load_knowledge_base()
        self.is_running = False

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

    def run_conversation(self):
        """Run a single conversation cycle (text-based)"""
        # Get user input
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return False

        if not user_input:
            print("Bot: Please say something.")
            return True

        # Get response from knowledge base
        response = self.get_response(user_input)
        print(f"Bot: {response}")

        # Check for exit command
        if any(word in user_input.lower() for word in ["goodbye", "bye", "exit", "quit"]):
            return False

        return True

    def run_continuous(self):
        """Run continuous text conversation"""
        print("Hospital Text Bot is ready!")
        print("Type your questions or 'quit' to exit.")
        print("Bot: Hello! Welcome to City Hospital Reception. How can I assist you today.")

        self.is_running = True
        while self.is_running:
            try:
                should_continue = self.run_conversation()
                if not should_continue:
                    break
            except KeyboardInterrupt:
                print("\nStopping bot...")
                self.is_running = False
                break
            except Exception as e:
                print(f"Error in conversation loop: {e}")
                print("Bot: I'm experiencing technical difficulties. Please try again.")

        print("Bot: Thank you for calling City Hospital. Have a great day!")

def main():
    """Main function to run the hospital text bot"""
    bot = HospitalTextBot("hospital_data.txt")

    try:
        bot.run_continuous()
    except Exception as e:
        print(f"Failed to start bot: {e}")

if __name__ == "__main__":
    main()