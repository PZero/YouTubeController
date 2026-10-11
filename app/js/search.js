// Ricerca con YouTube Data API v3 + riconoscimento di link/ID incollati.
// Costi quota: search.list = 100 unita', videos.list = 1 unita' (su 10.000/giorno).
import { parseIsoDuration } from './util.js';

const API = 'https://www.googleapis.com/youtube/v3/';

// Restituisce l'ID se il testo e' un link YouTube o un ID "plausibile", altrimenti null.
// Un ID nudo (11 caratteri) e' accettato solo se contiene cifre, '-' o '_' o maiuscole
// miste, per non scambiare per ID una parola di ricerca di 11 lettere.
export function parseVideoInput(text) {
  const t = (text || '').trim();
  const m = t.match(/(?:youtube(?:-nocookie)?\.com\/(?:watch\?(?:.*&)?v=|embed\/|shorts\/|live\/|v\/)|youtu\.be\/)([\w-]{11})/i);
  if (m) return m[1];
  if (/^[\w-]{11}$/.test(t) && (/[\d_-]/.test(t) || (/[A-Z]/.test(t) && /[a-z]/.test(t)))) return t;
  return null;
}

export class ApiError extends Error {}

function explain(status, body) {
  const err = body && body.error;
  const reason = err && err.errors && err.errors[0] && err.errors[0].reason;
  if (reason === 'quotaExceeded' || reason === 'dailyLimitExceeded')
    return 'Quota giornaliera della chiave API esaurita (si azzera a mezzanotte, ora del Pacifico). Puoi ancora incollare link o ID.';
  if (reason === 'keyInvalid' || (err && /API key not valid/i.test(err.message || '')))
    return 'Chiave API non valida: controllala nelle Impostazioni.';
  if (reason === 'accessNotConfigured' || reason === 'SERVICE_DISABLED')
    return 'YouTube Data API v3 non abilitata per questa chiave (Google Cloud Console → Libreria API).';
  if (reason === 'ipRefererBlocked' || reason === 'forbidden' || status === 403)
    return 'Richiesta rifiutata: la chiave ha restrizioni che non includono questo sito (' + location.host + ').';
  return `Errore della ricerca (${status}${reason ? ' ' + reason : ''}).`;
}

async function call(endpoint, params, apiKey) {
  const url = API + endpoint + '?' + new URLSearchParams({ ...params, key: apiKey });
  let res;
  try {
    res = await fetch(url, { referrerPolicy: 'strict-origin-when-cross-origin' });
  } catch (e) {
    throw new ApiError('Rete non raggiungibile: controlla la connessione.');
  }
  let body = null;
  try { body = await res.json(); } catch (e) { /* risposta non JSON */ }
  if (!res.ok) throw new ApiError(explain(res.status, body));
  return body;
}

// -> [{ id, title, channel, thumb, duration }]
export async function searchVideos(query, apiKey) {
  if (!apiKey) throw new ApiError('Per cercare serve una chiave YouTube Data API: inseriscila nelle Impostazioni. Intanto puoi incollare un link o un ID.');
  const data = await call('search', {
    part: 'snippet', type: 'video', maxResults: '25', q: query, safeSearch: 'none',
  }, apiKey);
  const items = (data.items || []).filter((it) => it.id && it.id.videoId).map((it) => ({
    id: it.id.videoId,
    title: decodeEntities(it.snippet.title),
    channel: decodeEntities(it.snippet.channelTitle),
    thumb: (it.snippet.thumbnails.medium || it.snippet.thumbnails.default || {}).url || '',
    duration: 0,
  }));
  // durate: un solo videos.list (1 unita') per tutti i risultati; se fallisce pazienza
  if (items.length) {
    try {
      const d = await call('videos', { part: 'contentDetails', id: items.map((i) => i.id).join(',') }, apiKey);
      const map = new Map((d.items || []).map((v) => [v.id, parseIsoDuration(v.contentDetails.duration)]));
      items.forEach((i) => { i.duration = map.get(i.id) || 0; });
    } catch (e) { /* durate non essenziali */ }
  }
  return items;
}

// I titoli di search.list arrivano con entita' HTML (&#39; &amp; ...)
function decodeEntities(s) {
  const t = document.createElement('textarea');
  t.innerHTML = s || '';
  return t.value;
}
