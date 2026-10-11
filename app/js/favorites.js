// Preferiti in localStorage. Ogni preferito salva anche il loop A-B e l'ultima posizione.
// Attenzione: Safari e l'app installata nella schermata Home hanno storage SEPARATI.
import { loadJson, saveJson, toast } from './util.js';

const KEY = 'ytc.favorites.v1';
let list = loadJson(KEY, []);
if (!Array.isArray(list)) list = [];
const listeners = new Set();

function persist() {
  saveJson(KEY, list);
  listeners.forEach((fn) => fn());
}

export const favorites = {
  all: () => list.slice(),
  get: (id) => list.find((f) => f.id === id) || null,
  has: (id) => list.some((f) => f.id === id),
  onChange: (fn) => listeners.add(fn),

  // video: { id, title, channel, thumb, duration }
  add(video, extra = {}) {
    if (!video || !video.id || this.has(video.id)) return;
    list.unshift({
      id: video.id,
      title: video.title || video.id,
      channel: video.channel || '',
      thumb: video.thumb || `https://i.ytimg.com/vi/${video.id}/mqdefault.jpg`,
      duration: video.duration || 0,
      loopA: null,
      loopB: null,
      lastPos: 0,
      addedAt: Date.now(),
      ...extra,
    });
    persist();
  },
  remove(id) {
    list = list.filter((f) => f.id !== id);
    persist();
  },
  // aggiorna campi (loopA/loopB/lastPos/titolo...) solo se il video e' tra i preferiti
  update(id, fields, silent = false) {
    const f = list.find((x) => x.id === id);
    if (!f) return;
    Object.assign(f, fields);
    if (silent) saveJson(KEY, list); else persist();
  },

  exportJson() {
    return JSON.stringify({ app: 'YouTubeController', version: 1, exportedAt: new Date().toISOString(), favorites: list }, null, 2);
  },
  // unisce per id: i preferiti importati sostituiscono quelli con lo stesso id
  importJson(text) {
    const data = JSON.parse(text);
    const arr = Array.isArray(data) ? data : data && data.favorites;
    if (!Array.isArray(arr)) throw new Error('formato non riconosciuto');
    let n = 0;
    for (const f of arr) {
      if (!f || typeof f.id !== 'string' || !/^[\w-]{11}$/.test(f.id)) continue;
      const clean = {
        id: f.id,
        title: String(f.title || f.id),
        channel: String(f.channel || ''),
        thumb: typeof f.thumb === 'string' && f.thumb.startsWith('https://') ? f.thumb : `https://i.ytimg.com/vi/${f.id}/mqdefault.jpg`,
        duration: +f.duration || 0,
        loopA: isFinite(f.loopA) && f.loopA !== null ? +f.loopA : null,
        loopB: isFinite(f.loopB) && f.loopB !== null ? +f.loopB : null,
        lastPos: +f.lastPos || 0,
        addedAt: +f.addedAt || Date.now(),
      };
      const i = list.findIndex((x) => x.id === f.id);
      if (i >= 0) list[i] = clean; else list.push(clean);
      n++;
    }
    persist();
    return n;
  },
};

// Esporta come file: su iPad usa il foglio di condivisione (Salva su File) se disponibile,
// altrimenti un normale download.
export async function exportFavoritesFile() {
  const text = favorites.exportJson();
  const name = `ytcontroller-preferiti-${new Date().toISOString().slice(0, 10)}.json`;
  try {
    const file = new File([text], name, { type: 'application/json' });
    if (navigator.canShare && navigator.canShare({ files: [file] })) {
      await navigator.share({ files: [file], title: 'Preferiti YouTubeController' });
      return;
    }
  } catch (e) {
    if (e && e.name === 'AbortError') return; // condivisione annullata dall'utente
  }
  const url = URL.createObjectURL(new Blob([text], { type: 'application/json' }));
  const a = document.createElement('a');
  a.href = url;
  a.download = name;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 5000);
  toast('Preferiti esportati');
}

export async function importFavoritesFile(file) {
  try {
    const n = favorites.importJson(await file.text());
    toast(`Importati ${n} preferiti`);
  } catch (e) {
    toast('File non valido: ' + e.message, 3000);
  }
}
