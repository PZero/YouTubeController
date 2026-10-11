// Piccole utilita' condivise.

export const $ = (id) => document.getElementById(id);

// 75 -> "1:15", 3725 -> "1:02:05"
export function fmtTime(s) {
  if (!isFinite(s) || s < 0) s = 0;
  s = Math.floor(s);
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = s % 60;
  const ss = String(sec).padStart(2, '0');
  return h ? `${h}:${String(m).padStart(2, '0')}:${ss}` : `${m}:${ss}`;
}

// Durata ISO 8601 di YouTube ("PT1H2M5S") -> secondi
export function parseIsoDuration(iso) {
  const m = /^P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$/.exec(iso || '');
  if (!m) return 0;
  return (+m[1] || 0) * 86400 + (+m[2] || 0) * 3600 + (+m[3] || 0) * 60 + (+m[4] || 0);
}

// localStorage protetto: in navigazione privata o con storage pieno puo' lanciare eccezioni.
export function loadJson(key, fallback) {
  try {
    const v = localStorage.getItem(key);
    return v ? JSON.parse(v) : fallback;
  } catch (e) {
    return fallback;
  }
}
export function saveJson(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch (e) {
    toast('Impossibile salvare i dati sul dispositivo');
    return false;
  }
}

let toastTimer = null;
export function toast(msg, ms = 1800) {
  const el = $('toast');
  el.textContent = msg;
  el.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.hidden = true; }, ms);
}

// Riporta il focus al documento, cosi' i tasti tornano ai comandi
// (dopo aver usato un campo di testo o chiuso un dialog).
export function refocus() {
  const a = document.activeElement;
  if (a && a !== document.body && typeof a.blur === 'function') a.blur();
  const sink = $('focusSink');
  if (sink) sink.focus({ preventScroll: true });
}

// true se l'utente sta scrivendo: in quel caso i comandi da tastiera vanno ignorati.
export function isTyping(target) {
  const el = target && target.nodeType === 1 ? target : document.activeElement;
  if (!el) return false;
  if (el.isContentEditable) return true;
  if (el.tagName === 'TEXTAREA' || el.tagName === 'SELECT') return true;
  if (el.tagName === 'INPUT') {
    const t = (el.type || 'text').toLowerCase();
    return !['checkbox', 'radio', 'button', 'submit', 'reset', 'range', 'file', 'color'].includes(t);
  }
  return false;
}
