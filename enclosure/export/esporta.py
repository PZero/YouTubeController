#!/usr/bin/env python3
"""Esporta i piatti di stampa (Bambu Lab A1 mini, 180 x 180, senza AMS: un colore per piatto)
in 3MF e prepara il pacchetto zip per la stampa.

Uso (dalla radice del repo o da qualsiasi cartella):
    python enclosure/export/esporta.py            # tutto (3MF in out/, zip in enclosure/export/)
    python enclosure/export/esporta.py --solo-prova
    python enclosure/export/esporta.py --solo 05 03   # rigenera solo i piatti indicati (prefisso del file) e ricompone lo zip

Richiede solo OpenSCAD (riga di comando) e la libreria standard di Python.
I 3MF intermedi vanno in enclosure/export/out/ (esclusa da git); lo zip finale in enclosure/export/.
Il LEGGIMI.md dello zip viene generato qui, con pesi e lunghezze di filamento calcolati dai volumi.
"""
import argparse
import math
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

QUI = Path(__file__).resolve().parent
ENCLOSURE = QUI.parent
REPO = ENCLOSURE.parent
SCAD = ENCLOSURE / "youtube_control.scad"
OUT = QUI / "out"
ZIP_STAMPA = QUI / "YouTubeController_stampa_A1mini.zip"
BED = 180.0          # piatto A1 mini
MARGINE = 5.0        # margine minimo dal bordo del piatto
PLA_DENS = 1.24      # g/cm3
FIL_D = 1.75         # mm
G_PER_M = PLA_DENS * math.pi * (FIL_D / 20) ** 2 * 100   # g per metro di filamento (~2,98)

# ordine = ordine di stampa consigliato. Un colore per piatto (senza AMS).
# file, plate in youtube_control.scad, colore, descrizione, gruppo, strato, pareti, riempimento, brim, nota di orientamento
PIATTI = [
    ("01_bianco_diffusore", 4, "bianco", "diffusore dell'anello LED", "completo",
     "0,20", "2", "100 % concentrico", "no",
     "Faccia a vista sul piatto (sottile 1 mm = 5 strati). SOLO per questo pezzo. PLA bianco opaco/naturale, non silk, non trasparente"),
    ("02_grigio_prova_tolleranze", 5, "grigio", "anelli di prova della manopola + diffusore di prova + tassello con sede anello LED", "prova",
     "0,20", "3", "15 %", "no",
     "Tassello e diffusore con la faccia a vista sul piatto, anelli in piedi. Il diffusore di prova serve solo a provare lo scatto: in grigio non fa luce"),
    ("03_nero_scocca", 1, "nero", "scocca", "completo",
     "0,20", "3", "15 % gyroid", "5 mm",
     "Faccia superiore sul piatto, sede del modulo vibrazione e ganci dell'anello verso l'alto. Nessun supporto: ponti brevi (<= 6 mm) e labbri di 1 mm"),
    ("04_nero_fondo_portaschede", 2, "nero", "fondo e portaschede", "completo",
     "0,20", "3", "15 %", "no",
     "Tutto in piano, nessun supporto. Svasature e scritte RST/BOOT sul lato a contatto col piatto. Ganci della SuperMini: 'Pareti precise' attivo"),
    ("05_rame_manopola_pannelli", 3, "rame", "manopola e 2 pannelli laterali", "completo",
     "0,16", "3", "20 %", "no",
     "Manopola capovolta (faccia superiore sul piatto), pannelli con la faccia esterna sul piatto. 'Pareti precise' attivo"),
]
DEFINE_COMUNI = ['mode="print"', 'part="all"', 'led_ring=true', 'diff_mode="insert"']


def trova_openscad():
    cand = [os.environ.get("OPENSCAD", ""),
            shutil.which("openscad.com") or "", shutil.which("openscad") or "",
            r"C:\Program Files\OpenSCAD\openscad.com",
            "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD", "/usr/bin/openscad"]
    for c in cand:
        if c and Path(c).exists():
            return c
    sys.exit("OpenSCAD non trovato: installarlo o impostare la variabile OPENSCAD")


