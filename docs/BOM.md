# Lista componenti (BOM)

Ogni voce va proposta con alternative e approvata dall'utente.

| Componente | Modello | Q.tà | Costo indicativo | Stato | Note |
|------------|---------|------|------------------|-------|------|
| Scheda con BLE | ESP32-S3 SuperMini (Ulegqin, chip ESP32-S3FH4R2) | 3 | ~15-20 € la confezione da 3 (~5-7 € l'una) | acquistato, in arrivo | Amazon, "Ulegqin ESP32 S3 Mini ESP32-S3 SuperMini ... 3 pezzi". Specifiche sotto |
| Encoder rotativo | EC11 vertical con pulsante integrato (Alps EC11E o clone, base verde), albero zigrinato 18 denti Ø6, bussola M7x0,75 | 1 | ~1-2 € (clone), ~3-4 € (Alps) | in possesso | A/C/B + 2 pin switch + 2 linguette. Impulsi/giro da verificare (15 o 20, 30 o 20 scatti). Push dell'encoder non usato (decisione 2026-10-11). Quote in `enclosure/dimensioni.md` |
| Pulsante | pulsante da pannello momentaneo NA tipo PBS-110 "7 mm", tasto blu, 2 terminali a paletta | 1 | ~0,3-0,5 € | in possesso | foro pannello 7 mm + dado. Sostituisce lo switch tattile 6x6 previsto prima: cambia il montaggio nella scatola |
| Caricatore + protezione batteria | modulo "4056" USB-C 4 fori: TP4056 (SOP-8) + DW01A (SOT-23-6) + FS8205A (TSSOP-8), pad B+ B- OUT+ OUT- | 1 | ~0,5-1 € | in possesso (fili già saldati su B+/B-) | carica **0,5 A: R3 originale 1,2 kΩ ("122") sostituita con 2,4 kΩ** (decisione 2026-10-11; SMD, formato da verificare sul modulo), fine carica 4,2 V (soglia C/10 = 50 mA); protezioni DW01A. Nessun load sharing. Collegamento in `firmware/README.md` |
| Batteria | Li-ion 18650 | 1 | ~4-8 € | da confermare | capacità 2500-3000 mAh; cella NON protetta va bene (protezione nel modulo) |
| Protezione da retroalimentazione USB | da scegliere: (a) Schottky SS14/1N5817 in serie OUT+ → 5V; (b) interruttore a slitta SS12D00 su OUT+; (c) entrambi | 0 | (a) ~0,05-0,1 €; (b) ~0,1-0,2 € | **non usato** (decisione 2026-10-09: batteria scollegata al primo flash; poi solo OTA) | serve perché il pin 5V della SuperMini coincide con il VBUS USB: vedi `firmware/README.md`, Alimentazione |
| Anello LED | WS2812B 16 LED, Ø45/Ø33, spessore 3 | 1 | ~2-4 € | in possesso | sotto il coperchio con diffusore; alimentato da VBAT tramite interruttore high-side; dato su GPIO2. Luminosità ~10-15% in firmware |
| Modulo vibrazione | motore a moneta ~Ø10 (prob. 1027, 3 V) su modulo GND/VCC/IN con transistor e diodo | 1 | ~1-2 € | in possesso | VCC da VBAT, IN da GPIO6 (PWM ~20 kHz); verificare pull-down su IN e assenza di LED "power" (se c'è, toglierlo) |
| Transistor interruttore anello (high-side) | **S8550** PNP TO-92 (alternativa nel kit: S9012) | 1 | 0 € | in possesso (kit TO-92) | Q1, emettitore a VBAT; hFE 85-300, Vce(sat) ~0,1-0,2 V a 100 mA. Pinout E-B-C o E-C-B secondo il produttore: verificare col tester |
| Transistor driver | **2N3904** NPN TO-92 (equivalenti nel kit: S8050, S9013, S9014, C1815, C945, 2N2222) | 1 | 0 € | in possesso (kit TO-92) | Q2, base su GPIO9; pinout JEDEC E-B-C |
| Resistenze interruttore anello | R1 4,7 kΩ (GPIO9 → base Q2), R2 10 kΩ (base Q2 → GND), R3 680 Ω (collettore Q2 → base Q1), R4 10 kΩ (base-emettitore Q1) | 4 | 0 € | in possesso (kit) | corrente di base di Q1 ~4-5 mA ad anello acceso |
| Resistenza dato anello | 330 Ω | 1 | 0 € | in possesso (kit) | in serie a DI, vicino alla SuperMini |
| Condensatore bulk anello | 47 µF (fino a 100 µF) 10-16 V elettrolitico | 1 | ~0,05-0,1 € | da verificare se in possesso | sul portaschede dopo Q1; nessun R-C di avvio graduale (la corrente è limitata dal BJT); opzionale 10 µF sulle piazzole dell'anello se sfarfalla |
| Condensatori vibrazione | 47-100 µF elettrolitico + 100 nF ceramico su VCC; 100 nF sui terminali del motore se assente | 1+2 | ~0,1 € | da verificare se in possesso | contro i disturbi del motore a spazzole |
| Pull-down IN vibrazione | 100 kΩ | 0-1 | 0 € | in possesso (kit) | solo se il modulo ne è privo |
| Resistenze lettura carica | 10 kΩ in serie (x2) + 100 kΩ pull-up a 3V3 (x2) | 4 | 0 € | in possesso (kit) | CHRG → GPIO8, STDBY → GPIO10 (opzione B; niente Schottky) |
| Connettore anello (scocca ↔ portaschede) | **JST-PH 2,0 mm 3 poli** (alternative: JST-XH 2,5; JST-SH 1,0; Dupont 2,54 non polarizzato, sconsigliato) | 1 coppia | ~0,1-0,2 €; kit PH con cavetti crimpati ~8-12 € | da verificare se in possesso | polarizzato: invertire +/− danneggia l'anello. Valutare un unico PH 8 poli per tutto ciò che sta sulla scocca |
| Schedina millefori | basetta 2,54 mm, ~30 x 20 mm | 1 | ~0,2-0,5 € | da verificare se in possesso | raccoglie transistor, resistenze, condensatori e connettore sul portaschede |
| Viti fondo/portaschede | M3x8 (o ST2,9x9,5) svasate autofilettanti | 8 | ~1 € | da comprare | 4 fondo-scocca + 4 portaschede-fondo |
| Viti TP4056 | M2x5 autofilettanti (M1,6 se fori piccoli) | 4 | ~0,5 € | da comprare | colonnine del portaschede |
| Contatti 18650 | coppia piastrina + molla ~11x12 mm (in alternativa 2 fascette 3,6 mm) | 1 | ~1-2 € | da comprare | sedi nella culla del portaschede |
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
