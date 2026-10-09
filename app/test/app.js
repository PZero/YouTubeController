// Pagina di prova fase 0: registra eventi tastiera/media e comanda un player YouTube.
// Nessuna chiave API: usa solo la IFrame Player API (gratuita, senza chiave).
'use strict';

const SEEK_STEP = 5; // secondi per scatto (provvisorio)
const MAX_LOG = 300;

const $ = (id) => document.getElementById(id);
const logEl = $('log');
const statusEl = $('status');
const banner = $('focusBanner');
const wrap = $('playerWrap');
const overlay = $('overlay');

let player = null;
let playerReady = false;
let lastEventTime = null;
const plainLog = []; // versione testo per "Copia registro"

// ---------- registro ----------
function esc(s) {
  return String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}
function clock() {
  const d = new Date();
  return d.toLocaleTimeString('it-IT', { hour12: false }) + '.' + String(d.getMilliseconds()).padStart(3, '0');
}
function addLog(html, text) {
  const now = performance.now();
  const delta = lastEventTime === null ? '-' : Math.round(now - lastEventTime);
  lastEventTime = now;
  const prefix = `${clock()} (Δ${delta}ms)`;
  const li = document.createElement('li');
  li.innerHTML = `<span class="t">${esc(prefix)}</span> ${html}`;
  logEl.prepend(li);
  while (logEl.children.length > MAX_LOG) logEl.lastChild.remove();
  plainLog.push(`${prefix} ${text}`);
  if (plainLog.length > 2000) plainLog.shift();
}
function describeActive() {
  const a = document.activeElement;
  if (!a || a === document.body) return 'documento';
  if (a.tagName === 'IFRAME') return 'IFRAME (player)';
  if (a.id === 'focusSink') return 'documento';
  return a.tagName.toLowerCase() + (a.id ? '#' + a.id : '');
}
function setStatus(s) { statusEl.textContent = 'player: ' + s; }

// ---------- player YouTube ----------
function parseVideoId(v) {
  v = v.trim();
  const m = v.match(/(?:v=|youtu\.be\/|embed\/|shorts\/)([\w-]{11})/);
  return m ? m[1] : v;
}

function createPlayer() {
  const id = parseVideoId($('videoId').value);
  if (player) { try { player.destroy(); } catch (e) { /* ignora */ } }
  playerReady = false;
  // destroy() rimuove il div: lo ricreiamo
  if (!$('player')) {
    const d = document.createElement('div');
    d.id = 'player';
    wrap.prepend(d);
  }
  setStatus('caricamento ' + id + '...');
  player = new YT.Player('player', {
    videoId: id,
    playerVars: {
      playsinline: 1,
      controls: $('optNoControls').checked ? 0 : 1,
      disablekb: $('optDisableKb').checked ? 1 : 0,
      rel: 0,
      origin: location.origin,
    },
    events: {
      onReady: () => {
        playerReady = true;
        setStatus('pronto (' + id + ')');
        addLog('<span class="focus">PLAYER pronto</span>', 'PLAYER pronto');
      },
      onStateChange: (e) => {
        const names = { '-1': 'non avviato', 0: 'finito', 1: 'in riproduzione', 2: 'in pausa', 3: 'buffering', 5: 'pronto' };
        const n = names[e.data] || e.data;
        setStatus(n + ' - ' + fmtTime());
        addLog(`<span class="focus">STATO</span> ${esc(n)}`, 'STATO ' + n);
      },
      onError: (e) => {
        setStatus('errore ' + e.data);
        addLog(`<span class="no">ERRORE player ${esc(e.data)}</span>`, 'ERRORE player ' + e.data);
      },
    },
  });
}
function fmtTime() {
  if (!playerReady) return '';
  return player.getCurrentTime().toFixed(1) + ' / ' + (player.getDuration() || 0).toFixed(0) + ' s';
}
window.onYouTubeIframeAPIReady = createPlayer;
(function loadApi() {
  const s = document.createElement('script');
  s.src = 'https://www.youtube.com/iframe_api';
  s.onerror = () => setStatus('impossibile caricare la IFrame API (rete?)');
  document.head.appendChild(s);
})();

