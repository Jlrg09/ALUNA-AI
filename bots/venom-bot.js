const venom = require('venom-bot');
const axios = require('axios');
const path = require('path');

// Permite configurar la ruta de Brave vía variable de entorno BRAVE_PATH.
// Usa la ruta por defecto de Windows si no está definida.
const BRAVE_PATH = process.env.BRAVE_PATH || 'C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe';
const PROFILE_DIR = path.resolve(process.cwd(), 'tokens', 'igu-brave-profile');

async function createWithBrave() {
  console.log('Iniciando Venom con Brave...');
  return venom.create(
    {
      session: 'igu-chat-session',
      multidevice: true,
      headless: false,
      useChrome: false,
      browserPathExecutable: BRAVE_PATH,
      logQR: true,
      disableSpins: true,
      autoClose: 0,
      waitForLogin: true,
      killProcessOnBrowserClose: false,
      createPathFileToken: true,
      folderNameToken: 'tokens',
      browserArgs: [
        '--disable-dev-shm-usage',
        '--start-maximized',
        '--no-first-run',
        '--no-default-browser-check',
        `--user-data-dir=${PROFILE_DIR}`,
        '--profile-directory=Default',
        '--disable-features=SameSiteByDefaultCookies,CookiesWithoutSameSiteMustBeSecure',
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
      ]
    },
    (base64Qr, asciiQR) => {
      console.log('Escanea este QR (también visible en Brave):');
      console.log(asciiQR);
    },
    (statusSession) => {
      console.log('Estado de sesión (Brave):', statusSession);
    }
  );
}

async function createWithChrome() {
  console.log('Intentando fallback con Chrome para generar QR...');
  return venom.create(
    {
      session: 'igu-chat-session',
      multidevice: true,
      headless: false,
      useChrome: true, // Fallback a Chrome por compatibilidad
      logQR: true,
      disableSpins: true,
      autoClose: 0,
      waitForLogin: true,
      killProcessOnBrowserClose: false,
      createPathFileToken: true,
      folderNameToken: 'tokens',
      browserArgs: [
        '--disable-dev-shm-usage',
        '--start-maximized',
        '--no-first-run',
        '--no-default-browser-check',
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
      ]
    },
    (base64Qr, asciiQR) => {
      console.log('Escanea este QR (fallback Chrome):');
      console.log(asciiQR);
    },
    (statusSession) => {
      console.log('Estado de sesión (Chrome):', statusSession);
    }
  );
}

async function bootstrap() {
  try {
    try {
      const client = await createWithBrave();
      return start(client);
    } catch (e) {
      console.warn('Brave no logró mostrar QR. Probando con Chrome...');
      const client = await createWithChrome();
      return start(client);
    }
  } catch (err) {
    console.error('Error al iniciar el cliente tras fallback:', err);
  }
}

bootstrap();

function start(client) {
  client.onMessage(async (message) => {
    if (!message.isGroupMsg && message.body) {
      try {
        const resp = await axios.post('http://localhost:5000/api/chat', {
          question: message.body,
          session_id: message.from
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
