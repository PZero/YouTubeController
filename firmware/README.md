# Firmware

Codice del controller: lettura di encoder e pulsante, invio dei tasti via BLE HID.

## Scheda: ESP32-S3 SuperMini

Chip ESP32-S3FH4R2 (4 MB flash, 2 MB PSRAM quad). Acquistata (3 pezzi), in arrivo. Specifiche e costo in `docs/BOM.md`, misure in `enclosure/dimensioni.md`.

### Pinout

Pin sugli header laterali (2 file, passo 2,54 mm; le fonti indicano 18 pin = 2 x 9, l'utente dalla foto conta 2 x 8: **verificare la serigrafia**):

| Pin | Funzione | Note |
|-----|----------|------|
| 5V | ingresso/uscita 5 V (VBUS USB) | |
| GND | massa | |
| 3V3 | uscita 3,3 V del regolatore | |
| 43 / 44 | TX / RX UART0 | console di default, evitare |
| 1, 2, 4, 5, 6, 7, 8 | GPIO liberi | sicuri, RTC (risveglio da deep sleep), ADC1 |
| 3 | strapping (sorgente JTAG) | evitare |
| 9-13 | GPIO (FSPI) | utilizzabili, ma preferire i precedenti |

Pad sul retro (saldatura difficile, non usare nel prototipo): GPIO14-18, 21, 33-42, 45-48.
Da evitare: GPIO0 (BOOT), 3, 45, 46 (strapping), 19/20 (USB D-/D+), 26-32 (flash/PSRAM, non esposti), 48 (LED RGB).

LED: WS2812 RGB su **GPIO48**; il LED rosso è dato anch'esso su GPIO48 da alcune fonti (probabilmente è solo il LED di alimentazione); LED blu di carica non pilotabile.

### GPIO proposti

| Segnale | GPIO | Collegamento |
|---------|------|--------------|
| Encoder A (CLK) | 4 | contatto a GND, `INPUT_PULLUP` (+ eventuale 10 kΩ esterno e 100 nF per antirimbalzo) |
| Encoder B (DT) | 5 | come sopra; comune dell'encoder a GND |
| Pulsante dell'encoder (SW) | 6 | a GND, `INPUT_PULLUP` |
| Switch play 6x6 | 7 | a GND, `INPUT_PULLUP` |
| LED di stato | 48 | WS2812 integrato |

Tutti sullo stesso lato degli header, tutti RTC GPIO: usabili come sorgente di risveglio `ext1` dal deep sleep.

### Programmazione

- Arduino IDE / PlatformIO, core arduino-esp32 3.x, scheda "ESP32S3 Dev Module".
- Impostazioni: `USB CDC On Boot: Enabled` (per vedere `Serial` sulla USB), Flash 4 MB, PSRAM "QSPI PSRAM" o disabilitata (mai OPI).
- Caricamento via USB nativa. Se la porta sparisce (sketch bloccato o in deep sleep): tenere premuto BOOT, premere/rilasciare RST (o collegare il cavo), rilasciare BOOT, caricare, poi RST.

### BLE HID tastiera: librerie candidate

| Libreria | Pro | Contro |
|----------|-----|--------|
| HijelHID_BLEKeyboard | basata su NimBLE-Arduino ≥2.3.8, core ≥3.3.7, testata su iPadOS | giovane, pochi utenti |
| T-vK ESP32-BLE-Keyboard (con `#define USE_NIMBLE`) | molto diffusa, molti esempi | poco mantenuta (ultimo push 2024), problemi segnalati con core 3.x e NimBLE 2.x: può richiedere patch o un core 2.x |
| ESP-IDF `esp_hid_device` (esempio ufficiale) | supporto Espressif, controllo totale | più codice, fuori da Arduino |

Proposta per il prototipo: HijelHID_BLEKeyboard; ripiego: T-vK con core 2.0.17. Nota: dal core 3.3.0 lo stack BLE predefinito è NimBLE; non includere `BluetoothSerial.h` (l'S3 non ha BT Classic).

### Alimentazione e consumi

- Regolatore 3,3 V a bordo: modello non documentato nelle fonti trovate (leggere la marcatura all'arrivo).
- Alcune versioni hanno pad batteria e caricatore TP4054 (100 mA, senza protezione della cella). Segnalato sul forum ESP32 un diodo Schottky tra 5V e batteria che si guasta caricando con batteria collegata e che può retro-alimentare VBUS: in prototipo **scollegare la batteria durante l'upload**.
- Consumi: deep sleep ~43 µA dichiarati per la scheda (regolatore e LED inclusi); BLE connesso da misurare (stima 20-50 mA, riducibile con power management/light sleep e CPU a 80 MHz).

### Problemi noti

- Variabilità tra lotti/produttori (pinout dei pad, LED, circuito batteria).
- Antenna ceramica a volte montata male o debole: provare la portata con la scheda dentro la scatola.
- Surriscaldamento: nessuna segnalazione specifica trovata per l'S3 SuperMini.

### Fonti

- https://espboards.dev/boards/esp32-s3-supermini (pinout, LED, batteria, deep sleep, problemi antenna)
- https://www.otronic.nl/en/esp32-s3-super-mini-4mb-flash-en-2mb-psram.html (dimensioni 22,52 x 18, GPIO sicuri)
- https://www.tinytronics.nl/en/development-boards/microcontroller-boards/with-wi-fi/esp32-s3-supermini-development-board-with-soldered-headers (24 x 18 mm, TP4054, GPIO 1-13/43/44 sugli header)
- https://devices.esphome.io/devices/TENSTAR-ROBOT-ESP32-S3-SuperMini/ (WS2812 su GPIO48, PSRAM quad)
- https://esp32.com/viewtopic.php?p=149991 (diodo del circuito batteria)
- https://forum.arduino.cc/t/esp32-s3-bluetooth-projects-now-wont-compile/1410775 (cambio stack BLE nel core 3.3)
- https://www.arduinolibraries.info/libraries/hijel-hid_ble-keyboard (libreria HID BLE)
