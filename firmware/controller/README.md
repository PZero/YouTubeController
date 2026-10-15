# Firmware del controller (v0)

Prima versione del firmware vero: encoder, pulsante con gesti, anello, vibrazione, **tastiera BLE HID**, WiFi di casa, rete di configurazione con portale captive e aggiornamento OTA. Logica di encoder/anello/vibrazione ripresa da `../test_comandi/`.

## File

| File | Contenuto |
|------|-----------|
| `controller.ino` | setup/loop, gesti del pulsante, rollback OTA |
| `config.h` | pin, soglie, tempi, nomi (unico posto da modificare per la taratura) |
| `ingressi.*` | encoder in interrupt, antirimbalzo del pulsante, livello di velocità (1/2/3 con isteresi) |
| `tasti.*` | mappa tasti (usage HID), coda con cadenza 33 ms, cancellazione delle frecce opposte |
| `ble_tastiera.*` | tastiera BLE HID con la libreria BLE del core (NimBLE), "Just Works" con bonding, servizio batteria |
| `feedback.*` | effetti dell'anello e vibrazione, non bloccanti |
| `rete.*` | WiFi (credenziali solo in NVS), portale, pagina web, OTA manuale (/update) e da GitHub Release |
| `monitor.html` | pagina Web Serial (Chrome/Edge) che interpreta i log |

## Compilazione e caricamento (batteria scollegata)

```
arduino-cli compile --fqbn "esp32:esp32:esp32s3:CDCOnBoot=cdc,PartitionScheme=min_spiffs" firmware/controller
arduino-cli upload -p COM3 --fqbn "esp32:esp32:esp32s3:CDCOnBoot=cdc,PartitionScheme=min_spiffs" firmware/controller
```

Librerie: solo core `esp32:esp32` 3.3.x (BLE, WiFi, WebServer, DNSServer, ESPmDNS, Preferences, Update, HTTPClient, NetworkClientSecure) più `Adafruit NeoPixel`.

**Partizioni: "Minimal SPIFFS" (`min_spiffs`)**, due slot app OTA da 1,9 MB + NVS. Lo schema di default della SuperMini (4 MB) ha due slot da 1,25 MB: con BLE + WiFi + TLS il binario è già vicino (vedi dimensione stampata dalla compilazione). Lo schema va scelto al primo flash via cavo: un .bin caricato via OTA deve essere compilato con **lo stesso** schema.

## Gesti

| Gesto | Uso normale | In OTA / portale |
|-------|-------------|------------------|
| Breve (< 0,7 s) | Spazio | esce (riavvio) |
| Media (0,7-2 s) | L | nulla |
| 2-10 s | nulla (annullato) | nulla |
| Lunga (≥ 10 s) | spegnimento immediato (deep sleep, vedi Sospensione) | nulla |
| Premuto + 5 scatti avanti | modalità OTA | - |
| Premuto + 5 scatti indietro | azzera WiFi e apre il portale | azzera WiFi |

Qualsiasi scatto con il pulsante premuto annulla breve/media/lunga e non invia frecce. La rotazione invia ←/→, Shift+←/→, Alt+←/→ secondo il livello di velocità.

## Riscontro (anello / vibrazione)

Come la tabella in `../README.md`, con queste scelte dove non era definito:
- all'avvio: 1 LED blu che gira finché l'iPad non si collega (massimo 60 s);
- OTA pronto (WiFi di casa collegato, pagina disponibile): viola tenue con 1 LED bianco che gira;
- uscita da OTA / portale: 2 lampi bianchi tenui + vibrazione 50 ms, poi riavvio;
- vibrazione sempre a **piena potenza** (duty 255, PWM 20 kHz) e **mai sotto 60 ms** (`VIB_MIN_MS`): più corti il motore non parte; impulso di 60 ms a ogni scatto (almeno 110 ms tra due, `VIB_SU_SCATTO`) e alla pressione del pulsante (`VIB_SU_PRESSIONE`), come in `test_comandi`.
- L'interruttore dell'anello (GPIO9) viene comandato già ora; sul banco l'anello è al 5V e non cambia nulla.

## BLE

