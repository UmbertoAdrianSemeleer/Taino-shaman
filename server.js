const { SerialPort } = require("serialport");
const { ReadlineParser } = require("@serialport/parser-readline");
const { WebSocketServer } = require("ws");

// Set up serial port
const port = new SerialPort({
  path: "COM7",
  baudRate: 9600,
});

// Use a parser to read full lines ending with newline
const parser = port.pipe(new ReadlineParser({ delimiter: "\n" }));

// Set up WebSocket server
const wss = new WebSocketServer({ port: 8765 });

wss.on("connection", (ws) => {
  console.log("Web client connected");
});

// When a full line is received
parser.on("data", (message) => {
  const trimmed = message.trim();
  console.log("Received from Arduino:", trimmed);

  if (trimmed === "button_clicked") {
    wss.clients.forEach((client) => {
      if (client.readyState === client.OPEN) {
        client.send("button_clicked");
      }
    });
  }
});
