TALKING SHAMAN – WHISPERS OF ATABEY

An interactive voice-based AI prototype embodying a Taíno behique (shaman) to preserve and share cultural knowledge through poetic storytelling.

============================================================

ABOUT THE PROJECT

Talking Shaman is a locally hosted AI experience that simulates a conversation with a Taíno behique (shaman). Users speak into a microphone and receive poetic responses grounded in Taíno cultural themes. The system combines speech recognition, language modeling, and voice synthesis to create a responsive, symbolic digital oracle.

Key features:

Real-time speech input via microphone

Poetic, symbolic AI responses with cultural nuance

ElevenLabs-generated voice for immersion

Ambient dripping sound while the AI "thinks"

============================================================

TECH STACK

Python 3.11+

Flask (API server)

OpenAI API (GPT-4o mini + Whisper)

ElevenLabs TTS API

JavaScript frontend with Web Audio API

PyMuPDF for extracting text from PDFs

============================================================

FOLDER STRUCTURE

project-root/
├── app.py                   (Flask backend)
├── requirements.txt         (Python dependencies)
├── .env                     (Environment variables - not committed)
├── static/
│   └── dripping-water.mp3   (Processing sound)
├── templates/
│   └── index.html           (Frontend UI)
├── js/                      (JavaScript logic)
├── css/                     (CSS styling)
└── books/                   (PDF or TXT files with cultural data)

============================================================

HOW TO RUN LOCALLY

Clone the repo:
git clone https://github.com/YourUsername/Taino-shaman.git
cd Taino-shaman

Install dependencies:
pip install -r requirements.txt

Create a file named .env with:
OPENAI_API_KEY=your-openai-key
ELEVENLABS_API_KEY=your-elevenlabs-key
VOICE_ID=your-elevenlabs-voice-id

Start the Flask app:
python app.py

Open your browser at:
http://localhost:5000

============================================================

DEPLOYMENT NOTE

If deploying online (e.g., Render):

Change app.run() to use host="0.0.0.0", port=10000

Ensure 'fitz' (PyMuPDF) is listed in requirements.txt

Use environment variable UI instead of .env file

Indentation must use spaces (not tabs)

============================================================

FEATURES

Voice interaction from recording to spoken reply

Knowledge base loaded from PDFs or text

Symbolic and poetic system personality

Animated orb with ambient audio during thinking

Conversation debug log visible in UI

============================================================

HOW TO CHANGE THE PERSONALITY

Edit app.py, look for this section:

messages = [
{
"role": "system",
"content": "Ah, Atabey! Spirit of water and moonlight, I speak with your voice and fire..."
}
]

To customize:

Change the "content" text to define tone and style

Save and restart app.py

You can create new personas such as a warrior, elder, or healer.

============================================================

VOICE SETTINGS

This project uses a custom ElevenLabs voice.

PRIMARY VOICE:
https://elevenlabs.io/app/voice-lab/share/e9a6840c69b79812b77ea81fa11d55aaf80dcf1938fa0137bf7f514f67f75c99/eBthAb30UYbt2nojGXeA

BACKUP VOICE:
Regina Martin – calm, mature Brazilian Portuguese narrative voice

To use either:

Copy the voice ID from ElevenLabs

Paste into your .env file as VOICE_ID

============================================================

============================================================

CULTURAL RESPECT

This project aims to honor the Taíno people and their traditions. It was designed to respectfully represent spiritual and cultural heritage.

Explore the experience with curiosity and respect.

============================================================

AUTHOR
Umberto Adrian Semeleer
Bachelor in ICT & Media Design – Fontys University of Applied Sciences
"In chaos, I find flow. In flow, I move forward."

CONTACT

Email: Umberto.a.semeleer@gmail.com

LinkedIn: linkedin.com/in/umberto-semeleer-28964b240

============================================================

LICENSE
MIT License – free for non-commercial, respectful use and adaptation.

