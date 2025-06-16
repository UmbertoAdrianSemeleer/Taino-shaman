const orb = document.getElementById('orb');
const statusText = document.getElementById('statusText');
const debugOutput = document.getElementById('debugOutput');
const audioPlayer = new Audio();
const thinkingAudio = new Audio('/static/driping water.mp3');
thinkingAudio.loop = true;
thinkingAudio.volume = 0.6;

let isRecording = false;
let audioContext, analyser, dataArray, animationFrameId;
let mediaRecorder, audioChunks = [];

async function setupMicStream() {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  setupMicVisualizer(stream);
  mediaRecorder = new MediaRecorder(stream);
  audioChunks = [];

  mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
  mediaRecorder.onstop = handleRecordingStop;
  mediaRecorder.start();
}

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
    };
  } catch (err) {
    thinkingAudio.pause();
    thinkingAudio.currentTime = 0;
    console.error('[Error]', err);
    statusText.textContent = 'Error during processing.';
    orb.className = 'orb idle';
  }
}

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
  }
}

function stopVoiceInput() {
  if (!isRecording) return;
  isRecording = false;
  mediaRecorder.stop();
}

// Input Events
orb.addEventListener('mousedown', () => startVoiceInput("orb"));
orb.addEventListener('mouseup', stopVoiceInput);
orb.addEventListener('touchstart', () => startVoiceInput("touch"));
orb.addEventListener('touchend', stopVoiceInput);

// Keyboard
document.addEventListener('keydown', (e) => {
  if ((e.key === 'Enter' || e.key === ' ') && !isRecording) {
    e.preventDefault();
    startVoiceInput("keyboard");
  }
});
document.addEventListener('keyup', (e) => {
  if (e.key === 'Enter' || e.key === ' ') {
    stopVoiceInput();
  }
});
