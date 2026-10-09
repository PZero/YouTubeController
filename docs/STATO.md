# Stato del progetto

_Ultimo aggiornamento: 2026-10-09_

## Fase attuale
**Fase 0 → 3 in parallelo.** Componenti scelti (ESP32 in arrivo), alimentazione definita, prima versione completa della scatola modulare. App non ancora iniziata.

## Fatto
- Utente: esperienza discreta, Bambu Lab A1 mini, OpenSCAD.
- Repository pubblico su GitHub: PZero/YouTubeController (email noreply, nessuna credenziale).
- Componenti documentati (datasheet, quote con fonte/affidabilità in `enclosure/dimensioni.md`, BOM): ESP32-S3 SuperMini, TP4056 USB-C con protezione, encoder EC11E zigrinato 18T, pulsante PBS-110, 18650. MT3608 scartato.
- Schema collegamenti in `firmware/README.md`: 18650 → TP4056 B+/B- → OUT+/OUT- → 5V/GND; encoder A/B su GPIO4/5; pulsante su GPIO7; partitore 220k/220k su GPIO1.
- Scatola (`enclosure/`): Qi tolto; pulsante PBS-110 con cappuccio; manopola con sede zigrinata + `test_ring`; **portaschede** (`portaschede.scad`) avvitato al fondo con ESP32 capovolta, fori spillo RST/BOOT, TP4056, culla 18650; presa USB-C ricarica a X=-12; scritte disattivate; 3 piatti di stampa entro 180×180; interferenze verificate = 0.
- Render in `docs/render/` (montato, retro, esploso, sezione, piatti).
- Pagina di prova tastiera/focus (`app/test/`) online su https://pzero.github.io/YouTubeController/test/ (GitHub Pages via Actions, pubblica solo `app/`).
- Chiave API YouTube creata dall'utente (con restrizioni), conservata fuori dal repo; andrà inserita nelle impostazioni della PWA sull'iPad.

## Prossimi passi
1. Test della pagina di prova sull'iPad (Safari e Home): l'utente incolla il registro ("Copia registro") + modello/versione iPadOS → scegliere i tasti del firmware e la strategia per il focus.
2. All'arrivo dell'ESP32: misure col calibro (lista sotto), aggiornare i parametri, stampare `test_ring` e portaschede di prova (PETG).
3. Prototipo su breadboard: firmware BLE HID (play/pausa, seek, pressione lunga 10 s = standby).

## Problemi aperti
- **Primo flash con la batteria scollegata** (niente diodo: pin 5V = VBUS → rischio sulla 18650). Da scrivere nelle istruzioni di montaggio.
- **OTA**: piano proposto in `firmware/README.md` (sezione OTA); l'utente deve confermare il gesto (pulsante + 5 scatti) e la build su GitHub Actions/Release.
- Antenna ESP32 vicina alla 18650 (involucro metallico): verificare la portata BLE col prototipo.
- Misure col calibro: SuperMini (spessore PCB, sporgenza USB-C), TP4056 (PCB, fori, USB-C, LED), encoder (bussola, albero, zigrinatura), PBS-110 (filetto, dado, tasto), cella e contatti.
- LED di carica visibili dal retro? Dipende dalla posizione reale sul TP4056 (eventuale light pipe).
- Margini stretti: culla 18650 a 0,5 mm dai condotti laterali; incastri ESP32 piccoli.
- Corrente di carica: valutare R3 2,4 kΩ (0,5 A) in scatola chiusa.
- Da comprare: viti M3x8 ×8, M2x5 ×4, contatti 18650 (vedi BOM).

## Fasi previste
0. Avvio e prototipo di validazione
1. Firmware funzionante su breadboard
2. PWA: ricerca e player controllato da tastiera
3. Scatola 3D (scocca + portaschede modulare) e assemblaggio
4. Rifiniture (decorazioni, scritte)
