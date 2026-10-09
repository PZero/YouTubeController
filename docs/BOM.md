# Lista componenti (BOM)

Ogni voce va proposta con alternative e approvata dall'utente.

| Componente | Modello | Q.tà | Costo indicativo | Stato | Note |
|------------|---------|------|------------------|-------|------|
| Scheda con BLE | ESP32-S3 SuperMini (Ulegqin, chip ESP32-S3FH4R2) | 3 | ~15-20 € la confezione da 3 (~5-7 € l'una) | acquistato, in arrivo | Amazon, "Ulegqin ESP32 S3 Mini ESP32-S3 SuperMini ... 3 pezzi". Specifiche sotto |
| Encoder rotativo | EC11 (proposto) | 1 | | da confermare | con pulsante integrato |
| Pulsante | switch tattile 6x6 (proposto) | 1 | | da confermare | play/stop |
| Alimentazione | da definire | | | da scegliere | USB-C; batteria + Qi da valutare (vedi note scheda) |

## Specifiche chiave: ESP32-S3 SuperMini

Fonti: [espboards.dev](https://espboards.dev/boards/esp32-s3-supermini), [Otronic](https://www.otronic.nl/en/esp32-s3-super-mini-4mb-flash-en-2mb-psram.html), [TinyTronics](https://www.tinytronics.nl/en/development-boards/microcontroller-boards/with-wi-fi/esp32-s3-supermini-development-board-with-soldered-headers), [ESPHome devices](https://devices.esphome.io/devices/TENSTAR-ROBOT-ESP32-S3-SuperMini/). Esistono più produttori/lotti con differenze: verificare sulla scheda arrivata.

- MCU: ESP32-S3 dual-core LX7 240 MHz; 4 MB flash e 2 MB PSRAM **quad** (QSPI) nel chip. PSRAM in modalità OPI = crash.
- Radio: Wi-Fi 2.4 GHz + **Bluetooth 5 LE** (niente Bluetooth Classic); antenna ceramica sul bordo opposto all'USB-C.
- USB: USB-C nativo (USB Serial/JTAG + CDC), nessun chip USB-seriale.
- Dimensioni: 23,50 x 18,00 mm (disegno quotato Nologo; i 22,52 di alcuni testi sono errati). Dettagli in `enclosure/dimensioni.md`.
- Alimentazione: 5 V da USB-C o pin 5V; regolatore 3,3 V ME6217C33 (800 mA), da schema Nologo. GPIO a 3,3 V, non tolleranti 5 V.
- Batteria: pad BAT+/BAT- sul retro + caricatore TP4054 e diodo BAT60B (schema Nologo) (100 mA, nessuna protezione della cella; jumper BOOST a 300 mA su alcune). **Da verificare** se presente sui nostri esemplari.
- LED: WS2812 RGB su GPIO48; LED rosso indicato anch'esso su GPIO48 (fonti dubbie); LED blu di carica non pilotabile.
- Consumi: deep sleep ~43 µA dichiarati per la scheda (espboards); BLE connesso stimato 20-50 mA senza risparmio energetico (da misurare).
