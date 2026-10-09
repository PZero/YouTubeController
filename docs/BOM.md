# Lista componenti (BOM)

Ogni voce va proposta con alternative e approvata dall'utente.

| Componente | Modello | Q.tà | Costo indicativo | Stato | Note |
|------------|---------|------|------------------|-------|------|
| Scheda con BLE | ESP32-S3 SuperMini (Ulegqin, chip ESP32-S3FH4R2) | 3 | ~15-20 € la confezione da 3 (~5-7 € l'una) | acquistato, in arrivo | Amazon, "Ulegqin ESP32 S3 Mini ESP32-S3 SuperMini ... 3 pezzi". Specifiche sotto |
| Encoder rotativo | EC11 vertical con pulsante integrato (Alps EC11E o clone, base verde), albero zigrinato 18 denti Ø6, bussola M7x0,75 | 1 | ~1-2 € (clone), ~3-4 € (Alps) | in possesso | A/C/B + 2 pin switch + 2 linguette. Impulsi/giro da verificare (15 o 20, 30 o 20 scatti). Premendo la manopola si ottiene un secondo comando (es. play/pausa alternativo). Quote in `enclosure/dimensioni.md` |
| Pulsante | pulsante da pannello momentaneo NA tipo PBS-110 "7 mm", tasto blu, 2 terminali a paletta | 1 | ~0,3-0,5 € | in possesso | foro pannello 7 mm + dado. Sostituisce lo switch tattile 6x6 previsto prima: cambia il montaggio nella scatola |
| Caricatore + protezione batteria | modulo "4056" USB-C 4 fori: TP4056 (SOP-8) + DW01A (SOT-23-6) + FS8205A (TSSOP-8), pad B+ B- OUT+ OUT- | 1 | ~0,5-1 € | in possesso (fili già saldati su B+/B-) | carica 1 A con R3 = 1,2 kΩ (verificare marcatura "122"), fine carica 4,2 V; protezioni DW01A. Nessun load sharing. Collegamento in `firmware/README.md` |
| Batteria | Li-ion 18650 | 1 | ~4-8 € | da confermare | capacità 2500-3000 mAh; cella NON protetta va bene (protezione nel modulo) |
| Protezione da retroalimentazione USB | da scegliere: (a) Schottky SS14/1N5817 in serie OUT+ → 5V; (b) interruttore a slitta SS12D00 su OUT+; (c) entrambi | 1 | (a) ~0,05-0,1 €; (b) ~0,1-0,2 € | da scegliere | serve perché il pin 5V della SuperMini coincide con il VBUS USB: vedi `firmware/README.md`, Alimentazione |
| Convertitore boost | modulo MT3608 (blu ~36x17 mm, induttore 22 µH, trimmer 3296W, SS34) | 1 | ~0,5-1 € | in possesso, **non usato** | OUT+ del TP4056 va direttamente (o via Schottky) al pin 5V: l'LDO ME6217C33 lavora già con 3,4-4,2 V; il boost aggiungerebbe consumo a vuoto (0,2-1,5 mA misurati da terzi, contro 43 µA della scheda in deep sleep) e il rischio di sovratensione dal trimmer mal regolato, senza pin EN |

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
