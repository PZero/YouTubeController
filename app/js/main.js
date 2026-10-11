// YouTubeController - avvio e collegamento dei moduli.
import { $, fmtTime, toast, refocus, loadJson, saveJson } from './util.js';
import { settings, initSettingsDialog } from './settings.js';
import { favorites, exportFavoritesFile, importFavoritesFile } from './favorites.js';
import { parseVideoInput, searchVideos } from './search.js';
import { createPlayerController, playerErrorText, STATE } from './player.js';
import { createFullscreen } from './fullscreen.js';
import { createControls } from './controls.js';

export const APP_VERSION = '1.0.0'; // allineare a CACHE_VERSION in sw.js
const LAST_KEY = 'ytc.last.v1';

let current = null;        // { id, title, channel, thumb, duration }
let results = [];
let playSession = false;   // true dal PLAYING fino a pausa/fine (per lo schermo pieno automatico)

// ---------------- moduli ----------------
const fs = createFullscreen($('stage'), (on) => {
  $('btnFull').setAttribute('aria-label', on ? 'Esci dallo schermo pieno' : 'Schermo pieno');
});

const player = createPlayerController('player', {
  onReady: () => controls.render(),
  onState: handleState,
  onError: (code) => {
    toast(playerErrorText(code), 3500);
    controls.showPlayInvite(false);
  },
});

const controls = createControls({
  player,
  fs,
  settings,
  isDialogOpen: () => dlg.isOpen(),
  onLoopChange: (a, b) => {
    if (current && favorites.has(current.id)) favorites.update(current.id, { loopA: a, loopB: b });
  },
});

const dlg = initSettingsDialog({
  onExport: exportFavoritesFile,
  onImport: importFavoritesFile,
  onChange: () => {},
});

// ---------------- caricamento video ----------------
function loadVideo(video, { autoplay = true } = {}) {
  const fav = favorites.get(video.id);
  current = {
    id: video.id,
    title: video.title || (fav && fav.title) || '',
    channel: video.channel || (fav && fav.channel) || '',
    thumb: video.thumb || (fav && fav.thumb) || `https://i.ytimg.com/vi/${video.id}/mqdefault.jpg`,
    duration: video.duration || (fav && fav.duration) || 0,
  };
  // riprende dall'ultima posizione salvata (solo per i preferiti, se non e' quasi alla fine)
  let start = 0;
  if (fav && fav.lastPos > 5 && (!fav.duration || fav.lastPos < fav.duration - 10)) start = fav.lastPos;
  // con un loop salvato si riparte da A (altrimenti partendo oltre B il loop non interverrebbe)
  if (fav && fav.loopA !== null && fav.loopB !== null && fav.loopA !== undefined && fav.loopB !== undefined
      && (start < fav.loopA || start >= fav.loopB)) start = fav.loopA;
  playSession = false;
  $('emptyHint').hidden = true;
  player.load(video.id, { start, autoplay });
  controls.setLoop(fav ? fav.loopA : null, fav ? fav.loopB : null);
  if (autoplay) controls.armPlayCheck();
  if (start) toast(`Riprendo da ${fmtTime(start)}`);
  saveJson(LAST_KEY, current);
  updateNowPlaying();
  renderLists();
}

function updateNowPlaying() {
  $('npTitle').textContent = current ? (current.title || current.id) : 'Nessun video';
  $('npChannel').textContent = current ? current.channel : '';
  const isFav = !!(current && favorites.has(current.id));
  $('btnFav').setAttribute('aria-pressed', String(isFav));
  $('btnFav').setAttribute('aria-label', isFav ? 'Rimuovi dai preferiti' : 'Aggiungi ai preferiti');
}

function handleState(s) {
  controls.onState(s);
  // completa titolo/autore quando il video e' stato caricato da link/ID
  if (current && (s === STATE.PLAYING || s === STATE.CUED || s === STATE.PAUSED)) {
    const t = player.title(), a = player.author(), d = player.duration();
    let changed = false;
    if (t && !current.title) { current.title = t; changed = true; }
    if (a && !current.channel) { current.channel = a; changed = true; }
    if (d && !current.duration) { current.duration = d; changed = true; }
    if (changed) {
      saveJson(LAST_KEY, current);
      updateNowPlaying();
      const fav = favorites.get(current.id);
      if (fav && (fav.title === fav.id || !fav.duration)) {
        favorites.update(current.id, { title: current.title || fav.title, channel: current.channel, duration: current.duration });
      }
    }
  }
  // schermo pieno automatico: entra all'inizio della riproduzione, esce in pausa/fine
  if (s === STATE.PLAYING) {
    if (!playSession && settings.autoFullscreen) fs.enter(false);
    playSession = true;
  } else if (s === STATE.PAUSED || (s === STATE.ENDED && !controls.loop.active) || s === STATE.CUED) {
    playSession = false;
    if (settings.autoFullscreen && fs.on) fs.exit();
    saveLastPos();
  }
}

function saveLastPos() {
  if (current && favorites.has(current.id) && player.ready) {
    favorites.update(current.id, { lastPos: Math.floor(player.time()) }, true);
  }
}
setInterval(() => { if (player.state() === STATE.PLAYING) saveLastPos(); }, 5000);
window.addEventListener('pagehide', saveLastPos);
document.addEventListener('visibilitychange', () => { if (document.hidden) saveLastPos(); });

