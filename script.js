const homePage = document.getElementById('homePage');
const textChatPage = document.getElementById('textChatPage');
const voiceChatPage = document.getElementById('voiceChatPage');
const homeBtn = document.getElementById('homeBtn');
const sendBtn = document.getElementById('sendBtn');
const textInput = document.getElementById('textInput');
const chatMessages = document.getElementById('chatMessages');
const micBtn = document.getElementById('micBtn');
const statusText = document.getElementById('statusText');
const loadingDots = document.getElementById('loadingDots');

function navigateTo(page) {
  homePage.classList.add('hidden');
  textChatPage.classList.add('hidden');
  voiceChatPage.classList.add('hidden');

  if (page === 'text') {
    textChatPage.classList.remove('hidden');
  } else if (page === 'voice') {
    voiceChatPage.classList.remove('hidden');
  } else {
    homePage.classList.remove('hidden');
  }
}

homeBtn.addEventListener('click', () => navigateTo('home'));

sendBtn.addEventListener('click', () => {
  const message = textInput.value.trim();
  if (!message) return;

  addMessage(message, 'user');
  textInput.value = '';
  sendBtn.disabled = true;

  setTimeout(() => {
    addMessage("This is a mock AI response.", 'bot');
    sendBtn.disabled = false;
  }, 1000);
});

function addMessage(text, sender) {
  const msg = document.createElement('div');
  msg.classList.add('message', sender);
  msg.textContent = text;
  chatMessages.appendChild(msg);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

let isRecording = false;

function startRecording() {
  isRecording = true;
  micBtn.classList.add('recording');
  statusText.textContent = "Recording...";
  loadingDots.classList.remove('hidden');
}

function stopRecording() {
  if (!isRecording) return;
  isRecording = false;
  micBtn.classList.remove('recording');
  statusText.textContent = "Processing...";
  loadingDots.classList.add('hidden');

  setTimeout(() => {
    statusText.textContent = "AI says: Hello there!";
  }, 1000);
}

// Support both mouse and touch
micBtn.addEventListener('mousedown', startRecording);
micBtn.addEventListener('mouseup', stopRecording);
micBtn.addEventListener('touchstart', (e) => {
  e.preventDefault(); // prevent duplicate events
  startRecording();
}, { passive: false });
micBtn.addEventListener('touchend', (e) => {
  e.preventDefault();
  stopRecording();
}, { passive: false });
