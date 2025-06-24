const WebSocket = require('ws');
const { SerialPort } = require('serialport');
const { ReadlineParser } = require('@serialport/parser-readline');

// ✅ Update this to match your Arduino's port
const ARDUINO_PORT = 'COM7';
const BAUD_RATE = 9600;

const port = new SerialPort({ path: ARDUINO_PORT, baudRate: BAUD_RATE });
const parser = port.pipe(new ReadlineParser({ delimiter: '\n' }));

const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', ws => {
  console.log("Browser connected to WebSocket server");
});

parser.on('data', line => {
  const message = line.trim();
  console.log("Arduino says:", message);

  // ✅ Broadcast to browser if message matches
  if (message === 'trigger_voice') {
    wss.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send("trigger_voice");
      }
    });
  }
});
