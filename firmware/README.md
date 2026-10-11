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
| 9-13 | GPIO (funzioni FSPI, libere: la flash dell'S3FH4R2 è interna su GPIO26-32) | utilizzabili come GPIO normali; anch'essi RTC |

Ordine fisico (disegno Nologo, vedi `enclosure/dimensioni.md`): fila 1 = 5V, GND, 3V3, 13, 12, 11, 10, 9, 8; fila 2 = TX, RX, 1, 2, 3, 4, 5, 6, 7. Sull'ESP32-S3 **tutti i GPIO 0-21 sono RTC**: qualunque pin degli header (tranne 43/44) può fare da sorgente `ext1`. Nessuno di 1, 2, 4-10 è strapping sull'S3 (lo sono 0, 3, 45, 46).

Pad sul retro (saldatura difficile, non usare nel prototipo): GPIO14-18, 21, 33-42, 45-48.
Da evitare: GPIO0 (BOOT), 3, 45, 46 (strapping), 19/20 (USB D-/D+), 26-32 (flash/PSRAM, non esposti), 48 (LED RGB).

LED: WS2812 RGB su **GPIO48**; il LED rosso è dato anch'esso su GPIO48 da alcune fonti (probabilmente è solo il LED di alimentazione); LED blu di carica non pilotabile.

### GPIO assegnati (aggiornato 2026-10-11)

| Segnale | GPIO | Fila header | Collegamento | Stato in deep sleep |
|---------|------|-------------|--------------|---------------------|
| Tensione batteria | 1 | 2 | partitore 220k/220k da OUT+ (vedi Alimentazione) | ingresso, nessun effetto |
| Anello LED, dato (DI) | 2 | 2 | 330 Ω in serie, vicino alla SuperMini | uscita bassa mantenuta (`gpio_hold_en`) o pull-down |
| Encoder A | 4 | 2 | contatto a GND, `INPUT_PULLUP` | non sorgente di risveglio |
| Encoder B | 5 | 2 | come sopra; comune C a GND | non sorgente di risveglio |
| Vibrazione, IN | 6 | 2 | diretto al pin IN del modulo (PWM LEDC) | basso: pull-down (100 kΩ esterno se il modulo non ne ha uno) |
| Pulsante PBS-110 | 7 | 2 | a GND, `INPUT_PULLUP` | `ext1`, attivo basso |
| Stato carica CHRG | 8 | 1 | 10 kΩ in serie verso il catodo del LED rosso (pin 7 TP4056), pull-up esterno 100 kΩ a 3V3 | `ext1`, attivo basso (solo se armato, vedi sotto) |
| Alimentazione anello (comando) | 9 | 1 | 4,7 kΩ verso la base dell'NPN driver (2N3904), pull-down 10 kΩ base→GND | flottante → anello spento dalle resistenze |
| Stato carica STDBY | 10 | 1 | 10 kΩ in serie verso il catodo del LED blu/verde (pin 6 TP4056), pull-up esterno 100 kΩ a 3V3 | `ext1`, attivo basso (solo durante la carica) |
| LED di stato | 48 | - | WS2812 integrato, non visibile in scatola | spento; solo debug |
| Riserva | 11, 12, 13 | 1 | liberi | |

Verifica dell'assegnazione proposta dal coordinatore: **confermata**. GPIO8-10 stanno sulla fila 1 (lato 5V/GND/3V3, comodo per i fili di alimentazione dell'anello e del caricatore), 2 e 6 sulla fila 2 accanto a encoder e pulsante. Tutti RTC, nessuno strapping, nessun conflitto con USB (19/20) o UART0 (43/44).
Unica cautela su GPIO9: lo stato al reset dei pin FSPI non è documentato in modo chiaro (alcuni hanno pull-up debole durante il boot); per questo il pull-down sulla base del driver è da **10 kΩ**; inoltre la resistenza base-emettitore del PNP (10 kΩ) richiede ~75 µA prima che il PNP conduca. Anche se l'anello ricevesse un po' di alimentazione per qualche ms durante il boot, senza dato i WS2812B restano spenti. Il firmware porta GPIO9 basso come prima istruzione di `setup()`. Da verificare sul prototipo; se serve, pull-down a 4,7 kΩ.
Nota: GPIO2 è vicino a GPIO1 (ADC batteria): leggere la batteria con l'anello fermo, il partitore ha già 100 nF.

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
- Deep sleep: risveglio `ext1` in modalità `ESP_EXT1_WAKEUP_ANY_LOW` (disponibile sull'S3) su GPIO7 (pulsante) più GPIO8/GPIO10 (caricatore) secondo le regole della sezione "Lettura dello stato di carica". A/B non usati come sorgente di risveglio (la manopola non deve accendere il controller in borsa). I pull-up in deep sleep vanno attivati con `rtc_gpio_pullup_en()` (dominio RTC_PERIPH acceso).

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

#### Riscontro all'utente — DECISO (2026-10-11)

Quattro canali, in ordine di importanza:
1. **Anello WS2812B 16 LED** attorno alla manopola, sotto il coperchio con diffusore (luce dove si guarda). Luminosità globale limitata a ~10-15% (valore 25-40 su 255, con correzione gamma), più un tetto di corrente in firmware (es. `FastLED.setMaxPowerInVoltsAndMilliamps(4, 100)` o equivalente).
2. **Vibrazione** per i gesti eseguiti senza guardare (impulsi brevi, intensità via PWM).
3. **Servizio batteria BLE** (Battery Service 0x180F, caratteristica 0x2A19 con notifica): livello nel widget Batterie di iPadOS. Percentuale dalla tensione con tabella non lineare (indicativa: 4,15 V = 100, 4,0 = 85, 3,85 = 60, 3,75 = 40, 3,65 = 20, 3,5 = 5, 3,3 = 0), aggiornata ogni ~60 s o a variazione ≥ 2%.
4. **Tasti innocui per la PWA** (F13-F16, mai usati da altre app) inviati prima degli eventi in cui il BLE si spegne. Da verificare che iPadOS li consegni a Safari come `KeyboardEvent`; servono le voci in `app/js/keymap.js` (impatto app). Se iPadOS non li consegna, restano luce + vibrazione.

| Tasto | Usage HID | Evento |
|-------|-----------|--------|
| F13 | 0x68 | ingresso in aggiornamento (OTA) |
| F14 | 0x69 | ingresso in standby |
| F15 | 0x6A | azzeramento WiFi |
| F16 | 0x6B | batteria scarica (sotto 3,5 V, una volta) |

Tabella eventi → effetto (colori e tempi iniziali, da tarare sul prototipo; "vibr." = impulso del motore):

| Evento | Luce sull'anello | Vibrazione | Note |
|--------|------------------|------------|------|
| Rotazione lenta / media / veloce | scia di 3-4 LED che gira nel verso della manopola e si dissolve in ~300 ms; colore per livello: lento ciano, medio giallo, veloce arancio | nessuna | il colore conferma il livello di salto; la scia segue gli scatti realmente letti, non la coda di invio |
| Pressione breve (play/pausa) | lampo bianco tenue su tutto l'anello, 80 ms | nessuna | l'effetto principale è nella PWA |
| Soglia 0,7 s raggiunta (pulsante ancora premuto) | 4 LED ambra fissi | 1 tick 30 ms | dice "se rilasci ora è loop A-B" |
| Soglia 2 s raggiunta (zona morta) | anello si spegne | nessuna | "rilasciando non succede nulla" |
| Loop A-B (rilascio tra 0,7 e 2 s, tasto L) | giro ambra completo in ~400 ms | 1 impulso 60 ms | **non** distingue A / B / cancella: il firmware non conosce lo stato del loop nella PWA (preferiti, tocchi): un contatore interno si desincronizzerebbe |
| Pressione verso i 10 s (standby) | da 2 a 10 s l'anello si riempie di rosso tenue in senso orario | a 10 s impulso lungo 300 ms | poi F14, dissolvenza e deep sleep |
| Risveglio (2 s premuto) | durante i 2 s l'anello si riempie di bianco; poi **livello batteria**: LED accesi in proporzione (16 = 100%), verde > 50%, giallo 20-50%, rosso < 20%, per 1,5 s | 1 impulso 80 ms a risveglio confermato | |
| BLE in attesa di connessione / abbinamento | 1 LED blu che gira lentamente (1 giro/2 s) | nessuna | si spegne dopo 60 s per risparmio (resta l'advertising) |
| BLE connesso | lampo blu su tutto l'anello, 300 ms | 1 impulso 50 ms | |
| BLE disconnesso | 2 lampi blu tenui | nessuna | |
| Caricatore collegato (anche da standby) | livello batteria in arancio con "respiro" lento per 5 s | 1 impulso 50 ms | poi spento; il livello letto in carica è sovrastimato (~+0,1 V) |
| Carica completata (STDBY) | anello verde pieno 3 s | nessuna | mostrato al risveglio da STDBY o alla pressione del pulsante col caricatore collegato |
| Ingresso in aggiornamento (premuto + 5 scatti avanti) | viola fisso | impulso lungo 300 ms | prima F13, poi stop BLE |
| OTA: connessione WiFi / AP aperto | viola che pulsa / viola e bianco alternati lenti | nessuna | |
| OTA: scaricamento | barra di avanzamento viola (LED accesi = % scaricata) | nessuna | |
| OTA: riuscito | verde pieno 1 s | 2 impulsi brevi | poi riavvio |
| OTA: errore / batteria < 3,7 V | rosso lampeggiante 3 volte | impulso lungo 300 ms | |
| Azzeramento WiFi (premuto + 5 scatti indietro) | anello rosso che si svuota in senso antiorario | 3 impulsi brevi | prima F15, poi rete di configurazione (effetto "AP aperto") |
| Batteria scarica (< 3,5 V) | 2 LED **rossi** lampeggiano 3 volte, ripetuto ogni 5 min in uso | 2 impulsi brevi solo la prima volta | F16 una volta; sotto 3,5 V la vibrazione è disattivata (cali di tensione) |
| Batteria esaurita (< 3,3 V) | rosso che si svuota | nessuna | poi deep sleep forzato |

Note:
- Sotto ~3,5 V il WS2812B è fuori specifica (VDD min 3,5 V): blu e verde si affievoliscono o cambiano tinta. Per questo gli avvisi di batteria usano solo il **rosso**, che funziona fino a ~3 V.
- Mai animazioni continue a riposo: dopo ogni effetto l'anello va a nero e, dopo ~2 s senza effetti, si toglie l'alimentazione (interruttore Q1/Q2), perché i 16 LED neri consumano comunque 10-16 mA.
- Il primo effetto dopo l'accensione dell'anello ha un ritardo di ~5 ms (carica del condensatore e reset dei LED): impercettibile.

### Alimentazione

Componenti in possesso: modulo "4056" USB-C (TP4056 + DW01A + FS8205A), cella 18650 (da confermare); boost MT3608 in possesso ma **non usato**.

Schema di alimentazione (decisione 2026-10-09: **niente diodo**; schema completo con anello, vibrazione e lettura carica nella sezione "Schema dei collegamenti completo"):

```
 18650 (+) ── B+  [modulo 4056]  OUT+ ═══════ nodo VBAT (3,0-4,2 V) ══┬── pin 5V SuperMini
 18650 (-) ── B-                 OUT- ═══════ nodo GND ═══════════════┼── pin GND SuperMini
                 USB-C del modulo = presa di ricarica del prodotto     │
                                                                      │
 VBAT ──[220 kΩ]──┬──[220 kΩ]── GND
                  └── GPIO1 (ADC1_CH0) + 100 nF verso GND
```

- Primo (e unico) flash via USB con la **batteria scollegata** (opzione A qui sotto); poi solo OTA.

- **Non usare i pad BAT+/BAT- della SuperMini**: il suo TP4054 (100 mA) e il diodo BAT60B sono un secondo caricatore senza protezione.
- OUT+ e B+ sono lo **stesso nodo** su questi moduli: la protezione (DW01A + FS8205A) interrompe solo il negativo (B- ↔ OUT-). Quindi OUT+ è di fatto il polo positivo della cella.
- **Rischio retroalimentazione**: sullo schema Nologo il pin 5V coincide con il VBUS dell'USB-C (non c'è diodo tra VBUS e pin 5V; c'è solo il BAT60B sul percorso dei pad BAT). Collegando la SuperMini al PC con OUT+ cablato direttamente al pin 5V, i 5 V del PC finirebbero sulla cella attraverso OUT+ = B+: carica non controllata a 5 V, rischio incendio della 18650. Da verificare col tester (resistenza VBUS ↔ pin 5V ≈ 0 Ω) sulla scheda arrivata. Soluzioni:

| Opzione | Pro | Contro | Costo |
|---------|-----|--------|-------|
| A. Scollegare la batteria (o OUT+) prima di ogni flash | nulla da aggiungere, nessuna caduta | basta una dimenticanza per un danno grave | 0 € |
| B. Schottky in serie OUT+ → 5V (SS14 / 1N5817 / BAT60) | protezione permanente, semplice | caduta 0,2-0,3 V a 30-100 mA: soglia utile della batteria sale di ~0,25 V (~10-15% di capacità persa) | ~0,05-0,1 € |
| C. Interruttore a slitta su OUT+ (SS12D00) | serve comunque come ON/OFF, zero caduta | protegge solo se è spento durante il flash | ~0,1-0,2 € |
| B + C | sicuro e con interruttore generale | caduta del diodo | ~0,2-0,3 € |

  **Decisione (2026-10-09): A**, niente diodo né interruttore. La scheda va al PC solo per il primo flash, con la batteria scollegata; poi solo OTA. Se un giorno servisse di nuovo il cavo (recupero estremo), **scollegare prima la batteria**: con OUT+ cablato al pin 5V i 5 V del PC andrebbero sulla cella. Un "diodo ideale" a P-MOSFET non è applicabile in modo semplice perché VBUS e pin 5V sono lo stesso nodo.

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
  - **Risolto (2026-10-11)** con la lettura di CHRG/STDBY (sezione "Lettura dello stato di carica"): col caricatore collegato il firmware riduce i consumi (anello al minimo, BLE con intervallo lungo) e dopo 5 min senza uso va in standby, dove la carica termina regolarmente. Restano utili (b) ridurre il consumo da connesso (light sleep, CPU 80 MHz) e il consiglio d'uso "caricare in standby".
- A carica finita l'ESP32 scarica la cella fino a 4,05 V e la carica riparte (micro-cicli, accettabili).
- Non scendere sotto 0,5 A (R3 oltre 2,4 kΩ): la fine carica diventerebbe ancora più incerta.
- Durante la carica il controller resta utilizzabile.

Soglie di tensione della batteria (cella collegata a OUT+, regolatore ME6217C33 con dropout ~0,1 V a 100 mA, più alto sui picchi radio di 200-300 mA; ESP32-S3 alimentato a 3,0-3,6 V, brown-out di default ~2,7 V):

| Vbat (cella collegata direttamente al pin 5V, nessun diodo) | Effetto |
|------|---------|
| ≥ ~3,45 V | 3V3 regolati pieni |
| ~3,2-3,45 V | funziona (3V3 = Vbat - dropout) |
| < ~3,1 V | rischio reset sui picchi BLE |

- Soglie firmware: avviso batteria scarica a **3,5 V** (anello rosso, F16, vibrazione disattivata), deep sleep forzato a **3,3 V**, niente OTA sotto **3,7 V**. Il distacco del DW01A a 2,4 V è solo l'ultima difesa: troppo basso per la salute della cella.
- Le soglie vanno lette **a carico fermo** (anello spento, motore fermo): sotto carico la tensione cala di ~0,05-0,1 V.
- Lettura batteria: partitore 220 kΩ / 220 kΩ tra OUT+ e OUT- (consumo ~9,5 µA) con 100 nF sul punto centrale, su **GPIO1** (ADC1_CH0, libero, RTC). 4,2 V → 2,1 V, entro la scala con attenuazione 11 dB. Usare `analogReadMilliVolts()` (calibrazione eFuse), media di 8-16 letture, leggere a radio ferma o mediare. Per azzerare il consumo si può alimentare il partitore da un GPIO solo durante la misura.

Autonomia stimata (18650 2500-3000 mAh, ~2000-2400 mAh utili fino a 3,4-3,5 V):
- In uso, BLE connesso 20-50 mA: ~40-120 ore.
- Standby in deep sleep: scheda ~43 µA + modulo ~10 µA + partitore ~10 µA ≈ 65 µA → oltre 3 anni in teoria; nella pratica conta l'autoscarica della cella (~2-3%/mese). Con il boost MT3608 lo standby salirebbe a 0,2-1,5 mA (2-12 mesi) senza alcun vantaggio: per questo non si usa.

### Anello LED WS2812B 16 LED

In possesso. Ø45/Ø33, spessore 3 (quote in `enclosure/dimensioni.md`). Piazzole di ingresso − / DI / + (usate), di uscita − / DO / +5V (non collegate).

**Interruttore di alimentazione (high-side)** — riprogettato con i transistor TO-92 del kit in possesso (vincolo: niente acquisti di singoli SMD). Serve perché i 16 LED neri assorbono 10-16 mA anche senza luce. Il PNP con emettitore a VBAT (fino a 4,2 V) **non si può comandare direttamente dal GPIO** (con il GPIO a 3,3 V resterebbe in conduzione: Vbe = -0,9 V): serve un NPN come driver.

Scelta:
- **Q1 high-side: S8550 (PNP)**. Ic max 0,5 A (1,5 A nelle versioni "SS8550"), hFE 85-300 a 100 mA secondo la classe (B 85-160, C 120-200, D 160-300), Vce(sat) ~0,1-0,2 V a 100 mA con Ib ~4-5 mA (0,5 V max a 500 mA). Alternativa equivalente nel kit: **S9012** (PNP, 0,5 A, hFE 64-300). Scartati: 2N3906 (200 mA max, Vce(sat) 0,4 V già a 50 mA: va bene solo per la scia, non per il caso peggiore), A1015 (150 mA), 2N5401 (alta tensione, hFE basso).
- **Q2 driver: 2N3904 (NPN)**. Deve assorbire solo ~5 mA; scelto rispetto all'S8050 perché ha il **pinout JEDEC standard (E-B-C)**, meno variabile. Equivalenti nel kit: S8050, S9013, S9014, C1815, C945, 2N2222.
- Il firmware limita la corrente dell'anello a **100 mA** (tetto di potenza della libreria), così Q1 lavora sempre ben saturo.

Resistenze (in possesso):

| Rif. | Valore | Posizione | Calcolo |
|------|--------|-----------|---------|
| R1 | 4,7 kΩ | GPIO9 → base Q2 | Ib(Q2) = (3,3 - 0,7)/4,7k - 0,7/10k ≈ 0,48 mA → Q2 saturo (β forzato ~10 su ~5 mA) |
| R2 | 10 kΩ | base Q2 → GND | pull-down: Q2 spento con GPIO flottante (boot, deep sleep) |
| R3 | 680 Ω | collettore Q2 → base Q1 | Ib(Q1) = (VBAT - 0,75 - 0,1)/680 - 0,075 mA ≈ **3,8 mA a 3,5 V, 4,9 mA a 4,2 V** → β forzato 20-26 a 100 mA: saturo anche con un S8550 di classe B |
| R4 | 10 kΩ | base Q1 → emettitore Q1 (VBAT) | garantisce lo spegnimento del PNP (scarica la base, assorbe le perdite di Q2) |

Effetto collaterale utile: la caduta di 0,1-0,2 V su Q1 abbassa un po' la VDD dell'anello e migliora il margine sul livello logico del dato a batteria piena (VIH 0,7 x 4,0 = 2,8 V).

| Opzione | Pro | Contro | Costo |
|---------|-----|--------|-------|
| **A. S8550 + 2N3904 (kit TO-92)** (proposta) | in possesso; si monta in breadboard e su millefori; avvio graduale intrinseco (vedi sotto) | ~4-5 mA di corrente di base persi ad anello acceso; caduta 0,1-0,2 V; pinout S8550 da verificare | 0 € |
| B. S9012 + S8050/S9013 (kit) | in possesso, prestazioni equivalenti | pinout da verificare su entrambi | 0 € |
| Scartata per costo: P-MOSFET AO3401A + N 2N7002 (SOT-23) | nessuna corrente di comando, caduta < 15 mV | acquisto di SMD singoli, adattatori per breadboard, serve R-C di avvio graduale | ~3-6 € a busta |
| Scartata: interruttore low-side (NPN sul negativo dell'anello) | un solo transistor | con il GND dell'anello scollegato il dato DI trova un ritorno attraverso i diodi interni: LED fantasma e consumo | |

**Pinout TO-92: verificarlo su ogni pezzo.** S8050/S8550/S90xx sono di solito **E-B-C** (faccia piatta verso di sé, piedini in basso, da sinistra), ma alcuni produttori usano **E-C-B**; C945/C1815/A1015 (stile giapponese) sono **E-C-B**; 2N2222 in TO-92 può essere E-B-C o C-B-E. Come verificare col tester:
1. **Prova diodi**: cercare il piedino comune che conduce (~0,6-0,7 V) verso entrambi gli altri: è la **base**. Se conduce con il puntale **rosso** sulla base è un NPN, con il **nero** sulla base è un PNP. Tra gli altri due piedini non deve condurre nulla in nessun verso.
2. Delle due giunzioni, quella **base-emettitore** ha una tensione di qualche mV più alta della base-collettore: così si distingue l'emettitore.
3. Conferma con lo **zoccolo hFE** del tester (NPN/PNP, E-B-C): nel verso giusto si leggono 100-300; con collettore ed emettitore scambiati si leggono valori bassi (5-30).

**Avvio graduale**: con i BJT **non servono R-C aggiuntivi**. La corrente di collettore di Q1 è limitata a circa hFE x Ib ≈ 0,6-1,5 A: il condensatore di bulk si carica in ~0,2-0,7 ms (energia ~0,4-0,8 mJ, nessun problema termico) e il calo di VBAT per l'ESP32 resta di ~0,1-0,15 V per meno di 1 ms. Per stare più larghi con lo S8550 (0,5 A continui) basta un bulk da **47 µF** invece di 100 µF (picco uguale, durata dimezzata). Nessun pericolo per il DW01A (cortocircuito a ~20 A).

**Dato**: 330 Ω in serie su DI, montato vicino alla SuperMini (smorza le riflessioni sul filo e limita la corrente se il dato è alto ad anello spento). Livelli: VIH del WS2812B = 0,7·VDD → 2,8 V a VBAT 4,0 V e **2,94 V a 4,2 V**; l'uscita dell'ESP32 a vuoto è ~3,3 V (minimo garantito da datasheet 0,8·VDD = 2,64 V, ma con carico capacitivo il valore reale è ~3,2-3,3 V). Margine ridotto solo a batteria appena carica: in pratica funziona. Se a 4,2 V comparissero sfarfallii: ripiego con un buffer 74AHCT1G125 alimentato da VBAT (~0,3 €) o un diodo 1N4148 in serie al + del solo primo LED (non praticabile su anello già montato). Da provare a batteria piena.

**Condensatore di bulk**: **47 µF** (fino a 100 µF) 10-16 V elettrolitico **sul portaschede, subito dopo Q1** e non sull'anello: con la corrente limitata a 100 mA e 10-20 cm di filo basta, mentre sotto il coperchio lo spazio è minimo. Gli anelli WS2812B in commercio hanno di norma un 100 nF per LED (verificare sul retro). Se comparissero sfarfallii: 10 µF saldato direttamente sulle piazzole +/− di ingresso.

**Sequenza obbligatoria (back-powering)**: senza alimentazione, un dato alto alimenterebbe il primo LED attraverso il diodo di protezione di DI.
- Accensione: GPIO2 uscita bassa → GPIO9 alto → attesa 5 ms (carica del bulk < 1 ms + reset dei WS2812B) → primo `show()`.
- Spegnimento: `show()` tutto nero → GPIO2 basso (il driver RMT deve avere livello di riposo basso, default per WS2812) → GPIO9 basso. Il BJT si spegne in pochi µs; il bulk si scarica nell'anello (quiescente ~15 mA) in ~10-20 ms. Nessuna attesa necessaria prima del deep sleep, purché il dato sia già basso.
- In deep sleep: GPIO2 basso mantenuto (`gpio_hold_en` / `gpio_deep_sleep_hold_en`) o in ingresso con pull-down; GPIO9 flottante (R2 tiene spento Q2, R4 tiene spento Q1).

Libreria: FastLED o Adafruit_NeoPixel (entrambe usano l'RMT sull'S3, nessun conflitto con il BLE); scegliere quella che supporta luminosità globale e limite di corrente (FastLED).

### Modulo vibrazione

In possesso: motore a moneta ~Ø10 (probabile 1027, 3 V nominali), modulo con pin GND / VCC / IN, transistor + diodo + resistenze a bordo, IN alto = vibra, ~70-90 mA (spunto ~100-120 mA per qualche ms).

- **VCC da VBAT** (non dal 3V3: il regolatore della SuperMini deve restare per l'ESP32 e lo spunto del motore lo disturberebbe). GND al nodo GND comune (OUT-).
- **IN da GPIO6**. La base del transistor ha già la sua resistenza sul modulo: corrente dal GPIO ~1-3 mA, va bene. Intensità con **PWM LEDC a ~20-25 kHz** (non udibile), 8 bit. Compensazione della tensione: duty ≈ 3,0 V / VBAT (≈ 70% a batteria carica), così l'intensità resta costante e il motore da 3 V non lavora a 4,2 V.
- **Pull-down su IN**: verificare col tester se il modulo ha una resistenza IN→GND. Se manca, aggiungere 100 kΩ IN→GND (durante boot e deep sleep il GPIO è flottante: il motore potrebbe ronzare o assorbire qualche mA).
- **LED di alimentazione**: alcuni moduli hanno un LED "power" sempre acceso (1-3 mA dalla cella anche in standby, ~1-2 mesi di autonomia persi all'anno). Se presente, **dissaldarlo o tagliarne la pista**.
- **Disturbi**: il motore a spazzole genera picchi sulla linea e ritorni di corrente. Contromisure: condensatore **47-100 µF + 100 nF** tra VCC e GND vicino al modulo; condensatore ceramico **100 nF direttamente sui terminali del motore** se non c'è; fili VCC/GND intrecciati e lontani dall'antenna della SuperMini. Il BLE non è disturbato in radiofrequenza in modo apprezzabile; il rischio vero è il calo di VBAT a batteria bassa → vibrazione **disattivata sotto 3,5 V**.
- Impulsi brevi (30-300 ms): consumo medio trascurabile.

### Lettura dello stato di carica (CHRG / STDBY)

Sul modulo 4056 ogni LED è collegato così: VBUS (5 V dell'USB-C) → resistenza (~1 kΩ) → LED → pin open-drain del TP4056 (pin 7 CHRG = LED rosso, acceso in carica; pin 6 STDBY = LED blu/verde, acceso a carica completa). Si salda un filo sul **catodo** di ciascun LED (lato verso il TP4056) o direttamente sui pin 7 / 6 del TP4056.

Verifica delle tensioni sul catodo:
- LED acceso: il pin è chiuso a massa → ~0,1-0,3 V.
- LED spento col caricatore collegato: il catodo sale a 5 V - Vf del LED a corrente quasi nulla. Per il rosso (Vf ~1,5 V a pochi µA) → **~3,5 V, oltre i 3,3 V** del GPIO (massimo assoluto 3,6 V): non distrugge nulla (la corrente è limitata dalla resistenza da 1 kΩ e dal LED), ma il pin viene alimentato attraverso il diodo di protezione. Per il blu/verde (Vf ~2,4-2,6 V) → ~2,5 V.
- Caricatore scollegato: VBUS a 0 V, LED in inversa, pin open-drain non alimentato (il datasheet ammette su CHRG/STDBY tensioni ben oltre VCC, quindi non dovrebbe esserci un diodo verso VCC) → nessuna corrente attesa dalla linea. **Da verificare** misurando la corrente di standby col caricatore scollegato.

| Opzione di collegamento | Livello basso (in carica) | Livello alto | Pro / contro | Costo |
|-------------------------|---------------------------|--------------|--------------|-------|
| **B. 10 kΩ in serie + pull-up esterno 100 kΩ verso 3V3** (scelta, 2026-10-11) | 0,2 + 3,1 x 10/110 ≈ **0,48 V** (VIL = 0,83 V) | ~3,3 V; con LED rosso spento al massimo ~3,45 V con corrente < 2 µA (innocuo, sotto il massimo assoluto 3,6 V) | solo resistenze in possesso; il pull-up esterno non richiede pull-up RTC in deep sleep; con il blu/verde spento il catodo resta a 3,3 V (il LED non conduce) | 0 € |
| A. Schottky BAT43 / 1N5819 + pull-up | ~0,45 V | 3,3 V netti | isolamento perfetto, ma da acquistare | ~0,05 € + spedizione |
| Scartata: NPN del kit come invertitore (base sul catodo tramite 100 kΩ) | | | logica invertita e **ambigua**: a caricatore scollegato il transistor è spento come quando il LED è acceso; la corrente di base passa nel LED (lieve bagliore al buio) | |
| Scartata: 10 kΩ in serie + pull-up interno (~45 kΩ, tolleranza ampia) | ~0,8 V | ok | livello basso al limite di VIL: letture incerte | |
| Scartata: partitore | | | inutile (il problema è solo il livello alto debole) e consuma | |

Consumo delle linee: a caricatore scollegato nessuno (LED in inversa, catodo e GPIO a 3,3 V); in carica ~30 µA per linea dal 3V3, irrilevante. In firmware: GPIO8/10 in ingresso **senza** pull interni.

Uso in firmware:
- Lettura con antirimbalzo e filtro: CHRG lampeggia (1-4 Hz) se la batteria manca o è in guasto; considerare valido uno stato stabile per ≥ 2 s.
- **Risveglio**: `ext1` `ANY_LOW` sulla maschera (GPIO7 sempre) + GPIO8 e/o GPIO10 secondo questa regola: **si arma una linea solo se in quel momento è alta**, altrimenti il chip si risveglierebbe subito in ciclo.
  - Caricatore scollegato (CHRG e STDBY alti): maschera = GPIO7 + GPIO8 → collegando il caricatore il controller si sveglia, mostra la carica (arancio) e torna in standby.
  - In carica (CHRG basso, STDBY alto): maschera = GPIO7 + GPIO10, più un timer di sicurezza (es. 30 min) per accorgersi dello scollegamento → a carica completa si sveglia, mostra verde e torna in standby.
  - Carica completa (STDBY basso): maschera = GPIO7 + timer (30-60 min); al risveglio da timer, se entrambe le linee sono alte il caricatore è stato tolto → si riarma GPIO8.
- **In uso con il caricatore collegato**: anello al minimo, BLE con intervallo di connessione lungo quando inattivo, standby automatico dopo 5 min senza comandi (così il TP4056 vede la corrente scendere sotto i 50 mA e termina la carica).
- Lo STDBY è opzionale: senza, la carica completa si vede solo dal LED del modulo (interno) o deducendola dalla tensione dopo lo scollegamento. Costo del filo in più trascurabile: consigliato.

### Schema dei collegamenti completo

```
                          MODULO 4056 (TP4056 + DW01A + FS8205A)
   18650 (+) ─── B+ ┐                                     ┌── OUT+ ══╦══ nodo VBAT (3,0-4,2 V)
   18650 (-) ─── B- ┘   USB-C = presa di ricarica         └── OUT- ══╬══ nodo GND (tutte le masse qui, mai su B-)
                         LED rosso: catodo = pin 7 CHRG ───────┐     ║
                         LED blu/verde: catodo = pin 6 STDBY ─┐│     ║
                                                              ││     ║
 SUPERMINI ESP32-S3                                           ││     ║
   5V  ═══════════════════════════════════════════════════════╪╪═════╣ VBAT
   GND ═══════════════════════════════════════════════════════╪╪═════╣ GND
   GPIO1 ──┬── 100 nF ── GND                                  ││
           └── nodo centrale partitore VBAT ─220k─┬─220k─ GND ││
   GPIO8  ───[10 kΩ]──────────────────────────────────────────┼┘   + 100 kΩ GPIO8 → 3V3
   GPIO10 ───[10 kΩ]──────────────────────────────────────────┘    + 100 kΩ GPIO10 → 3V3
   GPIO4 ── encoder A      GPIO5 ── encoder B      encoder C ── GND
   GPIO7 ── PBS-110 ── GND

 INTERRUTTORE ANELLO (sul portaschede, transistor TO-92 del kit)
                        VBAT
                          │
                   ┌──────┤
                 R4 10 kΩ │ E
                   │      │
                   ├──── B  Q1 S8550 (PNP)
                   │      │ C
                 R3 680 Ω ├──────────────┬────────────── LED+ ──┐
                   │                   47 µF                    │
                   │ C                   │                      │ connettore 3 poli
   GPIO9 ─R1 4,7k─┬─ B  Q2 2N3904 (NPN)  GND                    │ portaschede ↔ scocca
                  │  │ E                                        │
              R2 10 kΩ  GND                                     │
                  │                                             │
                 GND                                            │
   GPIO2 ──[330 Ω]──────────────────────────────────── DI ──────┤
   GND ─────────────────────────────────────────────────── − ───┘
                                                     ANELLO: piazzole ingresso + / DI / −
                                                             (uscita +5V / DO / − libere)

 VIBRAZIONE
   VBAT ──┬─────────────── VCC ┐
       47-100 µF + 100 nF      │ modulo vibrazione (transistor + diodo a bordo)
   GND ───┴─────────────── GND │   motore: + 100 nF sui terminali se assente
   GPIO6 ────────────────── IN ┘   (+ 100 kΩ IN→GND se il modulo non ha pull-down)
```

Tutto ciò che non è la SuperMini o il modulo 4056 (transistor, resistenze, condensatori, connettore) sta su una **schedina millefori** sul portaschede (quote indicative in `enclosure/dimensioni.md`).

Connettore anello (sulla scocca) ↔ portaschede:

| Opzione | Pro | Contro | Costo |
|---------|-----|--------|-------|
| **JST-PH 2,0 mm, 3 poli** (proposta) | polarizzato, compatto, tiene bene a frizione; cavetti già crimpati in commercio | serve crimpatrice o cavetti pronti; non entra in breadboard senza adattatore | ~0,1-0,2 € la coppia; kit con cavetti ~8-12 € |
| JST-XH 2,5 mm, 3 poli | polarizzato, robusto, entra quasi nel passo 2,54 (prototipo) | più grande (~10 x 5,8 x 7 la parte maschio) | ~0,1-0,2 € |
| JST-SH 1,0 mm, 3 poli | minuscolo | fragile, crimpatura difficile, fili sottili | ~0,2 € |
| Dupont 2,54 mm, 3 poli | economico, già disponibile | **non polarizzato**: invertire + e − danneggia l'anello; si allenta con le vibrazioni | ~0,05 € |

Se anche il modulo vibrazione, l'encoder e il pulsante stanno sulla scocca, valutare un unico connettore multipolare (JST-PH 8 poli: GND, encoder A, encoder B, pulsante, LED+, DI, VIB VCC, VIB IN) invece di più connettori a 3 poli identici: evita anche lo scambio tra connettori uguali. Da decidere con `design-3d` (dove va il motore).

### Consumi

| Stato | Corrente stimata | Note |
|-------|------------------|------|
| Deep sleep (standby) | ~43 µA scheda + ~10 µA modulo 4056 + ~10 µA partitore + perdite dei transistor spenti (nA) ≈ **65 µA** | i pull-up esterni di CHRG/STDBY non consumano a caricatore scollegato; verificare la perdita reale col tester (modulo vibrazione senza LED di alimentazione!) |
| In uso, BLE connesso, anello spento (Q1/Q2 interdetti) | 20-50 mA | da misurare; perdite dell'interruttore ≈ 0 |
| Comando dell'anello, ad anello alimentato | +4-5 mA (base di Q1, da VBAT) + ~0,5 mA (base di Q2, dal GPIO) | persi solo mentre l'anello è alimentato |
| Anello alimentato ma nero | +10-16 mA | quiescente dei 16 driver: per questo si toglie l'alimentazione dopo ~2 s |
| Anello, scia di 4 LED monocolore al 12% | +15-20 mA (quiescente compreso) | ~20 mA per canale al 100%, PWM 12% → ~2,4 mA per canale per LED |
| Anello, 16 LED bianchi al 12% (caso peggiore) | +100 mA (sarebbero ~125) | limitato dal tetto di corrente in firmware |
| Vibrazione | +70-90 mA (spunto ~120 mA) per 30-300 ms | media trascurabile |
| Picco totale possibile | ~525 mA (BLE 300 + anello 100 + comando 5 + motore 120) | ben sotto la sovracorrente del DW01A (~2,5-3 A); a batteria bassa limitato da soglie firmware |

Media realistica in uso (rotazioni frequenti, anello acceso ~10-20% del tempo): **+3-6 mA** (comando incluso) rispetto al solo BLE → autonomia in uso ridotta di ~10%. Deep sleep invariato.

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
- WS2812B (Worldsemi), VDD 3,5-5,3 V, VIH 0,7·VDD: https://cdn-shop.adafruit.com/datasheets/WS2812B.pdf
- S8550 / S8050 (datasheet tipici di vari produttori, hFE per classi B/C/D; pinout variabile)
- 2N3904 / 2N3906 (onsemi): https://www.onsemi.com/pdf/datasheet/2n3903-d.pdf , https://www.onsemi.com/pdf/datasheet/2n3906-d.pdf
- TP4056: pin 6 STDBY, pin 7 CHRG open-drain (datasheet sopra)
- ESP32-S3: RTC GPIO 0-21, `ext1` ANY_LOW: https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/system/sleep_modes.html

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
gesto → batteria ≥ 3,7 V? ── no → (anello rosso x3 + vibrazione lunga, nessuna azione)
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

Feedback (anello, vibrazione, tasti F13/F15): vedi la sezione "Riscontro all'utente — DECISO".
