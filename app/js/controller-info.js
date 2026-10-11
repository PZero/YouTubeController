// Informazioni sul CONTROLLER (solo promemoria): gesti fisici, aggiornamento firmware, WiFi.
// Unico punto da aggiornare quando cambia il firmware (ancora in sviluppo).
// La PWA NON comunica con il controller: niente Web Bluetooth su iPadOS e la tastiera HID va
// solo dal controller all'iPad. La pagina del controller e' http: si apre solo come link.

export const CONTROLLER_PAGE = 'http://192.168.4.1';
export const OTA_SSID = 'YTController-OTA';
export const RELEASES_URL = 'https://github.com/PZero/YouTubeController/releases/latest';
export const OTA_TIMEOUT_MIN = 5;
export const OTA_MIN_VBAT = '3,7 V';

// step: chiave in settings.steps, per mostrare i secondi attuali
export const GESTURES = [
  { gesture: 'Rotazione lenta',  step: 'fine',   descr: 'Avanti / indietro, passo fine' },
  { gesture: 'Rotazione media',  step: 'medium', descr: 'Avanti / indietro, passo medio' },
  { gesture: 'Rotazione veloce', step: 'fast',   descr: 'Avanti / indietro, passo veloce' },
  { gesture: 'Pressione breve',  descr: 'Play / pausa' },
  { gesture: 'Pressione media (0,7–2 s)', descr: 'Loop A-B: 1ª fissa A, 2ª fissa B e avvia, 3ª cancella' },
  { gesture: 'Pressione lunga (10 s)',    descr: 'Standby / risveglio' },
  { gesture: 'Pulsante premuto + 5 scatti avanti',   descr: 'Modalità aggiornamento firmware' },
  { gesture: 'Pulsante premuto + 5 scatti indietro', descr: 'Azzera il WiFi di casa' },
];

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const fmtSec = (v) => String(v).replace('.', ',') + ' s';

// steps = settings.steps attuali
export function renderControllerInfo(container, steps) {
  const rows = GESTURES.map((g) => {
    const d = g.step ? `${esc(g.descr)} (${fmtSec(steps[g.step])})` : esc(g.descr);
    return `<tr><td>${esc(g.gesture)}</td><td>${d}</td></tr>`;
  }).join('');

  // ri-render a ogni modifica dei passi: conserva le sezioni aperte
  const open = [...container.querySelectorAll('details')].map((d) => d.open);

  container.innerHTML = `
    <p class="hint">Solo promemoria: l'app non può inviare comandi al controller. I gesti dipendono dal firmware, ancora in sviluppo.</p>
    <details class="sub">
      <summary>Gesti del controller</summary>
      <table class="keymap ctrl-gestures">${rows}</table>
    </details>
    <details class="sub">
      <summary>Aggiornare il firmware</summary>
      <p class="hint"><b>Con il WiFi di casa configurato:</b> fai il gesto aggiornamento; il controller scarica da solo l'ultima versione da GitHub.</p>
      <p class="hint"><b>Senza WiFi di casa:</b></p>
      <ol class="steps">
        <li>Scarica il file <code>.bin</code> dall'<a href="${RELEASES_URL}" target="_blank" rel="noopener">ultima Release</a>.</li>
        <li>Fai il gesto aggiornamento (pulsante premuto + 5 scatti avanti).</li>
        <li>Dall'iPad collegati alla rete WiFi <code>${esc(OTA_SSID)}</code>.</li>
        <li>Apri <code>${CONTROLLER_PAGE}</code> e carica il file.</li>
      </ol>
      <p class="hint">La modalità si chiude da sola dopo ${OTA_TIMEOUT_MIN} minuti. Con batteria sotto ~${OTA_MIN_VBAT} l'aggiornamento viene rifiutato.</p>
    </details>
    <details class="sub">
      <summary>WiFi di casa</summary>
      <p class="hint">Si configura dalla stessa pagina ${CONTROLLER_PAGE}: le credenziali restano solo nel controller.
        Per azzerarlo: pulsante premuto + 5 scatti indietro, oppure "Dimentica WiFi" su quella pagina.</p>
      <div class="row"><a class="btn" href="${CONTROLLER_PAGE}" target="_blank" rel="noopener">Apri pagina del controller</a></div>
      <p class="hint">Funziona solo con l'iPad collegato alla rete <code>${esc(OTA_SSID)}</code> (controller in modalità aggiornamento).</p>
    </details>`;
  container.querySelectorAll('details').forEach((d, i) => { d.open = !!open[i]; });
}
