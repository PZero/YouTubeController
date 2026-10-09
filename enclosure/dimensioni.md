# Dimensioni condivise

Unica fonte di verità per le misure fisiche. La aggiorna `elettronica-firmware` quando sceglie un componente; la legge `design-3d` per il modello. Misure in millimetri.

| Elemento | Larghezza | Profondità | Altezza | Note (fori, connettori, albero) |
|----------|-----------|------------|---------|---------------------------------|
| Scheda (ESP32-S3 SuperMini) | 18,00 | 23,50 (PCB) + ~1,2-2,2 di USB-C sporgente | PCB ~1,0 (da misurare) + max 3,2 sopra (USB-C) = ~4,2-4,4 senza header; header maschi: +2,5 plastica +~6 pin sotto | Disegno quotato ufficiale Nologo. 2 file da 9 pin passo 2,54 sui lati lunghi, interasse file 15,24. USB-C centrata sul lato corto (lato pin 5V/TX); antenna ceramica sul lato corto opposto (tenere ≥5 mm da viti/metallo/encoder/bobina Qi). BOOT/RST sopra (dome 3x2x0,6). Lato inferiore senza componenti (solo pad + gambe THT della USB-C). Nessun foro di montaggio. Dettagli nella sezione sotto |
| Encoder | da definire | | | |
| Pulsante | da definire | | | |
| Batteria | da definire | | | |

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