// ---------- azioni ----------
function doAction(name) {
  if (!playerReady) return { ok: false, msg: name + ': player non pronto' };
  if (name === 'toggle') {
    const st = player.getPlayerState();
    if (st === 1 || st === 3) { player.pauseVideo(); return { ok: true, msg: 'pausa' }; }
    player.playVideo(); return { ok: true, msg: 'play' };
  }
  if (name === 'play') { player.playVideo(); return { ok: true, msg: 'play' }; }
  if (name === 'pause') { player.pauseVideo(); return { ok: true, msg: 'pausa' }; }
  if (name === 'back' || name === 'fwd') {
    const d = name === 'fwd' ? SEEK_STEP : -SEEK_STEP;
    const t = Math.max(0, player.getCurrentTime() + d);
    player.seekTo(t, true);
    return { ok: true, msg: `${d > 0 ? '+' : ''}${d} s -> ${t.toFixed(1)} s` };
  }
  return { ok: false, msg: 'azione sconosciuta ' + name };
}
function actionHtml(r) {
  return r.ok ? ` <span class="yes">ESEGUITA: ${esc(r.msg)}</span>` : ` <span class="no">NON ESEGUITA: ${esc(r.msg)}</span>`;
}

// Mappa provvisoria: key -> azione (alcuni tasti identificati anche per code)
const KEYMAP = {
  ArrowLeft: 'back', ArrowRight: 'fwd',
  ' ': 'toggle', Enter: 'toggle', k: 'toggle', K: 'toggle',
  MediaPlayPause: 'toggle', MediaPlay: 'play', MediaPause: 'pause', MediaStop: 'pause',
  MediaTrackNext: 'fwd', MediaTrackPrevious: 'back', MediaFastForward: 'fwd', MediaRewind: 'back',
};

function isTyping(el) {
  if (!el) return false;
  return (el.tagName === 'INPUT' && el.type !== 'checkbox') || el.tagName === 'TEXTAREA';
}

function onKey(e) {
  const mods = ['ctrlKey', 'altKey', 'shiftKey', 'metaKey'].filter((m) => e[m]).map((m) => m.replace('Key', '')).join('+') || '-';
  const where = describeActive();
  const isDown = e.type === 'keydown';
  let html = `<span class="${isDown ? 'kd' : 'ku'}">${isDown ? 'KEYDOWN' : 'keyup'}</span> key="${esc(e.key)}" code=${esc(e.code)} keyCode=${e.keyCode}`
    + (e.repeat ? ' <span class="rep">REPEAT</span>' : ' repeat=no') + ` mod=${mods} focus=${esc(where)}`;
  let text = `${isDown ? 'KEYDOWN' : 'keyup'} key="${e.key}" code=${e.code} keyCode=${e.keyCode} repeat=${e.repeat} mod=${mods} focus=${where}`;

  const action = KEYMAP[e.key];
  if (isDown && action) {
    if (isTyping(e.target)) {
      html += ' <span class="t">(campo di testo: ignorato)</span>';
      text += ' (campo di testo: ignorato)';
    } else {
      e.preventDefault(); // evita scroll con Spazio e attivazione dei pulsanti con Invio
      const r = doAction(action);
      html += actionHtml(r);
      text += r.ok ? ' ESEGUITA: ' + r.msg : ' NON ESEGUITA: ' + r.msg;
    }
  } else if (!isDown && action && !isTyping(e.target)) {
    e.preventDefault();
  }
  addLog(html, text);
}
// Fase di cattura sulla window: vediamo gli eventi prima di chiunque altro
window.addEventListener('keydown', onKey, true);
window.addEventListener('keyup', onKey, true);

// ---------- Media Session (tasti consumer control) ----------
function setupMediaSession() {
  if (!('mediaSession' in navigator)) {
    addLog('<span class="no">Media Session NON supportata</span>', 'Media Session NON supportata');
    return;
  }
  const map = { play: 'play', pause: 'pause', stop: 'pause', seekforward: 'fwd', seekbackward: 'back', nexttrack: 'fwd', previoustrack: 'back' };
  const registered = [];
  for (const [act, a] of Object.entries(map)) {
    try {
      navigator.mediaSession.setActionHandler(act, (details) => {
        const r = doAction(a);
        addLog(`<span class="media">MEDIA ${esc(act)}</span> ${esc(JSON.stringify(details || {}))} focus=${esc(describeActive())}` + actionHtml(r),
          `MEDIA ${act} focus=${describeActive()} ${r.ok ? 'ESEGUITA ' : 'NON ESEGUITA '}${r.msg}`);
      });
      registered.push(act);
    } catch (err) { /* azione non supportata da questo browser */ }
  }
  addLog(`<span class="media">Media Session</span> handler registrati: ${esc(registered.join(', '))}`, 'Media Session handler: ' + registered.join(', '));
}
setupMediaSession();

