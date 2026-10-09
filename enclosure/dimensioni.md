# Dimensioni condivise

Unica fonte di verità per le misure fisiche. La aggiorna `elettronica-firmware` quando sceglie un componente; la legge `design-3d` per il modello. Misure in millimetri.

| Elemento | Larghezza | Profondità | Altezza | Note (fori, connettori, albero) |
|----------|-----------|------------|---------|---------------------------------|
| Scheda (ESP32-S3 SuperMini) | 18,00 | 23,50 (PCB) + ~1,2-2,2 di USB-C sporgente | PCB ~1,0 (da misurare) + max 3,2 sopra (USB-C) = ~4,2-4,4 senza header; header maschi: +2,5 plastica +~6 pin sotto | Disegno quotato ufficiale Nologo. 2 file da 9 pin passo 2,54 sui lati lunghi, interasse file 15,24. USB-C centrata sul lato corto (lato pin 5V/TX); antenna ceramica sul lato corto opposto (tenere ≥5 mm da viti/metallo/encoder/bobina Qi). BOOT/RST sopra (dome 3x2x0,6). Lato inferiore senza componenti (solo pad + gambe THT della USB-C). Nessun foro di montaggio. Dettagli nella sezione sotto |
| Encoder (EC11E con switch, albero zigrinato) | 12,0 (corpo) | 11,6 (corpo); 14,2 con pin | corpo ~6,5 sopra PCB/fili + bussola 7 + albero 13 = albero lungo 20 dal piano di appoggio (variante 15 mm possibile: da misurare) | Bussola M7x0,75; albero Ø6 zigrinato 18 denti con taglio. Pin A-C-B passo 2,5 su un lato, switch 2 pin passo 5 sul lato opposto (a 14,5), linguette a 11,2 di interasse. Dettagli sotto |
| Pulsante (PBS-110 "7 mm") | Ø ~9,5 corpo | | ~27 totale (tasto + filetto + corpo + terminali), da misurare | Foro pannello 7,0 (7,2 stampato); filetto ~M7 o 1/4" (fonti divergenti); dado esagonale + rondella. Dettagli sotto |
| Caricatore TP4056 USB-C | ~17-17,5 | ~26-28 (PCB) + sporgenza USB-C ~0,5-1 | ~4,3-4,9 totale (USB-C la parte più alta) | 4 fori agli angoli (Ø e interasse da misurare); USB-C su un lato corto; pad B+/B-/OUT+/OUT- sul lato opposto. Dettagli sotto |
| Batteria 18650 | Ø18,5 (fino a ~19 con involucro) | 65,0 (non protetta; protette ~67-70) | | Più il portabatteria se usato (es. Keystone 1042: ~77 x 21 x 15 circa, da verificare) |
| Boost MT3608 | | | | non usato |

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
- Fissaggio possibile solo per bordi/contorno, pin header o pressione dall'alto: nessun foro. Lasciare libera la fascia dell'antenna (X > 20,5) da nervature massicce e da qualsiasi parte metallica.
- Prevedere sotto il PCB ~1 mm di gioco per le gambe dell'USB-C e i fili saldati ai pad BAT, se usati.
- Prevedere accesso a BOOT/RST (foro Ø ~2,5 sopra i pulsanti o coperchio apribile).
- Per la presa sul retro: il centro della USB-C sta a Z = spessore PCB + ~1,6 sopra la faccia inferiore del PCB.

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
| Scatti / impulsi | Alps: 30 scatti, 15 impulsi/giro; clone spesso 20/20 | Alps, annunci | **da verificare** a mano |

Confronto con `enclosure/youtube_control.scad` (da aggiornare a cura di `design-3d`):
- `shaft_d 6.15` + `shaft_flat 4.6` + grano M3: l'albero è zigrinato, non a D. Usare foro zigrinato 18 denti a pressione (vedi sotto) o foro tondo leggermente stretto; il grano M3 su zigrinatura tiene male.
- `enc_bush = 6`: probabilmente 7 (misurare). Con albero da 20: estremità a 20 - 3 (parete) = 17 sopra la faccia, non 16.
- `enc_shaft = 13`: coerente con albero da 20 e bussola da 7; se l'albero è da 15, diventa ~8 e la manopola va accorciata.
- `enc_hole = 7.3`: va bene per M7 (7,2-7,4 stampato).
- Parete 3 con incasso dado 1,2: restano ~1,8 di parete + dado 2 + rondella: compatibile con bussola da 5 o 7.
- Foro zigrinato in OpenSCAD per FDM: profilo a stella di 18 denti, Ø esterno 6,0-6,1, Ø di fondo ~5,3-5,4 (profondità dente ~0,35), ugello 0,4 stampa i denti male: soluzione pratica = foro tondo Ø 5,9-6,0 (pressione, la zigrinatura incide la plastica) oppure stella con gioco +0,1-0,15 e prova di stampa di un anello campione. Il taglio dell'albero permette di stringere le due metà: interferenza 0,1-0,2.

