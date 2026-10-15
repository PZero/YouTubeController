# Millefori unica 8 x 20 con la SuperMini saldata sopra

Decisione 2026-10-15: un'unica millefori **piatta nella corsia sinistra del portaschede** porta la ESP32-S3 SuperMini e tutta l'interfaccia: interruttore dell'anello (S8550 + 2N3904), 330 Ω sul dato, bulk dell'anello, partitore della batteria (GPIO1), letture CHRG/STDBY (GPIO8/10), **diodo Schottky OUT+ → pin 5V**, condensatori del motore, codino verso la scocca. La vecchia schedina 8 x 13 sopra il TP4056 è in [`archivio_8x13/`](archivio_8x13/README.md).

File:
- `millefori.py`: disposizione, piste, fili sotto la scheda, **verifica automatica** contro la netlist, SVG (solo libreria standard).
- `lato_componenti.svg`, `lato_saldature.svg` (vista da sotto **specchiata**): scala 1:1 + 3:1, da stampare al 100% (barra di 10 mm).

```
python millefori.py              # deve dare "VERIFICA OK"
python millefori.py --specchia   # solo se la fila 5V/GND/3V3 della SuperMini risulta a SINISTRA (vedi sotto)
```

La verifica controlla: ogni net connessa e nessun corto, i due terminali di ogni resistenza/condensatore sulle net giuste, nessun foro usato due volte, piste solo tra piazzole adiacenti, piazzole libere sotto le teste delle viti M3, **zona antenna libera** (nessuna piazzola, pista o corpo), elettrolitici ad almeno 10 mm dall'antenna, nessuna collisione in pianta, nessun corpo sotto la SuperMini, altezze ≤ 16 mm, lato saldature ≤ 2 mm.

## Taglio dalla 14 x 20 (40 x 60)

- Tenere **20 righe** (tutta la lunghezza, 60 mm, lati corti intatti) e **8 colonne** adiacenti a **uno dei lati lunghi** (quello che resta intatto, con i suoi 2 fori M3).
- Tagliare tra l'8ª e la 9ª colonna contando dal lato intatto, **a metà passo** (1,27 mm dai centri dell'8ª colonna): incidere più volte con il cutter su entrambe le facce lungo la fila di fori, spezzare, limare.
- Risultato: **22,5 x 60 mm** (3,49 di margine sul lato intatto + 7 passi + 1,27). La corsia del portaschede è 21,5: **serve ~1 mm in più** (design-3d), oppure tagliare anche il lato intatto (20,3 mm) e rinunciare ai fori M3 (fissaggio con perni o fori M2 da ricavare: chiedere).
- Faccia componenti: la basetta è a doppia faccia, quindi si sceglie la faccia in modo che, guardando dall'alto con la USB-C verso di sé (in basso), il **lato intatto sia a sinistra** (colonna A).

## Griglia e convenzioni

Colonne A…H (A = lato intatto), righe 1…20 (riga 1 = anteriore, USB-C). Coordinate in mm dall'angolo **anteriore-sinistro** (lato componenti): x verso destra, y verso il posteriore. Centro di A1 = (3,49; 5,87), passo 2,54.

```
           A       B       C       D       E       F       G       H
  20  |   .       .       .       .       .       .      C3-     C3+   |  <- posteriore
  19  | ~STDBY    .       .       .       .     ~GNDB    -GND   -VBAT  |
  18  |  R8*     ~DI      .       .       .      -GND    C4      C4    |
  17  |   R8      R5      .       .      -GND    R11*     .     ~VIBP  |
  16  |   R9     R5*    ~GNDA    -GND    -GND    R11     R10     R10*  |
  15  |  R9*      .     ~OUTM    R1*     C1-     C1+      .     -VBAT  |
  14  |  R7*      .      -GND     R1      .     ~LEDP     R4     R4*   |
  13  |   R7      .      Q2E     Q2B     Q2C     Q1C     Q1B     Q1E   |
  12  |   R6      .      R2*      R2     R3*      .       R3    ~OUTP  |
  11  |  R6*    (ant)   (ant)   (ant)   (ant)   (ant)    D1K     D1A*  |
  10  | ~CHRG   (ant)   (ant)   (ant)   (ant)   (ant)    -5V      .    |
   9  |  ~SW     SM7    (ant)   (ant)   (ant)   (ant)    -5V     SM8   |
   8  | ~VIBIN   SM6      .       .       .       .      -5V     SM9   |
   7  | ~ENCB    SM5      .       .       .       .      -5V     SM10  |
   6  | ~ENCA    SM4      .       .       .       .      -5V     SM11  |
   5  |   .      SM3      .       .       .       .      -5V     SM12  |
   4  |   C2     SM2      .       .       .       .      -5V     SM13  |
   3  |   C2     SM1      .       .       .       .      -5V    SM3V3  |
   2  |   .      SMRX     .       .       .       .      -5V    SMGND  |
   1  |   .      SMTX     .       .       .       .      -5V     SM5V  |  <- anteriore (USB-C)
```