// Strategia F: un <audio> silenzioso in loop rende la PAGINA "proprietaria" della sessione media
let silentAudio = null;
function silentWavUrl() {
  const rate = 8000, n = rate; // 1 s, 8 bit mono
  const buf = new ArrayBuffer(44 + n);
  const v = new DataView(buf);
  const str = (o, s) => { for (let i = 0; i < s.length; i++) v.setUint8(o + i, s.charCodeAt(i)); };
  str(0, 'RIFF'); v.setUint32(4, 36 + n, true); str(8, 'WAVEfmt ');
  v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true);
  v.setUint32(24, rate, true); v.setUint32(28, rate, true); v.setUint16(32, 1, true); v.setUint16(34, 8, true);
  str(36, 'data'); v.setUint32(40, n, true);
  for (let i = 0; i < n; i++) v.setUint8(44 + i, 128);
  return URL.createObjectURL(new Blob([buf], { type: 'audio/wav' }));
}
$('optSilentAudio').addEventListener('change', (e) => {
  if (e.target.checked) {
    if (!silentAudio) { silentAudio = new Audio(silentWavUrl()); silentAudio.loop = true; }
    silentAudio.play()
      .then(() => {
        if ('mediaSession' in navigator && window.MediaMetadata) {
          navigator.mediaSession.metadata = new MediaMetadata({ title: 'YouTubeController test' });
        }
        addLog('<span class="media">Audio silenzioso avviato</span>', 'Audio silenzioso avviato');
      })
      .catch((err) => addLog(`<span class="no">Audio silenzioso bloccato: ${esc(err.name)}</span>`, 'Audio silenzioso bloccato ' + err.name));
  } else if (silentAudio) {
    silentAudio.pause();
    addLog('<span class="media">Audio silenzioso fermato</span>', 'Audio silenzioso fermato');
  }
});

// ---------- focus ----------
function refocus(reason) {
  const a = document.activeElement;
  if (a && a.tagName === 'IFRAME') a.blur();
  window.focus();
  $('focusSink').focus({ preventScroll: true });
  if (reason) addLog(`<span class="focus">RIPRENDI FOCUS (${esc(reason)})</span> -> ${esc(describeActive())}, hasFocus=${document.hasFocus()}`,
    `RIPRENDI FOCUS (${reason}) -> ${describeActive()} hasFocus=${document.hasFocus()}`);
}
let lastFocusState = '';
function checkFocus() {
  const where = describeActive();
  const has = document.hasFocus();
  let state, cls;
  if (where === 'IFRAME (player)') { state = 'FOCUS NEL PLAYER: i tasti NON arrivano all\'app - premi "Riprendi focus"'; cls = 'bad'; }
  else if (!has) { state = 'PAGINA SENZA FOCUS (finestra in background o focus altrove)'; cls = 'bad'; }
  else if (isTyping(document.activeElement)) { state = 'FOCUS: campo di testo (' + where + ')'; cls = 'warn'; }
  else { state = 'FOCUS: pagina (i tasti arrivano all\'app)'; cls = 'ok'; }
  if (state !== lastFocusState) {
    banner.textContent = state;
    banner.className = 'banner ' + cls;
    if (lastFocusState) addLog(`<span class="focus">FOCUS</span> ${esc(where)} hasFocus=${has}`, `FOCUS ${where} hasFocus=${has}`);
    lastFocusState = state;
  }
  if ($('optAutoRefocus').checked && (where === 'IFRAME (player)' || !has) && document.visibilityState === 'visible') {
    refocus('auto');
  }
  if (playerReady && player.getPlayerState() === 1) setStatus('in riproduzione - ' + fmtTime());
}
setInterval(checkFocus, 500);
window.addEventListener('blur', () => {
  addLog(`<span class="focus">window BLUR</span> active=${esc(describeActive())}`, 'window BLUR active=' + describeActive());
  if ($('optAutoRefocus').checked) setTimeout(() => refocus('auto su blur'), 50);
  setTimeout(checkFocus, 60);
});
window.addEventListener('focus', () => { addLog('<span class="focus">window FOCUS</span>', 'window FOCUS'); checkFocus(); });
document.addEventListener('visibilitychange', () => addLog(`<span class="focus">visibilita: ${esc(document.visibilityState)}</span>`, 'visibilita ' + document.visibilityState));

