// Schermo pieno della PWA sul contenitore del player (#stage). MAI quello nativo di YouTube.
//
// Scelta: su iPadOS usiamo SOLO lo "pseudo-fullscreen" CSS (position:fixed; inset:0).
//  - Nell'app installata nella Home (standalone) non c'e' interfaccia del browser:
//    il fallback CSS e' gia' a tutto schermo.
//  - La Fullscreen API di iPadOS richiede un gesto utente (da tasto della tastiera
//    verrebbe rifiutata), aggiunge un pulsante "X" di sistema, si chiude con uno swipe
//    e non garantisce che gli eventi tastiera continuino ad arrivare alla pagina.
// Su desktop (prova con tastiera normale) proviamo anche la Fullscreen API, ma solo se
// la richiesta parte da un tocco/clic; se viene rifiutata resta il CSS, senza errori.

const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) ||
  (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1); // iPadOS si presenta come Mac
const isStandalone = window.matchMedia('(display-mode: standalone)').matches || navigator.standalone === true;
const useNativeApi = !isIOS && !isStandalone;

const RATIO = 16 / 9;

// getFill(): true = "Riempi" (video ritagliato, niente bande), false = "Adatta" (bande nere).
export function createFullscreen(stage, onChange, getFill = () => true) {
  let on = false;

  // Riempi: dimensiona l'iframe 16:9 in modo che copra tutto il contenitore (come object-fit: cover)
  // e lo centra; il box ha overflow:hidden e taglia l'eccesso. Adatta: l'iframe resta 100% x 100%
  // (YouTube mette le bande nere da solo).
  function layout() {
    const fill = on && getFill();
    stage.classList.toggle('fill', fill);
    const box = stage.querySelector('.video-box');
    if (!fill || !box) return;
    const W = box.clientWidth, H = box.clientHeight;
    if (!W || !H) return;
    let w = W, h = W / RATIO;
    if (h < H) { h = H; w = H * RATIO; }
    box.style.setProperty('--vw', w + 'px');
    box.style.setProperty('--vh', h + 'px');
    box.style.setProperty('--vx', (W - w) / 2 + 'px');
    box.style.setProperty('--vy', (H - h) / 2 + 'px');
  }
  window.addEventListener('resize', layout);
  window.addEventListener('orientationchange', () => setTimeout(layout, 150));

  const nativeEl = () => document.fullscreenElement || document.webkitFullscreenElement || null;

  function set(value, fromGesture = false) {
    if (value === on) return;
    on = value;
    stage.classList.toggle('fs', on);
    document.body.classList.toggle('fs-on', on);
    layout();
    if (useNativeApi) {
      try {
        if (on && fromGesture && !nativeEl()) {
          const req = stage.requestFullscreen || stage.webkitRequestFullscreen;
          const p = req && req.call(stage);
          if (p && p.catch) p.catch(() => { /* rifiutata: resta il CSS */ });
        } else if (!on && nativeEl()) {
          const exit = document.exitFullscreen || document.webkitExitFullscreen;
          const p = exit && exit.call(document);
          if (p && p.catch) p.catch(() => {});
        }
      } catch (e) { /* resta il CSS */ }
    }
    onChange && onChange(on);
  }

  // Uscita dal fullscreen nativo con Esc (desktop): sincronizza anche il CSS.
  const sync = () => { if (!nativeEl() && on) set(false); };
  document.addEventListener('fullscreenchange', sync);
  document.addEventListener('webkitfullscreenchange', sync);

  return {
    get on() { return on; },
    enter: (g) => set(true, g),
    exit: () => set(false),
    toggle: (g) => set(!on, g),
    layout,
  };
}
