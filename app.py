# === Import required libraries ===
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI  # OpenAI SDK (v1.83.0)
import requests
import base64
import os
import logging
from dotenv import load_dotenv
from glob import glob
import fitz  # PyMuPDF for reading PDFs

# === Load environment variables from .env file ===
load_dotenv()

# === Logging configuration ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("ai_conversations.log"),  # Log to file
        logging.StreamHandler()  # Log to console
    ]
)

# === Flask application setup ===
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# === API keys and IDs ===
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# === OpenAI client setup ===
client = OpenAI(api_key=OPENAI_API_KEY)

# === Directory where books are stored ===
BOOK_FOLDER = "books"

# === Utility function: Extract text from PDF ===
def extract_text_from_pdf(pdf_path):
    """Extracts text from each page of a PDF file using PyMuPDF."""
    doc = fitz.open(pdf_path)
    return "\n".join(page.get_text() for page in doc)

# === Utility function: Split long text into chunks ===
def split_text(text, chunk_size=500):
    """Splits text into smaller chunks for easier searching."""
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

# === Load all books into memory on startup ===
def load_all_books():
    """Reads and splits all .pdf and .txt files from the BOOK_FOLDER."""
    texts = []
    for filepath in glob(f"{BOOK_FOLDER}/*"):
        if filepath.lower().endswith(".pdf"):
            text = extract_text_from_pdf(filepath)
        elif filepath.lower().endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            continue  # Skip unsupported file types
        chunks = split_text(text)
        texts.extend(chunks)
    return texts

# === Preloaded book chunks for basic semantic search ===
book_chunks = load_all_books()

# === Main AI + TTS Endpoint ===
@app.route("/ask", methods=["POST"])
def ask():
    """
    Accepts a JSON request with a 'prompt',
    sends it to GPT with optional book context,
    and returns a spoken audio reply using ElevenLabs TTS.
    """
    user_input = request.json.get("prompt", "").strip()
    if not user_input:
        return jsonify({"error": "No text provided"}), 400

    # === Simple keyword-based relevance search ===
    relevant_text = ""
    if book_chunks:
        for chunk in book_chunks:
            if any(word in chunk.lower() for word in user_input.lower().split()):
                relevant_text = chunk
                break  # Take the first match (basic method)

    # === Construct GPT messages ===
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
        messages.append({
            "role": "system",
            "content": f"Relevant book info: {relevant_text}"
        })

    messages.append({"role": "user", "content": user_input})

    # === Call OpenAI GPT for response ===
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        reply_text = response.choices[0].message.content
        logging.info("Conversation:\nUser: %s\nAI: %s", user_input, reply_text)
    except Exception as e:
        logging.error("OpenAI API error: %s", e)
        return jsonify({"error": "OpenAI API failed", "details": str(e)}), 500

    # === Convert GPT reply to speech using ElevenLabs ===
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

# === Transcription Endpoint (Whisper) ===
@app.route("/transcribe", methods=["POST"])
def transcribe():
    """
    Accepts an audio file (WebM) and transcribes it using OpenAI Whisper API.
    """
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

# === Run the Flask server ===
if __name__ == "__main__":
    app.run(debug=True)