- Nome **"YouTube Controller"**, aspetto "tastiera", abbinamento **Just Works** (nessun PIN), bonding salvato in NVS: dopo un riavvio l'iPad si ricollega da solo.
- Report: 8 byte (modificatori, riservato, 6 tasti), Report ID 1; ogni tasto = pressione e rilascio subito dopo.
- Batteria: livello fisso 100% (`BLE_BATTERIA_SIMULATA`) finché il partitore non è collegato.
- Servizi HID costruiti a mano (non con `BLEHIDDevice` del core): report map, Input/Output Report e Protocol Mode accessibili **solo su link cifrato** (`READ_ENC`/`WRITE_ENC`), come `NimBLEHIDDevice` usato da ESP32-BLE-Keyboard di T-vK; il server chiede la cifratura alla connessione. Diagnostica: `BLE SICUREZZA ok cifrato=1 bond=1`, `BLE NOTIFICHE on` (CCCD dell'Input Report scritto dall'iPad); senza notifiche i tasti risultano `NON_SOTTOSCRITTO`.
- **BLE e WiFi non convivono**: con NimBLE inizializzato la scansione WiFi manda l'S3 in panic (Interrupt WDT, provato). I gesti OTA / azzera WiFi inviano F13 / F15, salvano la richiesta in RAM RTC e **riavviano senza BLE** (`INFO riavvio in modalita_rete ...`, poi `BLE SOSPESO modalita_rete`). Si esce sempre con un riavvio, che riaccende il BLE.
- Dopo ogni cambio della struttura GATT (come il 2026-10-14): su iPad **"Dimentica questo dispositivo"** e riabbinare, altrimenti iOS usa la struttura memorizzata e non riceve i tasti. Se non si ricollega, cancellare anche il bonding sulla scheda (oggi: "Erase All Flash" via cavo).

## Sospensione (v0.1.3)