`R1*` = foro su cui poggia il corpo della resistenza in piedi, `~NET` = filo verso l'alto, `-NET` = sola pista sul retro, `SMxx` = pin della SuperMini, `(ant)` = zona antenna.

## SuperMini

- Pin sulle colonne **B** (TX, RX, 1…7) e **H** (5V, GND, 3V3, 13…8), righe 1-9 (file a 15,24 = 6 fori). **Prima di saldare** verificare sulla serigrafia che, con la USB-C verso di sé, la fila **5V/GND/3V3 sia a destra**; se è a sinistra usare `--specchia` (SVG `*_specchiata.svg`) e girare la basetta (lato intatto a destra).
- Montaggio: **strip maschio standard 2 x 1x9** (plastica 2,5 mm lasciata come distanziale): pin corti nella SuperMini, lunghi nella millefori, tagliati sotto a ~1 mm. Altezza: **6,7 mm** sopra la millefori (2,5 + PCB 1,0 + USB-C 3,2). Robusto per inserire il cavo USB, ispezionabile, lascia passare le piste sotto. Scartati: saldatura diretta a filo (le gambe della USB-C sporgono ~1 mm sotto la SuperMini e non resta posto per le piste) e strip femmina (13 mm, più fragile).
- PCB della SuperMini: x 4,65-22,65, y 4,28-27,78. **USB-C**: x 9,2-18,1 (centro 13,65), fronte della presa a **y ≈ 0,8** (con sporgenza 3,5 misurata; 3,1 se la sporgenza fosse 1,2): la presa resta **0,8 mm dietro** il bordo della millefori, che non si può accorciare (foro M3 a y 2). Centro della presa ~5,1 mm sopra la faccia superiore della millefori.
- Sotto la SuperMini nessun componente: solo le piste del 5V (colonna G) e i fili sotto la scheda.
- **Antenna** (fine della SuperMini, centro-sinistra): zona x 4,8-17,8, y 24,2-32,5 (righe 9-11, colonne B-F) **senza piazzole usate, piste o corpi**; elettrolitici a ≥ 10 mm (C1 a 11,3, C3 a 24,5). I fili sotto la scheda passano **lungo i bordi** (colonne A e H), non sotto l'antenna.

## Componenti

| Rif. | Valore | Fori | Funzione |
|------|--------|------|----------|
| SM | ESP32-S3 SuperMini | B1-B9, H1-H9 | |
| D1 | **1N5817** Schottky 1 A, DO-41, in piedi | corpo H11 = **anodo** (OUT+), piedino ripiegato in G11 = **catodo** (fascia in alto) | protezione: la USB della SuperMini non arriva alla cella |
| Q1 | S8550 PNP | E = H13, B = G13, C = F13, **faccia piatta verso il posteriore** | interruttore anello |
| Q2 | 2N3904 NPN | E = C13, B = D13, C = E13, **faccia piatta verso l'anteriore** | driver di Q1 |
| R1 | 4,7 kΩ | D15 / D14 | GPIO9 → base Q2 |
| R2 | 10 kΩ | C12 / D12 | base Q2 → GND |
| R3 | 680 Ω | E12 / G12 (piedino lungo sopra F12, libero) | collettore Q2 → base Q1 |
| R4 | 10 kΩ | H14 / G14 | base-emettitore Q1 |
| R5 | 330 Ω | B16 / B17 | serie al dato DI |
| C1 | 47 µF 16 V elettrolitico 5 x 11 | + F15, − E15 | bulk anello |
| R10 / R11 | 220 kΩ / 220 kΩ | H16 / G16, F17 / F16 | partitore batteria |
| C2 | 100 nF ceramico | A3 (GPIO1) / A4 (GND della SuperMini) | filtro ADC, vicino al pin |
| C3 | **47-100 µF 10-16 V** elettrolitico 5 x 11 | + H20, − G20 | **motore vibrazione** |
| C4 | **100 nF** ceramico | H18 / G18 | **motore vibrazione** |
| R6 / R8 | 10 kΩ | A11 / A12, A18 / A17 | serie CHRG / STDBY |
| R7 / R9 | 100 kΩ | A14 / A13, A15 / A16 | pull-up GPIO8 / GPIO10 a 3V3 |

Resistenze in piedi (corpo sul primo foro), altezze: elettrolitici 11,5 (massimo), resistenze e diodo ~10, TO-92 ~8, SuperMini 6,7, ceramici ~6, fili ~3. **Tutto ≤ 16**. Lato saldature ≤ 1,8 (piedini a ~1 mm, fili 30 AWG).

