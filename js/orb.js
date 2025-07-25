const orb = document.getElementById('orb');
const statusText = document.getElementById('statusText');
const debugOutput = document.getElementById('debugOutput');
const audioPlayer = new Audio();
const thinkingAudio = new Audio('/static/driping water.mp3');
thinkingAudio.loop = true;
thinkingAudio.volume = 0.6;

let isRecording = false;
let isBusy = false;  // ✅ Prevent repeated triggers
let audioContext, analyser, dataArray, animationFrameId;
let mediaRecorder, audioChunks = [];

// === WebSocket for Arduino trigger ===
const ws = new WebSocket("ws://localhost:8080");

ws.onopen = () => console.log("WebSocket connected to Arduino");
ws.onmessage = (event) => {
  if (event.data === "trigger_voice") {
    if (isBusy) {
      console.log("Ignored: already processing");
      return;
    }

    console.log("Arduino button pressed → startVoiceInput()");
    isBusy = true;
    startVoiceInput("arduino");

    // Failsafe: auto-stop after 6 seconds if needed
    setTimeout(() => {
      if (isRecording) stopVoiceInput();
    }, 6000);
  }
};

// === Microphone setup ===
async function setupMicStream() {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  setupMicVisualizer(stream);
  mediaRecorder = new MediaRecorder(stream);
  audioChunks = [];

  mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
  mediaRecorder.onstop = handleRecordingStop;
  mediaRecorder.start();
}

// === Orb animation ===
function setupMicVisualizer(stream) {
  audioContext = new (window.AudioContext || window.webkitAudioContext)();
  const source = audioContext.createMediaStreamSource(stream);
  analyser = audioContext.createAnalyser();
  analyser.fftSize = 512;
  dataArray = new Uint8Array(analyser.frequencyBinCount);
  source.connect(analyser);
  animateOrb();
}

function animateOrb() {
  analyser.getByteFrequencyData(dataArray);
  const avg = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
  const scale = 1 + avg / 256;
  orb.style.transform = `scale(${scale.toFixed(2)})`;
  animationFrameId = requestAnimationFrame(animateOrb);
}

function stopVisualizer() {
  cancelAnimationFrame(animationFrameId);
  if (audioContext) audioContext.close();
  orb.style.transform = 'scale(1)';
}

// === Handle stop and AI response ===
async function handleRecordingStop() {
  stopVisualizer();
  orb.className = 'orb processing';
  statusText.textContent = 'Processing...';

  thinkingAudio.currentTime = 0;
  thinkingAudio.play();

  const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.webm');

  try {
    const transcriptRes = await fetch('http://localhost:5000/transcribe', { method: 'POST', body: formData });
    const transcriptData = await transcriptRes.json();

    const aiRes = await fetch('http://localhost:5000/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: transcriptData.text })
    });
    const aiData = await aiRes.json();

    thinkingAudio.pause();
    thinkingAudio.currentTime = 0;

    orb.className = 'orb speaking';
    statusText.textContent = 'Speaking...';
    debugOutput.textContent = `You said: "${transcriptData.text}"\nShaman: "${aiData.text}"`;

    audioPlayer.src = 'data:audio/mp3;base64,' + aiData.audio;
    audioPlayer.play();
    audioPlayer.onended = () => {
      orb.className = 'orb idle';
      statusText.textContent = 'Click or press a key to speak';
      isBusy = false;  // ✅ Unlock after speaking
    };
  } catch (err) {
    thinkingAudio.pause();
    thinkingAudio.currentTime = 0;
    console.error('[Error]', err);
    statusText.textContent = 'Error during processing.';
    orb.className = 'orb idle';
    isBusy = false;  // ✅ Make sure it's unlocked on error
  }
}

// === Start voice recording ===
async function startVoiceInput(source = "UI") {
  if (isRecording) return;
  isRecording = true;
  orb.className = 'orb recording';
  statusText.textContent = 'Recording... Speak now';

  try {
    await setupMicStream();
  } catch (err) {
    console.error('[Mic] Access error:', err);
    statusText.textContent = 'Mic access denied';
    orb.className = 'orb idle';
    isRecording = false;
    isBusy = false;  // ✅ Unlock if failed to start
  }
}

function stopVoiceInput() {
  if (!isRecording) return;
  isRecording = false;
  mediaRecorder.stop();
}

// === Input Events ===
orb.addEventListener('mousedown', () => {
  if (!isBusy) {
    isBusy = true;
    startVoiceInput("orb");
  }
});
orb.addEventListener('mouseup', stopVoiceInput);
orb.addEventListener('touchstart', () => {
  if (!isBusy) {
    isBusy = true;
    startVoiceInput("touch");
  }
});
orb.addEventListener('touchend', stopVoiceInput);

// === Keyboard Events ===
document.addEventListener('keydown', (e) => {
  if ((e.key === 'Enter' || e.key === ' ') && !isRecording && !isBusy) {
    e.preventDefault();
    isBusy = true;
    startVoiceInput("keyboard");
  }
});
document.addEventListener('keyup', (e) => {
  if (e.key === 'Enter' || e.key === ' ') {
    stopVoiceInput();
  }
});
