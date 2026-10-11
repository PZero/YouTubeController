#!/usr/bin/env python3
"""Esporta i piatti di stampa (Bambu Lab A1 mini, 180 x 180) in 3MF e prepara gli zip.

Uso (dalla radice del repo o da qualsiasi cartella):
    python enclosure/export/esporta.py            # tutto
    python enclosure/export/esporta.py --solo-prova

Richiede solo OpenSCAD (riga di comando) e la libreria standard di Python.
I file generati vanno in enclosure/export/out/ (esclusa da git).
"""
import argparse
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
BED = 180.0          # piatto A1 mini
MARGINE = 5.0        # margine minimo dal bordo del piatto
PLA_DENS = 1.24      # g/cm3

# nome file, numero di "plate" in youtube_control.scad, descrizione, insieme
PIATTI = [
    ("00_prova_tolleranze", 5, "anelli di prova sede zigrinata + diffusore + tassello con sede anello LED", "prova"),
    ("01_scocca",           1, "scocca (faccia superiore sul piatto)", "completo"),
    ("02_fondo_portaschede_pannelli", 2, "fondo, portaschede, 2 pannelli laterali", "completo"),
    ("03_manopola_cappuccio", 3, "manopola, cappuccio pulsante, anelli di prova", "completo"),
    ("04_diffusore",        4, "diffusore anello LED (PLA bianco)", "completo"),
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo-prova", action="store_true")
    args = ap.parse_args()

    openscad = trova_openscad()
    OUT.mkdir(parents=True, exist_ok=True)
    righe, errori = [], []
    for nome, plate, descr, gruppo in PIATTI:
        if args.solo_prova and gruppo != "prova":
            continue
        dest = OUT / f"{nome}.3mf"
        print(f"- {dest.name}: {descr} ...", flush=True)
        esporta(openscad, plate, dest)
        mn, mx, vol = misura_3mf(dest)
        size = [mx[i] - mn[i] for i in range(3)]
        ok = size[0] <= BED - 2 * MARGINE and size[1] <= BED - 2 * MARGINE and size[2] <= BED and abs(mn[2]) < 0.01
        if not ok:
            errori.append(nome)
        righe.append((nome, size, vol, ok))
        print(f"  ingombro {size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm, "
              f"PLA pieno {vol / 1000 * PLA_DENS:.0f} g  {'OK' if ok else 'FUORI PIATTO'}")

    # file di accompagnamento
    impost = QUI / "IMPOSTAZIONI_STAMPA.md"
    lic = REPO / "LICENSE"
    leggimi = OUT / "LEGGIMI.txt"
    leggimi.write_text(
        "YouTubeController - scatola stampabile (Bambu Lab A1 mini, tutto in PLA)\n"
        "Controller fisico per YouTube: manopola (encoder) + pulsante, BLE HID verso iPad.\n\n"
        "File: un .3mf per piatto, pezzi gia' orientati e disposti entro 180 x 180.\n"
        "Stampare prima 00_prova_tolleranze. Impostazioni: IMPOSTAZIONI_STAMPA.md.\n"
        "Sorgenti parametrici (OpenSCAD) nel repository del progetto, cartella enclosure/.\n"
        "Licenza: MIT (vedi LICENSE).\n", encoding="utf-8")
    extra = [p for p in (impost, lic, leggimi) if p.exists()]
    if not lic.exists():
        print("ATTENZIONE: LICENSE non trovato nella radice del repo")

    gruppi = {"prova": ["prova"], "completo": ["prova", "completo"]}
    for zipnome, inclusi in gruppi.items():
        if args.solo_prova and zipnome != "prova":
            continue
        zpath = OUT / f"YouTubeController_{zipnome}.zip"
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for nome, _, _, gruppo in PIATTI:
                f = OUT / f"{nome}.3mf"
                if gruppo in inclusi and f.exists():
                    z.write(f, f.name)
            for p in extra:
                z.write(p, p.name)
        print(f"- {zpath.name} ({zpath.stat().st_size // 1024} kB)")

    if errori:
        sys.exit(f"Pezzi fuori dal piatto: {', '.join(errori)}")
    print("Fatto: tutti i piatti entro", BED - 2 * MARGINE, "mm")


if __name__ == "__main__":
    main()
