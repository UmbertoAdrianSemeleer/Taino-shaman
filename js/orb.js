// Get references to HTML elements
const orb = document.getElementById('orb');             // The visual orb element
const statusText = document.getElementById('statusText'); // Text element to show status like "Recording..." etc.
const debugOutput = document.getElementById('debugOutput'); // Element to show debug info like what the user said
const audioPlayer = new Audio();                         // Used to play back the spoken AI response

// Set up state variables
let isRecording = false;                                 // Tracks if the mic is recording
let audioContext, analyser, dataArray, animationFrameId; // For mic visualizer
let mediaRecorder, audioChunks = [];                     // For recording mic audio

// Ask the browser to access the microphone
async function setupMicStream() {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true }); // Ask for mic access
  setupMicVisualizer(stream);                    // Start the visualizer (the orb changes size with sound)
  mediaRecorder = new MediaRecorder(stream);     // Create a recorder from the mic stream
  audioChunks = [];                              // Reset recorded audio chunks

  // Save audio data as it's recorded
  mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

  // When recording stops, process the audio
  mediaRecorder.onstop = handleRecordingStop;

  // Start recording
  mediaRecorder.start();
}

// Set up mic visual feedback (orb changes size with voice volume)
function setupMicVisualizer(stream) {
  audioContext = new (window.AudioContext || window.webkitAudioContext)(); // Create audio context
  const source = audioContext.createMediaStreamSource(stream);             // Use mic as input
  analyser = audioContext.createAnalyser();                                // Analyze sound volume
  analyser.fftSize = 512;
  dataArray = new Uint8Array(analyser.frequencyBinCount);                 // Data array for frequencies
  source.connect(analyser);                                               // Connect mic to analyzer
  animateOrb();                                                           // Start animation loop
}

// An
