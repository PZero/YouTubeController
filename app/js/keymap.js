// Mappa tasti CENTRALIZZATA: il firmware del controller deve inviare questi tasti.
// Ogni voce: tasti accettati (valori di KeyboardEvent.key), modificatori richiesti, azione.
// Nota: con Alt (Option) premuto, su Mac/iPad e.key per le frecce resta "ArrowLeft"/"ArrowRight"
// (Option altera solo i caratteri stampabili), quindi basta leggere e.altKey.
// Le lettere invece con Option cambiano (es. Option+L = "¬"): per "l" usiamo anche e.code.

export const KEYMAP = [
  { action: 'seek', dir: -1, speed: 'fine',   keys: ['ArrowLeft'],  shift: false, alt: false, label: '←',         descr: 'Indietro (passo fine)' },
  { action: 'seek', dir: +1, speed: 'fine',   keys: ['ArrowRight'], shift: false, alt: false, label: '→',         descr: 'Avanti (passo fine)' },
  { action: 'seek', dir: -1, speed: 'medium', keys: ['ArrowLeft'],  shift: true,  alt: false, label: 'Shift + ←', descr: 'Indietro (passo medio)' },
  { action: 'seek', dir: +1, speed: 'medium', keys: ['ArrowRight'], shift: true,  alt: false, label: 'Shift + →', descr: 'Avanti (passo medio)' },
  { action: 'seek', dir: -1, speed: 'fast',   keys: ['ArrowLeft'],  shift: null,  alt: true,  label: 'Alt + ←',   descr: 'Indietro (passo veloce)' },
  { action: 'seek', dir: +1, speed: 'fast',   keys: ['ArrowRight'], shift: null,  alt: true,  label: 'Alt + →',   descr: 'Avanti (passo veloce)' },
  { action: 'toggle', keys: [' ', 'Spacebar'], label: 'Spazio', descr: 'Play / pausa (pulsante del controller)' },
  { action: 'toggle', keys: ['Enter', 'k', 'K', 'MediaPlayPause'], label: 'Invio, K, Play/Pausa multimediale', descr: 'Alias di play / pausa', alias: true },
  { action: 'play',  keys: ['MediaPlay'],  label: 'Play multimediale',  descr: 'Play', alias: true },
  { action: 'pause', keys: ['MediaPause', 'MediaStop'], label: 'Pausa/Stop multimediale', descr: 'Pausa', alias: true },
  { action: 'loop',  keys: ['l', 'L'], codes: ['KeyL'], label: 'L', descr: 'Loop A-B: 1ª fissa A, 2ª fissa B e attiva, 3ª cancella' },
  { action: 'fullscreen', keys: ['f', 'F'], codes: ['KeyF'], label: 'F', descr: 'Schermo pieno on/off (solo tastiera, non dal controller)', alias: true },
  { action: 'fsExit', keys: ['Escape'], label: 'Esc', descr: 'Esci dallo schermo pieno', alias: true },
];

// Restituisce la voce della mappa corrispondente all'evento, o null.
export function resolveKey(e) {
  if (e.metaKey || e.ctrlKey) return null; // scorciatoie di sistema (Cmd+..., Ctrl+...)
  for (const m of KEYMAP) {
    const keyOk = m.keys.includes(e.key) || (m.codes && m.codes.includes(e.code));
    if (!keyOk) continue;
    if (m.alt !== undefined && m.alt !== null && m.alt !== e.altKey) continue;
    if (m.shift !== undefined && m.shift !== null && m.shift !== e.shiftKey) continue;
    return m;
  }
  return null;
}