Pull-down 100 kΩ su IN della vibrazione: **non sulla millefori** (non c'è massa vicino a A8); va saldato tra IN e GND sul modulo **solo se** il motore ronza al boot (il modulo provato non ne ha avuto bisogno finora).

## Diodo D1: verso e conseguenze

`OUT+ (VBAT) ── |>|── pin 5V SuperMini`, anodo verso il TP4056. Con la USB della SuperMini collegata (caricamento firmware) il PC alimenta solo la SuperMini, mai la cella. Costo: ~0,3 V in meno al pin 5V (a 3,6 V di cella la SuperMini vede ~3,3 V e il 3V3 scende a ~3,2): **in firmware alzare la soglia di batteria scarica / spegnimento** di ~0,2 V. L'anello, il motore e il partitore restano su VBAT (prima del diodo); con la sola USB e la cella scollegata **anello e vibrazione non si accendono**.

## Fili

Verso l'alto (lato componenti), siliconico 26-28 AWG:

| Foro | Net | Verso |
|------|-----|-------|
| H12 | VBAT | TP4056 **OUT+** (24-26 AWG) |
| C15 | GND | TP4056 **OUT−** (24-26 AWG): **punto di massa comune** (C14-C15) |
| A10 | CHRG | TP4056 catodo LED rosso (pin 7) |
| A19 | STDBY | TP4056 catodo LED blu/verde (pin 6) |

Sotto la scheda (filo isolato 30 AWG, GND 26 AWG), dalla piazzola del pin della SuperMini alla piazzola indicata, lungo i bordi:

| Da (pin SM) | A | Net |
|-------------|---|-----|
| H2 (GND) | C14 e A4 | GND (due fili) |
| H3 (3V3) | A14 | 3V3 |
| H7 (GPIO10) | A16 | GPIO10 |
| H8 (GPIO9) | D15 | GPIO9 |
| H9 (GPIO8) | A12 | GPIO8 |
| B3 (GPIO1) | G16 | GPIO1 |
| B4 (GPIO2) | B16 | GPIO2 |

Il 5V va per pista: H1 → G1 … G11 (catodo di D1).

## Connettore verso la scocca: codino + connettore volante 2 x 5 con chiave

Un header 2 x 5 **diritto** sulla millefori con la spina Dupont è alto ~16,5 mm + 3-5 di curvatura dei fili ≈ **20 mm**, oltre i 16 disponibili; angolato sporgerebbe ~20 mm oltre il bordo. Soluzione: **9 fili saldati sulla millefori** (codino, 15-20 cm) che finiscono in un **alloggiamento Dupont 2 x 5 femmina**; dal lato scocca un alloggiamento 2 x 5 maschio. **Chiave**: posizione 5 tappata nel femmina e pin 5 tagliato nel maschio (girata di 180° la posizione tappata cade sul pin 6: non entra). Segno di vernice sul lato del pin 1.

| Pin | Segnale | Foro sulla millefori |
|-----|---------|----------------------|
| 1 | encoder A (GPIO4) | A6 |
| 2 | encoder B (GPIO5) | A7 |
| 3 | switch encoder (GPIO7) | A9 |
| 4 | GND encoder (comune C + secondo terminale dello switch) | C16 |
| 5 | **chiave** | - |
| 6 | vibrazione IN (GPIO6) | A8 |
| 7 | anello + commutato (LED+) | F14 |
| 8 | anello DI (dopo la 330 Ω) | B18 |
| 9 | vibrazione VCC (VBAT) | H17 |
| 10 | GND anello + vibrazione | F19 |

Dispari su una fila, pari sull'altra. Alternativa a profilo basso, se si accetta un acquisto: box header IDC 2 x 5 schermato + cavo piatto (~13 mm, chiave intrinseca), ma occupa ~24 fori: non sta.

## Fissaggio

2 fori **M3 originali** sul lato intatto, **da misurare** (valori del modello: Ø3,2, centri a (2,0; 2,0) e (2,0; 58,0)). Viti M3 a testa bassa (ISO 7380 / DIN 7985, testa Ø5,5); nessuna piazzola usata entro 3,65 mm. Il lato destro (tagliato) va appoggiato su una battuta o su 1-2 perni del portaschede (fori liberi: B12-B15, C17-C20, D17-D20, E18-E20): da definire con design-3d.

## Ordine di saldatura

1. Taglio e pulizia; segnare A1 sulla faccia componenti.
2. Prova del pinout dei TO-92 col tester (vedi `archivio_8x13/README.md`, stessa procedura).
3. Piste del retro (`lato_saldature.svg`, specchiato), compresa la colonna G del 5V **prima** della SuperMini (dopo non si raggiunge più dall'alto).
4. Strip maschio e **SuperMini** (USB-C in avanti, controllo della fila 5V a destra).
5. Resistenze, D1 (fascia in alto, piedino in G11), TO-92, ceramici, elettrolitici.
6. Fili sotto la scheda lungo i bordi; fili verso il TP4056; codino.
7. Controlli col tester: VBAT-GND ~440 kΩ (partitore), 5V-GND aperto, VBAT → 5V ≈ 0,15-0,3 V in prova diodi (al contrario aperto), LED+ isolato da VBAT e GND, nessun corto tra piazzole vicine (53 coppie).
8. Prima accensione con alimentatore limitato (3,7 V, 100 mA) su OUT+/OUT−; poi la USB della SuperMini.
