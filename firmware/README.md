# Firmware

Codice del controller: lettura di encoder e pulsante, invio dei tasti via BLE HID.

## Scheda: ESP32-S3 SuperMini

Chip ESP32-S3FH4R2 (4 MB flash, 2 MB PSRAM quad). Acquistata (3 pezzi), in arrivo. Specifiche e costo in `docs/BOM.md`, misure in `enclosure/dimensioni.md`.

### Pinout

Pin sugli header laterali (2 file da 9, passo 2,54 mm, confermato dal disegno Nologo):

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
| Tensione batteria | 1 | partitore 220k/220k da OUT+ del modulo 4056 (vedi Alimentazione) |

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

### Encoder e pulsante: collegamento e lettura

Encoder EC11E con pulsante integrato (albero zigrinato) e pulsante da pannello PBS-110 (NA), entrambi in possesso.

| Componente | Pin | Collegamento |
|------------|-----|--------------|
| Encoder | A | GPIO4 |
| Encoder | C (centrale) | GND |
| Encoder | B | GPIO5 |
| Encoder, switch integrato | S1 / S2 | GPIO6 / GND |
| Pulsante PBS-110 | terminale 1 / 2 | GPIO7 / GND (non polarizzato) |

- Pull-up: `INPUT_PULLUP` interni (~45 kΩ) bastano per il prototipo; con fili lunghi o rimbalzi evidenti aggiungere 10 kΩ verso 3V3 su A e B e 10 nF-100 nF verso GND (filtro RC, costante ~0,1-1 ms).
- Quadratura: leggere A e B con interrupt su entrambi i fronti (o polling a 1 kHz) e una macchina a stati a tabella (16 transizioni, quelle non valide scartate). Contare un passo solo a stato di riposo (scatto) raggiunto: con 30 scatti/15 impulsi lo scatto cade su A=B (00 e 11), con 20/20 su 11; verificare a mano quanti scatti/giro ha il nostro. Libreria pronta in alternativa: `ESP32Encoder` (contatore hardware PCNT, filtro glitch integrato).
- Debounce pulsanti: software 20-30 ms (stato stabile per N ms prima di emettere il tasto); un tasto per pressione, nessuna ripetizione.
- Mappatura: rotazione = freccia sinistra/destra; PBS-110 = spazio; switch dell'encoder = libero per una seconda funzione (es. play/pausa alternativo, o pressione lunga = altro comando), da decidere in `docs/DECISIONI.md`.
- Deep sleep: GPIO4-7 sono RTC, risveglio `ext1` con livello basso su GPIO6/7 (pressione) ed eventualmente su A/B.

### Alimentazione

Componenti in possesso: modulo "4056" USB-C (TP4056 + DW01A + FS8205A), cella 18650 (da confermare); boost MT3608 in possesso ma **non usato**.

Schema proposto:

```
 18650 (+) ── B+  [modulo 4056]  OUT+ ──(D1 Schottky SS14, anodo su OUT+)──┬── pin 5V SuperMini
 18650 (-) ── B-                 OUT- ─────────────────────────────────────┼── pin GND SuperMini
                 USB-C del modulo = presa di ricarica del prodotto          │
                                                                           │
 OUT+ ──[220 kΩ]──┬──[220 kΩ]── OUT-        (opzionale) SW1 a slitta in serie a OUT+ come interruttore
                  └── GPIO1 (ADC1_CH0) + 100 nF verso GND
```

- **Non usare i pad BAT+/BAT- della SuperMini**: il suo TP4054 (100 mA) e il diodo BAT60B sono un secondo caricatore senza protezione.
- OUT+ e B+ sono lo **stesso nodo** su questi moduli: la protezione (DW01A + FS8205A) interrompe solo il negativo (B- ↔ OUT-). Quindi OUT+ è di fatto il polo positivo della cella.
- **Rischio retroalimentazione**: sullo schema Nologo il pin 5V coincide con il VBUS dell'USB-C (non c'è diodo tra VBUS e pin 5V; c'è solo il BAT60B sul percorso dei pad BAT). Collegando la SuperMini al PC con OUT+ cablato direttamente al pin 5V, i 5 V del PC finirebbero sulla cella attraverso OUT+ = B+: carica non controllata a 5 V, rischio incendio della 18650. Da verificare col tester (resistenza VBUS ↔ pin 5V ≈ 0 Ω) sulla scheda arrivata. Soluzioni:

