# Impostazioni di stampa - YouTubeController

Stampante: **Bambu Lab A1 mini** (piatto 180 × 180), ugello **0,4**, tutto in **PLA**.
I file `.3mf` sono generati da `enclosure/export/esporta.py`: ogni file è un piatto, con i pezzi già orientati per la stampa e disposti entro 170 × 170.

Licenza: **MIT** (file `LICENSE` incluso). Sorgenti parametrici OpenSCAD in `enclosure/` del repository.

## Ordine consigliato (un colore per piatto, senza AMS)
1. **01_bianco_diffusore** (PLA bianco, solo per questo pezzo): per primo, per sapere subito se l'avanzo di bianco basta.
2. **02_grigio_prova_tolleranze** (~30 min): anelli di prova (gioco 0,05/0,10/0,15 → `knurl_fit`), diffusore di prova (se lasco `diff_c = 0`, se duro `diff_snap = 0.10`), tassello con sede dell'anello LED (se duro `lr_barb = 0.25`, se lasco `lr_c = 0.15`).
3. **03_nero_scocca**, **04_nero_fondo_portaschede**, **05_rame_manopola_pannelli**.

## Impostazioni per piatto

| Piatto | Filamento | Strato | Pareti | Riempimento | Supporti | Brim | Orientamento / note | PLA (pieno, limite sup.) |
|--------|-----------|--------|--------|-------------|----------|------|---------------------|-----------|
| 01_bianco_diffusore | PLA bianco opaco/naturale (non trasparente, non "silk") | 0,20 | 2 | **100 %**, concentrico | no | no | Faccia a vista sul piatto, 1 mm = 5 strati | ~1 g |
| 02_grigio_prova_tolleranze | PLA grigio | 0,20 | 3 | 15 % | no | no | Tassello e diffusore con la faccia a vista sul piatto; anelli in piedi | ~9 g |
| 03_nero_scocca | PLA nero | 0,20 | 3 | 15 % gyroid | **no** | 5 mm consigliato | Faccia superiore sul piatto. Ponti ≤ 6 mm (tasche dei ganci, ponti del diffusore), finestra USB-C del fronte 14,5 x 8,5 (ponte ~14 mm con angoli r 2,5) e labbri di 1 mm della sede vibrazione | ~78 g |
| 04_nero_fondo_portaschede | PLA nero | 0,20 | 3 | 15 % | no | no | Tutto in piano. Fermi a C della millefori e tasca del connettore: "Pareti precise" attivo | ~52 g |
| 05_rame_manopola_pannelli | PLA rame | 0,16 | 3 | 20 % | no | no | Manopola capovolta, pannelli con la faccia esterna sul piatto. "Pareti precise" attivo | ~22 g |

I grammi sono calcolati dal volume pieno dei pezzi e sono un limite superiore (il LEGGIMI dello zip ha i valori esatti): peso reale e tempi li dà Bambu Studio dopo lo slicing.

Profilo di base per tutti i piatti: "0.20mm Standard @BAMBU A1M", filamento "Bambu PLA Basic" o "Generic PLA". Lasciare la ventola come da profilo PLA.

## Avvertenze PLA
- **Limite termico ~55 °C**: oltre questa temperatura il PLA si ammorbidisce e si deforma. Non lasciare il controller al sole, in auto o vicino a fonti di calore.
- **Ricarica**: il caricatore TP4056 (limitato a 0,5 A) scalda le colonnine del portaschede su cui è avvitato. Va caricato a temperatura ambiente, non in luoghi caldi.
- **Ganci a scatto**: i ganci sono dimensionati per PLA, con deformazione al massimo ~1,4 %. Si possono montare e smontare più volte, ma senza forzarli oltre il dente.
- **Nervature del modulo vibrazione**: il modulo va infilato con decisione una volta sola. Le nervature in PLA si schiacciano poco (interferenza 0,15 mm).

## Bambu Studio: dall'apertura alla pubblicazione su MakerWorld
1. Apri Bambu Studio e scegli la stampante **Bambu Lab A1 mini** con ugello 0,4 mm.
2. Usa **File > Importa > Importa 3MF/STL** e scegli `01_scocca.3mf`. Alla domanda se caricare come oggetto unico, conferma.
   - Ogni file è un oggetto unico con più corpi. Per dare impostazioni diverse ai singoli pezzi (per esempio i pannelli e la manopola): tasto destro sull'oggetto, poi **Dividi > In oggetti**.
3. Per ogni piatto successivo usa **Aggiungi piatto** (icona "+" in alto) e importa il file 3MF corrispondente: un progetto con 5 piatti numerati come i file (un colore per piatto).
4. Per ogni piatto assegna il filamento (colore) e il profilo di processo indicati nella tabella, senza attivare i supporti.
   - Se un pezzo risulta fuori posto, premi **Disponi** (tasto A).
5. Esegui **Elabora piatto** (slicing) e controlla in anteprima soprattutto:
   - i ponti della scocca;
   - le tasche dei ganci dell'anello e i labbri della sede vibrazione;
   - il diffusore pieno.
6. Salva con **File > Salva progetto**: si ottiene un file `.3mf` con piatti, filamenti e impostazioni.
7. Pubblicazione: **File > Pubblica** (Publish to MakerWorld), oppure carica il `.3mf` del progetto su makerworld.com. Allega le foto e la licenza **MIT**.
