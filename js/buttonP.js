const socket = new WebSocket("ws://localhost:8765");

socket.onopen = () => {
  document.getElementById("status").innerText = "Connected to WebSocket.";
};

socket.onmessage = async (event) => {
  if (event.data === "button_clicked") {
    document.getElementById("status").innerText = "Listening... Speak now.";
    await startVoiceInput();
  }
};

async function startVoiceInput() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    const audioChunks = [];

    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: "audio/webm" });

      const formData = new FormData();
      formData.append("audio", audioBlob, "voice.webm");

      document.getElementById("status").innerText = "Transcribing...";

      const transcribeRes = await fetch("http://localhost:5000/transcribe", {
        method: "POST",
        body: formData
      });

      const transcribeJson = await transcribeRes.json();
      const transcript = transcribeJson.text;
      console.log("Transcript:", transcript);

      if (!transcript) {
        document.getElementById("status").innerText = "No speech detected.";
        return;
      }

      document.getElementById("status").innerText = "Asking the Shaman...";
      const askRes = await fetch("http://localhost:5000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: transcript })
      });

      const askJson = await askRes.json();
      console.log("AI Response:", askJson.text);
      document.getElementById("status").innerText = askJson.text;

      const audio = new Audio("data:audio/mp3;base64," + askJson.audio);
      audio.play();
    };

    mediaRecorder.start();
    setTimeout(() => mediaRecorder.stop(), 4000); // 4 seconds max
  } catch (err) {
    console.error("Voice input error:", err);
    document.getElementById("status").innerText = "Error: " + err.message;
  }
}
