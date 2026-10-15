#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Millefori unica 8 x 20 con la ESP32-S3 SuperMini saldata sopra - YouTubeController.

Disposizione, piste sul retro, fili sotto la scheda, verifica automatica contro la
netlist (firmware/README.md) e generazione degli SVG 1:1. Solo libreria standard.

  python millefori.py              # deve dare "VERIFICA OK" e rigenera gli SVG
  python millefori.py --specchia   # se la fila 5V/GND/3V3 della SuperMini risulta a SINISTRA

Convenzioni (vista dal LATO COMPONENTI, anteriore in basso nei disegni):
  - colonne A..H da sinistra a destra; A = lato lungo INTATTO della 14x20 (fori M3 originali),
    H = lato tagliato;
  - righe 1..20 dall'ANTERIORE (riga 1: USB-C della SuperMini) al POSTERIORE;
  - x in mm dal bordo sinistro, y in mm dal bordo anteriore; A1 = foro anteriore-sinistro.
"""

import argparse
import math
import os
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

# =============================================================================
# PARAMETRI
# =============================================================================

COLONNE = "ABCDEFGH"
N_RIGHE = 20
PASSO = 2.54
# Millefori 40 x 60, 14 x 20 fori: margini dal bordo al centro del primo foro (DA MISURARE)
MARG_SX = 3.49                # lato lungo intatto: (40 - 13 x 2,54) / 2
MARG_DX = 1.27                # lato tagliato: taglio a meta' tra la colonna H e la successiva
MARG_Y = 5.87                 # lati corti intatti: (60 - 19 x 2,54) / 2
LARGH = MARG_SX + (len(COLONNE) - 1) * PASSO + MARG_DX     # 22,54
LUNG = 60.0
CORSIA = 21.5                 # larghezza libera nel portaschede (design-3d)

# Fori M3 originali sul lato intatto (DA MISURARE sulla scheda)
M3_X, M3_Y = 2.0, 2.0
D_M3, R_TESTA_M3 = 3.2, 2.75  # testa M3 a calotta (ISO 7380 / DIN 7985) Ø5,5
R_LIBERO = R_TESTA_M3 + 0.9   # nessuna piazzola usata sotto la testa della vite

# SuperMini (enclosure/dimensioni.md): pin a 1,59 dal bordo corto, file a 1,38 dal bordo lungo
SM_LUNG, SM_LARG = 23.5, 18.0
SM_PIN_BORDO = 1.59
SM_FILA_BORDO = 1.38
SM_USB_SPORG = 3.5            # 27,0 totale misurato - 23,5 PCB (1,2-3,5 secondo le fonti)
SM_HEADER = 2.5               # strip maschio standard: plastica 2,5 tra le due schede
SM_H = SM_HEADER + 1.0 + 3.2  # header + PCB + USB-C = 6,7 sopra la millefori
SM_RIGA1 = 1                  # riga dei pin 5V / TX
# Antenna (coordinate SuperMini: X dall'USB, Y dalla fila 5V), affid. C
ANT_X = (21.2, 23.4)
ANT_Y = (7.9, 14.9)
ANT_MARGINE = 3.0             # mm di rispetto laterale attorno all'antenna
ANT_RIGHE_LIBERE = 2          # righe libere oltre l'estremo antenna
DIST_ELETTROLITICO = 10.0     # mm minimi tra elettrolitici e antenna

H_MAX = 16.0                  # altezza max sopra il PCB (soffitto z 30, colonnine 3)
H_MAX_SALDATURE = 2.0
H_SALDATURE = 1.8             # piedini tagliati, ponticelli e fili sotto la scheda (30 AWG)
TOLLERANZA = 0.15
TOLLERANZA_FILO = 0.30        # un filo siliconico si piega

R_DIAM, R_H = 2.5, 10.0
D_DIAM, D_H = 2.7, 10.0       # 1N5817 DO-41 in piedi
TO92_LUNGO, TO92_PIATTO, TO92_TONDO, TO92_H = 2.3, 1.4, 2.3, 8.0
C_EL_DIAM, C_EL_H = 5.0, 11.5
C_CER_LUNGO, C_CER_SPESS, C_CER_H = 4.5, 2.5, 6.0
FILO_R, FILO_H = 0.55, 3.0

SPECCHIA = False


def _xy(nome):
    i = COLONNE.index(nome[0])
    r = int(nome[1:])
    x = MARG_SX + i * PASSO
    if SPECCHIA:
        x = LARGH - x
    return (x, MARG_Y + (r - 1) * PASSO)


def _mx(x):
    return LARGH - x if SPECCHIA else x


def fissaggi():
    return [{"nome": "M3 anteriore", "xy": (_mx(M3_X), M3_Y), "r": D_M3 / 2},
            {"nome": "M3 posteriore", "xy": (_mx(M3_X), LUNG - M3_Y), "r": D_M3 / 2}]


def sm_geometria():
    """Rettangolo del PCB SuperMini, posizione USB-C, rettangolo antenna."""
    x5v = _xy(f"H{SM_RIGA1}")[0]
    xtx = _xy(f"B{SM_RIGA1}")[0]
    y0 = _xy(f"H{SM_RIGA1}")[1] - SM_PIN_BORDO
    s = 1 if x5v > xtx else -1           # la Y della SuperMini va dalla fila 5V verso la fila TX
    bordo5v = x5v + s * SM_FILA_BORDO
    xs = sorted([bordo5v, bordo5v - s * SM_LARG])
    ax = sorted([bordo5v - s * ANT_Y[0], bordo5v - s * ANT_Y[1]])
    return {"pcb": (xs[0], y0, xs[1], y0 + SM_LUNG),
            "usb_y": y0 - SM_USB_SPORG,
            "usb_x": (bordo5v - s * 9.0 - 4.47, bordo5v - s * 9.0 + 4.47),
            "ant": (ax[0], y0 + ANT_X[0], ax[1], y0 + ANT_X[1])}


def zona_antenna():
    g = sm_geometria()
    a = g["ant"]
    y1 = g["pcb"][3] + ANT_RIGHE_LIBERE * PASSO + PASSO / 2 - 0.5 * PASSO
    # fino a meta' passo oltre l'ultima riga libera
    ultima = None
    for r in range(1, N_RIGHE + 1):
        if _xy(f"A{r}")[1] > g["pcb"][3]:
            ultima = r + ANT_RIGHE_LIBERE - 1
            break
    y1 = _xy(f"A{ultima}")[1] + PASSO / 2
    return ("R", a[0] - ANT_MARGINE, a[1] - PASSO / 2, a[2] + ANT_MARGINE, y1)


# =============================================================================
# DISPOSIZIONE
# =============================================================================

SM_PIN_H = ["5V", "GND", "3V3", "13", "12", "11", "10", "9", "8"]
SM_PIN_B = ["TX", "RX", "1", "2", "3", "4", "5", "6", "7"]


def comp_R(ref, valore, corpo, filo, nota=""):
    return {"ref": ref, "tipo": "R", "valore": valore, "nota": nota,
            "pin": {"corpo": corpo, "filo": filo}, "h": R_H}


def comp_TO92(ref, valore, centro, piatto, pinout="EBC"):
    n = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}[piatto]
    f = (-n[0], -n[1])
    sx = (-f[1], f[0])
    i, r = COLONNE.index(centro[0]), int(centro[1:])
    fori = [f"{COLONNE[i + sx[0] * k]}{r + sx[1] * k}" for k in (1, 0, -1)]
    return {"ref": ref, "tipo": "TO92", "valore": valore, "pin": {pinout[k]: fori[k] for k in range(3)},
            "piatto": piatto, "centro": centro, "pinout": pinout, "h": TO92_H}


def comp_filo(nome, foro, verso, colore, lungh, gruppo):
    return {"ref": "W_" + nome, "tipo": "filo", "valore": verso, "pin": {"1": foro}, "h": FILO_H,
            "colore_filo": colore, "lungh": lungh, "net_nome": nome, "gruppo": gruppo}


def costruisci():
    sm_pin = {}
    for k in range(9):
        sm_pin[SM_PIN_H[k]] = f"H{SM_RIGA1 + k}"
        sm_pin[SM_PIN_B[k]] = f"B{SM_RIGA1 + k}"
    comp = [
        {"ref": "SM", "tipo": "SM", "valore": "ESP32-S3 SuperMini su strip maschio 2 x 1x9", "pin": sm_pin, "h": SM_H},
        {"ref": "D1", "tipo": "D", "valore": "1N5817 Schottky 1 A (anodo = OUT+, catodo = pin 5V)",
         "pin": {"A": "H11", "K": "G11"}, "corpo": "H11", "h": D_H},
        # interruttore anello
        comp_TO92("Q1", "S8550 (PNP)", centro="G13", piatto="N"),
        comp_R("R4", "10k", corpo="H14", filo="G14", nota="base-emettitore Q1"),
        comp_R("R3", "680", corpo="E12", filo="G12", nota="collettore Q2 -> base Q1 (piedino lungo sopra F12)"),
        comp_TO92("Q2", "2N3904 (NPN)", centro="D13", piatto="S"),
        comp_R("R2", "10k", corpo="C12", filo="D12", nota="pull-down base Q2"),
        comp_R("R1", "4,7k", corpo="D15", filo="D14", nota="GPIO9 -> base Q2"),
        {"ref": "C1", "tipo": "C_el", "valore": "47 uF 16 V (bulk anello)", "pin": {"+": "F15", "-": "E15"}, "h": C_EL_H},
        comp_R("R5", "330", corpo="B16", filo="B17", nota="serie dato anello"),
        # partitore batteria
        comp_R("R10", "220k", corpo="H16", filo="G16", nota="partitore alto"),
        comp_R("R11", "220k", corpo="F17", filo="F16", nota="partitore basso"),
        {"ref": "C2", "tipo": "C_cer", "valore": "100 nF (filtro GPIO1)", "pin": {"1": "A3", "2": "A4"}, "h": C_CER_H},
        # vibrazione
        {"ref": "C3", "tipo": "C_el", "valore": "100 uF 10-16 V (motore)", "pin": {"+": "H20", "-": "G20"}, "h": C_EL_H},
        {"ref": "C4", "tipo": "C_cer", "valore": "100 nF (motore)", "pin": {"1": "H18", "2": "G18"}, "h": C_CER_H},
        # lettura carica: catena in colonna A
        comp_R("R6", "10k", corpo="A11", filo="A12", nota="serie CHRG"),
        comp_R("R7", "100k", corpo="A14", filo="A13", nota="pull-up GPIO8"),
        comp_R("R9", "100k", corpo="A15", filo="A16", nota="pull-up GPIO10"),
        comp_R("R8", "10k", corpo="A18", filo="A17", nota="serie STDBY"),
        # fili verso il TP4056
        comp_filo("OUTP", "H12", "TP4056 OUT+ (VBAT)", "rosso", "6-10 cm", "TP4056"),
        comp_filo("OUTM", "C15", "TP4056 OUT- (massa)", "nero", "6-10 cm", "TP4056"),
        comp_filo("CHRG", "A10", "TP4056 catodo LED rosso (pin 7)", "marrone/bianco", "6-10 cm", "TP4056"),
        comp_filo("STDBY", "A19", "TP4056 catodo LED blu/verde (pin 6)", "azzurro/bianco", "6-10 cm", "TP4056"),
        # codino verso la scocca (connettore volante 2x5)
        comp_filo("ENCA", "A6", "J1.1 encoder A", "giallo", "codino", "J1"),
        comp_filo("ENCB", "A7", "J1.2 encoder B", "verde", "codino", "J1"),
        comp_filo("SW", "A9", "J1.3 switch encoder", "blu", "codino", "J1"),
        comp_filo("GNDA", "C16", "J1.4 GND encoder (comune C + switch)", "nero", "codino", "J1"),
        comp_filo("VIBIN", "A8", "J1.6 vibrazione IN", "viola", "codino", "J1"),
        comp_filo("LEDP", "F14", "J1.7 anello + (LED+)", "arancione", "codino", "J1"),
        comp_filo("DI", "B18", "J1.8 anello DI", "bianco", "codino", "J1"),
        comp_filo("VIBP", "H17", "J1.9 vibrazione VCC (VBAT)", "rosso", "codino", "J1"),
        comp_filo("GNDB", "F19", "J1.10 GND anello + vibrazione", "nero", "codino", "J1"),
    ]
    tracce = [
        ("5V", "H1-G1-G2-G3-G4-G5-G6-G7-G8-G9-G10-G11"),
        ("ENC_A", "B6-A6"), ("ENC_B", "B7-A7"), ("VIB_IN", "B8-A8"), ("SW", "B9-A9"),
        ("VBAT", "H11-H12-H13-H14-H15-H16-H17-H18-H19-H20"),
        ("B_Q1", "G12-G13-G14"),
        ("C_Q2", "E12-E13"),
        ("B_Q2", "D12-D13-D14"),
        ("LED+", "F13-F14-F15"),
        ("GND", "C12-C13-C14-C15-C16-D16-E16-E15"),
        ("GND", "E16-E17-F17-F18-G18-G19-G20"),
        ("GND", "F18-F19"),
        ("GPIO1", "G16-F16"), ("GPIO1", "B3-A3"),
        ("DI", "B17-B18"),
        ("CHRG", "A10-A11"), ("GPIO8", "A12-A13"), ("3V3", "A14-A15"),
        ("GPIO10", "A16-A17"), ("STDBY", "A18-A19"),
    ]
    # fili isolati sotto la scheda (30 AWG; GND e 5V 26 AWG): dal pin della SuperMini al punto di arrivo
    fili_sotto = [
        ("GND", "H2", "C14"), ("GND", "H2", "A4"), ("3V3", "H3", "A14"), ("GPIO10", "H7", "A16"),
        ("GPIO9", "H8", "D15"), ("GPIO8", "H9", "A12"), ("GPIO1", "B3", "G16"), ("GPIO2", "B4", "B16"),
    ]
    return comp, tracce, fili_sotto


def netlist():
    return {
        "VBAT": ["W_OUTP.1", "D1.A", "Q1.E", "R4", "R10", "C3.+", "C4", "W_VIBP.1"],
        "5V": ["SM.5V", "D1.K"],
        "GND": ["SM.GND", "W_OUTM.1", "Q2.E", "R2", "R11", "C1.-", "C2", "C3.-", "C4", "W_GNDA.1", "W_GNDB.1"],
        "3V3": ["SM.3V3", "R7", "R9"],
        "LED+": ["Q1.C", "C1.+", "W_LEDP.1"],
        "DI": ["R5", "W_DI.1"],
        "GPIO2": ["SM.2", "R5"],
        "B_Q1": ["Q1.B", "R4", "R3"],
        "C_Q2": ["Q2.C", "R3"],
        "B_Q2": ["Q2.B", "R1", "R2"],
        "GPIO9": ["SM.9", "R1"],
        "GPIO1": ["SM.1", "R10", "R11", "C2"],
        "GPIO8": ["SM.8", "R6", "R7"],
        "CHRG": ["W_CHRG.1", "R6"],
        "GPIO10": ["SM.10", "R8", "R9"],
        "STDBY": ["W_STDBY.1", "R8"],
        "ENC_A": ["SM.4", "W_ENCA.1"],
        "ENC_B": ["SM.5", "W_ENCB.1"],
        "VIB_IN": ["SM.6", "W_VIBIN.1"],
        "SW": ["SM.7", "W_SW.1"],
    }


J1_PINOUT = [
    (1, "encoder A (GPIO4)"), (2, "encoder B (GPIO5)"), (3, "switch encoder (GPIO7)"),
    (4, "GND encoder (comune C + switch)"), (5, "CHIAVE (piedino tagliato / foro tappato)"),
    (6, "vibrazione IN (GPIO6)"), (7, "anello + commutato (LED+)"), (8, "anello DI (dopo 330)"),
    (9, "vibrazione VCC (VBAT)"), (10, "GND anello + vibrazione"),
]

COLORI = {
    "VBAT": "#d40000", "5V": "#ff4d4d", "GND": "#3a3a3a", "3V3": "#f781bf", "LED+": "#ff8c00", "DI": "#1a9850",
    "GPIO2": "#7fcf6f", "B_Q1": "#e7298a", "C_Q2": "#8c510a", "B_Q2": "#d8b365", "GPIO9": "#7570b3",
    "GPIO1": "#1f78b4", "GPIO8": "#17becf", "CHRG": "#9edae5", "GPIO10": "#9467bd", "STDBY": "#c5b0d5",
    "ENC_A": "#bcbd22", "ENC_B": "#6b8e23", "VIB_IN": "#8a2be2", "SW": "#4169e1",
}
DESCR_NET = {
    "VBAT": "VBAT = OUT+ TP4056 (3,0-4,2 V)", "5V": "pin 5V SuperMini (dopo D1)", "GND": "massa comune",
    "3V3": "3V3 SuperMini", "LED+": "anello + commutato", "DI": "dato anello (dopo 330)", "GPIO2": "GPIO2",
    "B_Q1": "base Q1", "C_Q2": "collettore Q2", "B_Q2": "base Q2", "GPIO9": "GPIO9 comando anello",
    "GPIO1": "GPIO1 partitore", "GPIO8": "GPIO8 CHRG", "CHRG": "CHRG (catodo LED rosso)", "GPIO10": "GPIO10 STDBY",
    "STDBY": "STDBY (catodo LED blu/verde)", "ENC_A": "encoder A (GPIO4)", "ENC_B": "encoder B (GPIO5)",
    "VIB_IN": "vibrazione IN (GPIO6)", "SW": "switch encoder (GPIO7)",
}
NET_FILO = {"OUTP": "VBAT", "OUTM": "GND", "GNDA": "GND", "GNDB": "GND", "VIBP": "VBAT", "LEDP": "LED+",
            "ENCA": "ENC_A", "ENCB": "ENC_B", "VIBIN": "VIB_IN"}


# =============================================================================
# GEOMETRIA
# =============================================================================

def valido(nome):
    try:
        return nome[0] in COLONNE and 1 <= int(nome[1:]) <= N_RIGHE
    except ValueError:
        return False


def adiacenti(a, b):
    ia, ra = COLONNE.index(a[0]), int(a[1:])
    ib, rb = COLONNE.index(b[0]), int(b[1:])
    return abs(ia - ib) + abs(ra - rb) == 1


def rett(x0, y0, x1, y1):
    return ("R", min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))


def corpi(c):
    t = c["tipo"]
    if t == "R":
        x, y = _xy(c["pin"]["corpo"])
        return [("C", x, y, R_DIAM / 2)]
    if t == "D":
        x, y = _xy(c["corpo"])
        return [("C", x, y, D_DIAM / 2)]
    if t == "filo":
        x, y = _xy(c["pin"]["1"])
        return [("C", x, y, FILO_R)]
    if t == "C_el":
        (x1, y1), (x2, y2) = _xy(c["pin"]["+"]), _xy(c["pin"]["-"])
        return [("C", (x1 + x2) / 2, (y1 + y2) / 2, C_EL_DIAM / 2)]
    if t == "C_cer":
        (x1, y1), (x2, y2) = _xy(c["pin"]["1"]), _xy(c["pin"]["2"])
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        if abs(x1 - x2) > abs(y1 - y2):
            return [rett(cx - C_CER_LUNGO / 2, cy - C_CER_SPESS / 2, cx + C_CER_LUNGO / 2, cy + C_CER_SPESS / 2)]
        return [rett(cx - C_CER_SPESS / 2, cy - C_CER_LUNGO / 2, cx + C_CER_SPESS / 2, cy + C_CER_LUNGO / 2)]
    if t == "TO92":
        cx, cy = _xy(c["centro"])
        p = c["piatto"]
        if SPECCHIA and p in "EW":
            p = "W" if p == "E" else "E"
        if p in "NS":
            y0, y1 = (cy - TO92_TONDO, cy + TO92_PIATTO) if p == "N" else (cy - TO92_PIATTO, cy + TO92_TONDO)
            return [rett(cx - TO92_LUNGO, y0, cx + TO92_LUNGO, y1)]
        x0, x1 = (cx - TO92_TONDO, cx + TO92_PIATTO) if p == "E" else (cx - TO92_PIATTO, cx + TO92_TONDO)
        return [rett(x0, cy - TO92_LUNGO, x1, cy + TO92_LUNGO)]
    if t == "SM":
        g = sm_geometria()
        return [("R",) + g["pcb"]]
    raise ValueError(t)


def compenetrazione(a, b):
    if a[0] == "C" and b[0] == "C":
        return a[3] + b[3] - math.hypot(a[1] - b[1], a[2] - b[2])
    if a[0] == "R" and b[0] == "C":
        a, b = b, a
    if a[0] == "C" and b[0] == "R":
        _, cx, cy, r = a
        _, x0, y0, x1, y1 = b
        if x0 <= cx <= x1 and y0 <= cy <= y1:
            return r + min(cx - x0, x1 - cx, cy - y0, y1 - cy)
        dx = max(x0 - cx, 0, cx - x1)
        dy = max(y0 - cy, 0, cy - y1)
        return r - math.hypot(dx, dy)
    _, ax0, ay0, ax1, ay1 = a
    _, bx0, by0, bx1, by1 = b
    return min(min(ax1, bx1) - max(ax0, bx0), min(ay1, by1) - max(ay0, by0))


def dentro(xy, r):
    return r[1] <= xy[0] <= r[3] and r[2] <= xy[1] <= r[4]


# =============================================================================
# VERIFICA
# =============================================================================

class Esito:
    def __init__(self):
        self.errori, self.avvisi, self.ok = [], [], []

    def controlla(self, cond, msg_ok, msg_err):
        (self.ok.append(msg_ok) if cond else self.errori.append(msg_err))


def verifica(comp, tracce, fili_sotto):
    e = Esito()
    refs = {c["ref"]: c for c in comp}
    nets = netlist()
    usati_sm = {t.split(".")[1] for ts in nets.values() for t in ts if t.startswith("SM.")}

    uso = {}
    for c in comp:
        for p, h in c["pin"].items():
            if not valido(h):
                e.errori.append(f"{c['ref']}.{p}: foro {h} fuori griglia")
                continue
            uso.setdefault(h, []).append(f"{c['ref']}.{p}")
    doppi = {h: v for h, v in uso.items() if len(v) > 1}
    e.controlla(not doppi, f"nessun foro usato due volte ({len(uso)} fori con piedino o filo)",
                f"fori usati due volte: {doppi}")

    archi = []
    for net, perc in tracce:
        fori = perc.split("-")
        for a, b in zip(fori, fori[1:]):
            if not (valido(a) and valido(b)):
                e.errori.append(f"pista {perc}: foro non valido")
            elif not adiacenti(a, b):
                e.errori.append(f"pista {perc}: {a}-{b} non adiacenti")
            else:
                archi.append((a, b, net))
    fori_pista = {h for a, b, _ in archi for h in (a, b)}
    for net, a, b in fili_sotto:
        if not (valido(a) and valido(b)):
            e.errori.append(f"filo sotto {net} {a}-{b}: foro non valido")

    padre = {}

    def trova(x):
        padre.setdefault(x, x)
        while padre[x] != x:
            padre[x] = padre[padre[x]]
            x = padre[x]
        return x

    for a, b, _ in archi:
        padre[trova(a)] = trova(b)
    for _, a, b in fili_sotto:
        padre[trova(a)] = trova(b)
    for h in uso:
        trova(h)

    def foro_di(term):
        ref, _, pin = term.partition(".")
        return refs[ref]["pin"][pin]

    gruppo_net = {}
    for net, terms in nets.items():
        polari = [t for t in terms if "." in t]
        gruppi = {trova(foro_di(t)) for t in polari}
        e.controlla(len(gruppi) == 1, f"net {net}: connessa",
                    f"net {net}: NON connessa ({', '.join(f'{t}@{foro_di(t)}' for t in polari)})")
        gruppo_net[net] = trova(foro_di(polari[0]))
    inv = {}
    for net, g in gruppo_net.items():
        inv.setdefault(g, []).append(net)
    corti = [v for v in inv.values() if len(v) > 1]
    e.controlla(not corti, "nessun corto tra net diverse", f"CORTO tra le net: {corti}")
    for c in comp:
        if c["tipo"] in ("R", "C_cer"):
            attese = sorted(n for n, terms in nets.items() for t in terms if t == c["ref"])
            trovate = sorted(inv[trova(h)][0] if trova(h) in inv else "(isolato)" for h in c["pin"].values())
            e.controlla(trovate == attese, f"{c['ref']} {c['valore']}: {' / '.join(attese)}",
                        f"{c['ref']}: collegato a {trovate}, atteso {attese}")
    for c in comp:
        for p, h in c["pin"].items():
            if c["tipo"] == "SM" and p not in usati_sm:
                if trova(h) in inv or h in fori_pista:
                    e.errori.append(f"SM.{p} ({h}) non usato ma collegato")
                continue
            if trova(h) not in inv:
                e.errori.append(f"{c['ref']}.{p} ({h}) non appartiene a nessuna net")
    for net, perc in tracce:
        reale = inv.get(trova(perc.split("-")[0]), ["(nessuna)"])[0]
        if reale != net:
            e.errori.append(f"pista {perc}: dichiarata {net}, collegata a {reale}")
    for net, a, b in fili_sotto:
        reale = inv.get(trova(a), ["(nessuna)"])[0]
        if reale != net:
            e.errori.append(f"filo sotto {a}-{b}: dichiarato {net}, collegato a {reale}")

    occupati = set(uso) | fori_pista
    # fissaggi
    for f in fissaggi():
        fx, fy = f["xy"]
        vicini = [h for h in occupati if math.hypot(_xy(h)[0] - fx, _xy(h)[1] - fy) < R_LIBERO]
        e.controlla(not vicini, f"{f['nome']} ({fx:.2f}; {fy:.2f}): nessuna piazzola usata entro {R_LIBERO:.2f} mm",
                    f"{f['nome']}: piazzole usate sotto la testa: {vicini}")
    # zona antenna
    za = zona_antenna()
    in_za = [h for h in occupati if dentro(_xy(h), za) and not (h in refs["SM"]["pin"].values())]
    e.controlla(not in_za, f"zona antenna ({za[1]:.1f}-{za[3]:.1f} x {za[2]:.1f}-{za[4]:.1f} mm): "
                f"nessuna piazzola, pista o piedino", f"zona antenna occupata: {sorted(in_za)}")
    corpi_za = [c["ref"] for c in comp if c["tipo"] != "SM" for s in corpi(c) if compenetrazione(s, za) > 0]
    e.controlla(not corpi_za, "zona antenna: nessun corpo", f"zona antenna: corpi {corpi_za}")
    # elettrolitici lontani dall'antenna
    ant = ("R",) + sm_geometria()["ant"]
    for c in comp:
        if c["tipo"] == "C_el":
            s = corpi(c)[0]
            d = -compenetrazione(s, ant)
            e.controlla(d >= DIST_ELETTROLITICO, f"{c['ref']} a {d:.1f} mm dall'antenna",
                        f"{c['ref']} a {d:.1f} mm dall'antenna (min {DIST_ELETTROLITICO})")
    # collisioni (in pianta)
    sag = [(c["ref"], c["tipo"], s) for c in comp for s in corpi(c)]
    sag += [(f["nome"], "vite", ("C", f["xy"][0], f["xy"][1], R_TESTA_M3)) for f in fissaggi()]
    coll = []
    for i in range(len(sag)):
        for j in range(i + 1, len(sag)):
            p = compenetrazione(sag[i][2], sag[j][2])
            tol = TOLLERANZA_FILO if "filo" in (sag[i][1], sag[j][1]) else TOLLERANZA
            if p > tol:
                coll.append(f"{sag[i][0]}/{sag[j][0]} ({p:.2f} mm)")
    e.controlla(not coll, f"nessuna collisione tra corpi (tolleranza {TOLLERANZA}, fili {TOLLERANZA_FILO})",
                f"collisioni: {coll}")
    fuori = []
    for c in comp:
        for s in corpi(c):
            box = (s[1] - s[3], s[2] - s[3], s[1] + s[3], s[2] + s[3]) if s[0] == "C" else s[1:]
            lim = 0.3 + (0.15 if c["tipo"] == "SM" else 0)
            if box[0] < -lim or box[1] < -lim or box[2] > LARGH + lim or box[3] > LUNG + lim:
                fuori.append(c["ref"])
    e.controlla(not fuori, "tutti i corpi entro il bordo", f"corpi oltre il bordo: {fuori}")
    alti = [f"{c['ref']} {c['h']}" for c in comp if c["h"] > H_MAX]
    e.controlla(not alti, f"altezze <= {H_MAX} mm (max {max(c['h'] for c in comp)})", f"oltre {H_MAX} mm: {alti}")
    e.controlla(H_SALDATURE <= H_MAX_SALDATURE, f"lato saldature {H_SALDATURE} <= {H_MAX_SALDATURE} mm",
                f"lato saldature troppo alto")
    g = sm_geometria()
    e.ok.append(f"USB-C: fronte della presa a y = {g['usb_y']:.2f} mm dal bordo anteriore "
                f"(negativo = sporge), x {g['usb_x'][0]:.2f}-{g['usb_x'][1]:.2f}")
    if LARGH > CORSIA:
        e.avvisi.append(f"larghezza {LARGH:.2f} mm > corsia {CORSIA} mm del portaschede: da rivedere con design-3d")
    e.avvisi.append(f"{len(fili_sotto)} fili isolati sotto la scheda (vedi README)")

    net_foro = {}
    for h in occupati:
        g_ = trova(h)
        if g_ in inv:
            net_foro[h] = inv[g_][0]
    vicine = sum(1 for h, n in net_foro.items() for h2, n2 in net_foro.items()
                 if h < h2 and adiacenti(h, h2) and n != n2)
    e.avvisi.append(f"{vicine} coppie di piazzole adiacenti di net diverse: stagnare con attenzione")
    return e, net_foro, archi


# =============================================================================
# USCITE
# =============================================================================

def etichetta(c, p):
    t = c["tipo"]
    if t == "R":
        return c["ref"] + ("*" if p == "corpo" else "")
    if t == "D":
        return f"D1{p}" + ("*" if c["pin"][p] == c["corpo"] else "")
    if t == "filo":
        return "~" + c["net_nome"]
    if t == "SM":
        return "SM" + p
    if t == "TO92":
        return c["ref"] + p
    return c["ref"] + p


def mappa_ascii(comp, net_foro):
    cella = {}
    for c in comp:
        for p, h in c["pin"].items():
            cella[h] = etichetta(c, p)
    za = zona_antenna()
    righe = ["        " + "".join(f"{c:^8}" for c in COLONNE) + "  (lato componenti)"]
    for r in range(N_RIGHE, 0, -1):
        s = f"  {r:>2}  |"
        for col in COLONNE:
            h = f"{col}{r}"
            if h in cella:
                t = cella[h]
            elif h in net_foro:
                t = "-" + net_foro[h][:5]
            elif dentro(_xy(h), za):
                t = "(ant)"
            else:
                t = "."
            s += f"{t:^8}"
        righe.append(s + "|" + ("  <- posteriore" if r == N_RIGHE else "  <- anteriore (USB-C)" if r == 1 else ""))
    righe.append("  legenda: R1* corpo della resistenza in piedi, ~NET filo verso l'alto, -NET solo pista, "
                 "SMxx pin della SuperMini, (ant) zona antenna libera")
    return "\n".join(righe)


def _t(x, y, testo, size, ancora="middle", colore="#000", peso="normal", extra=""):
    return (f'<text x="{x:.3f}" y="{y:.3f}" font-size="{size:.3f}" text-anchor="{ancora}" '
            f'font-family="Arial, Helvetica, sans-serif" font-weight="{peso}" fill="{colore}" {extra}>'
            f'{escape(testo)}</text>')


def disegna_scheda(lato, comp, net_foro, archi, fili_sotto, s, ox, oy, dettagli):
    spec = lato == "saldature"

    def X(x):
        return ox + s * ((LARGH - x) if spec else x)

    def Y(y):
        return oy + s * (LUNG - y)

    def R_(r, **kw):
        x0, y0, x1, y1 = r
        att = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
        return (f'<rect x="{min(X(x0), X(x1)):.3f}" y="{Y(y1):.3f}" width="{abs(x1 - x0) * s:.3f}" '
                f'height="{(y1 - y0) * s:.3f}" {att}/>')

    el = []
    lw = 0.06 * s
    el.append(R_((0, 0, LARGH, LUNG), fill="#e9dcc0" if not spec else "#d9c9a3", stroke="#555", stroke_width=f"{lw:.3f}"))
    za = zona_antenna()
    el.append(R_(za[1:], fill="#3399ff", fill_opacity="0.15", stroke="#3399ff", stroke_width=f"{lw:.3f}"))
    g = sm_geometria()
    if not spec:
        el.append(R_(g["pcb"], fill="#2d6a4f", fill_opacity="0.18", stroke="#2d6a4f", stroke_width=f"{1.5 * lw:.3f}",
                     stroke_dasharray=f"{0.5 * s:.3f},{0.3 * s:.3f}"))
        el.append(R_((g["usb_x"][0], g["usb_y"], g["usb_x"][1], g["usb_y"] + 7.3), fill="#999", fill_opacity="0.5",
                     stroke="#555", stroke_width=f"{lw:.3f}"))
        el.append(R_(g["ant"], fill="#3399ff", fill_opacity="0.5"))
    fs = 0.9 * s if dettagli else 1.1
    for col in COLONNE:
        x = _xy(col + "1")[0]
        el.append(_t(X(x), Y(LUNG) - 0.4 * s, col, fs, peso="bold"))
        el.append(_t(X(x), Y(0) + 0.4 * s + fs, col, fs, peso="bold"))
    for r in range(1, N_RIGHE + 1):
        y = _xy(f"A{r}")[1]
        el.append(_t(min(X(0), X(LARGH)) - 0.5 * s, Y(y) + fs * 0.35, str(r), fs, ancora="end"))
        el.append(_t(max(X(0), X(LARGH)) + 0.5 * s, Y(y) + fs * 0.35, str(r), fs, ancora="start"))
    if spec:
        for a, b, net in archi:
            (xa, ya), (xb, yb) = _xy(a), _xy(b)
            el.append(f'<line x1="{X(xa):.3f}" y1="{Y(ya):.3f}" x2="{X(xb):.3f}" y2="{Y(yb):.3f}" '
                      f'stroke="{COLORI.get(net, "#000")}" stroke-width="{1.05 * s:.3f}" stroke-linecap="round"/>')
    for col in COLONNE:
        for r in range(1, N_RIGHE + 1):
            h = f"{col}{r}"
            x, y = _xy(h)
            if spec:
                net = net_foro.get(h)
                el.append(f'<circle cx="{X(x):.3f}" cy="{Y(y):.3f}" r="{0.85 * s:.3f}" '
                          f'fill="{COLORI[net] if net else "#c98b4a"}" stroke="#7a4a1a" stroke-width="{0.03 * s:.3f}"/>')
            el.append(f'<circle cx="{X(x):.3f}" cy="{Y(y):.3f}" r="{0.45 * s:.3f}" fill="#fff" '
                      f'stroke="#666" stroke-width="{0.03 * s:.3f}"/>')
    if spec:
        for net, a, b in fili_sotto:
            (xa, ya), (xb, yb) = _xy(a), _xy(b)
            el.append(f'<line x1="{X(xa):.3f}" y1="{Y(ya):.3f}" x2="{X(xb):.3f}" y2="{Y(yb):.3f}" '
                      f'stroke="{COLORI.get(net, "#000")}" stroke-width="{0.35 * s:.3f}" '
                      f'stroke-dasharray="{0.8 * s:.3f},{0.4 * s:.3f}" stroke-linecap="round"/>')
            if dettagli:
                el.append(_t((X(xa) + X(xb)) / 2, (Y(ya) + Y(yb)) / 2 - 0.3 * s, f"filo {net}", 0.5 * s,
                             peso="bold", extra='stroke="#fff" stroke-width="0.6" paint-order="stroke"'))
    for f in fissaggi():
        fx, fy = f["xy"]
        el.append(f'<circle cx="{X(fx):.3f}" cy="{Y(fy):.3f}" r="{f["r"] * s:.3f}" fill="#222"/>')
        el.append(f'<circle cx="{X(fx):.3f}" cy="{Y(fy):.3f}" r="{R_TESTA_M3 * s:.3f}" fill="none" stroke="#222" '
                  f'stroke-width="{lw:.3f}" stroke-dasharray="{0.3 * s:.3f},{0.2 * s:.3f}"/>')
    for c in comp:
        t = c["tipo"]
        if spec:
            if dettagli:
                for p, h in c["pin"].items():
                    x, y = _xy(h)
                    el.append(_t(X(x), Y(y) - 0.95 * s, etichetta(c, p).replace("*", ""), 0.45 * s,
                                 extra='stroke="#fff" stroke-width="0.25" paint-order="stroke"'))
            continue
        if t == "SM":
            if dettagli:
                for p, h in c["pin"].items():
                    x, y = _xy(h)
                    el.append(_t(X(x), Y(y) + 0.2 * s, p, 0.55 * s, colore="#000", peso="bold",
                                 extra='stroke="#fff" stroke-width="0.5" paint-order="stroke"'))
                pc = g["pcb"]
                el.append(_t(X((pc[0] + pc[2]) / 2), Y((pc[1] + pc[3]) / 2), "SuperMini (sopra)", 0.7 * s,
                             colore="#2d6a4f", peso="bold"))
                el.append(_t(X((pc[0] + pc[2]) / 2), Y(g["usb_y"] + 3.5), "USB-C", 0.6 * s, peso="bold"))
            continue
        for sg in corpi(c):
            if t == "filo":
                net = NET_FILO.get(c["net_nome"], c["net_nome"])
                el.append(f'<circle cx="{X(sg[1]):.3f}" cy="{Y(sg[2]):.3f}" r="{0.75 * s:.3f}" fill="none" '
                          f'stroke="{COLORI.get(net, "#000")}" stroke-width="{0.25 * s:.3f}"/>')
                if dettagli:
                    el.append(_t(X(sg[1]), Y(sg[2]) - 0.95 * s, c["net_nome"], 0.5 * s, peso="bold",
                                 extra='stroke="#fff" stroke-width="0.25" paint-order="stroke"'))
                continue
            if sg[0] == "C":
                fill = {"R": "#d2b48c", "C_el": "#2b4c7e", "D": "#333"}.get(t, "#aaa")
                el.append(f'<circle cx="{X(sg[1]):.3f}" cy="{Y(sg[2]):.3f}" r="{sg[3] * s:.3f}" fill="{fill}" '
                          f'fill-opacity="0.75" stroke="#333" stroke-width="{lw:.3f}"/>')
            else:
                fill = {"TO92": "#222", "C_cer": "#e3a32b"}.get(t, "#aaa")
                el.append(R_(sg[1:], fill=fill, fill_opacity="0.55", stroke="#333", stroke_width=f"{lw:.3f}"))
        if t in ("R", "D"):
            hs = list(c["pin"].values())
            (xa, ya), (xb, yb) = _xy(hs[0]), _xy(hs[1])
            el.append(f'<line x1="{X(xa):.3f}" y1="{Y(ya):.3f}" x2="{X(xb):.3f}" y2="{Y(yb):.3f}" '
                      f'stroke="#555" stroke-width="{0.12 * s:.3f}"/>')
            if dettagli:
                xc, yc = _xy(c["pin"]["corpo"] if t == "R" else c["corpo"])
                el.append(_t(X(xc), Y(yc) + 0.1 * s, c["ref"], 0.6 * s, peso="bold", colore="#000" if t == "R" else "#fff"))
                if t == "R":
                    el.append(_t(X(xc), Y(yc) + 0.7 * s, c["valore"], 0.45 * s))
                else:
                    xk, yk = _xy(c["pin"]["K"])
                    el.append(_t(X(xk), Y(yk) - 0.95 * s, "K (fascia)", 0.45 * s, colore="#c00", peso="bold"))
        elif t == "TO92" and dettagli:
            for pin, h in c["pin"].items():
                x, y = _xy(h)
                el.append(_t(X(x), Y(y) + 0.2 * s, pin, 0.6 * s, peso="bold",
                             extra='stroke="#ff0" stroke-width="0.6" paint-order="stroke"'))
            sg = corpi(c)[0]
            el.append(_t(X((sg[1] + sg[3]) / 2), Y((sg[2] + sg[4]) / 2) - 0.9 * s, c["ref"], 0.55 * s,
                         colore="#fff", peso="bold"))
        elif t == "C_el" and dettagli:
            for p in ("+", "-"):
                x, y = _xy(c["pin"][p])
                el.append(_t(X(x), Y(y) + 0.3 * s, p, 0.9 * s, colore="#fff", peso="bold"))
            sg = corpi(c)[0]
            el.append(_t(X(sg[1]), Y(sg[2]) - 1.0 * s, c["ref"], 0.55 * s, colore="#fff", peso="bold"))
        elif t == "C_cer" and dettagli:
            sg = corpi(c)[0]
            el.append(_t(X((sg[1] + sg[3]) / 2), Y((sg[2] + sg[4]) / 2) + 0.2 * s, c["ref"], 0.55 * s, peso="bold"))
    if dettagli:
        el.append(_t(X((za[1] + za[3]) / 2), Y(za[4]) + 0.8 * s, "zona antenna: libera", 0.5 * s, colore="#1f5fbf",
                     peso="bold", extra='stroke="#fff" stroke-width="0.6" paint-order="stroke"'))
    return el


def svg_pagina(lato, comp, net_foro, archi, fili_sotto, percorso):
    spec = lato == "saldature"
    s_big = 3.0
    ox1, oy1 = 14.0, 40.0
    ox4, oy4 = 62.0, 40.0
    PW, PH = 200.0, oy4 + s_big * LUNG + 30.0
    el = ['<?xml version="1.0" encoding="UTF-8"?>',
          f'<svg xmlns="http://www.w3.org/2000/svg" width="{PW}mm" height="{PH}mm" viewBox="0 0 {PW} {PH}">',
          f'<rect x="0" y="0" width="{PW}" height="{PH}" fill="#fff"/>']
    titolo = ("LATO SALDATURE - VISTA SPECCHIATA (colonne H..A); tratteggi = fili isolati sotto la scheda"
              if spec else "LATO COMPONENTI - vista dall'alto (SuperMini tratteggiata, sopra la millefori)")
    el.append(_t(8, 9, "Millefori 8 x 20 con SuperMini - YouTubeController", 5, ancora="start", peso="bold"))
    el.append(_t(8, 16, titolo, 3.2, ancora="start", colore="#c00" if spec else "#000", peso="bold"))
    el.append(_t(8, 22, "Stampare al 100%: la barra sotto la vista 1:1 deve misurare 10 mm. Anteriore (USB-C) in basso.",
                 2.6, ancora="start"))
    el.append(_t(8, 26.5, "Colonna A = lato lungo intatto della 14x20 (fori M3). Azzurro = zona antenna da lasciare libera.",
                 2.6, ancora="start"))
    el.append(_t(ox1 + LARGH / 2, oy1 - 6.5, "scala 1:1", 3, peso="bold"))
    el.append(_t(ox4 + s_big * LARGH / 2, oy4 - 6.5, "ingrandita 3:1", 3, peso="bold"))
    el += disegna_scheda(lato, comp, net_foro, archi, fili_sotto, 1.0, ox1, oy1, False)
    el += disegna_scheda(lato, comp, net_foro, archi, fili_sotto, s_big, ox4, oy4, True)
    yb = oy1 + LUNG + 7
    el.append(f'<line x1="{ox1}" y1="{yb}" x2="{ox1 + 10}" y2="{yb}" stroke="#000" stroke-width="0.4"/>')
    el.append(f'<line x1="{ox1}" y1="{yb - 1.2}" x2="{ox1}" y2="{yb + 1.2}" stroke="#000" stroke-width="0.3"/>')
    el.append(f'<line x1="{ox1 + 10}" y1="{yb - 1.2}" x2="{ox1 + 10}" y2="{yb + 1.2}" stroke="#000" stroke-width="0.3"/>')
    el.append(_t(ox1 + 12, yb + 1, "10 mm", 2.4, ancora="start"))
    yl, x = yb + 7, 4.0
    if spec:
        el.append(_t(x, yl, "Net", 3, ancora="start", peso="bold"))
        yl += 4
        for net, col in COLORI.items():
            el.append(f'<rect x="{x}" y="{yl - 2.2}" width="5" height="2.5" fill="{col}"/>')
            el.append(_t(x + 6.5, yl, f"{net}: {DESCR_NET[net]}", 1.9, ancora="start"))
            yl += 3.1
    else:
        el.append(_t(x, yl, "Componenti", 3, ancora="start", peso="bold"))
        yl += 4
        for c in comp:
            if c["tipo"] != "filo":
                el.append(_t(x, yl, f"{c['ref']}: {c['valore']}"[:52], 1.9, ancora="start"))
                yl += 3.0
    el.append("</svg>")
    with open(percorso, "w", encoding="utf-8") as fh:
        fh.write("\n".join(el))


def main():
    global SPECCHIA
    ap = argparse.ArgumentParser(description="Millefori 8x20 con SuperMini: disposizione, verifica, SVG")
    ap.add_argument("--specchia", action="store_true", help="fila 5V/GND/3V3 della SuperMini a sinistra")
    ap.add_argument("--senza-svg", action="store_true")
    args = ap.parse_args()
    SPECCHIA = args.specchia

    comp, tracce, fili_sotto = costruisci()
    esito, net_foro, archi = verifica(comp, tracce, fili_sotto)
    print(f"Millefori {len(COLONNE)}x{N_RIGHE} fori ({LARGH:.2f} x {LUNG:.1f} mm), specchiata: {SPECCHIA}")
    print(mappa_ascii(comp, net_foro))
    print()
    print(f"Ponticelli sul retro: {len(archi)}; fili isolati sotto: {len(fili_sotto)}")
    for m in esito.ok:
        print("  OK      ", m)
    for m in esito.avvisi:
        print("  AVVISO  ", m)
    for m in esito.errori:
        print("  ERRORE  ", m)
    if esito.errori:
        print("  (SVG non rigenerati)")
    elif not args.senza_svg:
        cartella = os.path.dirname(os.path.abspath(__file__))
        suff = "_specchiata" if SPECCHIA else ""
        for lato in ("componenti", "saldature"):
            p = os.path.join(cartella, f"lato_{lato}{suff}.svg")
            svg_pagina(lato, comp, net_foro, archi, fili_sotto, p)
            try:
                ET.parse(p)
                print(f"  OK       {os.path.basename(p)} scritto, XML valido")
            except ET.ParseError as ex:
                esito.errori.append(str(ex))
                print(f"  ERRORE   {os.path.basename(p)}: XML non valido ({ex})")
    print()
    if esito.errori:
        print(f"VERIFICA FALLITA: {len(esito.errori)} errori")
        sys.exit(1)
    print("VERIFICA OK")


if __name__ == "__main__":
    main()
