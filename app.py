from flask import Flask, request, jsonify
import requests
import base64
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv

# LangChain vector search
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# === Load environment variables ===
load_dotenv()

app = Flask(__name__)
CORS(app)

# === API keys ===
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

# === Load Vector DB ===
embedding_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
vectorstore = FAISS.load_local(
    "shaman_index",
    embedding_model,
    allow_dangerous_deserialization=True
)
# === AI + TTS Endpoint ===
@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("prompt", "")
    if not user_input:
        return jsonify({"error": "No text provided"}), 400

    try:
        # === Search the vector DB for relevant knowledge ===
        results = vectorstore.similarity_search(user_input, k=3)
        context = "\n\n".join([r.page_content for r in results])

        # === Poetic system prompt + document context ===
        system_prompt = (
            "You are a Taíno behique (shaman) and the powerful voice of the goddess Atabey. "
            "You speak with strength, spirit, and deep conviction—each word like a drumbeat from the heart of the earth. "
            "Your language is poetic, symbolic, and rich with emotion. "
            "Use bold, expressive phrases like 'Ah!', 'Mmm!', 'I feel it in my bones!', or 'It is with thunder I say…' "
            "Let your voice rise like a chant—full of fire, sorrow, joy, or awe. "
            "Speak as if standing before the fire, guiding a circle. "
            "When asked for facts or cultural knowledge, shift into the role of an elder sage. "
            "Use no more than three strong phrases per response. Every response must feel like spoken word.\n\n"
            "Use the following Taíno cultural knowledge to guide your answer:\n"
            f"{context}"
        )

        # === Call GPT ===
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )
        reply_text = response.choices[0].message.content

    except Exception as e:
        print("OpenAI API error:", e)
        return jsonify({"error": "OpenAI API failed", "details": str(e)}), 500

    # === Convert GPT text to speech with ElevenLabs ===
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
        print("Whisper API error:", e)
        return jsonify({"error": "Whisper API failed", "details": str(e)}), 500

# === Run Server ===
if __name__ == "__main__":
    app.run(debug=True)
