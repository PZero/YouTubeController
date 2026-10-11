# Scatola 3D

Modello parametrico della scatola (OpenSCAD 2021.01). Le misure dei componenti stanno in `dimensioni.md` (unica fonte di verità, comprese le interfacce fisse fondo/portaschede/presa USB).

## File
- `youtube_control.scad`: file principale (scocca, fondo, pannelli, manopola, anello, cappuccio, anelli di prova, piatti, assembly). Si apre e si esporta solo questo.
- `portaschede.scad`: portaschede intercambiabile (SuperMini, TP4056, culla 18650). Incluso dal principale, non autonomo.
- `componenti.scad`: modelli semplificati dei componenti (anche anello LED, modulo vibrazione, schedina millefori), solo per l'anteprima (`show_electronics`) e per i controlli di interferenza. Mai esportati.
- `verifica_interferenze.scad`: controllo interferenze (`-D chk=1..15`), esito atteso nell'intestazione del file.

## Parametri di uso
- `mode = "print"` con `plate = 1 | 2 | 3 | 4` (0 = tutti affiancati, solo anteprima)
- `led_ring = true` (anello LED + diffusore; `false` = anello decorativo `collar`); `diff_mode = "insert" | "mmu"`; `vib_on`, `mf_on`, `vib_top_contact` in `portaschede.scad`; `"assembly"`; `"exploded"`.
- `part = "body" | "lid" | "sled" | "panel" | "knob" | "collar" | "diffuser" | "cap" | "test_ring"`: esporta il singolo pezzo (ignora `plate`).
- Esempio: `openscad -o piatto2.stl -D 'mode="print"' -D plate=2 youtube_control.scad` (render CGAL ~2-4 min).

## Piatti (Bambu Lab A1 mini, 180 x 180)

| Piatto | Pezzi | Colore proposto | Orientamento / note |
|--------|-------|-----------------|---------------------|
| 0 (prima) | `test_ring` da solo (`part="test_ring"`) | qualsiasi | Prova della sede zigrinata: infilare l'albero nei 3 anelli (1/2/3 tacche = gioco 0,05/0,10/0,15) e riportare il migliore in `knurl_fit` |
| 1 | scocca | principale (grafite) | Piano superiore inclinato sul piatto, nessun supporto. Lamatura del pulsante e fori dei perni: piccoli ponti (abilitare "bridging"; opzionale strato sacrificale). Brim consigliato |
| 2 | fondo, portaschede, 2 pannelli | secondario (grigio chiaro) | Tutto in piano, nessun supporto. Svasature e scritte RST/BOOT sul lato a contatto col piatto. Ganci della SuperMini e labbri: sbalzi < 1 mm |
| 3 | manopola, cappuccio, anelli di prova (anello decorativo solo se `led_ring = false`) | accento (ottone) | Manopola e cappuccio capovolti (faccia superiore sul piatto). Nessun supporto |
| 4 | diffusore (`diff_mode = "insert"`) | PETG o PLA **bianco naturale/traslucido** (non trasparente) | Faccia a vista sul piatto, 1 mm, 100 % riempimento (strati concentrici), nessun supporto. Variante `"mmu"` con AMS lite: niente piatto 4, si esportano `part="body"` e `part="diffuser"` con `plate=1` e si caricano come parti dello stesso oggetto |

Materiale: PETG consigliato per portaschede e fondo (calore del TP4056 in carica, ganci a scatto); PLA va bene per il resto. Strato 0,2 mm, 3 perimetri; manopola, cappuccio e anelli di prova con ugello 0,4 e "precise wall" attivo.

## Minuteria da comprare
- 8 viti M3x8 (o ST2,9x9,5) a testa svasata, autofilettanti per plastica: 4 fondo → scocca, 4 fondo → portaschede.
- 4 viti M2x5 autofilettanti (o M1,6 se i fori del TP4056 sono < 2 mm) per il TP4056.
- 1 coppia di contatti per 18650 (piastrina + molla, ~11 x 12 mm, spessore ≤ 0,6) oppure 2 fascette da 3,6 mm come ritegno.
- Dado M7 dell'encoder e dado del PBS-110: già forniti con i componenti.

## Montaggio
1. Pulsante: dall'interno nel foro Ø7,2; rondella e dado dall'esterno nella lamatura; cappuccio calzato a pressione sul tasto blu (una goccia di colla se lasco).
2. Diffusore: a scatto dall'alto nella corona attorno al foro encoder (si toglie spingendo dall'interno attraverso le finestre).
3. Anello LED: LED verso l'alto, piazzole verso destra-retro (arco a 30°), spinto dall'interno fino allo scatto dei 4 ganci; fili già saldati.
4. Encoder: dall'interno (passa nel foro dell'anello), dado M7 sulla faccia superiore; manopola a pressione sull'albero zigrinato (taglio dell'albero allargato leggermente se lasca).
5. Portaschede: SuperMini capovolta (componenti verso il basso), lato antenna sotto i labbri, poi lato USB-C giù fino allo scatto dei ganci. TP4056 con 4 viti M2. Contatti 18650 nelle fessure delle testate, fili dai fori in basso (il filo + passa nel tunnel sotto il modulo vibrazione). Modulo vibrazione infilato dall'alto contro la culla (retro piatto verso la cella, motore verso il retro). Schedina millefori infilata dall'alto nelle guide (componenti verso il davanti).
6. Connettore JST-PH scocca → schedina; portaschede avvitato al fondo (4 M3 dal basso); fondo + portaschede nella scocca, 4 M3 negli angoli.
7. Primo caricamento firmware: con fondo e portaschede estratti la USB-C della SuperMini è libera (canalino nella piastra per la spina). Reset: spillo nel foro RST del fondo (BOOT nel foro accanto).
