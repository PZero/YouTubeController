# Stato del progetto

_Ultimo aggiornamento: 2026-10-09_

## Fase attuale
**Fase 0 — Avvio e scelta componenti.** Componenti principali in possesso (scheda in arrivo); architettura di alimentazione definita; scatola di partenza fornita dall'utente.

## Fatto
- Utente: esperienza discreta; stampante Bambu Lab A1 mini; CAD OpenSCAD (scritto in `CLAUDE.md`).
- Script scatola dell'utente salvato in `enclosure/youtube_control.scad` (compila; layout di stampa 184×189 mm, **non entra** nel piatto 180×180).
- Repository git inizializzato (autore locale fnicora).
- Scheda ESP32-S3 SuperMini: quote dal disegno ufficiale Nologo (23,5×18 mm, 2×9 pin), pinout, GPIO proposti (encoder 4/5, push encoder 6, tasto 7), note firmware.
- Alimentazione: 18650 → modulo TP4056 USB-C con protezione (B+/B-) → OUT+/OUT- sul pin 5V/GND della scheda. Boost MT3608 scartato.
- Riconosciuti: encoder tipo EC11 con pulsante e **albero zigrinato**; pulsante da pannello tipo PBS-110 (M7, dado).
- Ricerca datasheet/quote di TP4056, encoder e pulsante affidata a `elettronica-firmware` (in corso a fine sessione: verificare che BOM, `dimensioni.md` e `firmware/README.md` siano aggiornati).

## Prossimi passi
1. Rivedere il riepilogo dei tre componenti e le modifiche richieste allo script `.scad`.
2. Progettare con `design-3d` il **portaschede** avvitato al fondo (scheda, TP4056, 18650) e adeguare la scocca (encoder zigrinato, pulsante PBS-110, presa USB-C del TP4056).
3. Prototipo su breadboard: firmware BLE HID + pagina di test su iPad (tasti ricevuti, focus sul player, tastiera a schermo).

## Problemi aperti
- Ricarica Qi: tenere o togliere la sede sul fondo (in attesa dell'utente).
- Portabatteria 18650: modello da definire / foto da ricevere.
- Manopola: foro a D da sostituire con foro zigrinato (o boccola).
- Pulsante: sostituisce switch 6×6 + cap + bracket; verificare spazio sotto il piano inclinato.
- Ruolo dei pulsanti: push dell'encoder = play/pausa? tasto separato = OTA/altro?
- Primo flash via USB: scollegare la batteria (rischio retroalimentazione su OUT+).
- Misurare col calibro: spessore PCB e sporgenza USB-C della SuperMini; quote del TP4056.
- Layout di stampa da compattare o stampare per pezzi.
- Scritte sulla scocca: "YOYO CONTROL" (refuso?) e "SELECT".
- OTA via WiFi: proposta modalità access point con pressione lunga (da confermare).

## Fasi previste
0. Avvio e prototipo di validazione
1. Firmware funzionante su breadboard
2. PWA: ricerca e player controllato da tastiera
3. Scatola 3D (scocca + portaschede modulare) e assemblaggio
4. Rifiniture
