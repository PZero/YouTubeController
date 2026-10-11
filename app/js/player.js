// Wrapper minimo attorno alla YouTube IFrame Player API (gratuita, senza chiave).
// Controlli YouTube disattivati: comandi, barra e schermo pieno li gestisce la PWA.

export const STATE = { UNSTARTED: -1, ENDED: 0, PLAYING: 1, PAUSED: 2, BUFFERING: 3, CUED: 5 };

const PLAYER_VARS = {
  controls: 0,        // niente controlli YouTube (li fa la PWA)
  fs: 0,              // niente schermo pieno nativo: ruberebbe i tasti alla PWA
  disablekb: 1,       // il player non gestisce la tastiera
  playsinline: 1,     // su iPad niente player nativo a tutto schermo
  rel: 0,             // video correlati solo dello stesso canale
  modestbranding: 1,  // deprecato da YouTube, innocuo
  iv_load_policy: 3,  // niente annotazioni
};

let apiPromise = null;
function loadApi() {
  if (apiPromise) return apiPromise;
  apiPromise = new Promise((resolve, reject) => {
    if (window.YT && window.YT.Player) return resolve(window.YT);
    const prev = window.onYouTubeIframeAPIReady;
    window.onYouTubeIframeAPIReady = () => { if (prev) prev(); resolve(window.YT); };
    const s = document.createElement('script');
    s.src = 'https://www.youtube.com/iframe_api';
    s.onerror = () => { apiPromise = null; reject(new Error('IFrame API non caricata (rete?)')); };
    document.head.appendChild(s);
  });
  return apiPromise;
}

// Gestore unico del player. handlers: { onReady, onState(state), onError(code) }
export function createPlayerController(elementId, handlers) {
  let yt = null;
  let ready = false;
  let pending = null; // video richiesto prima che il player sia pronto

  const ctl = {
    get ready() { return ready; },
    videoId: null,

    async load(id, { start = 0, autoplay = true } = {}) {
      ctl.videoId = id;
      const req = { videoId: id, startSeconds: Math.max(0, Math.floor(start)) };
      if (!yt) {
        pending = { req, autoplay };
        const YT = await loadApi();
        if (yt) return;
        yt = new YT.Player(elementId, {
          width: '100%',
          height: '100%',
          playerVars: { ...PLAYER_VARS, origin: location.origin },
          events: {
            onReady: () => {
              ready = true;
              const p = pending; pending = null;
              if (p) p.autoplay ? yt.loadVideoById(p.req) : yt.cueVideoById(p.req);
              handlers.onReady && handlers.onReady();
            },
            onStateChange: (e) => handlers.onState && handlers.onState(e.data),
            onError: (e) => handlers.onError && handlers.onError(e.data),
          },
        });
        return;
      }
      if (!ready) { pending = { req, autoplay }; return; }
      autoplay ? yt.loadVideoById(req) : yt.cueVideoById(req);
    },

    play() { if (ready) yt.playVideo(); },
    pause() { if (ready) yt.pauseVideo(); },
    seek(t) { if (ready) yt.seekTo(Math.max(0, t), true); },
    state() { return ready ? yt.getPlayerState() : STATE.UNSTARTED; },
    time() { return ready ? (yt.getCurrentTime() || 0) : 0; },
    duration() { return ready ? (yt.getDuration() || 0) : 0; },
    title() {
      try { return (ready && yt.getVideoData && yt.getVideoData().title) || ''; } catch (e) { return ''; }
    },
    author() {
      try { return (ready && yt.getVideoData && yt.getVideoData().author) || ''; } catch (e) { return ''; }
    },
    isPlaying() {
      const s = ctl.state();
      return s === STATE.PLAYING || s === STATE.BUFFERING;
    },
  };
  return ctl;
}

export function playerErrorText(code) {
  return ({
    2: 'ID video non valido',
    5: 'Errore del player HTML5',
    100: 'Video non trovato o privato',
    101: 'Il proprietario non consente la riproduzione incorporata',
    150: 'Il proprietario non consente la riproduzione incorporata',
  })[code] || 'Errore del player (' + code + ')';
}
