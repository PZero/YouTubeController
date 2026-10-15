# Stato del progetto

_Ultimo aggiornamento: 2026-10-15_

## Fase attuale
**Fase 1 quasi chiusa, assemblaggio V1 in corso.** Firmware v0.1.3 funzionante con l'iPad; PWA 1.1.4; scatola V1 pronta da stampare.

## Fatto
- Fase 0: tastiera BLE su iPad validata.
- **Firmware v0.1.3** (`firmware/controller/`): tastiera BLE HID che funziona con l'iPad (cifratura e bonding, ricollegamento automatico), encoder in interrupt (20 scatti/giro), 3 velocità, gesti (breve, media, 10 s, OTA, reset WiFi), anello LED, vibrazione a ogni scatto (impulsi a piena potenza da 60 ms), portale WiFi, OTA manuale `/update`, **autospegnimento dopo 5 min** con conto alla rovescia rosso (32 s) e risveglio tenendo premuto 2 s. Log seriale + `monitor.html` (Web Serial).
- Prove su breadboard: `firmware/test_comandi/` (encoder, pulsante, anello, vibrazione).
- **PBS-110 eliminato**: si usa il pulsante integrato dell'encoder (GPIO7).
- **PWA 1.1.4**: video predefinito all'avvio, schermo pieno senza bande (modalità Riempi) con barra a scomparsa, focus sempre ai comandi in schermo pieno, aggiornamento automatico anche dall'icona Home.
- **Scatola V1** (`enclosure/`, zip in `enclosure/export/`): vibrazione agganciata sotto la faccia superiore, millefori libera nella corsia sinistra (max ~22,8×60×15), fronte liscio, USB-C del TP4056 sul retro, interferenze 0. Colori: corpo nero, manopola/pannelli rame, diffusore bianco, prove in grigio.
- **V1 elettronica semplificata** (come nei test): anello e vibrazione dal pin 5V (= batteria), niente transistor né lettura carica; interruttore interno sul + al posto del diodo.
- Millefori 8×20 con SuperMini saldata progettata e verificata (`firmware/millefori/`, per la versione completa).
- **PCB JLCPCB v1** pronto (`pcb/jlcpcb/`: Gerber, BOM, CPL corretti, DRC 0): **ordine rimandato** (~40 € con spedizione).

## Prossimi passi
1. Finire la prova della sospensione: spegnimento a 5 min e risveglio (pressione breve = niente, 2 s = accende).
2. Misurare lo spessore PCB del modulo vibrazione, poi stampare la scatola V1 (prima il piatto grigio di prova) e assemblare.
3. Provare in schermo pieno la PWA 1.1.4 col controller senza toccare lo schermo; tarare le soglie delle 3 velocità (oggi "veloce" già a ~5 scatti/s).

## Problemi aperti
- **Sicurezza batteria**: senza diodo, aprire l'interruttore interno PRIMA di collegare la USB della SuperMini.
- Anello sempre alimentato in V1: ~10-16 mA anche spento e in sospensione (autonomia da fermo ~10 giorni).
- Log `BLE SICUREZZA errore 13` ogni tanto, connessione comunque funzionante: da capire.
- Annullamento del conto alla rovescia e risveglio "puliti" non ancora provati (la cattura seriale riavvia la scheda: non aprire la porta durante la prova).
- Manca il workflow GitHub per le Release (OTA da GitHub risponde 404); soglie batteria da alzare di 0,2 V col diodo.
- Tasti F13–F16 da aggiungere a `app/js/keymap.js`.
- PCB v2 (futuro): driver vibrazione integrato, piste lontane dall'antenna, eventuale caricatore integrato.
- Misure ancora da prendere: spessore PCB vibrazione, sporgenza USB-C SuperMini, fori M3 della millefori.

## Fasi previste
0. Validazione (fatto) · 1. Firmware su breadboard (quasi fatto) · 2. PWA (fatta, rifiniture) · 3. Scatola e assemblaggio V1 (in corso) · 4. Rifiniture, PCB, pubblicazione su MakerWorld
