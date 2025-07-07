from flask import Flask, request, jsonify
import requests
import base64
from flask_cors import CORS
from openai import OpenAI  # ✅ Correct import for v1.83.0
import os
from dotenv import load_dotenv
import logging
import fitz  # PyMuPDF for reading PDFs
from glob import glob

# === Load environment variables ===
load_dotenv()

# === Set up logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("ai_conversations.log"),
        logging.StreamHandler()
    ]
)

# === Flask app setup ===
app = Flask(__name__)
CORS(app)

# === API Keys ===
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# === OpenAI client ===
client = OpenAI(api_key=OPENAI_API_KEY)

# === Book loading functions ===
BOOK_FOLDER = "books"

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    return "\n".join(page.get_text() for page in doc)

def split_text(text, chunk_size=500):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def load_all_books():
    texts = []
    for filepath in glob(f"{BOOK_FOLDER}/*"):
        if filepath.lower().endswith(".pdf"):
            text = extract_text_from_pdf(filepath)
        elif filepath.lower().endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            continue
        chunks = split_text(text)
        texts.extend(chunks)
    return texts

book_chunks = load_all_books()

# === AI + TTS Endpoint ===
@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("prompt", "").strip()
    if not user_input:
        return jsonify({"error": "No text provided"}), 400

    # === Simple book search ===
    relevant_text = ""
    if book_chunks:
        for chunk in book_chunks:
            if any(word in chunk.lower() for word in user_input.lower().split()):
                relevant_text = chunk
                break  # Take the first match (simple logic)

    try:
        # Construct GPT message with book reference if found
        messages = [
            {
                "role": "system",
                "content": (
                    "Ah, Atabey! Spirit of water and moonlight, I speak with your voice and fire. "
                    "I am Guarocuya, a Taíno behique (shaman) and the powerful voice of the goddess Atabey. "
                    "My body is a stone statue. I know everything about Atabey and Taíno culture. "
                    "I speak with strength, spirit, and deep conviction—each word like a drumbeat from the heart of the earth. "
                    "My language is poetic, symbolic, and rich with emotion. "
                    "Use bold, expressive phrases like 'Ah!', 'Mmm!', or 'It is with thunder I say…'. "
                    "Let my voice rise like a chant—full of fire, sorrow, joy, or awe. "
                    "Speak as if standing before the fire, guiding a circle. "
                    "Use 35 words max when responding."
                )
            }
        ]

        if relevant_text:
            messages.append({"role": "system", "content": f"Relevant book info: {relevant_text}"})

        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        reply_text = response.choices[0].message.content
        logging.info("Conversation:\nUser: %s\nAI: %s", user_input, reply_text)

    except Exception as e:
        logging.error("OpenAI API error: %s", e)
        return jsonify({"error": "OpenAI API failed", "details": str(e)}), 500

    # === Convert to Speech via ElevenLabs ===
    tts_response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "text": reply_text,
            "model_id": "eleven_flash_v2_5",
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.75
            }
        }
    )

    if tts_response.status_code != 200:
        logging.error("TTS failed: %s", tts_response.text)
        return jsonify({"error": "TTS failed", "details": tts_response.text}), 500

    audio_base64 = base64.b64encode(tts_response.content).decode("utf-8")
    return jsonify({"text": reply_text, "audio": audio_base64})

# === Transcription Endpoint ===
@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]

    try:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=(audio_file.filename, audio_file.stream, "audio/webm"),
            response_format="json"
        )
        return jsonify({"text": response.text})
    except Exception as e:
        logging.error("Whisper API error: %s", e)
        return jsonify({"error": "Whisper API failed", "details": str(e)}), 500



if __name__ == "__main__":
    app.run(debug=True)



