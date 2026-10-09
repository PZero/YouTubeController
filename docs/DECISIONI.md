# Registro delle decisioni

Una voce per decisione: data, decisione, motivazione. Le voci non si riscrivono: se una decisione cambia, se ne aggiunge una nuova che la sostituisce.

| Data | Decisione | Motivazione |
|------|-----------|-------------|
| 2026-10-09 | Il controller si presenta come tastiera BLE HID (da validare con prototipo) | Safari su iPadOS non supporta Web Bluetooth |
| 2026-10-09 | Una sola sessione coordinatrice con tre subagenti (elettronica-firmware, app-pwa, design-3d) | Un unico interlocutore; contesti separati, meno token |
| 2026-10-09 | La memoria del progetto sta nei file in `docs/`, aggiornati con `/fine-sessione` | Le sessioni ripartono pulite senza rileggere le chat |
| 2026-10-09 | Modello 3D come codice parametrico | Modificabile dagli agenti e allineabile alle misure dei componenti |
| 2026-10-09 | CAD: OpenSCAD; base di partenza `enclosure/youtube_control.scad` fornito dall'utente | L'utente conosce OpenSCAD e ha già un modello di scatola |
| 2026-10-09 | Stampa su Bambu Lab A1 mini (180×180 mm) | Stampante dell'utente: limita il piatto di stampa |
| 2026-10-09 | Scheda: ESP32-S3 SuperMini (già acquistata) | Già in possesso dell'utente; BLE 5 per HID tastiera, USB-C nativo, molto piccola (~22,5×18 mm) |
| 2026-10-09 | Alimentazione a batteria 18650; la presa USB-C sul retro serve solo a ricaricarla | Scelta dell'utente: controller senza fili |
| 2026-10-09 | Firmware: primo caricamento via cavo, poi aggiornamenti OTA via WiFi | La porta USB della scheda resta chiusa nella scatola |
| 2026-10-09 | Scatola modulare: portaschede intercambiabile avvitato al fondo; il fondo ha un attacco fisso e generico | Se cambia l'elettronica si ristampa solo il portaschede; viti per evitare giochi |
| 2026-10-09 | Portaschede fissato al fondo con viti autofilettanti | Scelta dell'utente: semplicità, coerente con le viti del fondo |
| 2026-10-09 | Niente boost: uscita OUT del TP4056 direttamente sul pin 5V della SuperMini | L'LDO di bordo regge 3,4-4,2 V; il boost consumerebbe a vuoto e rischierebbe sovratensioni |
| 2026-10-09 | Eliminata la ricarica Qi | Si ricarica dalla USB-C del TP4056; fondo più semplice, niente disturbi all'antenna |
| 2026-10-09 | Un solo pulsante (PBS-110): pressione breve = play/pausa, pressione lunga 10 s = standby / risveglio; push dell'encoder non usato | Interfaccia minima, niente interruttore di accensione |
| 2026-10-09 | Foro per spillo sul fondo in corrispondenza del tasto RST della SuperMini | Reset senza aprire la scatola (la batteria resta sempre collegata) |
| 2026-10-09 | Portabatteria 18650 stampato nel portaschede | L'utente non ha un portabatteria; resta tutto nel modulo intercambiabile |
| 2026-10-09 | Stampa su più piatti (anche per colori diversi) | Il layout unico non entra nella A1 mini |
| 2026-10-09 | Presa USB-C di ricarica spostata sul retro a X=-12 | Batteria a destra per non toccare il pulsante; a +14 il TP4056 urtava la torretta d'angolo |
| 2026-10-09 | Niente scritte incise sulla scocca (engrave_text=false) | Decorazioni da valutare a progetto finito |
| 2026-10-09 | Repository pubblico su GitHub (PZero/YouTubeController), commit con email noreply; nessuna credenziale nel repo | Backup e pubblicazione della PWA con GitHub Pages; privacy dell'utente |
| 2026-10-09 | Hosting PWA: GitHub Pages | Gratuito, HTTPS, pubblica direttamente dal repository |