- **Autospegnimento** dopo `SOSPENSIONE_DOPO` = 5 min senza scatti né pressioni (anche con l'iPad collegato; mai in OTA o portale).
- **Conto alla rovescia** negli ultimi 32 s: 16 LED rossi, uno si spegne ogni 2 s (`SOSPENSIONE CONTO <s>`). Uno scatto o una pressione lo annulla (`SOSPENSIONE ANNULLATA`, vibrazione 60 ms) e **non** genera tasti: serve solo a "svegliare".
- **Spegnimento** (fine del conto o pressione ≥ 10 s): vibrazione 300 ms, anello nero, iPad disconnesso (`BLE SPENTO`), attesa del rilascio del pulsante, GPIO2 / GPIO6 / GPIO9 bassi mantenuti (`gpio_hold`), deep sleep con risveglio `ext1` su GPIO7 (pull-up RTC). Log `SOSPENSIONE ORA <motivo>`. In deep sleep **la USB sparisce**: per caricare firmware risvegliarlo (o premere RST).
- **Risveglio**: premere lo switch e tenerlo **2 s** (`SOSPENSIONE RISVEGLIO`, lampo e vibrazione); se si rilascia prima torna subito a dormire senza accendere anello né BLE (`SOSPENSIONE RISVEGLIO_ANNULLATO`, di solito non visibile perché la USB non fa in tempo a comparire). La pressione di risveglio non genera Spazio / L; l'iPad si ricollega col bond salvato.
- V1 senza transistor: l'anello è sempre alimentato e i 16 LED neri consumano comunque ~10-16 mA in deep sleep (da misurare): accettato per ora.

## Comandi di debug da seriale

Una lettera inviata sulla seriale (es. dalla console di Arduino IDE): `O` = gesto OTA, `R` = gesto azzera WiFi, `Q` = esci dalla modalità rete, `S` = sospensione dopo 40 s (dopo 8 s fermo parte il conto da 32 s), `N` = sospensione normale (5 min), `Z` = sospendi subito, `V` = vibrazione 500 ms, `H` = GPIO6 alto 500 ms senza PWM. Servono a provare i percorsi senza la manopola.

## WiFi, portale, OTA

- Credenziali di casa **solo in NVS** (namespace `ytc`, chiavi `ssid`, `pass`); mai nei log, mai rimandate nella pagina.
- Rete di configurazione: **`YTController-XXXX`** (ultime 4 cifre del MAC), indirizzo **http://192.168.4.1/**, portale captive (DNS che risponde a tutto).
- Password della rete di configurazione: **`ytcontroller`** (in `config.h`). **Non è un segreto**: è pubblica nel repository. Scelta rispetto alla rete aperta perché evita collegamenti casuali e le richieste di "rete non protetta"; la vera protezione è che la rete esiste solo dopo un gesto fisico e per 5 minuti. Si può sostituire dalla pagina (salvata in NVS, chiave `ap_pass`).
- Pagina: reti trovate, SSID, password, "Salva e collega", "Dimentica WiFi", "Cerca aggiornamento su GitHub" (se collegato a casa), caricamento .bin (`/update`), cambio password AP, "Esci".
- Modalità OTA: con WiFi di casa configurato si collega (timeout 20 s; se fallisce apre il portale), pubblica la pagina su `http://<ip>/` e `http://ytcontroller.local/`, poi controlla subito l'ultima Release di `PZero/YouTubeController` (`firmware.json`: `version`, `size`, `sha256`; poi `firmware.bin` con verifica di dimensione e SHA-256, certificati dal bundle del core). Si aggiorna solo se la versione è maggiore di `FW_VERSION`.
- Uscita automatica dopo **5 min** senza attività (pagine, pulsante, manopola), oppure pressione breve.
- Rollback: la nuova immagine parte "in prova" ed è convalidata dopo 10 s di funzionamento (`OTA CONVALIDATA`); se si riavvia prima (crash), il bootloader torna alla precedente.
- La pagina `/update` in modalità OTA è raggiungibile da chiunque sia sulla rete di casa per quei 5 minuti (nessuna password): rischio accettato per ora.
- **Manca il workflow GitHub Actions** che pubblica `firmware.bin` + `firmware.json` nella Release: oggi il controllo risponde `OTA ERRORE json_http 404 nessuna_release`.

## Formato dei log (seriale USB, 115200)

Una riga per evento, campi separati da spazi, prefisso stabile in testa. Mai password.

| Riga | Significato |
|------|-------------|
| `ENC <+1\|-1> <pos> <livello> <scatti/s>` | scatto; livello 0 = pulsante premuto (nessun tasto) |
| `BTN 1` / `BTN 0 <ms>` | pressione / rilascio con durata |
| `GESTO BREVE\|MEDIA\|LUNGA\|OTA\|RESET_WIFI\|ANNULLATO [dettaglio]` | gesto riconosciuto |
| `TASTO <nome> INVIATO\|NON_COLLEGATO\|NON_SOTTOSCRITTO <in coda>` | tasto uscito dalla coda (Spazio, L, Sinistra, Shift+Destra, Alt+Sinistra, F13...) |
| `BLE PUBBLICITA <nome>` / `BLE CONNESSO` / `BLE DISCONNESSO` / `BLE SOSPESO modalita_rete` | stato della tastiera |
| `BLE SICUREZZA ok cifrato=<0/1> bond=<0/1>` / `BLE SICUREZZA errore <codice>` | esito della cifratura / abbinamento |
| `BLE NOTIFICHE on\|off <valore CCCD>` | l'iPad ha abilitato / disabilitato le notifiche dell'Input Report |
| `VIB <ms>` | impulso di vibrazione |
| `SOSPENSIONE CONTO <s>\|ANNULLATA\|ORA <motivo>\|ATTESA_RILASCIO\|RISVEGLIO\|RISVEGLIO_ANNULLATO` | autospegnimento e risveglio |
| `BLE SPENTO` | iPad disconnesso prima del deep sleep |
| `WIFI SPENTO\|CONNESSIONE <ssid>\|CONNESSO <ip> <rssi>\|ERRORE <motivo>\|SALVATO <ssid>\|AZZERATO\|NON_CONFIGURATO` | WiFi di casa |
| `PORTALE APERTO <url> <motivo> <ssid>` / `PORTALE SCANSIONE <n>` / `PORTALE CHIUSO <motivo>` | rete di configurazione |
| `OTA INGRESSO\|PRONTO <url> <url_mdns>\|CONTROLLO\|VERSIONE <remota> <locale>\|NESSUN_AGGIORNAMENTO\|SCARICO <%>\|CARICAMENTO <%>\|RIUSCITO\|ERRORE <motivo>\|USCITA <motivo>\|CONVALIDATA` | aggiornamento |
| `VIVO <s> <transizioni non valide> <heap KB> <stato BLE>` | battito ogni 5 s |
| `INFO ...` / `ERRORE ...` | avvio (versione, partizione, motivo del reset), riavvii, avvisi |