## Pulsante da pannello PBS-110 - quote meccaniche

Componente in possesso: momentaneo NA, bussola metallica filettata con dado esagonale e rondella, corpo cilindrico nero, tasto blu, 2 terminali a paletta con foro. Nessun disegno ufficiale: dati da annunci divergenti.

| Quota | Valore | Fonte | Affid. |
|-------|--------|-------|--------|
| Foro pannello | 7,0 (stampato: 7,2-7,3) | tutti gli annunci | B |
| Filettatura | ~M7 oppure 1/4" (6,35) | ifuturetech dice 1/4", altri 7 mm | **da misurare** |
| Diametro max (corpo/dado) | ~9,5 | ifuturetech | C |
| Lunghezza totale | ~27 (26 premuto: corsa ~1) | ifuturetech | C |
| Tasto | Ø 6-7, sporgenza sopra il dado ~4-6 | annunci divergenti | **da misurare** |
| Lunghezza filetto utile / spessore pannello max | non pubblicata, stimato 4-6 | nessuna fonte | **da misurare** |
| Dado | esagono ~9-10 sui piatti, spessore ~2 | stima | **da misurare** |
| Ingombro sotto il pannello | corpo Ø ~9,5 + terminali saldati con fili: ~15-20 | stima | **da misurare** |
| Corsa / forza | ~1 mm / non pubblicata | ifuturetech | C |
| Portata contatti / vita | 1 A 250 VAC (alcuni 3 A 12 VDC); vita non pubblicata, tipica ~10.000 cicli | annunci | C |

Impatto su `enclosure/youtube_control.scad` (da aggiornare a cura di `design-3d`):
- Il sistema switch 6x6 + tasto stampato con flangia + supporto con M2 (`btn_hole_d 16.5`, `cap_*`, `sw_*`, `br_*`, `screw_dx`, `boss_*`) non serve più.
- Nuovo montaggio: foro Ø 7,2 nella parete da 3 (spessore compatibile), dado all'interno; opzionale incasso esagonale dal lato interno o rondella antirotazione.
- Estetica: si può mantenere un cappuccio stampato (Ø ~16) che calza sul tasto blu a pressione; attenzione che il cappuccio non tocchi il dado/la parete nella corsa (~1 mm) e che resti guidato.
- Spazio interno: con piano a z0 = 43, tilt 10° e tasto a s = -33, la faccia interna sta a circa 34 mm dal fondo esterno, ~31 dal fondo interno: il pulsante (~15-20 sotto la parete) ci sta, ma va evitata la sovrapposizione con la 18650 (Ø 18,5) e con il portaschede in quella zona.

## Interfacce fisse scocca / fondo / portaschede

Quote nel sistema della scocca (`youtube_control.scad`): X larghezza (centro scocca = 0), Y lunghezza (+Y = retro, centro = 0), Z dalla faccia esterna del fondo. Cambiarle richiede di ristampare più pezzi: il portaschede si adatta a queste quote, non il contrario.

| Interfaccia | Valore | Pezzi coinvolti |
|-------------|--------|-----------------|
| Presa USB-C di ricarica sul retro | apertura 13 x 7 (r 3), centro X = **-12** (prima +14), Z = 14 | scocca, TP4056 sul portaschede |
| Viti fondo → scocca | 4x M3x8 svasate autofilettanti, centri (±26,68; ±44,18) | fondo, scocca |
| Viti fondo → portaschede | 4x M3x8 svasate autofilettanti dal basso, centri (-27; -35), (27; -35), (-12; 43), (12; 43); torrette Ø7 con foro pilota 2,6 | fondo, portaschede |
| Foro spillo RST | Ø1,8 con imbocco svasato Ø4, centro (-16,55; -9,4) | fondo, portaschede (tubetto guida), SuperMini |
| Foro spillo BOOT (facoltativo) | Ø1,8, centro (-7,55; -9,4) | come sopra |
| Spessore fondo / piastra portaschede | 3,0 / 2,8 (piastra da Z = 3 a 5,8) | fondo, portaschede |

Motivo dello spostamento della presa USB (da X = +14 a X = -12): il portabatteria 18650 occupa il lato +X per quasi tutta la lunghezza (unico spazio libero dal corpo del pulsante, che sta a X = -10 davanti); il TP4056 va quindi sul lato -X dietro la SuperMini. A X = 14 il modulo (17,3 di larghezza) avrebbe toccato la torretta angolare; a -12 restano 1,8 mm.
