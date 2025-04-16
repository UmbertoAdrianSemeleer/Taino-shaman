# app.py
from flask import Flask, request, jsonify  # Flask for web server and request handling
import requests  # Used to make API requests to ElevenLabs
import base64  # Used to encode audio data for the browser
from flask_cors import CORS  # Enable cross-origin requests for local development
import openai  # OpenAI client for GPT-based conversation
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

# Endpoint to handle user input and return spoken response
@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("prompt", "")  # Get user input from request
    if not user_input:
        return jsonify({"error": "No text provided"}), 400  # Handle empty input

    try:
        # Use OpenAI GPT-3.5 to generate a response as a Taíno shaman
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a Taíno behique (shaman) who speaks in poetic, nature-inspired language. Your role is to guide and teach with ancestral wisdom, responding calmly, humbly, and with spiritual insight. You refer to the spirits, the moon, and nature when answering. "
                },
                {"role": "user", "content": user_input}
            ]
        )
        reply_text = response.choices[0].message.content  # Extract text from OpenAI response
    except Exception as e:
        print("OpenAI API error:", e)  # Log error to terminal
        return jsonify({"error": "OpenAI API failed", "details": str(e)}), 500  # Return error response

    # Send reply to ElevenLabs API to convert text to speech
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

    # If TTS fails, return an error
    if response.status_code != 200:
        return jsonify({"error": "TTS failed", "details": response.text}), 500

    # Encode the audio as base64 for use in HTML <audio> element
    audio_base64 = base64.b64encode(response.content).decode("utf-8")

    # Return both the reply text and the base64-encoded audio
    return jsonify({"text": reply_text, "audio": audio_base64})

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
