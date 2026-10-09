# Pagina di prova (fase 0)

Serve a validare l'ipotesi "controller = tastiera BLE HID" su Safari/iPadOS, **senza chiave API**
(usa solo la YouTube IFrame Player API). Nessuna build, nessuna dipendenza: `index.html`, `app.js`, `style.css`.

Indirizzo pubblicato: https://pzero.github.io/YouTubeController/test/

## Cosa fa
- Player YouTube incorporato; ID (o URL) del video modificabile, pulsante "Carica".
- Registro a schermo di tutti i `keydown`/`keyup` (key, code, keyCode, repeat, modificatori, ora, Δms dall'evento precedente, elemento con il focus) e delle azioni Media Session (play, pause, stop, seekforward, seekbackward, nexttrack, previoustrack).
- Mappa provvisoria: ArrowLeft/ArrowRight = -5/+5 s; Spazio/Invio/k = play-pausa; tasti media (MediaPlayPause, MediaTrackNext/Previous, ...) e azioni Media Session. Ogni riga dice se l'azione e' stata ESEGUITA o no.
- Banner verde/rosso sul focus (rosso se il focus e' finito nell'iframe del player o la pagina non ha il focus) e pulsante "Riprendi focus".
- Strategie confrontabili con un interruttore: A overlay trasparente sopra il player, B `pointer-events: none` sull'iframe, C recupero automatico del focus, D player senza controlli, E `disablekb=1` (D ed E si applicano premendo "Carica"), F audio silenzioso per rendere la pagina proprietaria della Media Session.
- Campo di ricerca finto per verificare la tastiera a schermo.
- Checklist di test a schermo e pulsante "Copia registro" (include user agent e modalita').

## Pubblicazione su GitHub Pages (una volta sola)
1. Su GitHub: **Settings -> Pages -> Build and deployment -> Source: GitHub Actions**.
2. Fai push su `main` (il workflow `.github/workflows/pages.yml` parte quando cambia `app/`), oppure avvialo a mano da **Actions -> "Pubblica app su GitHub Pages" -> Run workflow**.
3. Viene pubblicata SOLO la cartella `app/` (docs, firmware, enclosure non sono serviti).

Se il ramo principale non si chiama `main`, cambia `branches:` nel workflow.

## Prova in locale (senza iPad)
```
cd app
python -m http.server 8000
```
Apri http://localhost:8000/test/ e usa la tastiera del PC (frecce, Spazio, Invio, k).
Nota: alcuni video non sono incorporabili da `file://`; usa sempre un server.

## Test sull'iPad
1. Apri l'indirizzo in Safari; poi ripeti dopo "Condividi -> Aggiungi a Home" (il badge in alto dice "browser" o "app installata").
2. Segui la checklist a schermo. Alla fine premi "Copia registro" e incolla il testo nelle note.

### Cosa annotare
- Modello iPad, versione iPadOS, Safari o app installata.
- Codici esatti (key/code) inviati da manopola e pulsante; se arrivano tutti gli scatti a rotazione veloce (Δms), se compaiono REPEAT indesiderati.
- Se i tasti media arrivano come `keydown`, come riga `MEDIA`, o per niente (con e senza strategia F).
- Dopo un tocco sul video: il focus si perde? Quale strategia (A-E) lo conserva? "Riprendi focus" funziona?
- Se il primo play da controller parte senza toccare lo schermo (autoplay) e con audio.
- Tastiera a schermo: compare toccando la ricerca con la tastiera BT collegata? Si richiama col tasto globo / freccia giu'?
- Comportamento dopo blocco/sblocco, cambio app, standby del controller (tempo di riconnessione).

## Limiti noti di iPadOS da verificare
- Un tocco sull'iframe sposta il focus nel documento YouTube (cross-origin): da li' i tasti non arrivano alla pagina.
- Autoplay con audio richiede un gesto dell'utente: un tasto della tastiera fisica potrebbe non bastare per il primo play.
- La Media Session della pagina riceve i tasti media solo se e' la pagina stessa a riprodurre audio; l'audio dell'iframe YouTube potrebbe "prendersi" i comandi.
