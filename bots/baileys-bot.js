const makeWASocket = require('@whiskeysockets/baileys').default;
const { useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const qrcode = require('qrcode-terminal');
const P = require('pino');
const axios = require('axios');
const path = require('path');

(async () => {
  // Persist auth in tokens/baileys_auth
  const authDir = path.resolve(process.cwd(), 'tokens', 'baileys_auth');
  const { state, saveCreds } = await useMultiFileAuthState(authDir);
  const { version } = await fetchLatestBaileysVersion();

  const sock = makeWASocket({
    version,
    logger: P({ level: 'warn' }),
    printQRInTerminal: true, // QR en terminal (evita navegador)
    auth: state,
    syncFullHistory: false,
    markOnlineOnConnect: false
  });

  // Persist credentials updates
  sock.ev.on('creds.update', saveCreds);

  // Log QR explicitly too (some terminals)
  sock.ev.on('connection.update', (update) => {
    const { qr, connection, lastDisconnect } = update;
    if (qr) {
      console.log('\nEscanea este QR (Baileys):');
      qrcode.generate(qr, { small: true });
    }
    if (connection === 'close') {
      const shouldReconnect = (lastDisconnect?.error?.output?.statusCode) !== DisconnectReason.loggedOut;
      console.warn('Conexión cerrada. Reintentar:', shouldReconnect);
      if (shouldReconnect) {
        setTimeout(() => process.nextTick(() => require('child_process').spawn(process.argv[0], process.argv.slice(1), { stdio: 'inherit' })), 2000);
      } else {
        console.error('Sesión cerrada (logged out). Borra tokens/baileys_auth si quieres reiniciar.');
      }
    } else if (connection === 'open') {
      console.log('✅ Conectado a WhatsApp (Baileys).');
    }
  });

  // Mensajes entrantes -> backend
  sock.ev.on('messages.upsert', async ({ messages, type }) => {
    if (!messages || !messages.length) return;
    const msg = messages[0];
    if (!msg.message || msg.key.fromMe) return;

    try {
      const jid = msg.key.remoteJid;
      const text = msg.message?.conversation || msg.message?.extendedTextMessage?.text || '';
      if (!text.trim()) return;

      const resp = await axios.post('http://localhost:5000/api/chat', { question: text.trim() });
      const answer = resp?.data?.answer || 'No pude procesar tu pregunta.';
      await sock.sendMessage(jid, { text: answer });
    } catch (err) {
      console.error('Error al conectar con el backend:', err?.message || err);
    }
  });
})();