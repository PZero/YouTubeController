# Schedina millefori di interfaccia

Raccoglie tutto ciò che non è la SuperMini o il modulo 4056: interruttore dell'anello (Q1 S8550 + Q2 2N3904), resistenza del dato, condensatore di bulk, partitore della batteria, resistenze di lettura CHRG/STDBY e il connettore verso la scocca. Schema di riferimento: `firmware/README.md`, sezione "Schema dei collegamenti completo".

Posizione (soluzione C del design-3d): **coricata sopra il modulo TP4056**, zona posteriore sinistra del portaschede, lato saldature verso il modulo.

File:
- `millefori.py`: disposizione, piste, **verifica automatica** contro la netlist, generazione degli SVG (solo libreria standard). Tutte le quote incerte sono parametri in testa al file.
- `lato_componenti.svg`: vista dall'alto, scala 1:1 + 4:1.
- `lato_saldature.svg`: vista da sotto **specchiata** (colonne H…A), piste colorate per net con legenda, scala 1:1 + 4:1.

Gli SVG si stampano al 100% (barra di controllo da 10 mm). Quelli nel repository sono della variante di default (connettore angolato, con chiave).

```
python millefori.py                       # variante di default: deve dare "VERIFICA OK"
python millefori.py --connettore diritto  # fallisce di proposito: header diritto + spina = 16,5 mm > 12
python millefori.py --senza-chiave        # pin 5 di J1 = terzo GND
python millefori.py --pinout-q1 ECB       # mostra che un S8550 E-C-B non va montato così
```

La verifica controlla: ogni net connessa, nessun corto tra net, i due terminali di ogni resistenza/condensatore sulle net giuste, nessun foro usato due volte, piste solo tra piazzole adiacenti, fori di fissaggio e righe riservate liberi, nessuna collisione tra i corpi (in pianta), altezza ≤ 12 mm ovunque e ≤ 10 mm nella zona critica, elettrolitico nella metà anteriore e fuori dalla verticale del chip, lato saldature ≤ 2 mm. Gli SVG vengono riletti come XML per controllarne la validità.

## Griglia e convenzioni

