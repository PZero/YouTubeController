# Dimensioni condivise

Unica fonte di verità per le misure fisiche. La aggiorna `elettronica-firmware` quando sceglie un componente; la legge `design-3d` per il modello. Misure in millimetri.

| Elemento | Larghezza | Profondità | Altezza | Note (fori, connettori, albero) |
|----------|-----------|------------|---------|---------------------------------|
| Scheda (ESP32-S3 SuperMini) | 18,00 (misurato dall'utente 2026-10-11, A) | 23,50 (PCB) + ~1,2-2,2 di USB-C sporgente; **27,0 totale con la USB-C misurato dall'utente (2026-10-11, A)** → la USB-C sporge ~3,5 se il PCB è 23,5 (lunghezza del solo PCB da misurare) | PCB ~1,0 (da misurare) + max 3,2 sopra (USB-C) = ~4,2-4,4 senza header (**5,0 misurato dall'utente in corrispondenza della USB-C, A**); header maschi: +2,5 plastica +~6 pin sotto | Disegno quotato ufficiale Nologo. 2 file da 9 pin passo 2,54 sui lati lunghi, interasse file 15,24. USB-C centrata sul lato corto (lato pin 5V/TX); antenna ceramica sul lato corto opposto (tenere ≥5 mm da viti/metallo/encoder/bobina Qi). BOOT/RST sopra (dome 3x2x0,6). Lato inferiore senza componenti (solo pad + gambe THT della USB-C). Nessun foro di montaggio. Dettagli nella sezione sotto **Dal 2026-10-15 è saldata sulla millefori unica** (strip maschio 2 x 1x9, plastica 2,5 lasciata come distanziale): altezza **6,7 sopra la millefori** (2,5 + PCB 1,0 + USB-C 3,2), componenti in alto, USB-C verso il fronte della scocca, sporgenza **3,5** (27,0 totali). Niente più sede capovolta sul portaschede |
| Encoder (EC11E con switch, albero zigrinato) — **dal 2026-10-14 il suo pulsante integrato fa play/pausa e tutti i gesti** | 12,0 (corpo) | 11,6 (corpo); 14,2 con pin | corpo ~6,5 sopra PCB/fili + bussola 7 + albero 13 = albero lungo 20 dal piano di appoggio (variante 15 mm possibile: da misurare) | Bussola M7x0,75; albero Ø6 zigrinato 18 denti con taglio. Pin A-C-B passo 2,5 su un lato, switch 2 pin passo 5 sul lato opposto (a 14,5), linguette a 11,2 di interasse. Dettagli sotto |
| ~~Pulsante (PBS-110 "7 mm")~~ **ELIMINATO il 2026-10-14** | | | | Decisione dell'utente: play/pausa e gesti con il pulsante integrato dell'encoder (switch a 2 pin sul lato opposto ai pin A-C-B). Foro, lamatura, dado, cappuccio e spazio riservato rimossi dal modello. Dati storici nella sezione sotto |
| Caricatore TP4056 USB-C | ~17-17,5 | ~26-28 (PCB) + sporgenza USB-C ~0,5-1 | ~4,3-4,9 totale (USB-C la parte più alta) | 4 fori agli angoli (Ø e interasse da misurare); USB-C su un lato corto; pad B+/B-/OUT+/OUT- sul lato opposto. Dettagli sotto |
| Batteria 18650 (Jesspow, non protetta) | Ø18,5 (misurato dall'utente 2026-10-11, A) | 65,0 (misurato dall'utente 2026-10-11, A) | | Più il portabatteria se usato (es. Keystone 1042: ~77 x 21 x 15 circa, da verificare) |
| Boost MT3608 | | | | non usato |
| Anello LED WS2812B 16 LED | Ø est. 45,0 | Ø int. 33,0 | 3,0 (PCB + LED) | Misure dell'utente col calibro (2026-10-11), affidabilità A. LED 5050 su una faccia. Retro piatto con 6 piazzole in un arco (~60°, sul raggio medio ~19,5): − / DO / +5V (uscita) e − / DI / + (ingresso, da usare; filo rosso già saldato su +). Saldature sporgono ~1 mm sul retro: prevedere spazio e uscita dei 3 fili (foto utente 2026-10-11, affidabilità B). Va sotto il coperchio, centrato sull'encoder (manopola Ø32 → LED appena fuori dal bordo) |
| Modulo vibrazione (motore a moneta ~Ø10, prob. 1027) — **dal 2026-10-14 sotto la faccia superiore della scocca, non più sul portaschede** | 21,0 (lato con i pin) | 23,0 | 5,0 nel punto più spesso (PCB + motore, senza pin) | Misure dell'utente col calibro 2026-10-11, affidabilità A. **Spessore del solo PCB da misurare** (modello 1,6; serve alla sede a incastro). Pin GND/VCC/IN passo 2,54 sul lato da 21 (da dissaldare e sostituire con fili); 2 fori di fissaggio sul lato dei pin (Ø e interasse non misurati: fissaggio a incastro, fori non necessari). Transistor, diodo e resistenze a bordo; IN alto = vibra; ~70-90 mA. Dalla foto dell'utente, affidabilità C |
| Pacco elettronico V1: millefori unica 8 x 20 + SuperMini saldata sopra, in guaina/kapton, **NON fissato** (portaschede) | **22,54** (3,49 + 7 x 2,54 + 1,27: lato sinistro intatto, destro tagliato a metà passo); con guaina ~22,8 | **60** (20 righe); con guaina ~60,2 | PCB 1,6 + **max 11,5 sopra** (elettrolitici 5 x 11; resistenze e diodo in piedi ~10; TO-92 ~8; SuperMini 6,7) + **max 1,8 sotto** (saldature e fili): **~15 dalla piastra** | Disposizione in `firmware/millefori/` (README, SVG, `millefori.py`); affidabilità B/C. Decisione 2026-10-15 (V1, PCB JLCPCB rimandato): elettronica semplificata "come nei test" e **pacco libero nella corsia sinistra** del portaschede (nessuna vite, niente fermi). Corsia: X da -23 (faccia del condotto del pannello sinistro) a +0,7 (parete della culla) = **23,7**, Y da -42,0 a +20,0 = **62,0** (3 nervature basse alte 5, spessore 0,8: 1 davanti X -20…-3, 2 dietro X -20…-14 e -8…-2). Gioco totale **0,9 in larghezza** (0,45 per lato: condotto e culla sono fissi) e **1,8 in lunghezza** (0,9 per lato): davanti la torretta angolare della scocca (r 4,2 a X -26,68, Y -44,18) entra fino a X -22,5, quindi il pacco non può andare più avanti di Y -42,2; dietro c'è il TP4056 (bordo a Y 20,4). **Vincolo dei bracci dei pannelli**: i denti dei bracci entrano fino a X = ±21,25 (con 0,4 di gioco 20,85) tra Z 14,6 e 21,8, Y da -26,0 a -23,1: il pacco deve avere i primi ~2 mm dal bordo sinistro bassi (solo PCB e saldature, max 8,8 dalla piastra). Nella millefori è così: la colonna A parte a 3,49 e i corpi a x ≥ 2,1 (R, C2); NON mettere componenti alti entro 2 mm dal bordo sinistro e non girare la scheda di 180° |
| Transistor S8550 / 2N3904 (TO-92) | ~4,6 (4,4-5,2) | ~3,6 (3,4-4,0) | corpo ~4,6 + piedini (accorciati a ~3-5 su millefori) | Package TO-92 standard, affidabilità B. Sostituiscono i MOSFET SOT-23 (vincolo costi 2026-10-11) |
| Condensatore 47-100 µF 16 V elettrolitico | Ø5 (o Ø6,3) | | 11 (o 7) + piedini | Affidabilità B (taglie standard); sulla millefori, in piedi (11,5 sopra la faccia componenti), a >= 10 dall'antenna |
| Connettore scocca → portaschede: **codino di 9 fili saldato sulla millefori + connettore volante Dupont 2 x 5 con chiave** (femmina sul codino, maschio sul cablaggio della scocca) | 12,7 (5 contatti) | 5,1 (2 file) | ~25 la coppia innestata in piedi, + ~5 di curvatura dei fili | Sostituisce il pin header 2x4 sulla schedina (decisione 2026-10-15, `firmware/millefori/README.md`: un header 2x5 diritto con la spina arriva a ~20 mm, oltre i 16 disponibili; angolato sporgerebbe ~20 mm). Pin: encoder A, B, switch, GND encoder, (chiave), vibrazione IN, anello +, DI, vibrazione VCC, GND anello+vibrazione. Posto a coperchio chiuso: **tasca "parcheggio"** sul portaschede (vedi interfacce). Affidabilità B (dimensioni standard Dupont; altezza della coppia da misurare) |

## ESP32-S3 SuperMini - quote meccaniche

Sistema di riferimento (vista dall'alto, lato componenti): origine nell'angolo del PCB sul **lato USB-C** e sulla fila **5V/GND/3V3**; X lungo i 23,5 mm (dall'USB-C verso l'antenna), Y lungo i 18 mm (dalla fila 5V verso la fila TX/RX), Z dalla faccia superiore del PCB.

Affidabilità: **A** = disegno quotato/schema ufficiale Nologo; **B** = footprint KiCad di terzi o datasheet del componente; **C** = stima da render (scala ~30,7 px/mm, ±0,3 mm) o valore tipico. Tutto ciò che è B/C va confermato col calibro prima di stampare gli incastri.

| Quota | Valore | Fonte | Affid. |
|-------|--------|-------|--------|
| Lunghezza PCB (X) | 23,50 | disegno Nologo | A |
| Larghezza PCB (Y) | 18,00 | disegno Nologo | A |
| Raggio angoli PCB | ~1,0 | footprint KiCad 9veedz | B |
| Spessore PCB | non pubblicato; tipico 1,0 (possibili 1,2/1,6) | nessuna | **da misurare** |
| Passo pin | 2,54 | disegno Nologo | A |
| Pin per fila | 9 (2 file) | disegno + schema Nologo (H1/H2 "Header 9") | A |
| Distanza primo/ultimo pin di fila | 20,32 (= 8 x 2,54) | disegno Nologo | A |
| Primo pin dal bordo corto (X) | 1,59 da entrambi i lati ((23,5-20,32)/2) | derivato dal disegno | A |
| Interasse tra le due file (Y) | 15,24 | footprint KiCad (fori a ±7,62) | B |
| Fila pin dal bordo lungo | 1,38 (fori header); pad semi-forati (castellated) sul bordo | footprint KiCad; render ~1,2 | B |
| Foro pin | Ø1,0, pad ovale 1,5 x ~3,0 | footprint KiCad | B |
| Ordine fila Y=1,38 (da X=1,59) | 5V, GND, 3V3, 13, 12, 11, 10, 9, 8 | disegno Nologo | A |
| Ordine fila Y=16,62 (da X=1,59) | TX, RX, 1, 2, 3, 4, 5, 6, 7 | disegno Nologo | A |
| USB-C: tipo | SMD Type-C 16P (tipo HRO TYPE-C-31-M-12), gambe schermo passanti | schema Nologo; datasheet tipico | A/B |
| USB-C: larghezza corpo | 8,94 (8,79-9,09) | datasheet TYPE-C-31-M-12 (LCSC/qeda); footprint 8,94 | B |
| USB-C: lunghezza corpo | 7,30-7,35 | datasheet LCSC | B |
| USB-C: altezza sopra PCB | 3,16-3,21 | datasheet (qeda 3,21) | B |
| USB-C: centro in Y | 9,0 (centrata) | render Nologo (~9,1) + footprint | B |
| USB-C: sporgenza oltre il bordo PCB | **1,2** (footprint) vs **~2,2** (render Nologo) | fonti divergenti | **da misurare** |
| USB-C: gambe schermo sotto il PCB | ~0,5-1,0 dopo saldatura | stima | C |
| Pulsante RESET | dome 3 x 2 x 0,6; X ≈ 7,6-9,6, Y ≈ 2,3-6,6 (vicino alla fila 5V) | schema Nologo (dimensioni) + render (posizione) | A dim. / C pos. |
| Pulsante BOOT | dome 3 x 2 x 0,6; X ≈ 7,6-9,6, Y ≈ 11,3-15,7 (vicino alla fila TX) | come sopra | A dim. / C pos. |
| LED RGB WS2812 (GPIO48) | ~2,0 x 2,0, h ~0,8-0,9 (WS2812 "0807"/2020); X ≈ 16,8-18,9, Y ≈ 2,4-4,4 | schema Nologo (tipo); render (posizione) | B dim. / C pos. |
| LED rosso (GPIO48) e blu (carica) | 0402, h ~0,4; posizione non quotata | schema Nologo | A tipo / C pos. |
| Chip ESP32-S3FH4R2 | QFN56 7 x 7, h ~0,85-0,9, ruotato 45°; centro X ≈ 15,3, Y ≈ 9,0 | distributori (7x7 VFQFN); render | B / C |
| Regolatore ME6217C33M5G, caricatore TP4054 | SOT23-5, h max ~1,45 | schema Nologo; datasheet SOT23-5 tipico | A tipo / B h |
| Antenna ceramica | ~2 x 7 vista dall'alto, h ~1; X ≈ 21,2-23,4, Y ≈ 7,9-14,9 (al bordo opposto all'USB) | render Nologo | C |
| Zona antenna senza rame | ultimi ~3 mm in X (X ≈ 20,5-23,5) | render Nologo | C |
| Altezza max componenti lato superiore | 3,2 (USB-C); resto ≤ ~1,5 | datasheet USB-C + SOT23 | B |
| Componenti lato inferiore | nessuno (montaggio SMD su un solo lato); solo pad GPIO14-48 (passo ~1,8), pad BAT+ / BAT- (vicino al lato USB, X ≈ 2), gambe passanti USB-C | wiki Nologo ("单面表面贴装"); schema; footprint KiCad | A/B |
| Fori di montaggio | nessuno | disegno Nologo | A |

Note per gli incastri:
- **V1 (2026-10-15): la SuperMini è saldata sulla millefori (strip maschio) e il pacco è libero nella corsia, isolato con guaina/kapton**: nessun incastro, nessuna sede sul portaschede. Resta valido: fascia dell'antenna (ultimi ~3 mm in X; sulla millefori x 4,8-17,8, y 24,2-32,5) senza piazzole, nervature e metallo; la cella sta a >= 5 dalla zona antenna (se il pacco sta in corsia a destra: 5,0; a sinistra: più di 10).
- (storico) gioco sotto il PCB per le gambe dell'USB-C: ora la scheda sta sulla strip, a 2,5 dalla millefori.
- BOOT/RST: nessun foro (2026-10-15). I tasti sono in alto, a ~14,5 dal piano; si premono a scheda aperta (fondo e portaschede estratti).
- (storico) finestra USB-C sul fronte: rimossa, vedi "Fronte della scocca".

Fonti:
- Wiki Nologo (disegno quotato `dimension.jpg`, schema `1.png`, data 10/08/2024): https://wiki.nologo.tech/product/esp32/esp32s3/esp32s3supermini/esp32S3SuperMini.html
- Footprint KiCad di terzi: https://github.com/9veedz/esp32s3supermini
- USB-C TYPE-C-31-M-12: https://lcsc.com/product-detail/C165948.html, https://git.cuvoodoo.info/kingkevin/qeda_library/src/branch/master/connector/usb-c_hro_type-c-31-m-12.yaml

## Caricatore TP4056 USB-C con protezione - quote meccaniche

Componente in possesso (serigrafia "4056", variante a 4 fori, lato opposto all'USB con due scassi semicircolari agli angoli e una "M"). Non esiste un disegno quotato ufficiale: i venditori danno misure diverse (26x17, 28x17,3, 29x17,3). Riferimento: X lungo il lato lungo (dall'USB-C verso i pad), Y lungo il lato corto, Z dalla faccia superiore del PCB. Affidabilità come sopra (A/B/C).

| Quota | Valore | Fonte | Affid. |
|-------|--------|-------|--------|
| Lunghezza PCB (X) | 26-28 (più citato 28) | open-electronics 28x17,3x4,9; ifuturetech 26x17 | **da misurare** |
| Larghezza PCB (Y) | 17-17,3 | come sopra | C |
| Spessore PCB | 1,0-1,6 (tipico 1,2) | nessuna fonte | **da misurare** |
| Altezza totale | 4,3-4,9 | annunci (29x17,3x4,3; 28x17,3x4,9) | C |
| Componente più alto | USB-C, ~3,2-3,5 sopra il PCB | tipico USB-C SMD | C |
| Sporgenza USB-C oltre il bordo | ~0,5-1,0 | stima | **da misurare** |
| Larghezza corpo USB-C | ~8,9 | tipico (come SuperMini) | B |
| Fori di montaggio | 4 agli angoli, Ø presumibile 1,5-2,0, interasse non pubblicato | nessuna fonte | **da misurare** (Ø, interasse X e Y, distanza dai bordi) |
| Scassi semicircolari lato pad | 2 agli angoli: verificare se sono fori aperti utilizzabili come appoggio o solo intagli | foto utente | **da misurare** |
| LED (rosso carica / blu o verde carico) | SMD 0603/0805, h ~0,6-0,8; posizione da rilevare sul pezzo | nessuna fonte | **da misurare** |
| Pad B+/B-/OUT+/OUT- | sul lato corto opposto all'USB; fili già saldati su B+/B- | foto utente | A (presenza) |
| Lato inferiore | in genere senza componenti, piazzole IN+/IN- e pad | annunci | C |
| Dissipazione | in carica a 1 A il TP4056 scalda (fino a ~1,3 W); limitazione termica a 120 °C | datasheet TP4056 | B |

Note per gli incastri:
- Accesso frontale alla USB-C del modulo (è la presa di ricarica del prodotto): la sua posizione nella scatola va decisa con `design-3d` insieme a quella della SuperMini (che serve solo per il flash).
- Lasciare visibili i 2 LED (finestrella o materiale traslucido sottile) e un po' d'aria attorno al TP4056 durante la carica.
- Fori probabilmente Ø ~1,5-2: viti autofilettanti M1,6-M2 o perni stampati con ritegno; verificare col calibro.
- Le sporgenze dei fili su B+/B-/OUT+/OUT- richiedono ~3-5 mm liberi oltre il bordo pad.

## Encoder EC11E con pulsante - quote meccaniche

Componente in possesso: clone tipo Alps EC11E vertical con switch, corpo metallico ~12 mm su base verde, albero zigrinato. Riferimento: footprint KiCad `RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm` (origine nel pin A; albero in X=7,5, Y=2,5).

| Quota | Valore | Fonte | Affid. |
|-------|--------|-------|--------|
| Corpo vista dall'alto | 12,0 x 11,6 | footprint KiCad (F.Fab 1,5-13,5 x -3,3-8,3) | B |
| Altezza corpo (PCB → piano di appoggio/base bussola) | ~6,5 | tipico EC11E con switch | **da misurare** |
| Bussola | M7x0,75, lunghezza ~7 (5 su alcune varianti) | Alps/Mouser (Bourns PEC11R analogo: LB 7 per albero 20) | B, lunghezza **da misurare** |
| Albero: lunghezza dal piano di appoggio | 20 (quindi ~13 sopra la bussola) oppure 15 | annunci clone "20 mm, parte rotante 12-13 mm" | **da misurare** |
| Albero: diametro / tipo | Ø6,0 zigrinato, 18 denti, con taglio longitudinale | Bourns PEC11R (18 TEETH), clone tipici | B (contare i denti) |
| Zigrinatura: lunghezza | ~7-10 dalla punta | stima | **da misurare** |
| Taglio (slot) | larghezza ~1,0, profondità ~5-8 | stima | **da misurare** |
| Pin A, C, B | in linea, passo 2,5 (A a 0, C a 2,5, B a 5), Ø foro 1,0 | footprint KiCad | B |
| Pin switch S1/S2 | lato opposto, a 14,5 dai pin A-C-B, passo 5,0 | footprint KiCad | B |
| Linguette di fissaggio | a X=7,5, interasse 11,2 (Y=-3,1 e 8,1), foro asolato 2,8 x 1,5 | footprint KiCad | B |
| Ingombro totale con pin (vista dall'alto) | ~17,5 x 14,2 | footprint (courtyard) | B |
| Dado M7x0,75 | esagono ~9-10 sui piatti, spessore ~2; rondella Ø ~10-12 x 0,5 | tipico | **da misurare** |
| Spessore pannello max | lunghezza bussola - dado - rondella ≈ 7 - 2,5 = ~4,5 | derivato | C |
| Pulsante integrato | corsa 0,5 ±0,3, forza ~6 N (Alps EC11E15244G1) | Alps | B (clone diverso) |
| Scatti / impulsi | **20 scatti/giro** (misurato dall'utente a mano, 2026-10-14); 60 zigrinature della manopola = 3 per scatto | utente | A |
| Spinta assiale del pulsante | ~6 N a ogni pressione, corsa 0,5 ±0,3; la manopola poggia sulla punta dell'albero (fondo del foro = punta) e a fine corsa (0,8) restano 0,5 tra dado+rondella e manopola | Alps, modello | verifica del 2026-10-14 sotto |

### Verifica della spinta assiale (2026-10-14)
- Percorso del carico: dito → manopola → punta albero → switch nel corpo; la reazione passa dalla bussola al dado M7 e da lì sulla faccia (3,0 di PLA) con la rondella: pressione ≈ 6 N / ~50 mm² ≈ 0,1 MPa, trascurabile. Dado + rondella 2,5 + parete 3,0 = 5,5 su 7,0 di bussola: filetto sufficiente. **Non stringere a fondo** (il PLA sotto il dado cede nel tempo): bastano pochi decimi di giro oltre il contatto.
- Il disco centrale (r < 16,65) che porta l'encoder è collegato alla faccia solo da 4 ponti (diffusore "insert"): larghezza 3,0 (era 2,0) x spessore 2,0, lunghezza 5,7. Stima con 6 N al centro: ~2 MPa; spinta sul bordo della manopola (r 16, leva): ~6 MPa; flessione < 0,01 mm. Resistenza del PLA nel piano degli strati ~40-50 MPa. Margine buono, ma da provare a mano sulla scocca stampata.
- Foro di battuta: `bore_slack = 0` (la punta tocca il fondo del foro: la spinta non passa per l'attrito dello zigrino); se l'albero è più corto, la manopola scende da sola alla prima pressione.
- Cava per dado nella manopola: era 1,2, ora 2,0 (`nut_recess_h` derivato da dado 2,0 + rondella 0,5 + corsa 0,8): prima dado e manopola si toccavano a fine corsa. Sotto la manopola restano 1,0 sopra la faccia/diffusore a fine corsa.

Confronto con `enclosure/youtube_control.scad` (da aggiornare a cura di `design-3d`):
- `shaft_d 6.15` + `shaft_flat 4.6` + grano M3: l'albero è zigrinato, non a D. Usare foro zigrinato 18 denti a pressione (vedi sotto) o foro tondo leggermente stretto; il grano M3 su zigrinatura tiene male.
- `enc_bush = 6`: probabilmente 7 (misurare). Con albero da 20: estremità a 20 - 3 (parete) = 17 sopra la faccia, non 16.
- `enc_shaft = 13`: coerente con albero da 20 e bussola da 7; se l'albero è da 15, diventa ~8 e la manopola va accorciata.
- `enc_hole = 7.3`: va bene per M7 (7,2-7,4 stampato).
- Parete 3 con incasso dado 1,2: restano ~1,8 di parete + dado 2 + rondella: compatibile con bussola da 5 o 7.
- Foro zigrinato in OpenSCAD per FDM: profilo a stella di 18 denti, Ø esterno 6,0-6,1, Ø di fondo ~5,3-5,4 (profondità dente ~0,35), ugello 0,4 stampa i denti male: soluzione pratica = foro tondo Ø 5,9-6,0 (pressione, la zigrinatura incide la plastica) oppure stella con gioco +0,1-0,15 e prova di stampa di un anello campione. Il taglio dell'albero permette di stringere le due metà: interferenza 0,1-0,2.

## Pulsante da pannello PBS-110 - ELIMINATO (2026-10-14)

Decisione dell'utente: il pulsante da pannello non si usa più; play/pausa e tutti i gesti passano dal pulsante integrato dell'encoder EC11E. Motivo: un solo organo di comando in mano, meno fori e componenti. Rimosso dal modello (foro Ø7,2, lamatura per dado, anello inciso, cappuccio, ingombro interno di 20 mm) e dal pacchetto di stampa. I dati raccolti (foro 7,0, M7 o 1/4", corpo Ø9,5, ~27 di lunghezza) restano nella cronologia git del file. Lo spazio liberato (davanti all'anello LED) ospita ora il modulo vibrazione.

## Interfacce fisse scocca / fondo / portaschede

Quote nel sistema della scocca (`youtube_control.scad`): X larghezza (centro scocca = 0), Y lunghezza (+Y = retro, centro = 0), Z dalla faccia esterna del fondo. Cambiarle richiede di ristampare più pezzi: il portaschede si adatta a queste quote, non il contrario.

| Interfaccia | Valore | Pezzi coinvolti |
|-------------|--------|-----------------|
| Presa USB-C di ricarica sul retro | apertura 13 x 7 (r 3), centro X = **-12** (prima +14), Z = 14 | scocca, TP4056 sul portaschede |
| Viti fondo → scocca | 4x M3x8 svasate autofilettanti, centri (±26,68; ±44,18) | fondo, scocca |
| Viti fondo → portaschede | 4x M3x8 svasate autofilettanti dal basso, centri (-27; -35), (27; -35), (-12; 43), (12; 43); torrette Ø7 con foro pilota 2,6 | fondo, portaschede |
| ~~Foro spillo RST~~ **RIMOSSO 2026-10-15** | | RST/BOOT sono sul lato superiore della SuperMini (dall'esterno non si raggiungono): si accede a scatola aperta. Il fondo è senza fori e senza scritte |
| ~~Foro spillo BOOT~~ **RIMOSSO 2026-10-15** | | come sopra |
| Spessore fondo / piastra portaschede | 3,0 / 2,8 (piastra da Z = 3 a 5,8) | fondo, portaschede |
| Anello LED sotto la faccia superiore (eccezione alla regola modulare) | coassiale all'encoder (piano superiore x = 0, s = 14); PCB parallelo alla faccia, faccia inferiore a 7,0 dalla faccia superiore (centro: Y ≈ 15,0, Z ≈ 38,5); 4 ganci a scatto + 4 battute | scocca, anello |
| Corona diffusore nella faccia superiore | r 16,6-22,4 attorno all'asse encoder | scocca, diffusore |
| Connettore scocca → portaschede | codino di fili dal pacco (bordo posteriore, Y 19) → **connettore volante Dupont 2 x 5** parcheggiato in una **tasca a U** dietro la culla (tenuta: sta in una zona libera, non ingombra; con la V1 semplificata i fili possono anche andare diretti): interno X 7,0…20,3 (13,1), Y 33,0…38,3 (5,3), pareti 1,2 alte 8,5 (spina in piedi, ~25 + curvatura dei fili); tacca bassa 8 x 3,5 sulla parete sinistra per il mazzo del codino. Percorso del codino: bordo posteriore del pacco (Y 19) → canale tra TP4056 (bordo X -3,35) e culla (X 0,7) → dietro la testata della culla (Y 29,4-33) → tasca; ~70 mm. La coppia sta a 0,55 dai bracci a scatto del pannello destro (X 20,85) | pacco, scocca |
| Modulo vibrazione | sotto la faccia superiore, davanti all'anello: PCB (21 x 23) con il retro piatto contro la faccia interna, x ±10,5, s da -35,4 a -12,4 (piano), motore verso l'interno (max 5 sotto la faccia); lato pin verso l'encoder | scocca (sede `vt_*`) |
| Corsia del pacco elettronico (libera, senza fissaggi) | piana (piastra a z 5,8), X -23…0,7, Y -42,0…20,0; 3 nervature di contenimento alte 5 (vedi riga componenti). Il pacco (~22,8 x 60,2 x 15) si muove di 0,45 in X e 0,9 in Y: verificato agli estremi (controlli 13 e 24). Rimossi: torrette M3, fermi a C, battute, fori pilota | portaschede |
| Fronte della scocca | **liscio** (finestra USB-C della SuperMini rimossa il 2026-10-15): la scheda libera non ha una presa a posizione definita; firmware via OTA o a scatola aperta | scocca |
| Presa USB-C di ricarica (TP4056), controllo del 2026-10-15 | centro presa Z = 14,0 (PCB 11,2 + 1,2 + 1,6) = centro foro usb_z; faccia della presa a Y 49,2 (0,3 dalla parete interna), X = -12 = centro foro; foro 13 x 7 r 3: una spina 12 x 6,5 con angoli r 2,5 passa senza toccare (controllo 22) | scocca, TP4056 |

### Anello LED, diffusore, vibrazione, schedina - quote derivate (design-3d, 2026-10-11)

Coordinate: "piano" = sistema del piano superiore inclinato (x larghezza, s lungo la pendenza, n normale; n = 0 faccia superiore, n < 0 verso l'interno); "scocca" = X, Y, Z come sopra. Parametri in `youtube_control.scad` (`lr_*`, `diff_*`) e `portaschede.scad` (`vib_*`, `mf_*`).

| Quota | Valore | Note |
|-------|--------|------|
| Centro anello | piano (0; 14) = asse encoder | manopola Ø32 copre fino a r 16; LED (r ~17-22) appena fuori |
| Aria cima LED → faccia interna | 1,0 (`lr_air`) | faccia inferiore PCB a n = -7,0 |
| Distanza LED → diffusore | 3,0 (inserto: ponti 2,0 + aria 1,0); 1,0 in multi-materiale (diffusore pieno da 3) | passo LED ~7,7: la distanza attenua i punti luce, non li elimina |
| Spessore PCB anello | **da misurare** (modello 1,6) | serve solo alla quota delle battute (`lr_pcb_t`) |
| Ganci anello | 4, a 45° dall'arco piazzole e poi ogni 90°; braccio 3 x 0,8 radicato in una tasca profonda fino a 2 dalla faccia superiore (lunghezza libera ~5,1); dente 0,3 sotto il bordo del PCB | gioco radiale 0,25; deformazione ~1,4 % (PLA) |
| Battute anello | 4, alternate ai ganci; appoggio 0,4 sul bordo esterno (r 22,1-22,5) | i LED arrivano a r ~22 se centrati su 19,5 (affid. B) |
| Arco piazzole | centrato a 30° (verso destra-retro, `lr_pad_ang`) | i fili scendono sopra la cella, lontano dall'encoder |
| Diffusore "insert" | anello r 16,65-22,35, spessore 1,0, sottosquadro 0,15 sul bordo esterno (entra a scatto dall'alto); gioco 0,05 per lato | sotto: 4 ponti larghi 2,0 allineati ai ganci reggono il disco centrale dell'encoder |
| Diffusore "mmu" | corona piena r 16,6-22,4 per tutto lo spessore (3,0), senza ponti | stampato con la scocca (AMS lite), stessa trasformazione |
| Modulo vibrazione (sede sulla scocca, `vt_*`) | PCB a contatto con la faccia interna (z = -3,0 … -4,6), pinzato da 4 labbri (6 x 1,0, copertura bordo 1,0) con nervature di pinzatura 0,15 (PLA) e tenuto in avanti da 2 ganci a scatto sul piano (braccio 0,8 x 8,0, dente 0,6); pareti 1,2, battuta lato encoder con tacca fili 8 mm; gioco 0,2; battuta a s = -11,0 (anello e ganci a s > -9,7) | si infila dal davanti a scocca capovolta; richiede lo spessore PCB (modello 1,6, **da misurare**; se più sottile: biadesivo sottile o goccia di colla). Sostituisce la sede sul portaschede (scartata: vibrazione smorzata). |
| Variante vibrazione sul portaschede | **rimossa dal modello il 2026-10-15** (codice `vib_*`, `vib_on`, sede in piedi): scartata il 2026-10-14, dalla scocca la vibrazione si sente di più | |
| ~~Schedina millefori in piedi~~ | **sostituita** il 2026-10-15 dalla millefori unica piatta (riga sopra): guide, testata JST e vincoli "componenti verso il davanti max 6,5" non esistono più | |
| Vincolo cella | la culla (X 0,7…22,5; Y -47…29,4) non si sposta. Con 18650 protetta (67-70) la culla si allunga di 2-5 mm verso il retro (Y 29,4 → 34,4): la tasca del connettore (Y 31,8…39,5) va spostata di ~5 mm | |
| Fascetta della cella | **una sola**, a Y = 21,6 (dietro la corsia del pacco; la parete sinistra della culla è occupata dal pacco fino a Y 19,1): le due di prima (Y -24 e +6,5) passavano dove sta il pacco; la cella è tenuta anche dai contatti a molla | portaschede |
| Bracci a scatto pannelli laterali | arrivano a X = ±21,25 (Y ≈ -24,7 e 32,7, Z 15-26): la culla 18650 li toccava (~1,6 mm³), ora c'è una tacca di 0,4 | difetto preesistente corretto |

Motivo dello spostamento della presa USB (da X = +14 a X = -12): il portabatteria 18650 occupa il lato +X per quasi tutta la lunghezza (il lato -X era libero perché il pulsante PBS-110, ora eliminato, stava davanti); il TP4056 va quindi sul lato -X dietro la SuperMini. A X = 14 il modulo (17,3 di larghezza) avrebbe toccato la torretta angolare; a -12 restano 1,8 mm.
