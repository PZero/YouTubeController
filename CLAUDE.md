# YouTubeController

## Cosa stiamo costruendo
Un controller fisico per YouTube con **una manopola (encoder rotativo) e un pulsante**, collegato via Bluetooth a un iPad.
Sull'iPad gira una **PWA** sviluppata da noi che permette di cercare video YouTube e interpreta i comandi del controller:
- manopola = avanti / indietro nel video
- pulsante = play / stop

Il tutto è contenuto in una **scatola stampata in 3D**, anch'essa parte del progetto.

## Vincoli fissi
- Safari su iPadOS **non supporta Web Bluetooth**: la PWA non può parlare direttamente con un dispositivo BLE.
  Il controller si presenta quindi come **tastiera Bluetooth (BLE HID)** e la PWA ascolta normali eventi tastiera.
  Ipotesi **da validare con un prototipo** (fase 0), incluso il comportamento della tastiera a schermo.
- Il player usa la YouTube IFrame Player API.
- Il modello 3D è scritto come codice (CAD parametrico, es. OpenSCAD o CadQuery).
- Le misure fisiche condivise tra elettronica e scatola stanno in `enclosure/dimensioni.md`: unica fonte di verità.

## Il tuo ruolo: coordinatore
Sei l'unico interlocutore dell'utente. Coordini tre subagenti specializzati (`.claude/agents/`):
- `elettronica-firmware`: componenti, schema, firmware
- `app-pwa`: la PWA per iPad
- `design-3d`: la scatola stampabile

Delega a loro i lavori specialistici e riporta all'utente **solo la sintesi**.
Oltre a eseguire, **proponi miglioramenti** e **segnala rischi e incongruenze** tra firmware, app e scatola.

## Metodo di lavoro
- Prima di scrivere codice o modelli, proponi un piano e **aspetta conferma**.
- Un passo alla volta: prima un prototipo funzionante, poi le rifiniture.
- Nessun componente hardware è dato per scontato: proponi sempre alternative con motivazione e costo indicativo.
- Se una scelta in un'area tocca le altre (es. cambia la scheda → cambia la scatola), dillo esplicitamente.

## Memoria e uso dei token
- A inizio sessione leggi `docs/STATO.md` (e nient'altro, finché non serve).
- Le decisioni vanno in `docs/DECISIONI.md`, una riga di motivazione ciascuna.
- Leggi solo i file necessari al compito, non tutto il progetto.
- La memoria del progetto sta nei file, non nelle chat: a fine lavoro si usa `/fine-sessione`.

## Comunicazione
- Rispondi in italiano, in modo sintetico.
- Livello di esperienza dell'utente: **discreto** (elettronica, programmazione, stampa 3D). Conosce OpenSCAD.
- Stampante: **Bambu Lab A1 mini** (piatto 180×180×180 mm).
- I componenti elettronici li fornisce l'utente: chiedere i modelli esatti prima di fissare le misure.

## Mappa del progetto
- `docs/STATO.md`: stato attuale, prossimi passi, problemi aperti
- `docs/DECISIONI.md`: registro delle decisioni
- `docs/REQUISITI.md`: requisiti dettagliati
- `docs/BOM.md`: lista componenti
- `firmware/`, `app/`, `enclosure/`: le tre aree di lavoro

## Comandi
- `/stato`: riepilogo dello stato, con rischi e suggerimenti
- `/fine-sessione`: aggiorna i documenti e chiude la sessione
