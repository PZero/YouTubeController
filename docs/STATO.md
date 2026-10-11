# Stato del progetto

_Ultimo aggiornamento: 2026-10-11_

## Fase attuale
**Fase 1 (prototipo firmware) in partenza; PWA completa (fase 2); scatola alla seconda versione (fase 3).** ESP32 arrivato.

## Fatto
- Fase 0: tastiera BLE su iPad validata (tasti sempre ricevuti, nessuna strategia di focus; la tastiera a schermo compare toccando un campo).
- **PWA completa** online: https://pzero.github.io/YouTubeController/ — ricerca (chiave API sul dispositivo), preferiti con loop A-B, seek a 3 velocità con accumulo e un solo seekTo, loop A-B, schermo pieno automatico, sezione Controller, icona. Mappa tasti in `app/js/keymap.js`.
- Decisi: tasti (←/→, Shift, Alt, Spazio, L), gesti (breve/media/10 s/2 s risveglio, pulsante+5 scatti avanti = OTA, indietro = reset WiFi), OTA via GitHub Release + WiFi di casa opzionale, R3 2,4 kΩ (0,5 A).
- Nuovi componenti: **anello WS2812B 16 LED** attorno alla manopola (diffusore stampato a parte) e **modulo vibrazione**; interruttore anello S8550 + 2N3904 (kit); lettura carica CHRG/STDBY con resistenze. Schema in `firmware/README.md`.
- **Millefori** 8×13 coricata sopra il TP4056: layout, piste e verifica automatica in `firmware/millefori/` (verifica OK).
- Scatola: anello, diffusore, vibrazione, ganci rifatti per **PLA**, verifica interferenze = 0; esportazione per Bambu Studio/MakerWorld (`enclosure/export/esporta.py`, zip di prova consegnato).
- Tenuto il TP4056 (cella Jesspow 3300 mAh **non protetta**, Ø18,5×65); caricabatterie della SuperMini non usato.
- README del repository con foto (senza EXIF) e render; licenza MIT (MakerWorld: CC BY 4.0).

## Prossimi passi
1. **Prototipo su breadboard** (piano proposto, in attesa di ok): arduino-cli + core ESP32 3.x + libreria BLE keyboard; firmware v0 con encoder (3 velocità) e pulsante (breve/media); prova con la PWA sull'iPad e taratura soglie. Chiedere: breadboard/Dupont, fili su encoder e pulsante, ok a scaricare arduino-cli.
2. Misure col calibro → **design-3d** sposta la millefori nel portaschede (colonnine sopra il TP4056, via le guide in piedi) e aggiorna lo zip completo.
3. Stampa dello zip di prova (tolleranze PLA, scatto anello e diffusore).

## Problemi aperti
- **Misure mancanti**: interasse fori TP4056 (serve alla millefori); lunghezza del solo PCB della SuperMini (27 totale con USB-C: la presa sporgerebbe ~3,5 invece di 1,2-2,2); spessore PCB anello e raggio dei LED; resistenze del kit (lunghezza/diametro); posizione del motore sul modulo vibrazione; misure già in lista (encoder, PBS-110, contatti cella).
- `enclosure/dimensioni.md` descrive ancora la millefori **in piedi** (modello non aggiornato alla posizione sopra il TP4056).
- Caricabatterie integrato della SuperMini (pad B+/B−) alimentato dal pin 5V: misurare il consumo in standby.
- Tasti F13–F16 (avvisi alla PWA) da aggiungere a `keymap.js` e da verificare su iPadOS.
- Da verificare sul prototipo: pinout S8550 col tester, anello spento al boot, dato anello a 4,2 V, pull-down/LED di alimentazione del modulo vibrazione, portata BLE vicino alla 18650, primo play da tasto.
- TP4056 coperto dalla millefori: controllare la temperatura in carica (PLA ~55 °C).
- Primo flash con la batteria scollegata.
- Da comprare: viti M3x8 ×8, M2 (TP4056 + millefori), distanziali nylon M2, contatti 18650; verificare in casa millefori, Dupont 2×4, condensatori (2 elettrolitici 47–100 µF, 3 da 100 nF).

## Fasi previste
0. Avvio e prototipo di validazione (fatto)
1. Firmware funzionante su breadboard
2. PWA: ricerca e player controllato da tastiera (fatta, da provare col controller)
3. Scatola 3D (scocca + portaschede modulare) e assemblaggio
4. Rifiniture e pubblicazione su MakerWorld
