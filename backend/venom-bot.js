const venom = require('venom-bot');
const axios = require('axios');

venom
  .create({
    session: 'igu-chat-session',
    headless: true,
    executablePath: 'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--headless=new']
  })
  .then((client) => start(client))
  .catch((error) => {
    console.error('Error al crear el cliente:', error);
  });

function start(client) {
  client.onMessage(async (message) => {
    if (!message.isGroupMsg && message.body) {
      try {
        const resp = await axios.post('http://localhost:5000/api/chat', {
          question: message.body
        });
        const answer = resp.data.answer || 'No pude procesar tu pregunta.';
        await client.sendText(message.from, answer);
      } catch (err) {
        console.error('Error al conectar con el backend:', err);
        await client.sendText(message.from, 'Error al conectar con el chatbot.');
      }
    }
  });
}
