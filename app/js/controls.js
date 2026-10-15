// Comandi: tastiera (controller), seek con accumulo+debounce, loop A-B, play/pausa,
// invito "Tocca per avviare", barra di avanzamento.
import { $, fmtTime, toast, isTyping, refocus } from './util.js';
import { resolveKey } from './keymap.js';
import { STATE } from './player.js';

// Tempo senza nuovi scatti dopo cui si invia UN solo seekTo (ms).
export const SEEK_DEBOUNCE_MS = 300;
// Dopo playVideo(), se entro questo tempo non parte, mostra "Tocca il video per avviare".
const PLAY_CHECK_MS = 1200;
// Frequenza di controllo posizione (barra + loop). getCurrentTime() della IFrame API
// e' aggiornato dall'iframe ~4 volte al secondo: precisione del loop ~0,25 s.
const TICK_MS = 100;
// B deve stare almeno a questa distanza da A
const MIN_LOOP_S = 0.5;
// In schermo pieno la barra si nasconde dopo questo tempo senza comandi (ms)
const UI_HIDE_MS = 3000;

// deps: { player, fs, settings, isDialogOpen(), onLoopChange(a, b) }
export function createControls(deps) {
  const { player, fs, settings } = deps;

  // ---------------- seek con accumulo ----------------
  let target = null;     // posizione di destinazione accumulata (s)
  let origin = 0;        // posizione all'inizio della rotazione
  let seekTimer = null;
  let indicatorTimer = null;
  const indicator = $('seekIndicator');

  function seekBy(delta) {
    if (!player.ready || !player.videoId) return;
    const dur = player.duration();
    if (target === null) origin = player.time();
    const base = target === null ? origin : target;
    target = Math.max(0, dur > 0 ? Math.min(dur, base + delta) : base + delta);
    const diff = Math.round(target - origin);
    indicator.textContent = `${diff < 0 ? '←' : '→'} ${fmtTime(target)} (${diff >= 0 ? '+' : '−'}${Math.abs(diff)} s)`;
    indicator.hidden = false;
    clearTimeout(indicatorTimer);
    clearTimeout(seekTimer);
    seekTimer = setTimeout(flushSeek, SEEK_DEBOUNCE_MS);
    render();
  }

  function flushSeek() {
    clearTimeout(seekTimer);
    if (target === null) return;
    seekTo(target);
    target = null;
    indicatorTimer = setTimeout(() => { indicator.hidden = true; }, 700);
  }

  // seekTo(t, true) mantiene lo stato: se era in play continua, se in pausa resta in pausa.
  function seekTo(t) {
    player.seek(t);
    seekGuardUntil = performance.now() + 450; // getCurrentTime() si aggiorna con ritardo
    insideLoop = loop.active && t >= loop.a - 0.3 && t < loop.b;
    render(t);
  }

  // ---------------- loop A-B ----------------
  // Comportamento: il loop riporta ad A solo quando si supera B partendo da DENTRO
  // l'intervallo [A, B). Se l'utente salta oltre B (o prima di A) il loop resta attivo
  // ma non interviene finche' la riproduzione non rientra nell'intervallo.
  const loop = { a: null, b: null, active: false };
  let insideLoop = false;
  let seekGuardUntil = 0;

  function currentPos() {
    return target !== null ? target : player.time();
  }

  function loopStep() {
    if (!player.ready || !player.videoId) return;
    if (loop.active) {
      clearLoop();
      toast('Loop cancellato');
    } else if (loop.a === null) {
      loop.a = currentPos();
      toast(`A fissato a ${fmtTime(loop.a)}`);
    } else {
      let b = currentPos();
      if (Math.abs(b - loop.a) < MIN_LOOP_S) { toast('B troppo vicino ad A: ignorato'); return; }
      let swapped = false;
      if (b < loop.a) { [b, loop.a] = [loop.a, b]; swapped = true; }
      loop.b = b;
      loop.active = true;
      toast(`Loop ${fmtTime(loop.a)} – ${fmtTime(loop.b)}${swapped ? ' (A e B scambiati)' : ''}`, 2200);
      flushSeekCancel();
      seekTo(loop.a);
    }
    loopChanged();
  }

  function flushSeekCancel() {
    clearTimeout(seekTimer);
    target = null;
    indicator.hidden = true;
  }

  function clearLoop() {
    loop.a = null; loop.b = null; loop.active = false; insideLoop = false;
  }

  function setLoop(a, b) {
    clearLoop();
    if (isFinite(a) && a !== null) loop.a = +a;
    if (loop.a !== null && isFinite(b) && b !== null && b - loop.a >= MIN_LOOP_S) {
      loop.b = +b; loop.active = true;
    }
    loopChanged(false);
  }

  function loopChanged(notify = true) {
    const btn = $('btnLoop');
    btn.classList.toggle('on-a', loop.a !== null && !loop.active);
    btn.classList.toggle('on-ab', loop.active);
    btn.setAttribute('aria-label', loop.active ? 'Loop A-B attivo: tocca per cancellare'
      : loop.a !== null ? 'A fissato: tocca per fissare B' : 'Loop A-B: tocca per fissare A');
    if (notify && deps.onLoopChange) deps.onLoopChange(loop.a, loop.active ? loop.b : null);
    render();
  }

  // ---------------- play / pausa ----------------
  let playCheckTimer = null;

  function play() {
    if (!player.ready || !player.videoId) return;
    flushSeek();
    player.play();
    armPlayCheck();
  }
  function pause() {
    flushSeek();
    player.pause();
  }
  function toggle() {
    if (!player.ready || !player.videoId) { toast('Nessun video caricato'); return; }
    if (player.isPlaying()) pause(); else play();
  }

  // iPadOS puo' rifiutare il primo play non nato da un tocco diretto sull'iframe.
  function armPlayCheck() {
    clearTimeout(playCheckTimer);
    playCheckTimer = setTimeout(() => {
      const s = player.state();
      if (s !== STATE.PLAYING && s !== STATE.BUFFERING) showPlayInvite(true);
    }, PLAY_CHECK_MS);
  }
  // Con l'invito attivo l'overlay diventa "trasparente ai tocchi": il tocco raggiunge
  // l'iframe di YouTube, che con controls=0 avvia comunque la riproduzione.
  function showPlayInvite(show) {
    $('playInvite').hidden = !show;
    $('tapOverlay').classList.toggle('passthrough', show);
  }

  // ---------------- stato player ----------------
  function onState(s) {
    if (s === STATE.PLAYING) { clearTimeout(playCheckTimer); showPlayInvite(false); }
    if (s === STATE.ENDED && loop.active && insideLoop) {
      // B coincide con la fine del video: riparti da A
      seekTo(loop.a);
      player.play();
    }
    $('btnPlay').classList.toggle('playing', s === STATE.PLAYING || s === STATE.BUFFERING);
    render();
  }

  // ---------------- ciclo periodico: loop + barra ----------------
  setInterval(() => {
    if (!player.ready || !player.videoId) return;
    const t = player.time();
    if (performance.now() < seekGuardUntil) return;
    if (loop.active && player.state() === STATE.PLAYING) {
      if (t >= loop.b && insideLoop) {
        seekTo(loop.a);
        return;
      }
      insideLoop = t >= loop.a - 0.3 && t < loop.b;
    }
    render(t);
  }, TICK_MS);

  // ---------------- barra di avanzamento ----------------
  const track = $('progressTrack');
  let dragT = null;

  function render(tNow) {
    const dur = player.ready ? player.duration() : 0;
    const t = tNow !== undefined ? tNow : (player.ready ? player.time() : 0);
    const pct = (v) => (dur > 0 ? Math.max(0, Math.min(100, (v / dur) * 100)) : 0) + '%';
    $('progFill').style.width = pct(t);
    $('timeCur').textContent = fmtTime(t);
    $('timeDur').textContent = fmtTime(dur);
    const showTarget = target !== null ? target : dragT;
    $('progTarget').hidden = showTarget === null;
    if (showTarget !== null) $('progTarget').style.left = pct(showTarget);
    const mA = $('markA'), mB = $('markB'), reg = $('progLoop');
    mA.hidden = loop.a === null || !dur;
    if (!mA.hidden) mA.style.left = pct(loop.a);
    mB.hidden = !loop.active || !dur;
    reg.hidden = mB.hidden;
    if (!mB.hidden) {
      mB.style.left = pct(loop.b);
      reg.style.left = pct(loop.a);
      reg.style.width = `calc(${pct(loop.b)} - ${pct(loop.a)})`;
    }
  }

  function posFromEvent(e) {
    const r = track.getBoundingClientRect();
    const f = Math.max(0, Math.min(1, (e.clientX - r.left) / r.width));
    return f * player.duration();
  }
  $('progress').addEventListener('pointerdown', (e) => {
    if (!player.ready || !player.duration()) return;
    e.preventDefault();
    flushSeekCancel();
    dragT = posFromEvent(e);
    try { e.currentTarget.setPointerCapture(e.pointerId); } catch (err) { /* ignora */ }
    render();
  });
  $('progress').addEventListener('pointermove', (e) => {
    if (dragT === null) return;
    dragT = posFromEvent(e);
    render();
  });
  const endDrag = () => {
    if (dragT === null) return;
    const t = dragT;
    dragT = null;
    seekTo(t);
  };
  $('progress').addEventListener('pointerup', endDrag);
  $('progress').addEventListener('pointercancel', () => { dragT = null; render(); });

  // ---------------- barra sovrapposta (schermo pieno) ----------------
  // In schermo pieno la barra sta sopra il video e si nasconde dopo UI_HIDE_MS senza comandi.
  const stageEl = $('stage');
  let uiTimer = null;
  function uiVisible() { return !stageEl.classList.contains('ui-hidden'); }
  function pokeUi() {
    clearTimeout(uiTimer);
    stageEl.classList.remove('ui-hidden');
    if (fs.on) uiTimer = setTimeout(() => stageEl.classList.add('ui-hidden'), UI_HIDE_MS);
  }
  $('progress').addEventListener('pointerdown', pokeUi, true);

  // ---------------- tastiera ----------------
  function onKeyDown(e) {
    if (deps.isDialogOpen()) return;              // il dialog gestisce i suoi tasti
    if (isTyping(e.target)) {
      if (e.key === 'Escape') refocus();          // Esc chiude la tastiera e torna ai comandi
      return;                                     // mentre si scrive i comandi sono ignorati
    }
    const m = resolveKey(e);
    if (!m) return;
    pokeUi();
    e.preventDefault();                           // niente scroll con frecce/spazio, niente clic su pulsanti
    if (e.repeat && m.action !== 'seek') return;  // tenendo premuto ripete solo il seek
    switch (m.action) {
      case 'seek': seekBy(m.dir * (settings.steps[m.speed] || 1)); break;
      case 'toggle': toggle(); break;
      case 'play': play(); break;
      case 'pause': pause(); break;
      case 'loop': loopStep(); break;
      case 'fullscreen': fs.toggle(false); break;
      case 'fsExit': fs.exit(); break;
    }
  }
  window.addEventListener('keydown', onKeyDown, true);

  return { onState, toggle, play, pause, loopStep, setLoop, armPlayCheck, pokeUi, uiVisible, showPlayInvite, render,
    get loop() { return { ...loop }; } };
}
