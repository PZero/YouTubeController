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
| Pulsante dell'encoder (SW) | (6) | **non usato** (decisione 2026-10-11): non collegarlo; GPIO6 resta libero/riserva |
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
| Encoder, switch integrato | S1 / S2 | non collegati (push dell'encoder non usato) |
| Pulsante PBS-110 | terminale 1 / 2 | GPIO7 / GND (non polarizzato) |

- Pull-up: `INPUT_PULLUP` interni (~45 kΩ) bastano per il prototipo; con fili lunghi o rimbalzi evidenti aggiungere 10 kΩ verso 3V3 su A e B e 10 nF-100 nF verso GND (filtro RC, costante ~0,1-1 ms).
- Quadratura: leggere A e B con interrupt su entrambi i fronti (o polling a 1 kHz) e una macchina a stati a tabella (16 transizioni, quelle non valide scartate). Contare un passo solo a stato di riposo (scatto) raggiunto: con 30 scatti/15 impulsi lo scatto cade su A=B (00 e 11), con 20/20 su 11; verificare a mano quanti scatti/giro ha il nostro. Libreria pronta in alternativa: `ESP32Encoder` (contatore hardware PCNT, filtro glitch integrato).
- Debounce pulsanti: software 20-30 ms (stato stabile per N ms prima di emettere il tasto); un tasto per pressione, nessuna ripetizione.
- Deep sleep: GPIO4-7 sono RTC, risveglio `ext1` con livello basso su GPIO7 (pulsante PBS-110). A/B non usati come sorgente di risveglio (la manopola non deve accendere il controller in borsa).

### Mappa tasti (decisione 2026-10-11)

Riferimento autoritativo: `app/js/keymap.js`. Se cambia lì, va cambiato qui e nel firmware.

| Gesto | Tasto inviato | Report HID (modificatore / usage) |
|-------|---------------|------------------------------------|
| Rotazione lenta, indietro / avanti | ← / → | 0x00 / 0x50 / 0x4F |
| Rotazione media | Shift + ← / → | Left Shift (0x02) / 0x50 / 0x4F |
| Rotazione veloce | Alt + ← / → | Left Alt (0x04) / 0x50 / 0x4F |
| Pulsante, pressione breve | Spazio | 0x00 / 0x2C |
| Pulsante, pressione media | L (minuscola) | 0x00 / 0x0F |

- Ogni tasto = **un report di pressione con modificatore e tasto insieme**, seguito subito dal report di rilascio (tutto a zero). Non inviare il modificatore in un report separato, e non lasciare mai un tasto "premuto": se il rilascio tarda oltre ~500 ms iPadOS avvia la ripetizione automatica.
- Nessun Ctrl/Cmd (la PWA li ignora). F (schermo pieno) ed Esc non sono inviati dal controller.

#### Velocità della manopola: 3 livelli

Il firmware misura la velocità e sceglie il livello; la PWA somma gli eventi e fa un solo seek a fine rotazione.

- Misura: intervallo tra scatti consecutivi, velocità = media mobile degli ultimi 3 intervalli (finestra ~100-300 ms a seconda della velocità). Il primo scatto dopo una pausa > 300 ms è sempre "lento".
- Soglie iniziali (da tarare sul prototipo; dipendono dagli scatti/giro, 20 o 30):

| Livello | Velocità | Indicativamente (encoder 20 scatti/giro) |
|---------|----------|------------------------------------------|
| lento | < 5 scatti/s | meno di 1/4 di giro al secondo |
| medio | 5-12 scatti/s | |
| veloce | > 12 scatti/s | oltre ~0,6 giri/s |

- Isteresi: si sale di livello subito appena la media supera la soglia; si scende solo se la media resta sotto (soglia - 20%) per 2 scatti consecutivi. Evita l'alternanza di livelli a velocità di confine.
- Cambio di verso: azzera la media (ricomincia da "lento").
- Soglie e isteresi come costanti in testa al codice; in seguito eventualmente regolabili dalla pagina web dell'AP (NVS).

#### Un evento per scatto o raggruppare?

- Limite pratico: iPadOS usa per le periferiche HID un intervallo di connessione di ~15 ms (11,25-30 ms). Per ogni evento di connessione si possono inviare più notifiche, ma con libreria Arduino e coesistenza radio è prudente contare su ~1 notifica utile per evento. Ogni tasto = 2 report (pressione + rilascio) → circa **30 tasti/s** sostenibili in modo affidabile.
- Rotazione veloce realistica: 1-3 giri/s = 20-90 scatti/s → oltre il limite.
- Il raggruppamento vero (un solo tasto che "vale" N scatti) non è possibile con tasti semplici: la PWA conta i tasti.
- **Proposta**: un tasto per scatto, ma con **coda in firmware** e cadenza minima di invio (~33 ms per tasto, da tarare). Gli scatti in eccesso restano in coda, non si perdono; a fine rotazione la coda si svuota in poche centinaia di ms. Regole della coda:
  - capienza massima ~40 scatti; oltre si saturano (a velocità alta il passo è già grosso, la perdita è accettabile);
  - un cambio di verso cancella prima gli scatti in coda del verso opposto (risposta immediata all'inversione);
  - ogni voce in coda conserva il proprio livello.
- Alternativa da valutare se la coda risulta lenta: al livello veloce inviare 1 tasto ogni 2 scatti e far valere doppio il passo veloce nella PWA (richiede una modifica coordinata con l'app).
- **Impatto app**: il timeout di "fine rotazione" della PWA deve essere più lungo della cadenza della coda (≥ 150-200 ms), altrimenti un'unica rotazione veloce produce più seek.

### Gesti del pulsante (PBS-110, tabella unica)

Push dell'encoder **non usato**. Durate misurate dalla pressione stabile (dopo il debounce).

| Priorità | Gesto | Condizione | Azione | Quando scatta |
|----------|-------|------------|--------|---------------|
| 1 | Premuto + 5 scatti AVANTI | pulsante tenuto, 5 scatti consecutivi in avanti | modalità aggiornamento (vedi OTA) | al 5° scatto, senza aspettare il rilascio |
| 1 | Premuto + 5 scatti INDIETRO | pulsante tenuto, 5 scatti consecutivi indietro | azzera il WiFi di casa (NVS) e apre la rete di configurazione | al 5° scatto |
| 2 | Lunga | tenuto ≥ 10 s, nessuna rotazione | standby (deep sleep) / risveglio | a 10 s, ancora premuto; il rilascio successivo viene ignorato |
| 3 | Media | rilascio tra 0,7 e 2 s, nessuna rotazione | tasto L (loop A-B) | al rilascio |
| 4 | Breve | rilascio prima di 0,7 s, nessuna rotazione | Spazio (play/pausa) | al rilascio |
| - | Zona morta | rilascio tra 2 e 10 s, nessuna rotazione | nulla (annullamento volontario) | - |

Regole per evitare sovrapposizioni:
- Le finestre di durata sono disgiunte: < 0,7 / 0,7-2 / 2-10 (nulla) / ≥ 10 s.
- **Qualsiasi scatto** con il pulsante premuto annulla breve, media e lunga per quella pressione, e gli scatti **non** vengono inviati come frecce.
- Il conteggio dei 5 scatti si azzera se cambia verso; meno di 5 scatti e poi rilascio = nulla.
- Dopo un gesto con rotazione, nessun altro gesto fino al rilascio.
- Risveglio da standby: la pressione risveglia il chip (`ext1` su GPIO7); il firmware verifica che il pulsante resti premuto fino a 10 s complessivi, altrimenti torna in deep sleep (evita accensioni accidentali). Da valutare sul prototipo se basta una pressione più corta (es. 2 s): il boot dell'S3 richiede ~0,3-0,5 s.
- Spazio parte al rilascio: è inevitabile un ritardo pari alla durata della pressione (tipicamente 100-200 ms), il prezzo per distinguere breve e media.

#### Come capisce l'utente che il gesto è riuscito

Il LED WS2812 è interno e non visibile; la PWA riceve solo i tasti.

| Gesto | Riscontro senza modifiche |
|-------|---------------------------|
| Breve / media | effetto immediato nella PWA (play/pausa, punto A/B del loop) |
| Aggiornamento | compare la rete `YTController-OTA` (se manca il WiFi di casa); con WiFi di casa: il controller sparisce dai dispositivi Bluetooth dell'iPad e ricompare dopo il riavvio |
| Azzeramento WiFi | compare la rete `YTController-OTA` |
| Standby | nessuno diretto: il controller non risponde più e risulta scollegato nelle impostazioni Bluetooth |

Proposte da valutare (non decise):
- **A. Tasto "innocuo" prima del gesto**: il firmware invia un tasto che nessuna app usa (es. F13-F15, usage 0x68-0x6A) subito prima di spegnere il BLE; la PWA lo intercetta e mostra un avviso ("Controller: aggiornamento in corso", "standby"). Pro: riscontro chiaro nella PWA. Contro: va verificato che iPadOS consegni F13+ a Safari come `KeyboardEvent` (prova con la pagina di prova); serve una voce in `app/js/keymap.js`; non funziona se la PWA non è aperta. Costo 0 €.
- **B. Servizio batteria BLE (Battery Service 0x180F)**: iPadOS mostra il livello del controller nel widget Batterie; non dà riscontro sui gesti ma sì sullo stato di connessione e sulla carica. Utile comunque.
- **C. LED visibile tramite light pipe** nella scocca (impatto scatola): riscontro diretto anche senza iPad. Costo ~0 € (stampa) ma richiede di posizionare il WS2812 vicino a una parete.
- **D. Vibrazione** (micromotore + transistor): riscontro tattile; contro: consumo, spazio, componente in più (~1-2 €).

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
| Corrente di carica | I = 1200 / R3 (A con R in Ω): 1,2 kΩ = 1 A, 2 kΩ = 0,58 A, 2,4 kΩ = 0,5 A, 3 kΩ = 0,4 A | **Scelta (2026-10-11): R3 originale (1,2 kΩ, "122") sostituita con 2,4 kΩ → 0,5 A**. Meno calore in scatola chiusa (a 1 A fino a ~1,3 W). Carica completa di una 18650 da 2500-3000 mAh in ~5-6,5 h. Verificare con il tester la corrente reale (cloni) |
| Fine carica / ricarica automatica | a C/10 (**50 mA con 0,5 A**) / riparte sotto ~4,05 V | |
| Precarica cella molto scarica | sotto 2,9 V a C/10 | |
| Limitazione termica TP4056 | 120 °C (riduce la corrente) | |
| DW01A sovraccarica | ~4,30 V (4,25-4,35), rilascio ~4,10 V | |
| DW01A sovrascarica | ~2,4 V (2,3-2,5), rilascio ~3,0 V | dopo l'intervento il modulo può restare spento finché non si collega la USB-C di ricarica |
| DW01A sovracorrente | 150 mV sul doppio MOSFET (FS8205A ~2 x 25-30 mΩ) → ~2,5-3 A; corto 1,35 V | molto oltre i nostri consumi |
| Assorbimento a riposo dalla cella | TP4056 ~2,5 µA (max 6) + DW01A ~3 µA → ~5-10 µA; i LED sono alimentati dall'USB e a riposo sono spenti | da misurare: un utente ha misurato 1,6 mA su una copia del modulo |

Carica con carico collegato (nessun load sharing):
- Il TP4056 vede la somma cella + ESP32. **Con 0,5 A la soglia di fine carica è 50 mA, cioè dello stesso ordine del carico con BLE connesso (20-50 mA)**: se il controller resta acceso e collegato durante la carica, la fine carica può non arrivare mai (cella tenuta a 4,2 V in tensione costante: non pericoloso, ma stressa la cella e il LED "carico" non si accende). In standby (deep sleep, < 0,1 mA) il problema non c'è.
  - Mitigazioni da valutare: (a) consiglio d'uso "caricare in standby"; (b) ridurre il consumo da connesso (light sleep, CPU 80 MHz, intervallo di connessione più lungo quando inattivo) sotto ~20 mA; (c) leggere il pin CHRG del TP4056 (open-drain, attivo basso in carica) su un GPIO libero (es. GPIO8, con pull-up interno) per sapere quando è in carica e andare in standby dopo qualche minuto di inattività. Va saldato un filo sul pin 7 del TP4056 o sul lato LED del modulo.
- A carica finita l'ESP32 scarica la cella fino a 4,05 V e la carica riparte (micro-cicli, accettabili).
- Non scendere sotto 0,5 A (R3 oltre 2,4 kΩ): la fine carica diventerebbe ancora più incerta.
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

## OTA e WiFi — CONFERMATA (2026-10-11)
La scheda va al PC una sola volta (primo flash, **batteria scollegata**); poi solo OTA.
1. **Partizioni**: due slot app OTA (es. "Minimal SPIFFS 1.9MB APP with OTA"), scelte al primo flash: cambiarle in seguito richiede il cavo. NVS preservata (abbinamento BLE, password AP, WiFi di casa). Verificare che il binario con BLE + WiFi + TLS stia sotto ~1,9 MB (stima 1,3-1,6 MB).
2. **Rollback**: nuova immagine "in prova", marcata valida solo dopo auto-test (BLE avviato, input ok); altrimenti ritorno automatico alla precedente. Vale sia per l'upload manuale sia per lo scaricamento automatico.
3. **Attivazione**: WiFi spento nell'uso normale; si entra con pulsante premuto + 5 scatti AVANTI (vedi gesti). All'ingresso il BLE viene fermato (iPad scollegato) per liberare memoria e radio; uscita con riavvio, automatica dopo 5 min senza attività.
4. **Build su GitHub Actions** → Release di `PZero/YouTubeController` con asset a nome fisso: `firmware.bin` e `firmware.json` (versione, dimensione, SHA-256). **Nessun segreto nel binario**.
5. **Password dell'AP** salvata in NVS via seriale al primo flash.
6. **Controlli**: rifiuto sotto ~3,7 V di batteria; verifica immagine (dimensione, SHA-256 o MD5 con `Update.setMD5()`, opzionale firma); recupero estremo via USB + fori spillo BOOT/RST.

### WiFi di casa (opzionale)
- Configurato dalla pagina web dell'AP (elenco reti trovate + password). Credenziali **solo in NVS**, mai nel repository né nel binario.
- Si cancella con il gesto premuto + 5 scatti INDIETRO, oppure con "Dimentica WiFi" dalla pagina; dopo l'azzeramento si apre la rete di configurazione.
- Nota: la NVS non è cifrata (richiederebbe flash encryption, che complica OTA e recupero). Chi ha la scheda in mano può leggere la password di casa: rischio accettabile per un oggetto domestico, da dichiarare.

### Flusso del gesto aggiornamento
```
gesto → batteria ≥ 3,7 V? ── no → (nessuna azione; eventuale tasto di avviso)
           │ sì
           ▼
      ferma BLE → WiFi di casa configurato?
           │ sì                                   │ no
           ▼                                      │
      connessione (timeout 20 s) ── fallita ──────┤
           │ ok                                   │
           ▼                                      ▼
      GET firmware.json dell'ultima Release   AP `YTController-OTA` + pagina 192.168.4.1:
      versione > attuale?                      versione, configura WiFi, carica .bin,
        no → riavvio (niente da fare)          "Dimentica WiFi"; uscita dopo 5 min
        sì → scarica firmware.bin in streaming
             nello slot libero, verifica
             dimensione + SHA-256
             ok → riavvio sulla nuova immagine (in prova → rollback se l'auto-test fallisce)
             errore/timeout → apre l'AP (fallback)
```
- URL stabili senza API: `https://github.com/PZero/YouTubeController/releases/latest/download/firmware.json` (e `.bin`). GitHub risponde con redirect 302 verso `release-assets.githubusercontent.com` / `objects.githubusercontent.com`: abilitare il follow dei redirect (`HTTPC_FORCE_FOLLOW_REDIRECTS` con `HTTPClient`/`HTTPUpdate`). In alternativa l'API `api.github.com/repos/.../releases/latest` (richiede header `User-Agent`, limite 60 richieste/h per IP, JSON più grande da analizzare).
- TLS: `NetworkClientSecure` con **bundle di certificati radice** (`setCACertBundle`, bundle ESP-IDF "common" ~40-60 KB di flash) invece di un singolo certificato fissato: GitHub e la sua CDN cambiano catena nel tempo. Niente `setInsecure()`: l'integrità è comunque protetta dallo SHA-256, ma il bundle evita di scaricare file da un server falso.
- Il repository deve restare **pubblico**: con un repository privato servirebbe un token, vietato nel binario.

### Rischi dell'aggiornamento automatico
| Rischio | Dettaglio | Mitigazione |
|---------|-----------|-------------|
| Memoria | sessione TLS mbedTLS ~40-50 KB di heap interna + WiFi ~50-70 KB; insieme a NimBLE può mancare memoria interna (la PSRAM non aiuta per tutti i buffer) | fermare e deinizializzare il BLE prima del WiFi (o riavviare in "modalità aggiornamento" tramite flag in RTC/NVS, la via più pulita); buffer TLS ridotti se serve |
| TLS / data | senza ora corretta mbedTLS (default ESP-IDF) non controlla la scadenza dei certificati; se il bundle invecchia molto (anni) una nuova radice di GitHub può non essere riconosciuta | aggiornare regolarmente il core (il bundle arriva con il firmware stesso); fallback all'AP con upload manuale sempre disponibile |
| Redirect / formato URL | GitHub può cambiare host della CDN | follow redirect generico, bundle completo, fallback AP |
| Consumo | WiFi 100-300 mA di picco per 20-60 s (connessione + ~1,5 MB di download): ~2-5 mAh, trascurabile; il rischio è il calo di tensione sui picchi a batteria bassa | soglia 3,7 V prima di iniziare, scrittura in flash solo dopo connessione stabile |
| Timeout / rete lenta | download bloccato a metà | timeout di connessione 20 s, inattività 15 s, totale 3 min; immagine parziale mai attivata (lo slot attivo non cambia finché `Update.end()` non riesce) |
| Versione | rischio di reinstallare la stessa versione o tornare indietro | versione compilata (`FW_VERSION` dal tag della Release in GitHub Actions) confrontata con `firmware.json`; si aggiorna solo se maggiore |
| Coesistenza | WiFi e BLE sulla stessa radio | mai attivi insieme nel flusso proposto |

Feedback: LED interno non visibile → indicazioni nella sezione "Come capisce l'utente che il gesto è riuscito".
