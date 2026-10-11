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
| 2026-10-09 | Scartato il modulo di ricarica wireless "3IN1WPT_LICHARG" trovato dall'utente | Senza protezione evidente della cella, secondo caricatore da coordinare col TP4056, bobina vicina all'antenna: complessità non giustificata |
| 2026-10-09 | Chiave API YouTube inserita dall'utente nelle impostazioni della PWA (salvata solo sul dispositivo) | Repository pubblico: nessuna chiave nel codice né nel sito pubblicato |
| 2026-10-09 | Niente diodo su OUT+: la scheda va al PC solo per il primo flash, con la batteria scollegata; poi solo aggiornamenti OTA | Unica connessione USB prevista; evita la perdita di ~0,25 V di autonomia |
| 2026-10-11 | Nessuna strategia speciale per il focus nella PWA; codici dei tasti ancora da definire | Prova su iPad con tastiera BLE: tasti sempre ricevuti con ogni strategia; tocco su campo di testo offre la tastiera a schermo |
| 2026-10-11 | Avanzamento a velocità variabile: il firmware misura la velocità della manopola e invia un codice diverso per livello (lento/medio/veloce); la PWA assegna i secondi a ogni livello (regolabili) e invia un solo seekTo a fine rotazione | Misura precisa sulla scheda (il BLE raggruppa gli eventi); regolazione dei passi senza riflashare; niente buffering continuo |
| 2026-10-11 | Loop A-B comandato dal controller con pressione media del pulsante (0,7-2 s): 1ª = A, 2ª = B e avvio, 3ª = cancella | Distinta da pressione breve, lunga e gesto OTA; il doppio clic ritarderebbe ogni play/pausa |
| 2026-10-11 | I preferiti salvano anche i punti del loop A-B | Riprendere subito il passaggio da ripetere |
| 2026-10-11 | Player senza controlli YouTube (controls=0, fs=0); schermo pieno gestito dalla PWA sul contenitore del player | Lo schermo pieno nativo di iPadOS sottrae i tasti alla PWA |
| 2026-10-11 | Schermo pieno automatico al play e ridotto in pausa, più tasto nella PWA e tocco | Nessun gesto in più sul controller |
| 2026-10-11 | Codici tasti: ←/→ fine, Shift+←/→ medio, Alt+←/→ veloce, Spazio play/pausa, L loop A-B | Provabili subito con una tastiera BLE qualsiasi; ignorati mentre si scrive |
| 2026-10-11 | PWA in JavaScript semplice senza build, interfaccia minimale | Pubblicazione diretta su GitHub Pages, manutenzione semplice |
| 2026-10-11 | Schermo pieno su iPadOS solo via CSS (contenitore fisso a tutta finestra), niente Fullscreen API | Evita rifiuti da evento tastiera e perdita dei tasti; nell'app installata nella Home è a tutto schermo |
| 2026-10-11 | Loop A-B: riporta ad A solo se B viene superato partendo da dentro l'intervallo; un preferito con loop riparte da A | Un seek manuale fuori dal loop non viene "risucchiato" |
| 2026-10-11 | Icona generata da `app/icons/make_icons.py` (solo libreria standard Python) | Nessuna dipendenza da installare; SVG e PNG dalla stessa geometria |
| 2026-10-11 | OTA: si entra tenendo premuto il pulsante + 5 scatti di manopola | Gesto non confondibile con pressione breve, media e lunga |
| 2026-10-11 | Firmware compilato su GitHub Actions e pubblicato come Release | Build ripetibile, nessun ambiente di sviluppo locale necessario per gli aggiornamenti |
| 2026-10-11 | WiFi configurato dall'ESP32 con rete propria + pagina di configurazione al primo avvio; credenziali solo sulla scheda | Le Release sono pubbliche: nessuna password nel firmware |
| 2026-10-11 | R3 del TP4056 sostituita con 2,4 kΩ (carica a 0,5 A) | Meno calore in scatola chiusa; carica in ~5-6 h accettabile |
| 2026-10-11 | Azzeramento WiFi: pulsante premuto + 5 scatti all'indietro (anche "Dimentica WiFi" dalla pagina web dell'ESP32); la PWA ha una sezione "Controller" solo informativa | La PWA non può inviare comandi al controller (niente Web Bluetooth, la tastiera HID è solo in uscita) |
| 2026-10-11 | Riscontro dei gesti: servizio batteria BLE (livello nel widget iPadOS) + tasto innocuo intercettato dalla PWA (se iPadOS lo consegna) | Nessun costo hardware; risolve anche l'avviso di batteria scarica (LED interno non visibile) |
| 2026-10-11 | Standby con pressione di 10 s, risveglio con 2 s | Riaccendere deve essere rapido; lo standby resta difficile da attivare per errore |
| 2026-10-11 | Feedback: anello WS2812B 16 LED attorno alla manopola (sotto il coperchio, diffusore traslucido) + modulo vibrazione a moneta per i gesti | Componenti già in possesso dell'utente; luce dove si guarda, vibrazione senza guardare |
| 2026-10-11 | Alimentazione dell'anello interrotta da P-MOSFET comandato da GPIO; luminosità limitata a ~10-15% | 16 LED spenti assorbono 10-16 mA: scaricherebbero la batteria in standby |
