
from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# LOAD KNOWLEDGE BASE
def load_knowledge_base():

    kb = {}

    if os.path.exists("hospital_data.txt"):

        with open("hospital_data.txt", "r", encoding="utf-8") as file:

            for line in file:

                if ":" in line:

                    key, value = line.split(":", 1)

                    kb[key.strip().lower()] = value.strip()

    return kb


knowledge_base = load_knowledge_base()

# COMMANDS
commands = {

    ("appointment", "book", "schedule"):
        "You can book appointments from 9 AM to 5 PM.",

    ("doctor", "physician"):
        "Doctors are available Monday to Saturday.",

    ("emergency", "ambulance"):
        "Emergency services are available twenty four hours.",

    ("insurance", "claim"):
        "We accept all major insurance providers.",

    ("pharmacy", "medicine"):
        "Our pharmacy is open from 8 AM to 10 PM.",

    ("bye", "goodbye"):
        "Thank you for visiting City Hospital."
}


def get_response(user_input):

    user_input = user_input.lower()

    # COMMAND MATCHING
    for keywords, response in commands.items():

        if any(word in user_input for word in keywords):

            return response

    # KNOWLEDGE BASE MATCHING
    for key, value in knowledge_base.items():

        if key in user_input:

            return value

    return "Sorry, I did not understand that."


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    user_message = request.json.get("message")

    response = get_response(user_message)

    return jsonify({
        "response": response
    })


if __name__ == "__main__":

    app.run(debug=True)
