const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');
const path = require('path');

// Configuración de Brave (puedes sobreescribir con BRAVE_PATH)
const BRAVE_PATH = process.env.BRAVE_PATH || 'C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe';
const CHROME_PATH = process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe';

// Directorio de sesión persistente (wwebjs lo maneja, no requiere user-data-dir)
const AUTH_PATH = path.resolve(process.cwd(), 'tokens', 'wwebjs_auth');

function buildClient({ useBrave }) {
  const puppeteer = {
    headless: false,
    args: [
      '--disable-dev-shm-usage',
      '--no-first-run',
      '--no-default-browser-check',
      '--start-maximized'
    ],
    timeout: 60000
  };
  puppeteer.executablePath = useBrave ? BRAVE_PATH : CHROME_PATH;
  return new Client({
    authStrategy: new LocalAuth({ dataPath: AUTH_PATH, clientId: 'igu-bot' }),
    puppeteer,
    qrMaxRetries: 8
  });
}

function wireEvents(client, label = '') {
  client.on('qr', (qr) => {
    console.log(`\nEscanea este QR ${label ? '[' + label + ']' : ''}:`);
    qrcode.generate(qr, { small: true });
  });
  client.on('ready', () => {
    console.log(`✅ WhatsApp bot listo ${label ? '(' + label + ')' : ''}.`);
  });
  client.on('auth_failure', (msg) => {
    console.error(`❌ Falla de autenticación ${label ? '(' + label + ')' : ''}:`, msg);
  });
  client.on('disconnected', (reason) => {
    console.warn(`⚠️ Desconectado ${label ? '(' + label + ')' : ''}:`, reason);
  });
  client.on('message', async (msg) => {
    try {
      if (msg.fromMe || msg.isStatus) return;
      const text = (msg.body || '').trim();
      if (!text) return;
      const resp = await axios.post('http://localhost:5000/api/chat', { question: text, session_id: msg.from });
      const answer = (resp.data && resp.data.answer) ? resp.data.answer : 'No pude procesar tu pregunta.';
      await client.sendMessage(msg.from, answer);
    } catch (err) {
      console.error('Error al conectar con el backend:', err.message);
      try { await client.sendMessage(msg.from, 'Error al conectar con el chatbot.'); } catch (_) {}
    }
  });
}

async function main() {
  try {
    // Intento 1: Brave
    console.log('Intentando iniciar con Brave...');
    let client = buildClient({ useBrave: true });
    wireEvents(client, 'Brave');
    await client.initialize();
  } catch (err) {
    console.warn('Brave falló, intentando con Chrome por compatibilidad...', err?.message || err);
    try {
      const client = buildClient({ useBrave: false });
      wireEvents(client, 'Chrome');
      await client.initialize();
    } catch (e2) {
      console.error('No se pudo iniciar el bot con Brave ni con Chrome:', e2?.message || e2);
      process.exit(1);
    }
  }
}

main();