// ---------------- ricerca ----------------
let searchSeq = 0;
$('searchForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const q = $('searchInput').value.trim();
  refocus(); // chiude la tastiera a schermo e riporta i tasti ai comandi
  if (!q) return;
  const id = parseVideoInput(q);
  if (id) {
    loadVideo({ id });
    $('searchInput').value = '';
    return;
  }
  const seq = ++searchSeq;
  showTab('results');
  setStatus('Ricerca in corso…');
  try {
    const items = await searchVideos(q, settings.apiKey);
    if (seq !== searchSeq) return;
    results = items;
    setStatus(items.length ? '' : 'Nessun risultato.');
    renderLists();
  } catch (err) {
    if (seq !== searchSeq) return;
    setStatus(err.message, true);
  }
});

function setStatus(msg, isError = false) {
  const el = $('listStatus');
  el.textContent = msg;
  el.classList.toggle('error', isError);
}

// ---------------- elenchi ----------------
function showTab(which) {
  const res = which === 'results';
  $('tabResults').setAttribute('aria-selected', String(res));
  $('tabFavs').setAttribute('aria-selected', String(!res));
  $('listResults').hidden = !res;
  $('listFavs').hidden = res;
  if (!res) setStatus(favorites.all().length ? '' : 'Nessun preferito. Usa la stella sul player o nei risultati.');
  else if (!results.length && !$('listStatus').classList.contains('error')) setStatus('');
}
$('tabResults').addEventListener('click', () => showTab('results'));
$('tabFavs').addEventListener('click', () => showTab('favs'));

function videoItem(v, isFavList) {
  const li = document.createElement('li');
  li.className = 'video-item' + (current && current.id === v.id ? ' current' : '');
  li.tabIndex = -1;

  const th = document.createElement('div');
  th.className = 'thumb';
  const img = document.createElement('img');
  img.loading = 'lazy';
  img.alt = '';
  img.src = v.thumb || `https://i.ytimg.com/vi/${v.id}/mqdefault.jpg`;
  th.appendChild(img);
  if (v.duration) {
    const d = document.createElement('span');
    d.className = 'dur';
    d.textContent = fmtTime(v.duration);
    th.appendChild(d);
  }

  const meta = document.createElement('div');
  meta.className = 'meta';
  const t = document.createElement('div');
  t.className = 't';
  t.textContent = v.title || v.id;
  const c = document.createElement('div');
  c.className = 'c';
  c.textContent = v.channel || '';
  meta.append(t, c);
  if (isFavList && v.loopA !== null && v.loopB !== null && v.loopA !== undefined && v.loopB !== undefined) {
    const l = document.createElement('div');
    l.className = 'loopinfo';
    l.textContent = `Loop ${fmtTime(v.loopA)} – ${fmtTime(v.loopB)}`;
    meta.appendChild(l);
  }

  const fav = favorites.has(v.id);
  const star = document.createElement('button');
  star.type = 'button';
  star.className = 'icon-btn';
  star.setAttribute('aria-label', fav ? 'Rimuovi dai preferiti' : 'Aggiungi ai preferiti');
  star.setAttribute('aria-pressed', String(fav));
  star.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1 6.2L12 17.3 6.5 20.2l1-6.2L3 9.6l6.2-.9z"/></svg>';
  if (fav) star.querySelector('svg').style.cssText = 'fill:#ffd60a;stroke:#ffd60a';
  star.addEventListener('click', (e) => {
    e.stopPropagation();
    toggleFavorite(v);
  });

  li.append(th, meta, star);
  li.addEventListener('click', () => loadVideo(v));
  return li;
}

function renderLists() {
  $('listResults').replaceChildren(...results.map((v) => videoItem(v, false)));
  const favs = favorites.all();
  $('listFavs').replaceChildren(...favs.map((v) => videoItem(v, true)));
  $('favCount').textContent = favs.length ? String(favs.length) : '';
}

function toggleFavorite(v) {
  if (favorites.has(v.id)) {
    favorites.remove(v.id);
    toast('Rimosso dai preferiti');
  } else {
    const extra = {};
    if (current && current.id === v.id) {
      const l = controls.loop;
      extra.loopA = l.a;
      extra.loopB = l.active ? l.b : null;
      if (player.ready) extra.lastPos = Math.floor(player.time());
    }
    favorites.add(v, extra);
    toast('Aggiunto ai preferiti');
  }
}
favorites.onChange(() => { renderLists(); updateNowPlaying(); });

// ---------------- pulsanti ----------------
$('btnPlay').addEventListener('click', () => controls.toggle());
$('btnLoop').addEventListener('click', () => controls.loopStep());
$('btnFull').addEventListener('click', () => fs.toggle(true));
$('btnFav').addEventListener('click', () => { if (current) toggleFavorite(current); else toast('Nessun video caricato'); });
$('btnSettings').addEventListener('click', () => dlg.open());
// Tocco sul video: schermo pieno on/off (l'overlay evita che l'iframe riceva i tocchi)
$('tapOverlay').addEventListener('click', () => { if (current) fs.toggle(true); });

// Dopo un tocco su un pulsante (fuori dal dialog) il focus torna al documento:
// cosi' Spazio/Invio non "ripremono" il pulsante e vanno ai comandi.
document.addEventListener('click', (e) => {
  const b = e.target.closest && e.target.closest('button');
  if (b && !b.closest('dialog')) refocus();
});

// ---------------- avvio ----------------
$('appVersion').textContent = 'Versione ' + APP_VERSION;
renderLists();
const last = loadJson(LAST_KEY, null);
if (last && last.id) loadVideo(last, { autoplay: false }); // solo "cue", nessun avvio
refocus();

if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost')) {
  navigator.serviceWorker.register('sw.js').catch(() => { /* offline non disponibile */ });
}
