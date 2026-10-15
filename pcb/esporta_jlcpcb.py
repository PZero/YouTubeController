#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Esporta per JLCPCB: zip Gerber+drill, BOM.csv, CPL.csv, render. Richiede KiCad 10 (kicad-cli).
   Uso: python esporta_jlcpcb.py   (dopo genera_pcb.py e un DRC con --refill-zones --save-board)"""
import csv, os, shutil, subprocess, sys, zipfile, tempfile
QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
from netlist_pcb import PARTI
KCLI = os.environ.get("KICAD_CLI", r"C:\Users\fnico\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe")
PCB = os.path.join(QUI, "kicad", "youtube_controller.kicad_pcb")
OUT = os.path.join(QUI, "jlcpcb")
# correzione di rotazione KiCad -> libreria JLCPCB (DA VERIFICARE nell'anteprima JLCPCB)
ROT_OFF = {"SOT-23": 180, "D_SMA": 0, "R_0805": 0, "C_0805": 0, "C_1206": 0}

def run(*a):
    subprocess.run([KCLI, *a], check=True, stdout=subprocess.DEVNULL)

os.makedirs(OUT, exist_ok=True)
tmp = tempfile.mkdtemp()
run("pcb", "drc", "--refill-zones", "--save-board", "-o", os.path.join(tmp, "drc.rpt"), PCB)
run("pcb", "export", "gerbers", "--layers", "F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts",
    "--no-protel-ext", "--subtract-soldermask", "-o", tmp + os.sep, PCB)
run("pcb", "export", "drill", "--format", "excellon", "--excellon-units", "mm", "--excellon-zeros-format", "decimal",
    "--excellon-separate-th", "-o", tmp + os.sep, PCB)
zp = os.path.join(OUT, "youtube_controller_gerber.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(os.listdir(tmp)):
        if f.endswith((".gbr", ".drl")) and "map" not in f:
            z.write(os.path.join(tmp, f), f)
run("pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "front", "--smd-only", "-o", os.path.join(tmp, "pos.csv"), PCB)
rows = list(csv.DictReader(open(os.path.join(tmp, "pos.csv"), encoding="utf-8")))
with open(os.path.join(OUT, "CPL.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
    for r in rows:
        rot = (float(r["Rot"]) + ROT_OFF[r["Package"]]) % 360
        w.writerow([r["Ref"], "%.4fmm" % float(r["PosX"]), "%.4fmm" % float(r["PosY"]), "Top", "%d" % round(rot)])
# BOM raggruppata
gr = {}
for ref, (fp, val, lcsc, desc) in PARTI.items():
    gr.setdefault((val, fp, lcsc, desc), []).append(ref)
def key(r): return (r[0][0], int(r[1:]))
with open(os.path.join(OUT, "BOM.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    for (val, fp, lcsc, desc), refs in sorted(gr.items(), key=lambda kv: min(kv[1], key=key)[0] + "%03d" % key(min(kv[1], key=key))[1]):
        w.writerow([val, ",".join(sorted(refs, key=key)), fp, lcsc])
shutil.rmtree(tmp)
print("scritti:", os.listdir(OUT))