| Opzione | Pro | Contro | Costo |
|---------|-----|--------|-------|
| A. Scollegare la batteria (o OUT+) prima di ogni flash | nulla da aggiungere, nessuna caduta | basta una dimenticanza per un danno grave | 0 € |
| B. Schottky in serie OUT+ → 5V (SS14 / 1N5817 / BAT60) | protezione permanente, semplice | caduta 0,2-0,3 V a 30-100 mA: soglia utile della batteria sale di ~0,25 V (~10-15% di capacità persa) | ~0,05-0,1 € |
| C. Interruttore a slitta su OUT+ (SS12D00) | serve comunque come ON/OFF, zero caduta | protegge solo se è spento durante il flash | ~0,1-0,2 € |
| B + C | sicuro e con interruttore generale | caduta del diodo | ~0,2-0,3 € |

  Proposta per il prototipo: **B** (o B + C se si vuole un interruttore); A solo su breadboard, con attenzione. Un "diodo ideale" a P-MOSFET non è applicabile in modo semplice perché VBUS e pin 5V sono lo stesso nodo (non c'è un segnale VBUS separato per il gate).
- Con il diodo, quando la SuperMini è su USB la cella resta isolata e la scheda è alimentata dal PC; il modulo 4056 può caricare la cella in contemporanea senza conflitti.

Valori elettrici (datasheet; i cloni possono differire):

| Parametro | Valore | Note |
|-----------|--------|------|
| Tensione fine carica TP4056 | 4,20 V ±1% | CC/CV |
| Corrente di carica | I = 1200 / R3 (A con R in Ω): 1,2 kΩ = 1 A, 2 kΩ = 0,58 A, 2,4 kΩ = 0,5 A, 3 kΩ = 0,4 A | verificare la marcatura di R3 ("122" = 1,2 kΩ). In una scatola chiusa conviene 0,5 A (R3 → 2,4 kΩ): meno calore (1 A dissipa fino a ~1,3 W) |
| Fine carica / ricarica automatica | a C/10 (100 mA con 1 A) / riparte sotto ~4,05 V | |
| Precarica cella molto scarica | sotto 2,9 V a C/10 | |
| Limitazione termica TP4056 | 120 °C (riduce la corrente) | |
| DW01A sovraccarica | ~4,30 V (4,25-4,35), rilascio ~4,10 V | |
| DW01A sovrascarica | ~2,4 V (2,3-2,5), rilascio ~3,0 V | dopo l'intervento il modulo può restare spento finché non si collega la USB-C di ricarica |
| DW01A sovracorrente | 150 mV sul doppio MOSFET (FS8205A ~2 x 25-30 mΩ) → ~2,5-3 A; corto 1,35 V | molto oltre i nostri consumi |
| Assorbimento a riposo dalla cella | TP4056 ~2,5 µA (max 6) + DW01A ~3 µA → ~5-10 µA; i LED sono alimentati dall'USB e a riposo sono spenti | da misurare: un utente ha misurato 1,6 mA su una copia del modulo |

Carica con carico collegato (nessun load sharing):
- Il TP4056 vede la somma cella + ESP32. Con il nostro carico (20-50 mA) la fine carica a 100 mA arriva lo stesso, ma la cella si ferma un po' prima del pieno; a carica finita l'ESP32 scarica la cella fino a 4,05 V e la carica riparte (micro-cicli, accettabili).
- Se si scegliesse R3 per correnti basse (es. 130 mA con 10 kΩ) la fine carica potrebbe non arrivare mai: non scendere sotto ~400 mA.
- Durante la carica il controller resta utilizzabile.

Soglie di tensione della batteria (cella collegata a OUT+, regolatore ME6217C33 con dropout ~0,1 V a 100 mA, più alto sui picchi radio di 200-300 mA; ESP32-S3 alimentato a 3,0-3,6 V, brown-out di default ~2,7 V):

| Vbat | Senza diodo | Con Schottky (~0,25 V) |
|------|-------------|-------------------------|
| 3V3 regolati pieni | ≥ ~3,45 V | ≥ ~3,7 V |
| funziona (3V3 = Vbat - cadute) | fino a ~3,2 V | fino a ~3,45 V |
| rischio reset sui picchi BLE | < ~3,1 V | < ~3,35 V |

- Soglie firmware proposte (lette sull'ADC, quindi prima del diodo): avviso batteria scarica a **3,5 V** (LED WS2812 rosso lampeggiante), deep sleep forzato a **3,3 V** (con diodo: 3,6 / 3,45 V). Il distacco del DW01A a 2,4 V è solo l'ultima difesa: troppo basso per la salute della cella.
- Lettura batteria: partitore 220 kΩ / 220 kΩ tra OUT+ e OUT- (consumo ~9,5 µA) con 100 nF sul punto centrale, su **GPIO1** (ADC1_CH0, libero, RTC). 4,2 V → 2,1 V, entro la scala con attenuazione 11 dB. Usare `analogReadMilliVolts()` (calibrazione eFuse), media di 8-16 letture, leggere a radio ferma o mediare. Per azzerare il consumo si può alimentare il partitore da un GPIO solo durante la misura.

Autonomia stimata (18650 2500-3000 mAh, ~2000-2400 mAh utili fino a 3,4-3,5 V):
- In uso, BLE connesso 20-50 mA: ~40-120 ore.
- Standby in deep sleep: scheda ~43 µA + modulo ~10 µA + partitore ~10 µA ≈ 65 µA → oltre 3 anni in teoria; nella pratica conta l'autoscarica della cella (~2-3%/mese). Con il boost MT3608 lo standby salirebbe a 0,2-1,5 mA (2-12 mesi) senza alcun vantaggio: per questo non si usa.

### Consumi

- Deep sleep ~43 µA dichiarati per la scheda (regolatore e LED inclusi); BLE connesso da misurare (stima 20-50 mA, riducibile con power management/light sleep e CPU a 80 MHz).
- Segnalato sul forum ESP32 il guasto del diodo del circuito batteria della SuperMini con batteria sui pad BAT e USB collegata: un motivo in più per non usare i pad BAT.

### Problemi noti

- Variabilità tra lotti/produttori (pinout dei pad, LED, circuito batteria).
- Antenna ceramica a volte montata male o debole: provare la portata con la scheda dentro la scatola.
- Surriscaldamento: nessuna segnalazione specifica trovata per l'S3 SuperMini.

### Fonti

- https://espboards.dev/boards/esp32-s3-supermini (pinout, LED, batteria, deep sleep, problemi antenna)
- https://www.otronic.nl/en/esp32-s3-super-mini-4mb-flash-en-2mb-psram.html (GPIO sicuri; la lunghezza 22,52 indicata è errata, vale 23,50 da disegno Nologo)
- https://www.tinytronics.nl/en/development-boards/microcontroller-boards/with-wi-fi/esp32-s3-supermini-development-board-with-soldered-headers (24 x 18 mm, TP4054, GPIO 1-13/43/44 sugli header)
- https://devices.esphome.io/devices/TENSTAR-ROBOT-ESP32-S3-SuperMini/ (WS2812 su GPIO48, PSRAM quad)
- https://esp32.com/viewtopic.php?p=149991 (diodo del circuito batteria)
- https://forum.arduino.cc/t/esp32-s3-bluetooth-projects-now-wont-compile/1410775 (cambio stack BLE nel core 3.3)
- https://www.arduinolibraries.info/libraries/hijel-hid_ble-keyboard (libreria HID BLE)
- Datasheet TP4056 (NanJing Top Power): https://www.radiolocman.com/datasheet/pdf.html?di=169473 ; riepilogo: https://mischianti.org/tp4056-lipo-battery-charger-high-resolution-pinout-datasheet-and-specs/
- Datasheet DW01A: https://uelectronics.com/wp-content/uploads/2021/05/Datasheet-DW01A.pdf ; https://best-microcontroller-projects.com/dw01a.html
- Consumo anomalo di un modulo 4056: https://forum.allaboutcircuits.com/threads/tp4056-current-consumption.164076/
- Dimensioni modulo 4056 USB-C: https://oe2.open-electronics.org/?p=48075 , https://ifuturetech.org/?p=19602
- Diodo e VBUS SuperMini: https://esp32.com/viewtopic.php?p=149991
- Encoder: Alps EC11E15244G1 https://tech.alpsalpine.com/e/products/detail/EC11E15244G1/ ; footprint KiCad RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm; Bourns PEC11R (albero zigrinato 18 denti)
- Pulsante PBS-110: https://ifuturetech.org/?p=59198
- MT3608, consumo a vuoto: https://hackaday.com/tag/mt3608/

## OTA — proposta (da confermare con l'utente, 2026-10-09)
La scheda va al PC una sola volta (primo flash, **batteria scollegata**); poi solo OTA.
1. **Partizioni**: due slot app OTA (es. "Minimal SPIFFS 1.9MB APP with OTA"), scelte al primo flash: cambiarle in seguito richiede il cavo. NVS preservata (abbinamento BLE con l'iPad).
2. **Rollback**: nuova immagine "in prova", marcata valida solo dopo auto-test (BLE avviato, input ok); altrimenti ritorno automatico alla precedente.
3. **Attivazione**: WiFi spento nell'uso normale; modalità OTA con gesto distinto dallo standby (proposta: pulsante premuto + 5 scatti di manopola); uscita automatica dopo 5 min.
4. **Aggiornamento da iPad**: access point `YTController-OTA` (WPA2), pagina su 192.168.4.1 con versione, upload del .bin da File, avanzamento. Eventualmente anche ArduinoOTA/espota.
5. **Build su GitHub Actions** → .bin nelle Release. **Nessun segreto nel binario**: password dell'AP salvata in NVS via seriale al primo flash.
6. **Controlli**: rifiuto sotto ~3,7 V di batteria; verifica immagine (dimensione/checksum, opzionale firma); recupero estremo via USB + fori spillo BOOT/RST.
Feedback: LED interno non visibile → l'indicazione è la comparsa della rete WiFi.
