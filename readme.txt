# Talking Taíno Shaman AI

A local, browser-based AI that simulates a Taíno *behique* (shaman), designed to engage users with poetic and spiritual responses using ChatGPT and ElevenLabs TTS.

---

## 🧠 What It Does
- Accepts **typed or spoken input** from a user in the browser
- Uses **OpenAI (ChatGPT)** to generate poetic, wisdom-filled replies
- Uses **ElevenLabs** to speak the response aloud using the "Clyde" voice
- Mimics the style and tone of a Taíno shaman, referencing nature, spirits, and ancestral knowledge

---

## 🚀 How to Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/taino-shaman-ai.git
cd taino-shaman-ai
```

### 2. Set Up Virtual Environment (Windows)
```bash
python -m venv ai-env
./ai-env/Scripts/activate.bat
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create a `.env` File with Your API Keys
```env
OPENAI_API_KEY=your-openai-key
ELEVENLABS_API_KEY=your-elevenlabs-key
VOICE_ID=2EiwWnXFnvU5JabPnv8n
```

### 5. Run the Flask Server
```bash
python app.py
```

### 6. Open the Interface
- Open `index.html` in your browser (Chrome recommended)
- Click the mic to talk, or type a message
- The shaman will respond with audio

---

## 📦 requirements.txt
```
Flask
flask-cors
requests
openai
python-dotenv
```

---

## 🛡️ Security
- All secrets are stored in a `.env` file
- `.env` is excluded from version control via `.gitignore`
- Never commit your API keys to GitHub

---

## 📄 License
This project is for educational and cultural exploration purposes. The C4 model and AI backend structure were inspired by Simon Brown's [C4 Model](https://c4model.com/).

---

## ✨ Future Ideas
- Add 3D avatar using Three.js
- Add myth/story/riddle buttons
- Support multiple languages (English, Spanish, Dutch)
- Host online for live interaction

---

## 🔗 Related Tools
- [OpenAI API](https://platform.openai.com/)
- [ElevenLabs API](https://www.elevenlabs.io/)
- [Flask (Python)](https://flask.palletsprojects.com/)
- [MDN Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
