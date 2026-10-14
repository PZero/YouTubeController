# Scatola 3D

Modello parametrico della scatola (OpenSCAD 2021.01). Le misure dei componenti stanno in `dimensioni.md` (unica fonte di verità, comprese le interfacce fisse fondo/portaschede/presa USB).

## File
- `youtube_control.scad`: file principale (scocca con sede del modulo vibrazione, fondo, pannelli, manopola, anello decorativo, anelli di prova, piatti, assembly). Si apre e si esporta solo questo.
- `portaschede.scad`: portaschede intercambiabile (SuperMini, TP4056, culla 18650). Incluso dal principale, non autonomo.
- `componenti.scad`: modelli semplificati dei componenti (anche anello LED, modulo vibrazione, schedina millefori), solo per l'anteprima (`show_electronics`) e per i controlli di interferenza. Mai esportati.
- `verifica_interferenze.scad`: controllo interferenze (`-D chk=1..20`), esito atteso nell'intestazione del file.

## Parametri di uso
- `mode = "print"` con `plate = 1 | 2 | 3 | 4` (0 = tutti affiancati, solo anteprima)
- `led_ring = true` (anello LED + diffusore; `false` = anello decorativo `collar`); `diff_mode = "insert" | "mmu"`; `vt_on` (sede vibrazione sulla scocca), `mf_on` in `portaschede.scad` (`vib_on` = variante scartata sul portaschede); `"assembly"`; `"exploded"`.
- `part = "body" | "lid" | "sled" | "panel" | "knob" | "collar" | "diffuser" | "test_ring"`: esporta il singolo pezzo (ignora `plate`).
- Esempio: `openscad -o piatto2.stl -D 'mode="print"' -D plate=2 youtube_control.scad` (render CGAL ~2-4 min).

## Piatti (Bambu Lab A1 mini, 180 x 180)

| Piatto | Pezzi | Colore (PLA) | Orientamento / note |
|--------|-------|--------------|---------------------|
| 5 (prima) | anelli di prova, diffusore di prova, tassello con sede anello | GRIGIO | Anelli: infilare l'albero (1/2/3 tacche = gioco 0,05/0,10/0,15) e riportare il migliore in `knurl_fit`; tassello e diffusore: faccia a vista sul piatto |
| 4 | diffusore (`diff_mode = "insert"`) | BIANCO (solo questo) | Faccia a vista sul piatto, 1 mm, 100 % riempimento, nessun supporto. Variante `"mmu"`: vedi sopra |
| 1 | scocca | NERO | Piano superiore inclinato sul piatto, nessun supporto. Ponti brevi (fori, tasche dei ganci), labbri della sede vibrazione 1 mm. Brim 5 mm |
| 2 | fondo, portaschede | NERO | Tutto in piano, nessun supporto. Svasature e scritte RST/BOOT sul lato a contatto col piatto |
| 3 | manopola, 2 pannelli (anello decorativo solo se `led_ring = false`) | RAME | Manopola capovolta (faccia superiore sul piatto); pannelli con la faccia esterna sul piatto. Nessun supporto |

Colori: scocca/fondo/portaschede neri (le parti interne spariscono, luce dell'anello e rame risaltano); manopola e pannelli in rame come unico accento. Pulsante PBS-110 eliminato il 2026-10-14: il pulsante e' quello integrato dell'encoder.

Materiale: **tutto PLA** (decisione utente); ganci a scatto dimensionati per PLA (deformazione <= ~1,4 %). PLA si ammorbidisce oltre ~55 °C: niente sole/auto, ricaricare a temperatura ambiente. Strato 0,2 mm, 3 perimetri; manopola, cappuccio e anelli di prova con ugello 0,4 e "precise wall" attivo.

Esportazione per Bambu Studio / MakerWorld: `python enclosure/export/esporta.py` (3MF per piatto + zip in `export/out/`, impostazioni in `export/IMPOSTAZIONI_STAMPA.md`). Lo zip per la stampa (`export/YouTubeController_stampa_A1mini.zip`) contiene un 3MF per piatto con il colore nel nome e un `LEGGIMI.md`.

## Minuteria da comprare
- 8 viti M3x8 (o ST2,9x9,5) a testa svasata, autofilettanti per plastica: 4 fondo → scocca, 4 fondo → portaschede.
- 4 viti M2x5 autofilettanti (o M1,6 se i fori del TP4056 sono < 2 mm) per il TP4056.
- 1 coppia di contatti per 18650 (piastrina + molla, ~11 x 12 mm, spessore ≤ 0,6) oppure 2 fascette da 3,6 mm come ritegno.
- Dado M7 dell'encoder: già fornito con il componente. Biadesivo sottile o cianoacrilato (solo se il PCB della vibrazione è più sottile di 1,6).

## Montaggio
1. Modulo vibrazione (pin già sostituiti da 3 fili): a scocca capovolta, infilato dal davanti nella sede sotto la faccia superiore, retro piatto contro la faccia, fino alla battuta (scatto dei 2 ganci); fili dalla tacca verso l'encoder.
2. Diffusore: a scatto dall'alto nella corona attorno al foro encoder (si toglie spingendo dall'interno attraverso le finestre).
3. Anello LED: LED verso l'alto, piazzole verso destra-retro (arco a 30°), spinto dall'interno fino allo scatto dei 4 ganci; fili già saldati.
4. Encoder: dall'interno (passa nel foro dell'anello), dado M7 sulla faccia superiore, stretto senza esagerare (la spinta del pulsante non deve allentarlo né schiacciare il PLA); manopola a pressione sull'albero zigrinato fino a battere sulla punta (taglio dell'albero allargato leggermente se lasca).
5. Portaschede: SuperMini capovolta (componenti verso il basso), lato antenna sotto i labbri, poi lato USB-C giù fino allo scatto dei ganci. TP4056 con 4 viti M2. Contatti 18650 nelle fessure delle testate, fili dai fori in basso (il filo + passa nel tunnel sotto il modulo vibrazione). Schedina millefori infilata dall'alto nelle guide (componenti verso il davanti).
6. Connettore JST-PH scocca → schedina; portaschede avvitato al fondo (4 M3 dal basso); fondo + portaschede nella scocca, 4 M3 negli angoli.
7. Primo caricamento firmware: con fondo e portaschede estratti la USB-C della SuperMini è libera (canalino nella piastra per la spina). Reset: spillo nel foro RST del fondo (BOOT nel foro accanto).