def esporta(openscad, plate, dest):
    cmd = [openscad, "-o", str(dest)]
    for d in DEFINE_COMUNI + [f"plate={plate}"]:
        cmd += ["-D", d]
    cmd.append(str(SCAD))
    r = subprocess.run(cmd, capture_output=True, text=True)
    log = r.stdout + r.stderr
    if r.returncode != 0 or not dest.exists() or "ERROR" in log:
        sys.exit(f"Errore OpenSCAD per {dest.name}:\n{log}")


def misura_3mf(path):
    """Ingombro e volume della mesh contenuta nel 3MF (mm, mm3)."""
    with zipfile.ZipFile(path) as z:
        nome = next(n for n in z.namelist() if n.endswith(".model"))
        xml = z.read(nome).decode("utf-8")
    v = [tuple(float(a) for a in m) for m in
         re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', xml)]
    t = [tuple(int(a) for a in m) for m in
         re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', xml)]
    mn = [min(p[i] for p in v) for i in range(3)]
    mx = [max(p[i] for p in v) for i in range(3)]
    vol = 0.0
    for a, b, c in t:
        (ax, ay, az), (bx, by, bz), (cx, cy, cz) = v[a], v[b], v[c]
        vol += (ax * (by * cz - bz * cy) - ay * (bx * cz - bz * cx) + az * (bx * cy - by * cx)) / 6
    return mn, mx, abs(vol)


def leggimi_md(misure):
    """LEGGIMI.md dello zip (breve). misure: nome -> (size, volume mm3)."""
    def peso(nome):
        return misure[nome][1] / 1000 * PLA_DENS if nome in misure else float("nan")

    g_bianco = peso("01_bianco_diffusore")
    # diffusore: 100 % pieno, quindi il peso e' quasi esatto; margine per skirt/linea di spurgo
    g_b_marg = g_bianco + 0.5
    m_b = g_b_marg / G_PER_M
    righe = []
    for nome, plate, colore, descr, gruppo, strato, pareti, riemp, brim, nota in PIATTI:
        g = peso(nome)
        righe.append(f"| `{nome}.3mf` | {colore.upper()} | {descr} | {strato} | {pareti} | {riemp} | {brim} | <= {g:.0f} g |")
    tab = "\n".join(righe)
    return f"""# YouTubeController - pacchetto di stampa (Bambu Lab A1 mini, PLA, un colore per piatto)

Un `.3mf` per piatto, pezzi gia' orientati e disposti entro 170 x 170 mm. Il numero nel nome e' l'ordine di stampa.
Nessun supporto su nessun piatto. Profilo di base: "0.20mm Standard @BAMBU A1M", ugello 0,4, filamento PLA.

## Pezzi per colore

| Colore | Pezzi | Perche' |
|--------|-------|---------|
| BIANCO | diffusore dell'anello LED (SOLO questo) | l'unico pezzo che deve far passare la luce |
| NERO | scocca, fondo, portaschede | corpo scuro: l'anello luminoso e il rame risaltano, le parti interne spariscono |
| RAME | manopola, 2 pannelli laterali a feritoie | un solo accento caldo, coordinato tra manopola e feritoie |
| GRIGIO | solo piatto di prova | filamento "di scarto" per le prove, non entra nel prodotto finale |
| ARGENTO | non usato | (alternativa: pannelli in argento invece che in rame) |

## Ordine di stampa e impostazioni

| File | Colore | Pezzi | Strato | Pareti | Riempimento | Brim | PLA (limite sup.) |
|------|--------|-------|--------|--------|-------------|------|-------------------|
{tab}

Orientamento (gia' nei file, non girare nulla):
""" + "\n".join(f"- `{n}`: {nota}." for n, _, _, _, _, _, _, _, _, nota in PIATTI) + f"""

## Diffusore bianco: quanto filamento serve
- Peso del pezzo (100 % pieno): **circa {g_bianco:.1f} g**; con margine per skirt/spurgo **circa {g_b_marg:.1f} g = {m_b:.2f} m** di filamento da 1,75 mm (~{m_b * 100:.0f} cm).
- Va stampato **per primo**, cosi' si sa subito se l'avanzo di bianco basta. Se lo scatto nella scocca risulta lasco o duro, regolare `diff_c` / `diff_snap` e ristampare (servira' altro bianco): per limitare il rischio si puo' provare lo scatto con il diffusore grigio del piatto 02 (non fa luce, ma ha la stessa forma).
- Il bianco serve **solo** per questo pezzo.

Se il bianco non c'e' o non basta: in **argento** (pigmento metallico) o **grigio** la luce passa quasi per niente a 1 mm. Alternative: (a) corona aperta, cioe' non montare il diffusore (i LED restano visibili nella feritoia e la polvere entra); (b) diffusore piu' sottile (`diff_t = 0.6` e rigenerare scocca + diffusore) in un colore chiaro; (c) stampa a vaso (una sola parete) in un colore chiaro.

## Note
- Prima della scocca stampare il piatto 02: gli anelli di prova danno il gioco da riportare in `knurl_fit` (manopola) e il tassello prova lo scatto dell'anello.
- PLA: non lasciare al sole o in auto (oltre ~55 C si deforma). Caricare a temperatura ambiente.
- Modulo vibrazione: scorre dal davanti nella sede sotto la faccia superiore della scocca (a scocca capovolta) fino alla battuta e scatta dietro i due ganci; il retro piatto resta a contatto con la faccia.
- Sorgenti parametrici (OpenSCAD) nel repository, cartella `enclosure/`. Licenza MIT (vedi `LICENSE`).
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo-prova", action="store_true")
    ap.add_argument("--solo", nargs="+", metavar="NN", help="rigenera solo i piatti con questo prefisso; gli altri 3MF in out/ restano")
    args = ap.parse_args()

    openscad = trova_openscad()
    OUT.mkdir(parents=True, exist_ok=True)
    # ripulisce i 3MF vecchi con nomi diversi
    for f in OUT.glob("*.3mf"):
        if f.stem not in {p[0] for p in PIATTI}:
            f.unlink()
    errori, misure = [], {}
    for nome, plate, colore, descr, gruppo, *_ in PIATTI:
        if args.solo_prova and gruppo != "prova":
            continue
        dest = OUT / f"{nome}.3mf"
        if args.solo and not any(nome.startswith(n) for n in args.solo):
            if dest.exists():                      # non rigenerato: si riusano le misure del file esistente
                mn, mx, vol = misura_3mf(dest)
                misure[nome] = ([mx[i] - mn[i] for i in range(3)], vol)
            continue
        print(f"- {dest.name} [{colore}]: {descr} ...", flush=True)
        esporta(openscad, plate, dest)
        mn, mx, vol = misura_3mf(dest)
        size = [mx[i] - mn[i] for i in range(3)]
        ok = size[0] <= BED - 2 * MARGINE and size[1] <= BED - 2 * MARGINE and size[2] <= BED and abs(mn[2]) < 0.01
        if not ok:
            errori.append(nome)
        misure[nome] = (size, vol)
        print(f"  ingombro {size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm, "
              f"PLA pieno {vol / 1000 * PLA_DENS:.1f} g  {'OK' if ok else 'FUORI PIATTO'}")

    if args.solo_prova:
        return
    leggimi = OUT / "LEGGIMI.md"
    leggimi.write_text(leggimi_md(misure), encoding="utf-8")
    lic = REPO / "LICENSE"
    if not lic.exists():
        print("ATTENZIONE: LICENSE non trovato nella radice del repo")
    with zipfile.ZipFile(ZIP_STAMPA, "w", zipfile.ZIP_DEFLATED) as z:
        for nome, *_ in PIATTI:
            z.write(OUT / f"{nome}.3mf", f"{nome}.3mf")
        z.write(leggimi, "LEGGIMI.md")
        if lic.exists():
            z.write(lic, "LICENSE")
    print(f"- {ZIP_STAMPA.relative_to(REPO)} ({ZIP_STAMPA.stat().st_size // 1024} kB)")

    if errori:
        sys.exit(f"Pezzi fuori dal piatto: {', '.join(errori)}")
    print("Fatto: tutti i piatti entro", BED - 2 * MARGINE, "mm")


if __name__ == "__main__":
    main()
