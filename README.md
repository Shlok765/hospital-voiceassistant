# 🏥 Hospital Voice Assistant

A browser-based AI hospital receptionist built using Flask, JavaScript Speech APIs, and Python.

This project started as a simple voice chatbot running locally on my computer, but I gradually converted it into a fully deployable web application that can answer common hospital reception questions using voice input and voice responses.

🌐 Live Demo:
https://hospital-voiceassistant-1.onrender.com

---

# 📌 What This Project Does

The assistant acts like a basic hospital receptionist.

Users can:

* click the microphone button
* ask questions naturally using voice
* receive spoken responses from the assistant

The chatbot currently answers common hospital-related queries such as:

* appointment timings
* doctor availability
* emergency services
* insurance information
* pharmacy timings
* ICU visiting hours
* lab tests
* departments
* billing information
* and many more

---

# 🎤 Features

* Voice input using browser microphone
* Voice output using speech synthesis
* Flask backend
* Real-time chat interface
* Hospital knowledge base
* Mobile and desktop compatible
* Deployed online using Render

---

# 🧠 How It Works

The complete flow of the application looks like this:

```text
User speaks into browser
        ↓
Browser Speech Recognition API converts speech to text
        ↓
Text is sent to Flask backend
        ↓
Python searches hospital knowledge base
        ↓
Best matching response is returned
        ↓
Browser converts response back into voice
```

---

# ⚙️ Tech Stack

### Backend

* Python
* Flask

### Frontend

* HTML
* CSS
* JavaScript

### Voice Technologies

* Web Speech API
* SpeechSynthesis API

### Deployment

* Render

---

# 📂 Project Structure

```text
voice_chatbot/
│
├── app.py
├── hospital_data.txt
├── requirements.txt
│
├── templates/
│   └── index.html
│
└── static/
```

---

# 🚀 Running The Project Locally

## 1. Clone Repository

```bash
git clone https://github.com/Shlok765/hospital-voiceassistant.git
```

---

## 2. Move Into Project Folder

```bash
cd hospital-voiceassistant
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Start Flask Server

```bash
py -3.11 app.py
```

---

## 5. Open In Browser

```text
http://127.0.0.1:5000
```

---

# 🌍 Deployment Process

This project is deployed using Render.

Steps used for deployment:

1. Push project to GitHub
2. Connect repository to Render
3. Create Web Service
4. Add build command:

```text
pip install -r requirements.txt
```

5. Add start command:

```text
gunicorn app:app
```

6. Deploy application

---

# 🏥 Hospital Knowledge Base

The chatbot uses a predefined hospital dataset stored in:

```text
hospital_data.txt
```

The file contains frequently asked hospital reception questions and answers.

Example:

```text
appointment: You can book appointments between 9 AM and 5 PM.

emergency: Emergency services are available 24 hours.

pharmacy: Our pharmacy is open from 8 AM to 10 PM.
```

---

# 🔮 Future Improvements

Some features I plan to add next:

* AI intent matching
* GPT integration
* Better UI/UX
* Database support
* Patient appointment system
* Authentication
* Multi-language support
* Whisper speech recognition
* Real doctor database
* Admin dashboard

---

# 💡 Why I Built This

I wanted to learn:

* Flask
* voice recognition
* speech synthesis
* deployment
* frontend/backend integration

Instead of making a basic chatbot, I decided to build something closer to a real-world AI receptionist system.

This project helped me understand:

* browser speech APIs
* Flask routing
* deployment workflows
* Git/GitHub
* Render hosting
* integrating frontend and backend together

---

# 👨‍💻 Author

Shlok Salunkhe

GitHub:
https://github.com/Shlok765
