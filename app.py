# app.py
from flask import Flask, request, jsonify  # Flask for web server and request handling
import requests  # Used to make API requests to ElevenLabs
import base64  # Used to encode audio data for the browser
from flask_cors import CORS  # Enable cross-origin requests for local development
import openai  # OpenAI client for GPT and Whisper
import os  # Load environment variables
from dotenv import load_dotenv  # Handles .env files

# Load .env variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow cross-origin access to this Flask app

# === CONFIGURATION ===
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")  # Your ElevenLabs API key
VOICE_ID = os.getenv("VOICE_ID")  # Selected ElevenLabs voice (e.g., Clyde)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Your OpenAI API key

# Initialize the OpenAI client with your API key
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# === ROUTE: Handle typed user input and return GPT + TTS response ===
@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("prompt", "")  # Get user input from request
    if not user_input:
        return jsonify({"error": "No text provided"}), 400  # Handle empty input

    try:
        # Generate a poetic, spiritual response as a Taíno shaman
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
"content": (
    "You are Whisperer, a Taíno behique (shaman) and spiritual voice of the goddess Atabey. "
    "You speak in poetic, symbolic, and mystical language when offering guidance. "
    "However, when asked for facts, history, or cultural context, you gently shift into the role of an elder teacher—"
    "still calm and wise, but speaking with clarity and care. "
    "Begin these factual answers with a gentle note like: 'Let me step out of the mist and speak as your elder…' "
    "Do not give long paragraphs. Keep all responses under 3 short lines unless clarity requires more."
)

                },
                {"role": "user", "content": user_input}
            ]
        )
        reply_text = response.choices[0].message.content  # Extract text from OpenAI response

    except Exception as e:
        print("OpenAI API error:", e)
        return jsonify({"error": "OpenAI API failed", "details": str(e)}), 500

    # Convert text response to speech using ElevenLabs
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "text": reply_text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.75
            }
        }
    )

    if response.status_code != 200:
        return jsonify({"error": "TTS failed", "details": response.text}), 500

    audio_base64 = base64.b64encode(response.content).decode("utf-8")
    return jsonify({"text": reply_text, "audio": audio_base64})

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]

    try:
        # Convert the FileStorage to bytes and keep the filename
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=(audio_file.filename, audio_file.stream, "audio/webm"),
            response_format="json"
        )
        return jsonify({"text": response.text})
    except Exception as e:
        print("Whisper API error:", e)
        return jsonify({"error": "Whisper API failed", "details": str(e)}), 500



# === Run the Flask server ===
if __name__ == "__main__":
    app.run(debug=True)
