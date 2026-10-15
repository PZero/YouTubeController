# Scatola 3D

Modello parametrico della scatola (OpenSCAD 2021.01). Le misure dei componenti stanno in `dimensioni.md` (unica fonte di verità, comprese le interfacce fisse fondo/portaschede/presa USB).

## File
- `youtube_control.scad`: file principale (scocca con sede del modulo vibrazione, fondo, pannelli, manopola, anello decorativo, anelli di prova, piatti, assembly). Si apre e si esporta solo questo.
- `portaschede.scad`: portaschede intercambiabile (corsia libera con 3 nervature per il pacco millefori 8x20 + SuperMini, TP4056, culla 18650, tasca del connettore volante). Incluso dal principale, non autonomo.
- `componenti.scad`: modelli semplificati dei componenti (anche anello LED, modulo vibrazione, inviluppo del pacco millefori + SuperMini, connettore volante), solo per l'anteprima (`show_electronics`) e per i controlli di interferenza. Mai esportati.
- `verifica_interferenze.scad`: controllo interferenze (`-D chk=1..24`; 21 = connettore volante, 22 = spina USB-C nella presa del TP4056 dal retro, 23 = tasca del connettore, 24 = pacco elettronico agli estremi della corsia con `-D pk_dx=±0.45 -D pk_dy=±0.9`), esito atteso nell'intestazione del file.

## Parametri di uso
- `mode = "print"` con `plate = 1 | 2 | 3 | 4` (0 = tutti affiancati, solo anteprima)
- `led_ring = true` (anello LED + diffusore; `false` = anello decorativo `collar`); `diff_mode = "insert" | "mmu"`; `vt_on` (sede vibrazione sulla scocca), `mf_on` in `portaschede.scad` (corsia del pacco + tasca connettore); `"assembly"`; `"exploded"`.
- `part = "body" | "lid" | "sled" | "panel" | "knob" | "collar" | "diffuser" | "test_ring"`: esporta il singolo pezzo (ignora `plate`).
- Esempio: `openscad -o piatto2.stl -D 'mode="print"' -D plate=2 youtube_control.scad` (render CGAL ~2-4 min).

## Piatti (Bambu Lab A1 mini, 180 x 180)

| Piatto | Pezzi | Colore (PLA) | Orientamento / note |
|--------|-------|--------------|---------------------|
| 5 (prima) | anelli di prova, diffusore di prova, tassello con sede anello | GRIGIO | Anelli: infilare l'albero (1/2/3 tacche = gioco 0,05/0,10/0,15) e riportare il migliore in `knurl_fit`; tassello e diffusore: faccia a vista sul piatto |
| 4 | diffusore (`diff_mode = "insert"`) | BIANCO (solo questo) | Faccia a vista sul piatto, 1 mm, 100 % riempimento, nessun supporto. Variante `"mmu"`: vedi sopra |
| 1 | scocca | NERO | Piano superiore inclinato sul piatto, nessun supporto. Ponti brevi (fori, tasche dei ganci), labbri della sede vibrazione 1 mm. Brim 5 mm |
| 2 | fondo, portaschede | NERO | Tutto in piano, nessun supporto. Svasature sul lato a contatto col piatto |
| 3 | manopola, 2 pannelli (anello decorativo solo se `led_ring = false`) | RAME | Manopola capovolta (faccia superiore sul piatto); pannelli con la faccia esterna sul piatto. Nessun supporto |

Colori: scocca/fondo/portaschede neri (le parti interne spariscono, luce dell'anello e rame risaltano); manopola e pannelli in rame come unico accento. Pulsante PBS-110 eliminato il 2026-10-14: il pulsante e' quello integrato dell'encoder.

Materiale: **tutto PLA** (decisione utente); ganci a scatto dimensionati per PLA (deformazione <= ~1,4 %). PLA si ammorbidisce oltre ~55 °C: niente sole/auto, ricaricare a temperatura ambiente. Strato 0,2 mm, 3 perimetri; manopola, cappuccio e anelli di prova con ugello 0,4 e "precise wall" attivo.

Esportazione per Bambu Studio / MakerWorld: `python enclosure/export/esporta.py` (3MF per piatto + zip in `export/out/`, impostazioni in `export/IMPOSTAZIONI_STAMPA.md`). Lo zip per la stampa (`export/YouTubeController_stampa_A1mini.zip`) contiene un 3MF per piatto con il colore nel nome e un `LEGGIMI.md`.

## Minuteria da comprare
- 8 viti M3x8 (o ST2,9x9,5) a testa svasata, autofilettanti per plastica: 4 fondo → scocca, 4 fondo → portaschede.
- 4 viti M2x5 autofilettanti (o M1,6 se i fori del TP4056 sono < 2 mm) per il TP4056.
- Guaina termorestringente o kapton per isolare il pacco millefori + SuperMini (libero nella corsia, nessuna vite). Strip maschio 2 x 1x9, connettore volante Dupont 2x5 maschio + femmina.
- 1 coppia di contatti per 18650 (piastrina + molla, ~11 x 12 mm, spessore ≤ 0,6) e 1 fascetta da 3,6 mm come ritegno (dietro la millefori).
- Dado M7 dell'encoder: già fornito con il componente. Biadesivo sottile o cianoacrilato (solo se il PCB della vibrazione è più sottile di 1,6).

## Montaggio
1. Modulo vibrazione (pin già sostituiti da 3 fili): a scocca capovolta, infilato dal davanti nella sede sotto la faccia superiore, retro piatto contro la faccia, fino alla battuta (scatto dei 2 ganci); fili dalla tacca verso l'encoder.
2. Diffusore: a scatto dall'alto nella corona attorno al foro encoder (si toglie spingendo dall'interno attraverso le finestre).
3. Anello LED: LED verso l'alto, piazzole verso destra-retro (arco a 30°), spinto dall'interno fino allo scatto dei 4 ganci; fili già saldati.
4. Encoder: dall'interno (passa nel foro dell'anello), dado M7 sulla faccia superiore, stretto senza esagerare (la spinta del pulsante non deve allentarlo né schiacciare il PLA); manopola a pressione sull'albero zigrinato fino a battere sulla punta (taglio dell'albero allargato leggermente se lasca).
5. Portaschede: TP4056 con 4 viti M2. Contatti 18650 nelle fessure delle testate, fili dai fori in basso, fascetta sulla cella (dietro la corsia). Pacco elettronico (millefori + SuperMini già saldate, isolato con guaina/kapton) appoggiato **libero** nella corsia sinistra tra le 3 nervature, SuperMini con la strip verso il fondo del pacco: **le prime ~2 mm dal bordo sinistro della millefori devono restare senza componenti alti** (denti dei bracci del pannello). Fili verso il TP4056 alle piazzole.
6. Connettore volante 2x5 (codino del pacco + cablaggio della scocca) innestato e **infilato in piedi nella tasca** dietro la culla (tacca bassa a sinistra per i fili); portaschede avvitato al fondo (4 M3 dal basso); fondo + portaschede nella scocca, 4 M3 negli angoli.
7. Aggiornamento firmware: via OTA o a scatola aperta (4 viti del fondo, fondo + portaschede estratti): il fronte della scocca è liscio, non c'è finestra USB per la SuperMini. La ricarica usa la presa del retro (TP4056). RST/BOOT non hanno fori.