- Millefori a piazzole singole, passo 2,54, **8 colonne (A…H) × 13 righe (1…13)**, taglio ~21 × 34 mm (`LARGH`, `LUNG`).
- Vista dal lato componenti con l'**anteriore in basso**: riga 1 = bordo anteriore (connettore J1, verso encoder e SuperMini), riga 13 = posteriore (verso la USB-C del TP4056). A1 = angolo anteriore-sinistro.
- **Zona critica** (verso l'encoder): angolo anteriore-destro 6 × 7 mm, componenti ≤ 10 mm (`ZONA_CRITICA`). Ci stanno solo J1 angolato (5,1) e il filo del pulsante.
- **Zona del chip TP4056** (scalda in carica): centro in larghezza ±5 mm, metà posteriore (`ZONA_CHIP`). L'elettrolitico C1 sta nella metà anteriore, fuori da questa zona.
- **Righe 12-13 riservate** (`RIGHE_RISERVATE`): nessun componente né pista. Ospitano i 2 fori posteriori, che devono coincidere con i fori lato USB-C del TP4056 (interasse non ancora misurato: `INTERASSE_TP_POST`, `CENTRO_TP_X`, `Y_FORI_TP_POST`). Qualunque interasse va bene finché i fori cadono in quelle righe.
- Fori anteriori di fissaggio: A1 e H1 (`FISSAGGI`). Tutti i fori si allargano a Ø2,2 per viti M2.

Mappa (stampata dallo script; `*` = foro su cui sta il corpo della resistenza in piedi, `~` = filo esterno, `-` = sola pista, `//` = riga riservata):

```
            A        B        C        D        E        F        G        H
  13  |   //      FISS      //       //       //       //      FISS      //    |  <- posteriore (USB-C TP4056)
  12  |   //       //       //       //       //       //       //       //    |
  11  | ~STDBY     R8*     -GND     -GND      R2*     -GND     C2.2     R11*   |
  10  |    .       R8      -GND      Q2E      R2        .      C2.1      R11   |
   9  | ~GPIO10    R9      -GND      Q2B      R1       R1*    ~GPIO9   ~GPIO1  |
   8  |    .       R9*     -GND      Q2C       .        .       R10     R10*   |
   7  |  ~3V3      R7*     -GND      R3*      R3       R4*      R4        .    |
   6  |    .       R7     ~GND_TP     .       Q1C      Q1B      Q1E     ~VBAT  |
   5  |   R6     ~GPIO8   ~GND_SM     .      -LED+      .        .        .    |
   4  |   R6*       .      -GND     C1.-     C1.+      R5       R5*    ~GPIO2  |
   3  |  ~CHRG      .     ~GPIO5    -GND     -LED+     -DI       .        .    |
   2  |    .     ~GPIO4    J1.2     J1.4     J1.6     J1.8    ~GPIO7      .    |
   1  |  FISS    -ENC_A    J1.1     J1.3     J1.5x    J1.7     -PULS    FISS   |  <- anteriore
```

(Nelle righe 12-13 "FISS" indica solo dove cadono i fori posteriori con i valori indicativi.)

## Componenti

| Rif. | Valore | Fori (corpo / piedino) | Funzione |
|------|--------|------------------------|----------|
| Q1 | S8550 PNP, TO-92 | E = G6, B = F6, C = E6; **faccia piatta verso il posteriore** | interruttore high-side dell'anello |
| Q2 | 2N3904 NPN, TO-92 | C = D8, B = D9, E = D10; **faccia piatta verso sinistra** (colonna C) | driver di Q1 |
| R1 | 4,7 kΩ | F9 / E9 | GPIO9 → base Q2 |
| R2 | 10 kΩ | E11 / E10 | base Q2 → GND |
| R3 | 680 Ω | D7 / E7 | collettore Q2 → base Q1 |
| R4 | 10 kΩ | F7 / G7 | base-emettitore Q1 |
| R5 | 330 Ω | G4 / F4 | serie al dato DI |
| R6 | 10 kΩ | A4 / A5 | serie CHRG |
| R7 | 100 kΩ | B7 / B6 | pull-up GPIO8 a 3V3 |
| R8 | 10 kΩ | B11 / B10 | serie STDBY |
| R9 | 100 kΩ | B8 / B9 | pull-up GPIO10 a 3V3 |
| R10 | 220 kΩ | H8 / G8 | partitore, lato VBAT |
| R11 | 220 kΩ | H11 / H10 | partitore, lato GND |
| C1 | 47 µF 16 V elettrolitico 5 × 11, in piedi | + = E4, − = D4 | bulk dell'anello dopo Q1 |
| C2 | 100 nF ceramico | G10 / G11 | filtro partitore (GPIO1) |
| J1 | pin header 2 × 4 passo 2,54, **angolato** (o diritto, vedi sotto) | C1…F2 | connettore scocca → portaschede |

Tutte le resistenze sono **in piedi** (1/4 W, ~10 mm di altezza): il corpo appoggia sul foro indicato per primo, il piedino ripiegato scende nell'altro. Altezze: resistenze ~10, TO-92 ~8, C1 ~11,5 (il più alto, max 12), C2 ~6, J1 angolato 5,1. Lato saldature: piedini tagliati a ~1 mm, ponticelli ~1 mm (≤ 1,5, limite 2).

I condensatori della vibrazione e l'eventuale pull-down su IN stanno **sul modulo vibrazione**; GPIO6 va con un filo diretto dalla SuperMini al modulo; OUT+/OUT− del TP4056 vanno direttamente a 5V/GND della SuperMini. Su questa schedina arrivano solo un filo VBAT e un filo GND dal TP4056.

## Connettore J1 (scocca → portaschede)

Header maschio 2 × 4 sul bordo anteriore (colonne C-F, righe 1-2), cavo con **Dupont femmina 2 × 4**. Pin 1 = C1, dispari sulla fila esterna (riga 1), pari sulla fila interna (riga 2).

| Pin | Foro | Segnale | Va a (lato scocca) |
|-----|------|---------|--------------------|
| 1 | C1 | encoder A → GPIO4 | encoder pin A |
| 2 | C2 | encoder B → GPIO5 | encoder pin B |
| 3 | D1 | GND | encoder C + secondo terminale del pulsante (unire sul lato scocca) |
| 4 | D2 | GND | anello − |
| 5 | E1 | **chiave**: piedino tagliato a filo, posizione tappata nella spina | - |
| 6 | E2 | LED+ (anello + commutato) | anello + |
| 7 | F1 | pulsante → GPIO7 | pulsante |
| 8 | F2 | DI (dopo la 330 Ω) | anello DI |

- **Chiave**: tagliare il pin 5 dell'header a filo della plastica e tappare la posizione 5 della spina (spezzone di pin incollato o goccia di colla). Girata di 180° la posizione tappata cadrebbe sul pin 4: la spina non entra. In più, segno di vernice sul lato del pin 1 di header e spina (la spina potrebbe ancora entrare spostata di una colonna). Se si preferisce un pin di riserva: `--senza-chiave` fa del pin 5 un terzo GND (ponticello D1-E1) e si usa solo la marcatura.
- I tre fili dell'anello stanno **affiancati sulla fila interna** (pin 4-6-8 = GND, LED+, DI), con LED+ in mezzo: girando una spina a 3 poli il + resta al suo posto.
- **Variante angolata (default)**: altezza 5,1 mm, ma pin e spina **sporgono in avanti oltre il bordo anteriore**: ~6 (pin) + ~14 (spina Dupont) + ~5 (curvatura dei fili) ≈ **20-25 mm** nel piano della schedina, a 1-5 mm di quota.
- **Variante diritta**: stessi fori, nessuna sporgenza in pianta, ma 8,5 mm a vuoto e **~16,5 mm con la spina** + 3-5 di fili: supera i 12 mm (e i 10 della zona critica, che sfiora). Ammissibile solo se il design-3d garantisce ~20 mm liberi sopra le righe 1-2. Lo script la segnala come errore.
- **Riduzione a 3 poli** (encoder e pulsante cablati direttamente alla SuperMini): montare solo un header 1 × 3 su D2-E2-F2 (angolato o diritto), lasciare vuoti C1, C2, D1, E1, F1, non fare le piste C1-B1-B2, C2-C3, F1-G1-G2 né i fili GPIO4/5/7. Encoder A/B → GPIO4/5, comune C e pulsante → GND, pulsante → GPIO7 direttamente sugli header della SuperMini. Il ponticello D1-D2 non serve (D2 resta collegato a D3). Una spina 1 × 3 Dupont non è polarizzata: marcare il verso (girandola si scambiano solo GND e DI, il + resta al centro).

## Fili esterni

Filo siliconico 26-28 AWG (VBAT e GND anche 24-26). Si infilano dal lato componenti e si saldano sotto. Lunghezze indicative: da confermare con il portaschede stampato (lasciare 1-2 cm di abbondanza).

| Foro | Net | Verso | Colore suggerito | Lunghezza |
|------|-----|-------|------------------|-----------|
| H6 | VBAT | TP4056 **OUT+** | rosso | 4-6 cm |
| C6 | GND | TP4056 **OUT−** | nero | 4-6 cm |
| A3 | CHRG | TP4056, catodo LED rosso (pin 7 del chip) | marrone/bianco | 3-5 cm |
| A11 | STDBY | TP4056, catodo LED blu/verde (pin 6 del chip) | azzurro/bianco | 3-5 cm |
| C5 | GND | SuperMini GND | nero | 6-8 cm |
| A7 | 3V3 | SuperMini 3V3 | arancione | 6-8 cm |
| H9 | GPIO1 | SuperMini GPIO1 (partitore batteria) | grigio | 6-8 cm |
| H4 | GPIO2 | SuperMini GPIO2 (dato anello, prima della 330) | bianco | 6-8 cm |
| B2 | GPIO4 | SuperMini GPIO4 (encoder A) | giallo | 6-8 cm |
| C3 | GPIO5 | SuperMini GPIO5 (encoder B) | verde | 6-8 cm |
| G2 | GPIO7 | SuperMini GPIO7 (pulsante) | blu | 6-8 cm |
| B5 | GPIO8 | SuperMini GPIO8 (CHRG) | marrone | 6-8 cm |
| G9 | GPIO9 | SuperMini GPIO9 (comando anello) | viola | 6-8 cm |
| A9 | GPIO10 | SuperMini GPIO10 (STDBY) | azzurro | 6-8 cm |

Sulla SuperMini: fila 1 = 5V, GND, 3V3, 13, 12, 11, 10, 9, 8; fila 2 = TX, RX, 1, 2, 3, 4, 5, 6, 7. Sul TP4056 il filo CHRG/STDBY va sul lato del LED verso il chip (catodo): verificare col tester (a USB collegata e LED acceso, il catodo è a ~0,2 V).

## Ordine di saldatura

1. **Preparazione**: tagliare 8 × 13 fori, limare i bordi. Forare A1 e H1 a Ø2,2. I fori posteriori **solo dopo** aver misurato il TP4056: appoggiare il modulo sotto la schedina nella posizione definitiva e usarlo come dima (righe 12-13). Pulire le piazzole (gomma abrasiva o alcool).
2. **Verifica dei transistor col tester** (sezione sotto) prima di piegarne i piedini.
3. **Resistenze in piedi** R1…R11, corpo sul foro indicato per primo; piedini tagliati a ~1 mm dopo la saldatura (conservare gli spezzoni per i ponticelli lunghi).
4. **C2**, poi **Q2** e **Q1** (orientamento della faccia piatta come nel disegno; piedini allargati a passo 2,54, corpo a ~3 mm dalla basetta).
5. **J1** (corpo plastico a filo del bordo anteriore se angolato), tagliare il pin 5 se si usa la chiave.
6. **C1** (+ in E4, − in D4; striscia del − verso la colonna D), corpo appoggiato alla basetta.
7. **Ponticelli sul retro** seguendo `lato_saldature.svg` (ricordarsi che è specchiato): stagno tra piazzole vicine per i tratti corti, spezzone di filo nudo stagnato per i tratti lunghi (GND C4…C11 e riga 11, LED+ E2…E6). Controllare a ogni net che non tocchi le piazzole adiacenti di altre net (45 coppie vicine).
8. **Controlli col tester** (sotto), poi **fili esterni**, infine di nuovo i controlli di corto.

## Pinout TO-92: verifica e adattamento

Il disegno presuppone **E-B-C** (faccia piatta verso di sé, piedini in basso, da sinistra): così sono il 2N3904 (JEDEC) e la maggior parte degli S8550. Verifica col tester:
1. **Prova diodi**: trovare il piedino che conduce (~0,6-0,7 V) verso entrambi gli altri = **base**. Puntale nero sulla base = PNP (S8550), rosso = NPN (2N3904). Tra gli altri due nessuna conduzione in nessun verso.
2. La giunzione **base-emettitore** ha una tensione di qualche mV più alta della base-collettore: così si riconosce l'emettitore.
3. Conferma con lo zoccolo **hFE** (E-B-C): nel verso giusto 100-300, con C ed E scambiati 5-30.

Se un transistor risulta **E-C-B** (base su un estremo): il disegno non va bene così com'è (`python millefori.py --pinout-q1 ECB` mostra le net che si scambiano). Soluzioni, in ordine di preferenza:
- usare un altro esemplare/modello del kit che sia E-B-C (S9012 per il PNP; S8050, S9013 per l'NPN): stesse funzioni, vedi `firmware/README.md`;
- incrociare i piedini B e C (tubetto termorestringente su uno dei due) in modo che la base finisca nel foro centrale (F6 per Q1, D9 per Q2) e il collettore nel foro del collettore (E6 per Q1, D8 per Q2); l'emettitore resta dov'è;
- se il pezzo fosse **C-B-E** (base al centro ma rovesciato) basta ruotarlo di 180° (faccia piatta dalla parte opposta).

## Controlli col tester prima di alimentare

Schedina senza SuperMini, senza anello, senza batteria. Misure tra le piazzole dei fili (o sui piedini):

| Tra | Atteso | Se diverso |
|-----|--------|------------|
| VBAT (H6) - GND (C6) | ~440 kΩ (sale lentamente: C2 si carica) | se < 100 kΩ: corto, cercare stagno tra net vicine |
| VBAT (H6) - GPIO1 (H9) | ~220 kΩ | R10 |
| GPIO1 (H9) - GND | ~220 kΩ | R11, C2 |
| VBAT (H6) - Q1 base (F6) | ~10 kΩ | R4 |
| GPIO9 (G9) - GND | ~14,7 kΩ (R1 + R2) | |
| Q2 collettore (D8) - Q1 base (F6) | ~680 Ω | R3 |
| GPIO2 (H4) - J1 pin 8 | ~330 Ω | R5 |
| GPIO8 (B5) - CHRG (A3) / GPIO10 (A9) - STDBY (A11) | ~10 kΩ | R6 / R8 |
| GPIO8 - 3V3 (A7) / GPIO10 - 3V3 | ~100 kΩ | R7 / R9 |
| J1 pin 6 (LED+) - GND | aperto (dopo la carica di C1) | mai 0 Ω |
| J1 pin 6 (LED+) - VBAT | aperto | Q1 montato male o in corto |
| J1 pin 1, 2, 7 - GPIO4, GPIO5, GPIO7 | 0 Ω | |
| J1 pin 3 e 4 - GND | 0 Ω | |
| 3V3 - GND, 3V3 - VBAT | aperto | |
| ogni piazzola - fori di fissaggio | aperto | |

Con resistenze di centinaia di kΩ il tester può leggere valori un po' più bassi se le punte toccano le dita.

## Prima accensione sicura

1. **Alimentatore da banco** a 3,7 V con limite di corrente 50 mA su VBAT (H6) / GND (C6); in mancanza, cella 18650 con una resistenza da 22 Ω in serie (limita un corto a ~190 mA). SuperMini e anello **scollegati**.
2. Corrente a riposo: ~8-9 µA (solo il partitore). GPIO1 (H9) = VBAT / 2. LED+ (J1 pin 6) ≈ 0 V.
3. Collegare GPIO9 (G9) a 3,3 V (un secondo canale dell'alimentatore, o 3V3 della SuperMini alimentata via USB **senza batteria**): LED+ sale a VBAT − 0,1-0,2 V; corrente in più ~4-5 mA (base di Q1). GPIO9 a GND: LED+ torna a 0 (lentamente senza carico: C1 si scarica solo nelle perdite; con una resistenza da 1 kΩ tra LED+ e GND scende subito).
4. Collegare l'anello con GPIO9 basso; poi tutto il resto. Prima del flash della SuperMini via USB, **batteria scollegata** (vedi `firmware/README.md`, Alimentazione).

## Fissaggio

- 4 viti M2 (anteriori A1 e H1, posteriori nei fori del TP4056). Colonnine stampate o **distanziali in nylon**: con distanziali metallici la parte metallica toccherebbe le piazzole vicine (B1 = encoder A, G1 = pulsante); in quel caso portare `R_LIBERO` a 3,0 e lo script segnalerà i fori da spostare.
- Distanza tra TP4056 e schedina: il lato saldature (≤ 2 mm) deve stare sopra la parte più alta del TP4056 (USB-C ~3,2-3,5 mm sopra il suo PCB) con 0,5-1 mm d'aria: distanziali di ~6-7 mm sopra il PCB del TP4056 (da definire col design-3d).
