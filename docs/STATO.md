# Stato del progetto

_Ultimo aggiornamento: 2026-10-09_

## Fase attuale
**Fase 0 — Avvio.** Struttura del progetto creata. Nessun codice, nessun componente scelto.

## Fatto
- Struttura delle cartelle, direttive (`CLAUDE.md`), subagenti e comandi.
- Individuato il vincolo Bluetooth su iPad e l'approccio BLE HID (tastiera).

## Prossimi passi
1. Definire il livello di esperienza dell'utente e scriverlo in `CLAUDE.md`.
2. Scegliere i componenti del prototipo (scheda, encoder, pulsante) e l'alimentazione.
3. Prototipo di validazione: breadboard + pagina web minimale su iPad, per verificare BLE HID e tastiera a schermo.

## Problemi aperti
- Scheda: da definire (ESP32 con BLE o nRF52).
- Alimentazione: batteria o USB, da definire.
- Tastiera a schermo dell'iPad con tastiera Bluetooth collegata: serve per la ricerca video, da verificare.
- CAD: OpenSCAD o CadQuery, da decidere.
- Dimensioni della scatola: dipendono dai componenti.

## Fasi previste
0. Avvio e prototipo di validazione
1. Firmware funzionante su breadboard
2. PWA: ricerca e player controllato da tastiera
3. Scatola 3D e assemblaggio
4. Rifiniture
