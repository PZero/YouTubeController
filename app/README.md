# App (PWA)

PWA per iPad: ricerca video YouTube e player comandato dagli eventi tastiera del controller
(manopola + pulsante, che si presenta all'iPad come tastiera Bluetooth).
Nessun framework, nessuna build, nessuna dipendenza: HTML + CSS + moduli ES.

- Indirizzo: https://pzero.github.io/YouTubeController/
- Pagina di prova fase 0 (invariata): https://pzero.github.io/YouTubeController/test/

## Installazione sull'iPad
1. Apri l'indirizzo in **Safari**.
2. Condividi → **Aggiungi a schermata Home** (nome "YT Controller").
3. Apri l'app dall'icona: gira a tutto schermo, senza barre di Safari.
4. Abbina il controller (o una tastiera Bluetooth qualsiasi) in Impostazioni iPadOS → Bluetooth.
5. Nell'app: ⚙ Impostazioni → incolla la chiave **YouTube Data API v3** (solo per la ricerca).

### Chiave API (non va mai nel repository)
Google Cloud Console → nuovo progetto → Libreria → abilita "YouTube Data API v3" → Credenziali →
Crea chiave API. Consigliato: **Restrizioni applicazione = Referrer HTTP** `https://pzero.github.io/*`
e **Restrizioni API = YouTube Data API v3**. La chiave si inserisce solo nell'app e resta nel
`localStorage` del dispositivo. Quota: 10.000 unità/giorno; una ricerca costa 100 (+1 per le durate),
quindi circa 100 ricerche al giorno. Incollare un link o un ID non consuma quota.

## Mappa tasti
Definita in un solo punto: `js/keymap.js` (il firmware si allinea a questa tabella).

| Tasto | Azione |
|---|---|
| `←` / `→` | indietro / avanti, passo fine (default 1 s) |
| `Shift` + `←` / `→` | passo medio (default 5 s) |
| `Alt` + `←` / `→` | passo veloce (default 30 s) |
| `Spazio` | play / pausa (pulsante del controller) |
| `L` | loop A-B: 1ª pressione fissa A, 2ª fissa B e attiva, 3ª cancella |
| `Invio`, `K`, tasti multimediali | alias di play/pausa (innocui) |
| `F` / `Esc` | schermo pieno on/off / uscita (solo tastiera, non servono al controller) |

- Passi regolabili nelle Impostazioni.
- **Accumulo + debounce**: gli scatti si sommano, sopra il video compare "→ 12:34 (+45 s)" e un
  segno bianco sulla barra; un solo `seekTo` parte 300 ms dopo l'ultimo scatto
  (`SEEK_DEBOUNCE_MS` in `js/controls.js`). Se il video era in play continua in play.
- Tenendo premuta una freccia l'autorepeat continua a sommare; Spazio e L ignorano l'autorepeat.
- I comandi sono ignorati mentre si scrive in un campo di testo (Esc o Invio chiudono la tastiera
  e riportano i tasti ai comandi); anche con le Impostazioni aperte.
- `Cmd`/`Ctrl` + tasto non vengono mai intercettati.

### Loop A-B
Il controllo avviene ogni 100 ms (la posizione fornita dalla IFrame API si aggiorna circa ogni
250 ms: precisione ~0,25 s). Il loop riporta ad A **solo quando si supera B partendo da dentro
l'intervallo**: se salti oltre B (o prima di A) il loop resta attivo ma non interviene finché la
riproduzione non rientra in [A, B). Se B < A vengono scambiati; se sono più vicini di 0,5 s B è ignorato.

## Gesti
- **Tocco sul video**: schermo pieno on/off (un livello trasparente sopra l'iframe intercetta i tocchi).
- **Tocco / trascinamento sulla barra**: salta a quel punto.
- Pulsanti sotto il video: play/pausa, A–B (come il tasto L), stella preferito, schermo pieno.
- Tocco su un risultato o un preferito: carica e avvia il video. Stella: aggiungi/rimuovi preferito.

## Controller (Impostazioni → Controller)
Sezione **solo informativa** (sottosezioni richiudibili): l'app non può inviare comandi al
controller (niente Web Bluetooth su iPadOS; la tastiera HID va solo dal controller all'iPad).
Contenuto: tabella dei gesti fisici (con i secondi attuali dei passi), come aggiornare il firmware
(automatico dal WiFi di casa, oppure manuale: `.bin` dall'ultima Release → gesto aggiornamento →
rete `YTController-OTA` → http://192.168.4.1), configurazione/azzeramento del WiFi di casa e un
link "Apri pagina del controller". La pagina 192.168.4.1 è http: dalla PWA (https) si apre solo
come link, nessuna richiesta diretta. Dati e testi in un solo punto: `js/controller-info.js`
(da aggiornare quando cambia il firmware, ancora in sviluppo).

## Schermo pieno

Da 1.1.2 a schermo pieno il video occupa tutto lo schermo e la barra è sovrapposta in basso (si nasconde dopo 3 s, riappare a ogni comando o tocco). Opzione "Riempi" (predefinita, taglia i bordi) o "Adatta" (bande nere) nelle impostazioni.
È quello della PWA sul contenitore del player, **mai** quello nativo di YouTube (`fs=0`), che
sottrarrebbe i tasti alla pagina. Su iPadOS si usa solo il "pseudo-fullscreen" CSS
(`position: fixed; inset: 0`): nell'app installata nella Home è già a tutto schermo, non serve un
gesto utente (funziona anche da tasto) e non c'è rischio di perdere gli eventi tastiera.
Su desktop si prova anche la Fullscreen API se la richiesta parte da un clic. Con
"Entra in play, esci in pausa" (default attivo) entra all'avvio della riproduzione ed esce in pausa.

## Dati salvati
Tutto nel `localStorage` del dispositivo (chiavi `ytc.*`): impostazioni e chiave API, preferiti
(con punti A/B e ultima posizione, aggiornata ogni 5 s in play), ultimo video aperto.
**Safari e l'app installata nella Home hanno storage separati**: usa Impostazioni → Esporta/Importa
JSON per spostare i preferiti (l'esportazione apre il foglio di condivisione → "Salva su File").
L'importazione unisce per ID video. Cancellando i dati del sito in Safari si perdono anche questi.

## Limiti noti / da verificare sull'iPad
- **Primo play**: iPadOS potrebbe rifiutare l'avvio partito da un tasto (o dal tocco su un elenco)
  perché l'iframe di YouTube è di un altro dominio. Se dopo 1,2 s il video non parte compare
  "Tocca il video per avviare": il livello trasparente si disattiva e il tocco arriva direttamente al
  player YouTube. Dopo il primo avvio i tasti funzionano.
- Tasti multimediali: iPadOS può usarli per il proprio "In riproduzione" senza passarli alla pagina.
- Il service worker mette in cache solo l'interfaccia (rete prima, cache se offline): senza rete
  l'app si apre ma YouTube non funziona. Per pulire le vecchie cache incrementa `CACHE_VERSION` in `sw.js`.
- Riprendere dall'ultima posizione vale solo per i preferiti; con un loop salvato si riparte da A.
- Titoli/durata di un video aperto da link si leggono dal player dopo il caricamento.

## Struttura
```
index.html             pagina unica
manifest.webmanifest   manifest PWA (standalone, orientamento libero)
sw.js                  service worker (cache della shell, non tocca YouTube/googleapis né test/)
css/style.css          stile (scuro di default, chiaro se richiesto dal sistema)
js/main.js             avvio e collegamenti, elenchi risultati/preferiti
js/keymap.js           MAPPA TASTI centralizzata
js/controls.js         tastiera, seek con accumulo, loop A-B, barra, invito al primo play
js/player.js           wrapper IFrame Player API
js/search.js           YouTube Data API v3 + riconoscimento link/ID
js/favorites.js        preferiti + esporta/importa
js/settings.js         impostazioni e relativo dialog
js/controller-info.js  GESTI del controller, aggiornamento firmware, WiFi (solo promemoria)
js/fullscreen.js       schermo pieno (CSS su iPadOS)
js/util.js             utilità
icons/                 icon.svg (sorgente) + PNG generate
icons/make_icons.py    rigenera icon.svg e PNG (solo libreria standard Python)
test/                  pagina di prova fase 0
```

## Provare senza controller
Qualsiasi tastiera (anche quella del computer): `python -m http.server 8765` dentro `app/` e apri
http://localhost:8765/. Senza chiave la ricerca mostra l'errore; incolla un link o un ID YouTube.

## Icone
`python app/icons/make_icons.py` rigenera `icon.svg` e le PNG (180 apple-touch-icon, 167, 152,
192, 512, maskable 512 con soggetto nella zona sicura, favicon 32). Sfondo pieno, nessuna trasparenza.
Dopo averle cambiate: incrementa `CACHE_VERSION` in `sw.js` (iPadOS rilegge l'icona solo
reinstallando l'app nella Home).
