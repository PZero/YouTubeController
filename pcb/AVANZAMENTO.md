# Avanzamento PCB (JLCPCB + PCBA)

## Passo 0 - strumenti e parti (fatto)
- KiCad 10.0.6: `C:\Users\fnico\AppData\Local\Programs\KiCad\10.0\bin\` (`kicad-cli.exe`, `python.exe` con pcbnew).
- `tools/jlc_cerca.py "parola"`: cerca nel catalogo JLCPCB (Basic/Extended, stock, prezzo) via API pubblica del sito.
- Scelte (tutte Basic, verificate con l'API il 2026-10-15):
  R 330 C17630, 2k2 C17520, 4k7 C17673, 10k C17414, 100k C149504, 220k C17556 (0805);
  C 100 nF 0805 C49678; bulk 100 uF 6,3 V X5R 1206 C15008 (ring e motore);
  Q2 NPN MMBT3904 C20526; Q1 **P-MOSFET AO3401A C15127 al posto del S8550** (e' Basic, S8550 e' Extended; Vds(on) ~0,1 V invece di 0,3-0,6 V di Vce_sat, nessuna corrente di base; stessa topologia con Q2);
  D1 SS14 SMA C2480.
- Con il MOSFET: R3 (Q2 collettore -> gate) 680 -> 2,2 k e **C5 100 nF gate-source** = avviamento lento (limita l'inrush del bulk ceramico 100 uF a ~2 A; con ceramico, senza questo, la protezione della cella potrebbe scattare). Vgs a regime = -VBAT*10k/(10k+2k2) = -3,0 V a 3,7 V (-2,7 V a 3,3 V): sotto la soglia piena (Rds 85 mOhm @ -2,5 V).

## Passo 1 - generatore, posizionamento, instradamento (fatto)
- `netlist_pcb.py` (netlist + distinta con LCSC), `layout_opt.py` (posizionamento automatico, seme 2) -> `layout_pcb.py`,
  `genera_pcb.py` (footprint, router a griglia 2 strati, scrittura .kicad_pcb/.kicad_pro), `etichette_pcb.py` (serigrafia, ordine delle net).
- Comandi: `python layout_opt.py 2 100000` ; `python genera_pcb.py` ; DRC: `kicad-cli pcb drc --refill-zones --save-board --severity-all -o drc.rpt kicad/youtube_controller.kicad_pcb`
- Coordinate: KiCad y = -y_doc (fronte USB-C in basso, come la millefori); Gerber/CPL positivi.
- Stato: tutte le 20 net instradate. Manca: DRC pulito, serigrafia, export JLCPCB (gerber, BOM, CPL, render), costi.

## Passo 2 - DRC ed export (fatto, 2026-10-15)
- Layout finale: `python layout_opt.py 6 120000` (XMAX 19,5: componenti a >= 3 mm dal bordo destro, per evitare i bordi di processo di JLCPCB e per i fermi a C) poi `python genera_pcb.py`.
- DRC: `kicad-cli pcb drc --refill-zones --save-board --severity-all -o drc.rpt kicad/youtube_controller.kicad_pcb` -> **0 violazioni, 0 non connessi** (regole in .kicad_pro: clearance min 0,127, foro min 0,3, anello 0,13, bordo rame 0,3; progetto con 0,2/0,25 di margine). Nessuno schematico (ERC non applicabile): la netlist sta in `netlist_pcb.py`, verificata a mano contro millefori.py.
- Export: `python esporta_jlcpcb.py` -> `jlcpcb/youtube_controller_gerber.zip` (Gerber + drill PTH/NPTH), `jlcpcb/BOM.csv`, `jlcpcb/CPL.csv`, `jlcpcb/render/fronte.png|retro.png`.
- Scheda 22,54 x 60, 2 strati, 1,6 mm, massa su B.Cu, keepout antenna (x 7,0-17,8 / 4,8-7,0, y 24,2-32,5) su entrambi gli strati, tutti i componenti SMD sul lato alto, nessuno sotto. Fori M3 (2;2) e (2;58); SuperMini: fori B1..B9 (x 6,03) e H1..H9 (x 21,27), pin 1 = B1 (TX, quadrato) vicino al fronte; J1 2x5 (pin 1 quadrato in basso a sinistra, dispari a sinistra, pari a destra; pin 5 = chiave, foro presente e non collegato); J2 1x4 (OUT+, OUT-, CHRG, STDBY).
- Da fare nell'anteprima JLCPCB: rotazioni di Q1, Q2 (SOT-23, +180 applicato) e polarita' di D1 (SS14, banda = catodo = lato 5V, verso la SuperMini/fronte... vedi render). Se sbagliate, correggere ROT_OFF in esporta_jlcpcb.py.
- Aperti: footprint SMD "YTC" custom (non in libreria KiCad) ; verificare la fila 5V della SuperMini a destra (come millefori); altezza connettore J1 (header diritto + spina ~20 mm: usare angolato o fili saldati); inrush C1/C3 ceramici (soft start con C5/R3 da validare al banco).
