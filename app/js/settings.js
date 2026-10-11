// Impostazioni (localStorage del dispositivo) e dialog relativo.
// La chiave API NON e' mai nel codice: la inserisce l'utente e resta in questo storage.
import { $, loadJson, saveJson, refocus } from './util.js';
import { KEYMAP } from './keymap.js';
import { renderControllerInfo } from './controller-info.js';

const KEY = 'ytc.settings.v1';
const DEFAULTS = {
  apiKey: '',
  steps: { fine: 1, medium: 5, fast: 30 },
  autoFullscreen: true,
};

const stored = loadJson(KEY, {});
export const settings = {
  ...DEFAULTS,
  ...stored,
  steps: { ...DEFAULTS.steps, ...(stored.steps || {}) },
};

export function saveSettings() {
  saveJson(KEY, settings);
}

function readStep(id, fallback) {
  const v = parseFloat(String($(id).value).replace(',', '.'));
  return isFinite(v) && v > 0 ? Math.min(v, 3600) : fallback;
}

function renderKeymap() {
  const esc = (s) => s.replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
  $('keymapTable').innerHTML = KEYMAP.map((m) =>
    `<tr><td>${m.label.split(', ').map((k) => `<kbd>${esc(k)}</kbd>`).join(' ')}</td><td>${esc(m.descr)}</td></tr>`
  ).join('') + '<tr><td>Tocco sul video</td><td>Schermo pieno on/off</td></tr>'
            + '<tr><td>Tocco sulla barra</td><td>Salta a quel punto</td></tr>';
}

// opts: { onExport(), onImport(file), onChange() }
export function initSettingsDialog(opts) {
  const dlg = $('settingsDlg');
  renderKeymap();

  function fill() {
    $('setApiKey').value = settings.apiKey;
    $('setApiKey').type = 'password';
    $('btnShowKey').textContent = 'Mostra';
    $('btnShowKey').setAttribute('aria-pressed', 'false');
    $('setStepFine').value = settings.steps.fine;
    $('setStepMed').value = settings.steps.medium;
    $('setStepFast').value = settings.steps.fast;
    $('setAutoFs').checked = settings.autoFullscreen;
    renderControllerInfo($('controllerInfo'), settings.steps);
  }

  // Salvataggio immediato a ogni modifica (niente "Salva" da dimenticare).
  function apply() {
    settings.apiKey = $('setApiKey').value.trim();
    settings.steps = {
      fine: readStep('setStepFine', DEFAULTS.steps.fine),
      medium: readStep('setStepMed', DEFAULTS.steps.medium),
      fast: readStep('setStepFast', DEFAULTS.steps.fast),
    };
    settings.autoFullscreen = $('setAutoFs').checked;
    saveSettings();
    renderControllerInfo($('controllerInfo'), settings.steps);
    opts.onChange && opts.onChange();
  }
  dlg.addEventListener('change', apply);
  dlg.addEventListener('input', (e) => { if (e.target.id === 'setApiKey') apply(); });

  // Invio in un campo del dialog: non chiudere il dialog, chiudi solo la tastiera a schermo.
  $('settingsForm').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.target.tagName === 'INPUT') {
      e.preventDefault();
      apply();
      e.target.blur();
    }
  });

  $('btnShowKey').addEventListener('click', () => {
    const inp = $('setApiKey');
    const show = inp.type === 'password';
    inp.type = show ? 'text' : 'password';
    $('btnShowKey').textContent = show ? 'Nascondi' : 'Mostra';
    $('btnShowKey').setAttribute('aria-pressed', String(show));
  });

  $('btnExport').addEventListener('click', () => opts.onExport());
  $('btnImport').addEventListener('click', () => $('importFile').click());
  $('importFile').addEventListener('change', (e) => {
    const f = e.target.files && e.target.files[0];
    if (f) opts.onImport(f);
    e.target.value = '';
  });

  dlg.addEventListener('close', () => {
    apply();
    refocus(); // i tasti tornano ai comandi
  });

  return {
    open() {
      fill();
      if (typeof dlg.showModal === 'function') dlg.showModal();
      else dlg.setAttribute('open', '');
    },
    isOpen: () => dlg.open,
  };
}
