# Impostazioni di stampa - YouTubeController

Stampante: **Bambu Lab A1 mini** (piatto 180 × 180), ugello **0,4**, tutto in **PLA**.
I file `.3mf` sono generati da `enclosure/export/esporta.py`: ogni file è un piatto, con i pezzi già orientati per la stampa e disposti entro 170 × 170.

Licenza: **MIT** (file `LICENSE` incluso). Sorgenti parametrici OpenSCAD in `enclosure/` del repository.

## Ordine consigliato
1. **00_prova_tolleranze**: si stampa per prima (~30 min) e serve a verificare gli accoppiamenti prima dei pezzi grandi.
   - **Anelli di prova** (1/2/3 tacche = gioco 0,05/0,10/0,15): infilare l'albero dell'encoder e riportare il gioco migliore in `knurl_fit`.
   - **Diffusore**: deve entrare a scatto nel tassello senza forzare troppo. Se è lasco, `diff_c = 0`; se è troppo duro, `diff_snap = 0.10`.
   - **Tassello della faccia superiore**: l'anello LED deve entrare spingendo e restare tenuto dai 4 denti. Se è troppo duro, `lr_barb = 0.25`; se è lasco, `lr_c = 0.15`.
2. Poi 01, 02, 03 e 04.

## Impostazioni per piatto

| Piatto | Filamento | Strato | Pareti | Riempimento | Supporti | Brim | Orientamento / note | PLA (pieno, limite sup.) |
|--------|-----------|--------|--------|-------------|----------|------|---------------------|-----------|
| 00_prova_tolleranze | PLA qualsiasi; diffusore in PLA bianco | 0,20 | 3 | 15 % (diffusore 100 %) | no | no | Tassello e diffusore con la faccia a vista sul piatto; anelli di prova in piedi | ~9 g |
| 01_scocca | PLA grafite (colore principale) | 0,20 | 3 | 15 % gyroid | **no** | 5 mm consigliato | Faccia superiore sul piatto. Lamatura del pulsante, ponti del diffusore e tasche dei ganci si stampano come brevi ponti (ponti ≤ 6 mm) | ~78 g |
| 02_fondo_portaschede_pannelli | PLA grigio chiaro | 0,20 | 3 | 15 % | no | no | Tutto in piano. Ganci SuperMini e pannelli: "Pareti precise" attivo | ~58 g |
| 03_manopola_cappuccio | PLA ottone/oro (accento) | 0,16 (o 0,20) | 3 | 20 % | no | no | Manopola e cappuccio capovolti (faccia superiore sul piatto). "Pareti precise" attivo | ~21 g |
| 04_diffusore | **PLA bianco** opaco/naturale (non trasparente, non "silk") | 0,20 | 2 | **100 %**, motivo concentrico | no | no | Faccia a vista sul piatto (piatto liscio = superficie liscia). Spessore 1 mm = 5 strati | ~1 g |

I grammi sono calcolati dal volume pieno dei pezzi e sono un limite superiore: peso reale e tempi li dà Bambu Studio dopo lo slicing.

Profilo di base per tutti i piatti: "0.20mm Standard @BAMBU A1M", filamento "Bambu PLA Basic" o "Generic PLA". Lasciare la ventola come da profilo PLA.

## Avvertenze PLA
- **Limite termico ~55 °C**: oltre questa temperatura il PLA si ammorbidisce e si deforma. Non lasciare il controller al sole, in auto o vicino a fonti di calore.
- **Ricarica**: il caricatore TP4056 (limitato a 0,5 A) scalda le colonnine del portaschede su cui è avvitato. Va caricato a temperatura ambiente, non in luoghi caldi.
- **Ganci a scatto**: i ganci sono dimensionati per PLA, con deformazione al massimo ~1,4 %. Si possono montare e smontare più volte, ma senza forzarli oltre il dente.
- **Nervature del modulo vibrazione**: il modulo va infilato con decisione una volta sola. Le nervature in PLA si schiacciano poco (interferenza 0,15 mm).

## Bambu Studio: dall'apertura alla pubblicazione su MakerWorld
1. Apri Bambu Studio e scegli la stampante **Bambu Lab A1 mini** con ugello 0,4 mm.
2. Usa **File > Importa > Importa 3MF/STL** e scegli `01_scocca.3mf`. Alla domanda se caricare come oggetto unico, conferma.
   - Ogni file è un oggetto unico con più corpi. Per dare impostazioni diverse ai singoli pezzi (per esempio il diffusore al 100 %): tasto destro sull'oggetto, poi **Dividi > In oggetti**.
3. Per ogni piatto successivo usa **Aggiungi piatto** (icona "+" in alto) e importa il file 3MF corrispondente: un progetto con 5 piatti numerati come i file.
4. Per ogni piatto assegna il filamento (colore) e il profilo di processo indicati nella tabella, senza attivare i supporti.
   - Se un pezzo risulta fuori posto, premi **Disponi** (tasto A).
5. Esegui **Elabora piatto** (slicing) e controlla in anteprima soprattutto:
   - i ponti della scocca;
   - le tasche dei ganci dell'anello;
   - il diffusore pieno.
6. Salva con **File > Salva progetto**: si ottiene un file `.3mf` con piatti, filamenti e impostazioni.
7. Pubblicazione: **File > Pubblica** (Publish to MakerWorld), oppure carica il `.3mf` del progetto su makerworld.com. Allega le foto e la licenza **MIT**.
