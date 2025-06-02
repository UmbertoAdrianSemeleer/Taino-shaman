import os
import asyncio
import threading
import base64
import requests
import serial
import websockets
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import openai

# === Load .env settings ===
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

# === Flask App Setup ===
app = Flask(__name__)
CORS(app)

# === WebSocket Client List ===
connected_clients = set()

# === Flask Route: /ask ===
@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("prompt", "")
    if not user_input:
        return jsonify({"error": "No text provided"}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are , a Taíno behique (shaman) and the powerful voice of the goddess Atabey. "
                        "You speak with strength, spirit, and deep conviction—each word like a drumbeat from the heart of the earth. "
                        "Your language is poetic, symbolic, and rich with emotion. "
                        "Use bold, expressive phrases like 'Ah!', 'Mmm!', 'I feel it in my bones!', or 'It is with thunder I say…' "
                        "Let your voice rise like a chant—full of fire, sorrow, joy, or awe. "
                        "Speak as if standing before the fire, guiding a circle. "
                        "When asked for facts or cultural knowledge, shift into the role of an elder sage. "
                        "Use no more than three strong phrases per response. Every response must feel like spoken word."
                    )
                },
                {"role": "user", "content": user_input}
            ]
        )
        reply_text = response.choices[0].message.content

    except Exception as e:
        print("OpenAI API error:", e)
        return jsonify({"error": "OpenAI API failed", "details": str(e)}), 500

    # Convert GPT response to speech using ElevenLabs
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
        return jsonify({"error": "TTS failed", "details": tts_response.text}), 500

    audio_base64 = base64.b64encode(tts_response.content).decode("utf-8")
    return jsonify({"text": reply_text, "audio": audio_base64})

# === Flask Route: /transcribe ===
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
        print("Whisper API error:", e)
        return jsonify({"error": "Whisper API failed", "details": str(e)}), 500

# === WebSocket Server ===
async def websocket_handler(websocket, path):
    connected_clients.add(websocket)
    print("[WebSocket] Client connected.")
    try:
        async for _ in websocket:
            pass
    finally:
        connected_clients.remove(websocket)
        print("[WebSocket] Client disconnected.")

# === Arduino Serial Listener ===
async def serial_listener():
    try:
        arduino = serial.Serial("COM7", 9600)  # Update COM port if needed
        print("[Arduino] Connected to COM7")
    except Exception as e:
        print("[Arduino] Serial connection failed:", e)
        return

    while True:
        try:
            line = arduino.readline().decode().strip()
            if line == "button_pressed":
                print("[Arduino] Button pressed — triggering browser voice input.")
                for client in connected_clients.copy():
                    try:
                        await client.send("trigger_voice")
                    except:
                        connected_clients.remove(client)
        except Exception as e:
            print("[Arduino] Error reading serial:", e)

# === Run Flask in a thread ===
def run_flask():
    app.run(host="0.0.0.0", port=5000)

# === Run WebSocket & Serial ===
async def run_async_services():
    await websockets.serve(websocket_handler, "localhost", 6789)
    await serial_listener()

# === Entry Point ===
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    print("[Server] Flask running on http://localhost:5000")
    print("[Server] WebSocket running on ws://localhost:6789")
    print("[Server] Ready for Arduino button...")

    asyncio.run(run_async_services())