// ---------- strategie ----------
$('optOverlay').addEventListener('change', (e) => {
  overlay.hidden = !e.target.checked;
  addLog(`strategia A overlay: ${e.target.checked ? 'ON' : 'OFF'}`, 'strategia A overlay ' + e.target.checked);
});
overlay.addEventListener('click', () => {
  const r = doAction('toggle');
  addLog('<span class="kd">TOCCO overlay</span>' + actionHtml(r), 'TOCCO overlay ' + r.msg);
  refocus();
});
$('optNoPointer').addEventListener('change', (e) => {
  wrap.classList.toggle('no-pointer', e.target.checked);
  addLog(`strategia B pointer-events:none: ${e.target.checked ? 'ON' : 'OFF'}`, 'strategia B ' + e.target.checked);
});
wrap.addEventListener('click', (e) => {
  // Con B attiva il tocco arriva al contenitore invece che all'iframe
  if (e.target === wrap) { const r = doAction('toggle'); addLog('<span class="kd">TOCCO contenitore player</span>' + actionHtml(r), 'TOCCO contenitore ' + r.msg); }
});
$('optAutoRefocus').addEventListener('change', (e) => addLog(`strategia C auto-refocus: ${e.target.checked ? 'ON' : 'OFF'}`, 'strategia C ' + e.target.checked));
['optNoControls', 'optDisableKb'].forEach((id) => $(id).addEventListener('change', () => addLog('opzione player cambiata: premi "Carica" per applicarla', 'opzione player cambiata')));

// ---------- pulsanti ----------
$('loadBtn').addEventListener('click', () => { if (window.YT && YT.Player) createPlayer(); refocus(); });
$('refocusBtn').addEventListener('click', () => refocus('pulsante'));
$('playBtn').addEventListener('click', () => { addLog('PULSANTE play/pausa' + actionHtml(doAction('toggle')), 'PULSANTE play/pausa'); refocus(); });
$('backBtn').addEventListener('click', () => { addLog('PULSANTE -5' + actionHtml(doAction('back')), 'PULSANTE -5'); refocus(); });
$('fwdBtn').addEventListener('click', () => { addLog('PULSANTE +5' + actionHtml(doAction('fwd')), 'PULSANTE +5'); refocus(); });
$('clearBtn').addEventListener('click', () => { logEl.innerHTML = ''; plainLog.length = 0; lastEventTime = null; refocus(); });
$('copyBtn').addEventListener('click', async () => {
  const head = `YouTubeController test - ${new Date().toISOString()}\nUA: ${navigator.userAgent}\nmodalita: ${modeText()}\n\n`;
  const txt = head + plainLog.join('\n');
  try { await navigator.clipboard.writeText(txt); addLog('<span class="yes">Registro copiato negli appunti</span>', 'registro copiato'); }
  catch (err) {
    // Ripiego: mostra il testo in un prompt da cui copiarlo a mano
    window.prompt('Copia manualmente:', txt);
  }
  refocus();
});

// ---------- modalita (Safari o app installata) ----------
function modeText() {
  const standalone = window.navigator.standalone === true || window.matchMedia('(display-mode: standalone)').matches;
  return standalone ? 'app installata (Home)' : 'browser';
}
$('mode').textContent = 'modalita: ' + modeText();
addLog(`<span class="focus">AVVIO</span> ${esc(modeText())} - ${esc(navigator.userAgent)}`, 'AVVIO ' + modeText() + ' ' + navigator.userAgent);
refocus();
checkFocus();
