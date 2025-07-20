TALKING SHAMAN – WHISPERS OF ATABEY
Interactive voice-based AI prototype embodying a Taíno behique (shaman) to preserve and share cultural knowledge through poetic storytelling.

GitHub Repo: https://github.com/UmbertoAdrianSemeleer/Taino-shaman

ABOUT THE PROJECT
Talking Shaman is a locally hosted AI installation that lets users speak with a digital Taíno shaman. The AI responds in poetic language rooted in Taíno culture using speech recognition, GPT-4 language generation, and voice synthesis.

KEY FEATURES

Real-time voice-to-AI-to-voice interaction

Symbolic poetic language

ElevenLabs voice (Regina Martin)

Ambient drip sound while processing

Optional Arduino button trigger

Keyboard (Enter/Spacebar) also supported

TECH STACK

Python Backend:

Python 3.11+

Flask

OpenAI GPT-4o-mini

OpenAI Whisper

PyMuPDF

ElevenLabs TTS (Regina Martin voice)

Frontend:

JavaScript (Web Audio API)

HTML/CSS

Optional Node Arduino Bridge:

Node.js

serialport

ws

FOLDER STRUCTURE

Taino-shaman-main/
├── app.py # Flask API
├── BTNserver.js # Node-Arduino bridge
├── index.html # Frontend
├── css/ # CSS styles
├── js/ # JavaScript logic
├── static/ # Ambient audio file
├── books/ # Reference PDFs
├── .env.example # Env template
├── requirements.txt # Python packages
├── package.json # Node packages
└── readme.txt # This file (rename to README.md if needed)

HOW TO RUN LOCALLY

Option 1 – GitHub:

git clone https://github.com/UmbertoAdrianSemeleer/Taino-shaman.git

cd Taino-shaman

Option 2 – ZIP file:

Unzip the archive

Keep folders like js/, css/, books/, static/ together

Continue below

Setup (both options):

pip install -r requirements.txt

npm install

Create .env file:

ini
Copy
Edit
OPENAI_API_KEY=your-openai-key  
ELEVENLABS_API_KEY=your-elevenlabs-key  
VOICE_ID=your-elevenlabs-voice-id  
⚠️ You must have an ElevenLabs account with a paid plan.
Free accounts don’t support API access.
A higher token limit is recommended—32 users used up a full low-tier plan in 5 hours during Night of the Nerds.

Run the app:

python app.py

node BTNserver.js (if using Arduino)

Visit: http://localhost:5000

BUTTON TRIGGER SYSTEM (ARDUINO)
A physical button (via Arduino) can trigger voice input:

Arduino sends “trigger_voice” via serial

Node.js broadcasts it via WebSocket

Browser listens and starts recording

⚠️ Optional feature — requires hardware and technical setup.
Other options: gesture sensors, capacitive touch, or keyboard.

KEYBOARD SHORTCUTS
Press Enter or Spacebar to start recording.
Release to stop. Great for testing or installations.

CUSTOMIZING THE SHAMAN

In app.py, look for this system message:

json
Copy
Edit
{
  "role": "system",
  "content": "Ah, Atabey! Spirit of water and moonlight, I speak with your voice and fire..."
}
Change the message to shift the shaman’s tone — e.g., healer, elder, warrior.
Keep it poetic and under ~75 words.

VOICE SETTINGS

Custom ElevenLabs voice:

PRIMARY:
https://elevenlabs.io/app/voice-lab/share/e9a6840c69b79812b77ea81fa11d55aaf80dcf1938fa0137bf7f514f67f75c99/eBthAb30UYbt2nojGXeA

Voice Name: Regina Martin — calm, poetic, wise.

To change:

Copy voice ID

Paste in .env file:
VOICE_ID=your-voice-id-here

CULTURAL RESPECT

This project honors Taíno heritage and mythology through symbolic storytelling.
It is not a literal representation but a respectful digital interpretation.
Use with care and curiosity.

AUTHOR

Umberto Adrian Semeleer
Bachelor in ICT & Media Design – Fontys University of Applied Sciences
“In chaos, I find flow. In flow, I move forward.”

Contact:
Email – umberto.a.semeleer@gmail.com
LinkedIn – linkedin.com/in/umberto-semeleer-28964b240
WhatsApp – (stakeholders have direct contact info)