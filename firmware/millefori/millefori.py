#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schedina millefori di interfaccia - YouTubeController.

Disposizione dei componenti, piste sul retro e verifica automatica contro la
netlist dello schema (firmware/README.md, versione S8550 + 2N3904).
Solo libreria standard. Genera:
  lato_componenti.svg  (vista dall'alto, scala 1:1 + ingrandita 4:1)
  lato_saldature.svg   (vista da sotto, SPECCHIATA, scala 1:1 + 4:1)

Uso:
  python millefori.py                      # variante di default (connettore angolato, con chiave)
  python millefori.py --connettore diritto # verifica la variante con header diritto
  python millefori.py --senza-chiave       # pin 5 di J1 usato come terzo GND invece che come chiave
  python millefori.py --pinout-q1 ECB      # mostra cosa succede con un S8550 E-C-B

Convenzioni (vista dal LATO COMPONENTI, anteriore in basso):
  - colonne A..H da sinistra a destra (lato corto, ~21 mm, 8 fori);
  - righe 1..13 dall'ANTERIORE (riga 1, bordo verso encoder/SuperMini, connettore J1)
    al POSTERIORE (riga 13, verso la USB-C del TP4056);
  - x in mm dal bordo sinistro, y in mm dal bordo anteriore;
  - il foro "A1" e' l'angolo anteriore-sinistro.
La schedina sta coricata sopra il modulo TP4056 (lato saldature verso il modulo).
"""

import argparse
import math
import os
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

# =============================================================================
# PARAMETRI (modificare qui)
# =============================================================================

COLONNE = "ABCDEFGH"          # 8 colonne
N_RIGHE = 13                  # 13 righe
PASSO = 2.54
LARGH = 21.0                  # mm, lato corto della schedina tagliata (misurare)
LUNG = 34.0                   # mm, lato lungo (misurare)
MARG_X = (LARGH - (len(COLONNE) - 1) * PASSO) / 2   # bordo -> centro foro
MARG_Y = (LUNG - (N_RIGHE - 1) * PASSO) / 2

# --- Fissaggio (viti M2) ---
D_FORO_FISS = 2.2             # foro da allargare con punta 2,2 (M2 passante)
R_TESTA_VITE = 1.9            # testa M2 ~3,8 lato componenti
H_TESTA_VITE = 1.6
# Raggio attorno al centro di ogni foro di fissaggio entro cui nessuna piazzola
# puo' essere usata. 2,0 = solo il foro stesso (distanziali in nylon o colonnine
# stampate). Con distanziali METALLICI portare a 3,0 (esclude anche i fori vicini).
R_LIBERO = 2.0
# Fori posteriori = fori del TP4056 lato USB-C. Interasse e posizione NON ancora
# misurati: valori indicativi. Le righe riservate restano libere per intero,
# quindi qualunque interasse misurato va bene finche' i fori cadono in quelle righe.
INTERASSE_TP_POST = 13.5      # DA MISURARE (interasse in X dei 2 fori posteriori del TP4056)
CENTRO_TP_X = LARGH / 2       # asse del TP4056 rispetto alla schedina (DA DEFINIRE con design-3d)
Y_FORI_TP_POST = LUNG - 1.9   # DA MISURARE (se i bordi posteriori sono allineati)
RIGHE_RISERVATE = [12, 13]    # nessun componente ne' pista: ospitano i fori posteriori


def _xy(nome):
    i = COLONNE.index(nome[0])
    r = int(nome[1:])
    return (MARG_X + i * PASSO, MARG_Y + (r - 1) * PASSO)


FISSAGGI = [
    {"nome": "F1 anteriore sinistro", "xy": _xy("A1")},
    {"nome": "F2 anteriore destro", "xy": _xy("H1")},
    {"nome": "F3 posteriore sinistro (= foro TP4056)",
     "xy": (CENTRO_TP_X - INTERASSE_TP_POST / 2, Y_FORI_TP_POST)},
    {"nome": "F4 posteriore destro (= foro TP4056)",
     "xy": (CENTRO_TP_X + INTERASSE_TP_POST / 2, Y_FORI_TP_POST)},
]

# --- Zone e altezze ---
H_MAX = 12.0                  # altezza massima lato componenti
H_MAX_SALDATURE = 2.0         # altezza massima lato saldature
H_SALDATURE = 1.5             # dichiarata: piedini tagliati a ~1 mm, ponticelli di stagno/filo nudo
ZONA_CRITICA = {"angolo": "anteriore-destro", "larg": 6.0, "prof": 7.0, "h_max": 10.0}
# Zona del chip TP4056 (sotto la schedina): centro in larghezza, meta' posteriore.
ZONA_CHIP = {"x0": LARGH / 2 - 5.0, "x1": LARGH / 2 + 5.0, "y0": LUNG / 2, "y1": LUNG}
TOLLERANZA = 0.15             # compenetrazione ammessa tra corpi (piedini che si piegano)

# --- Ingombri componenti (affidabilita' B/C, vedi enclosure/dimensioni.md) ---
R_DIAM, R_H = 2.5, 10.0       # resistenza 1/4 W in piedi: corpo sul foro "corpo", piedino ripiegato sull'altro
TO92_LUNGO, TO92_PIATTO, TO92_TONDO, TO92_H = 2.3, 1.4, 2.3, 8.0
C_EL_DIAM, C_EL_H = 5.0, 11.5     # 47 uF 16 V 5x11 in piedi (6,3x11 per 100 uF: verificare)
C_CER_LUNGO, C_CER_SPESS, C_CER_H = 4.5, 2.5, 6.0
FILO_R, FILO_H = 0.55, 3.0        # filo siliconico 26-28 AWG, uscita verso l'alto
J1_H = {"angolato": 5.1, "diritto": 16.5}  # diritto: 2,5 plastica + spina Dupont 14 (fili esclusi)


# =============================================================================
# DISPOSIZIONE
# =============================================================================

def comp_R(ref, valore, corpo, filo, nota=""):
    return {"ref": ref, "tipo": "R", "valore": valore, "nota": nota,
            "pin": {"corpo": corpo, "filo": filo}, "h": R_H}


def comp_TO92(ref, valore, centro, piatto, pinout):
    """piatto = direzione verso cui guarda la faccia piatta (N=posteriore, S=anteriore, E=destra, W=sinistra).
    pinout = ordine dei piedini letti con la faccia piatta verso di se', piedini in basso, da sinistra."""
    n = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}[piatto]
    f = (-n[0], -n[1])                 # direzione in cui guarda chi legge la faccia piatta
    sx = (-f[1], f[0])                 # sinistra di chi guarda (vista dall'alto, y verso il posteriore)
    i, r = COLONNE.index(centro[0]), int(centro[1:])
    fori = [f"{COLONNE[i + sx[0] * k]}{r + sx[1] * k}" for k in (1, 0, -1)]
    pin = {pinout[k]: fori[k] for k in range(3)}
    return {"ref": ref, "tipo": "TO92", "valore": valore, "pin": pin, "piatto": piatto,
            "centro": centro, "pinout": pinout, "h": TO92_H}


def comp_filo(net, foro, verso, colore, lungh):
    return {"ref": "W_" + net, "tipo": "filo", "valore": verso, "pin": {"1": foro},
            "h": FILO_H, "colore_filo": colore, "lungh": lungh, "net_nome": net}


def costruisci(args):
    chiave = not args.senza_chiave
    j1 = {"ref": "J1", "tipo": "J2x4", "valore": f"pin header 2x4 passo 2,54 {args.connettore}",
          "variante": args.connettore, "h": J1_H[args.connettore],
          "pin": {"1": "C1", "2": "C2", "3": "D1", "4": "D2", "5": "E1", "6": "E2", "7": "F1", "8": "F2"},
          "chiave": "5" if chiave else None}
    comp = [
        j1,
        {"ref": "C1", "tipo": "C_el", "valore": "47 uF 16 V elettrolitico", "pin": {"+": "E4", "-": "D4"},
         "h": C_EL_H},
        comp_R("R5", "330", corpo="G4", filo="F4", nota="serie dato anello"),
        comp_TO92("Q1", "S8550 (PNP)", centro="F6", piatto="N", pinout=args.pinout_q1),
        comp_R("R4", "10k", corpo="F7", filo="G7", nota="base-emettitore Q1"),
        comp_R("R3", "680", corpo="D7", filo="E7", nota="collettore Q2 -> base Q1"),
        comp_TO92("Q2", "2N3904 (NPN)", centro="D9", piatto="W", pinout=args.pinout_q2),
        comp_R("R1", "4,7k", corpo="F9", filo="E9", nota="GPIO9 -> base Q2"),
        comp_R("R2", "10k", corpo="E11", filo="E10", nota="pull-down base Q2"),
        comp_R("R10", "220k", corpo="H8", filo="G8", nota="partitore alto"),
        comp_R("R11", "220k", corpo="H11", filo="H10", nota="partitore basso"),
        {"ref": "C2", "tipo": "C_cer", "valore": "100 nF ceramico", "pin": {"1": "G10", "2": "G11"},
         "h": C_CER_H},
        comp_R("R6", "10k", corpo="A4", filo="A5", nota="serie CHRG"),
        comp_R("R7", "100k", corpo="B7", filo="B6", nota="pull-up GPIO8"),
        comp_R("R9", "100k", corpo="B8", filo="B9", nota="pull-up GPIO10"),
        comp_R("R8", "10k", corpo="B11", filo="B10", nota="serie STDBY"),
        # fili esterni: (net, foro, destinazione, colore, lunghezza indicativa)
        comp_filo("GPIO4", "B2", "SuperMini GPIO4 (encoder A)", "giallo", "6-8 cm"),
        comp_filo("GPIO5", "C3", "SuperMini GPIO5 (encoder B)", "verde", "6-8 cm"),
        comp_filo("GPIO7", "G2", "SuperMini GPIO7 (pulsante)", "blu", "6-8 cm"),
        comp_filo("GPIO2", "H4", "SuperMini GPIO2 (dato anello)", "bianco", "6-8 cm"),
        comp_filo("GPIO9", "G9", "SuperMini GPIO9 (comando anello)", "viola", "6-8 cm"),
        comp_filo("GPIO1", "H9", "SuperMini GPIO1 (tensione batteria)", "grigio", "6-8 cm"),
        comp_filo("GND_SM", "C5", "SuperMini GND", "nero", "6-8 cm"),
        comp_filo("3V3", "A7", "SuperMini 3V3", "arancione", "6-8 cm"),
        comp_filo("GPIO8", "B5", "SuperMini GPIO8 (CHRG)", "marrone", "6-8 cm"),
        comp_filo("GPIO10", "A9", "SuperMini GPIO10 (STDBY)", "azzurro", "6-8 cm"),
        comp_filo("VBAT", "H6", "TP4056 OUT+", "rosso", "4-6 cm"),
        comp_filo("GND_TP", "C6", "TP4056 OUT-", "nero", "4-6 cm"),
        comp_filo("CHRG", "A3", "TP4056 catodo LED rosso (pin 7)", "marrone/bianco", "3-5 cm"),
        comp_filo("STDBY", "A11", "TP4056 catodo LED blu/verde (pin 6)", "azzurro/bianco", "3-5 cm"),
    ]
    # Piste sul retro: (net attesa, percorso di piazzole adiacenti unite da stagno o filo nudo)
    tracce = [
        ("ENC_A", "C1-B1-B2"),
        ("ENC_B", "C2-C3"),
        ("PULS", "F1-G1-G2"),
        ("GND", "D1-D2-D3-D4-C4-C5-C6-C7-C8-C9-C10-C11-D11-E11-F11-G11-H11"),
        ("GND", "C10-D10"),
        ("LED+", "E2-E3-E4-E5-E6"),
        ("DI", "F2-F3-F4"),
        ("GPIO2", "G4-H4"),
        ("B_Q1", "E7-F7-F6"),
        ("VBAT", "H6-G6-G7-G8"),
        ("C_Q2", "D7-D8"),
        ("B_Q2", "D9-E9-E10"),
        ("GPIO9", "F9-G9"),
        ("GPIO1", "H8-H9-H10-G10"),
        ("CHRG", "A3-A4"),
        ("GPIO8", "A5-B5-B6"),
        ("3V3", "A7-B7-B8"),
        ("GPIO10", "A9-B9-B10"),
        ("STDBY", "A11-B11"),
    ]
    if not chiave:
        tracce.append(("GND", "D1-E1"))
    ponticelli_isolati = []    # lato componenti: nessuno necessario
    return comp, tracce, ponticelli_isolati, chiave


def netlist(chiave):
    """Netlist ESPLICITA dello schema (indipendente dalla disposizione).
    'R4' = un terminale di un componente non polarizzato; 'Q1.E' = terminale polarizzato."""
    n = {
        "VBAT":   ["W_VBAT.1", "Q1.E", "R4", "R10"],
        "GND":    ["W_GND_TP.1", "W_GND_SM.1", "J1.3", "J1.4", "C1.-", "Q2.E", "R2", "R11", "C2"],
        "LED+":   ["Q1.C", "C1.+", "J1.6"],
        "DI":     ["J1.8", "R5"],
        "GPIO2":  ["W_GPIO2.1", "R5"],
        "B_Q1":   ["Q1.B", "R4", "R3"],
        "C_Q2":   ["Q2.C", "R3"],
        "B_Q2":   ["Q2.B", "R1", "R2"],
        "GPIO9":  ["W_GPIO9.1", "R1"],
        "GPIO1":  ["W_GPIO1.1", "R10", "R11", "C2"],
        "GPIO8":  ["W_GPIO8.1", "R6", "R7"],
        "CHRG":   ["W_CHRG.1", "R6"],
        "3V3":    ["W_3V3.1", "R7", "R9"],
        "GPIO10": ["W_GPIO10.1", "R8", "R9"],
        "STDBY":  ["W_STDBY.1", "R8"],
        "ENC_A":  ["J1.1", "W_GPIO4.1"],
        "ENC_B":  ["J1.2", "W_GPIO5.1"],
        "PULS":   ["J1.7", "W_GPIO7.1"],
    }
    if not chiave:
        n["GND"].append("J1.5")
    return n


J1_FUNZIONE = {"1": "encoder A", "2": "encoder B", "3": "GND encoder (C) + pulsante",
               "4": "GND anello (-)", "5": "chiave (piedino tagliato)", "6": "anello + commutato (LED+)",
               "7": "pulsante", "8": "anello DI"}

COLORI = {
    "VBAT": "#d40000", "GND": "#3a3a3a", "LED+": "#ff8c00", "DI": "#1a9850", "GPIO2": "#7fcf6f",
    "B_Q1": "#e7298a", "C_Q2": "#8c510a", "B_Q2": "#d8b365", "GPIO9": "#7570b3", "GPIO1": "#1f78b4",
    "GPIO8": "#17becf", "CHRG": "#9edae5", "3V3": "#f781bf", "GPIO10": "#9467bd", "STDBY": "#c5b0d5",
    "ENC_A": "#bcbd22", "ENC_B": "#6b8e23", "PULS": "#4169e1",
}
DESCR_NET = {
    "VBAT": "VBAT = OUT+ TP4056 (3,0-4,2 V)", "GND": "GND = OUT- TP4056", "LED+": "anello + commutato (collettore Q1)",
    "DI": "dato anello (dopo 330)", "GPIO2": "GPIO2 (prima della 330)", "B_Q1": "base Q1", "C_Q2": "collettore Q2",
    "B_Q2": "base Q2", "GPIO9": "GPIO9 comando anello", "GPIO1": "GPIO1 partitore batteria", "GPIO8": "GPIO8 CHRG",
    "CHRG": "CHRG (catodo LED rosso)", "3V3": "3V3 SuperMini", "GPIO10": "GPIO10 STDBY",
    "STDBY": "STDBY (catodo LED blu/verde)", "ENC_A": "encoder A -> GPIO4", "ENC_B": "encoder B -> GPIO5",
    "PULS": "pulsante -> GPIO7",
}


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


def corpi(c):
    """Sagome in pianta: ('C', cx, cy, r) o ('R', x0, y0, x1, y1)."""
    t = c["tipo"]
    if t == "R":
        x, y = _xy(c["pin"]["corpo"])
        return [("C", x, y, R_DIAM / 2)]
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
            return [("R", cx - C_CER_LUNGO / 2, cy - C_CER_SPESS / 2, cx + C_CER_LUNGO / 2, cy + C_CER_SPESS / 2)]
        return [("R", cx - C_CER_SPESS / 2, cy - C_CER_LUNGO / 2, cx + C_CER_SPESS / 2, cy + C_CER_LUNGO / 2)]
    if t == "TO92":
        cx, cy = _xy(c["centro"])
        p = c["piatto"]
        if p in "NS":
            x0, x1 = cx - TO92_LUNGO, cx + TO92_LUNGO
            y0, y1 = (cy - TO92_TONDO, cy + TO92_PIATTO) if p == "N" else (cy - TO92_PIATTO, cy + TO92_TONDO)
        else:
            y0, y1 = cy - TO92_LUNGO, cy + TO92_LUNGO
            x0, x1 = (cx - TO92_TONDO, cx + TO92_PIATTO) if p == "E" else (cx - TO92_PIATTO, cx + TO92_TONDO)
        return [("R", x0, y0, x1, y1)]
    if t == "J2x4":
        xs = [_xy(h)[0] for h in c["pin"].values()]
        ys = [_xy(h)[1] for h in c["pin"].values()]
        if c["variante"] == "angolato":
            # corpo plastico a filo del bordo anteriore, gambe verticali sulla riga 2
            return [("R", min(xs) - 1.27, -1.5, max(xs) + 1.27, max(ys) + 0.5)]
        return [("R", min(xs) - 1.27, min(ys) - 1.27, max(xs) + 1.27, max(ys) + 1.27)]
    raise ValueError(t)


def compenetrazione(a, b):
    """>0 se le sagome si sovrappongono (mm di compenetrazione, approssimata)."""
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


def zona_critica_rett():
    z = ZONA_CRITICA
    ant, lato = z["angolo"].split("-")
    y0, y1 = (0.0, z["prof"]) if ant == "anteriore" else (LUNG - z["prof"], LUNG)
    x0, x1 = (LARGH - z["larg"], LARGH) if lato == "destro" else (0.0, z["larg"])
    return ("R", x0, y0, x1, y1)


def zona_chip_rett():
    return ("R", ZONA_CHIP["x0"], ZONA_CHIP["y0"], ZONA_CHIP["x1"], ZONA_CHIP["y1"])


# =============================================================================
# VERIFICA
# =============================================================================

class Esito:
    def __init__(self):
        self.errori, self.avvisi, self.ok = [], [], []

    def controlla(self, cond, msg_ok, msg_err):
        (self.ok.append(msg_ok) if cond else self.errori.append(msg_err))


def verifica(comp, tracce, ponticelli, chiave):
    e = Esito()
    refs = {c["ref"]: c for c in comp}

    # 1. fori validi e mai usati due volte
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

    # 2. pinout TO-92 coerente con la netlist (E-B-C scritto sul disegno)
    for c in comp:
        if c["tipo"] == "TO92":
            e.ok.append(f"{c['ref']} {c['valore']}: pinout {c['pinout']}, faccia piatta verso {c['piatto']}, "
                        f"E={c['pin']['E']} B={c['pin']['B']} C={c['pin']['C']}")

    # 3. piste: piazzole adiacenti, fori validi
    archi = []
    for net, perc in tracce:
        fori = perc.split("-")
        for a, b in zip(fori, fori[1:]):
            if not (valido(a) and valido(b)):
                e.errori.append(f"pista {perc}: foro non valido")
            elif not adiacenti(a, b):
                e.errori.append(f"pista {perc}: {a}-{b} non adiacenti (un ponticello di stagno unisce solo fori vicini)")
            else:
                archi.append((a, b, net))
    for net, a, b in ponticelli:
        archi.append((a, b, net))
    fori_pista = {h for a, b, _ in archi for h in (a, b)}

    # 4. connettivita' (union-find su piste e ponticelli)
    padre = {}

    def trova(x):
        padre.setdefault(x, x)
        while padre[x] != x:
            padre[x] = padre[padre[x]]
            x = padre[x]
        return x

    for a, b, _ in archi:
        padre[trova(a)] = trova(b)
    for h in uso:
        trova(h)

    def foro_di(term):
        ref, _, pin = term.partition(".")
        return refs[ref]["pin"][pin]

    nets = netlist(chiave)
    gruppo_net = {}
    for net, terms in nets.items():
        polari = [t for t in terms if "." in t]
        if not polari:
            e.errori.append(f"net {net}: nessun terminale polarizzato (verifica non univoca)")
            continue
        gruppi = {trova(foro_di(t)) for t in polari}
        e.controlla(len(gruppi) == 1, f"net {net}: connessa",
                    f"net {net}: NON connessa ({', '.join(f'{t}@{foro_di(t)}' for t in polari)})")
        gruppo_net[net] = trova(foro_di(polari[0]))
    # nessun corto: net diverse in gruppi diversi
    inv = {}
    for net, g in gruppo_net.items():
        inv.setdefault(g, []).append(net)
    corti = [v for v in inv.values() if len(v) > 1]
    e.controlla(not corti, "nessun corto tra net diverse", f"CORTO tra le net: {corti}")
    # componenti non polarizzati: i due terminali sulle net giuste
    for c in comp:
        if c["tipo"] in ("R", "C_cer"):
            attese = sorted(n for n, terms in nets.items() for t in terms if t == c["ref"])
            trovate = []
            for h in c["pin"].values():
                g = trova(h)
                trovate.append(inv.get(g, ["(nessuna)"])[0] if g in inv else "(isolato)")
            e.controlla(sorted(trovate) == attese, f"{c['ref']} {c['valore']}: {' / '.join(attese)}",
                        f"{c['ref']}: collegato a {sorted(trovate)}, atteso {attese}")
    # ogni piedino appartiene a una net (salvo la chiave)
    for c in comp:
        for p, h in c["pin"].items():
            if c.get("chiave") == p:
                if h in fori_pista:
                    e.errori.append(f"{c['ref']}.{p} (chiave, {h}) toccato da una pista")
                continue
            if trova(h) not in inv:
                e.errori.append(f"{c['ref']}.{p} ({h}) non appartiene a nessuna net")
    # piste: net attesa = net reale
    for net, perc in tracce:
        g = trova(perc.split("-")[0])
        reale = inv.get(g, ["(nessuna)"])[0]
        if reale != net:
            e.errori.append(f"pista {perc}: dichiarata {net}, collegata a {reale}")
    # rami morti
    grado = {}
    for a, b, _ in archi:
        grado[a] = grado.get(a, 0) + 1
        grado[b] = grado.get(b, 0) + 1
    morti = [h for h, g in grado.items() if g == 1 and h not in uso]
    if morti:
        e.avvisi.append(f"piazzole di pista senza piedino in fondo a un ramo: {morti}")

    # 5. fori di fissaggio e righe riservate liberi
    occupati = set(uso) | fori_pista
    for f in FISSAGGI:
        fx, fy = f["xy"]
        if not (D_FORO_FISS / 2 < fx < LARGH - D_FORO_FISS / 2 and D_FORO_FISS / 2 < fy < LUNG - D_FORO_FISS / 2):
            e.errori.append(f"{f['nome']}: fuori dalla schedina ({fx:.2f}; {fy:.2f})")
        vicini = [h for h in occupati if math.hypot(_xy(h)[0] - fx, _xy(h)[1] - fy) < R_LIBERO]
        e.controlla(not vicini, f"{f['nome']} ({fx:.2f}; {fy:.2f}): libero entro {R_LIBERO} mm",
                    f"{f['nome']}: fori occupati entro {R_LIBERO} mm: {vicini}")
    in_riservate = [h for h in occupati if int(h[1:]) in RIGHE_RISERVATE]
    e.controlla(not in_riservate, f"righe riservate {RIGHE_RISERVATE} libere",
                f"righe riservate occupate: {in_riservate}")

    # 6. ingombri: compenetrazioni, bordo, altezze, zone
    sag = [(c["ref"], s) for c in comp for s in corpi(c)]
    sag += [(f["nome"].split()[0], ("C", f["xy"][0], f["xy"][1], R_TESTA_VITE)) for f in FISSAGGI]
    coll = []
    for i in range(len(sag)):
        for j in range(i + 1, len(sag)):
            p = compenetrazione(sag[i][1], sag[j][1])
            if p > TOLLERANZA:
                coll.append(f"{sag[i][0]}/{sag[j][0]} ({p:.2f} mm)")
    e.controlla(not coll, f"nessuna collisione tra corpi (tolleranza {TOLLERANZA} mm)",
                f"collisioni: {coll}")
    fuori = []
    for c in comp:
        if c["tipo"] == "J2x4" and c["variante"] == "angolato":
            continue    # sporge di proposito oltre il bordo anteriore
        for s in corpi(c):
            box = (s[1] - s[3], s[2] - s[3], s[1] + s[3], s[2] + s[3]) if s[0] == "C" else s[1:]
            if box[0] < -0.3 or box[1] < -0.3 or box[2] > LARGH + 0.3 or box[3] > LUNG + 0.3:
                fuori.append(c["ref"])
    e.controlla(not fuori, "tutti i corpi entro il bordo (+0,3)", f"corpi oltre il bordo: {fuori}")
    alti = [f"{c['ref']} {c['h']}" for c in comp if c["h"] > H_MAX]
    e.controlla(not alti, f"altezze lato componenti <= {H_MAX} mm (max {max(c['h'] for c in comp)})",
                f"oltre {H_MAX} mm: {alti}")
    zc = zona_critica_rett()
    in_zona = [c for c in comp for s in corpi(c) if compenetrazione(s, zc) > 0]
    alti_zona = [f"{c['ref']} ({c['h']} mm)" for c in in_zona if c["h"] > ZONA_CRITICA["h_max"]]
    e.controlla(not alti_zona,
                f"zona critica {ZONA_CRITICA['angolo']} {ZONA_CRITICA['larg']}x{ZONA_CRITICA['prof']}: "
                f"<= {ZONA_CRITICA['h_max']} mm (presenti: {', '.join(sorted({c['ref'] for c in in_zona})) or 'nessuno'})",
                f"zona critica: troppo alti {alti_zona}")
    for c in comp:
        if c["tipo"] == "C_el":
            s = corpi(c)[0]
            e.controlla(compenetrazione(s, zona_chip_rett()) <= 0,
                        f"{c['ref']} fuori dalla verticale del chip TP4056",
                        f"{c['ref']} sopra la zona del chip TP4056")
            e.controlla(s[2] + s[3] <= LUNG / 2, f"{c['ref']} nella meta' anteriore",
                        f"{c['ref']} non sta nella meta' anteriore")
    e.controlla(H_SALDATURE <= H_MAX_SALDATURE, f"lato saldature {H_SALDATURE} mm <= {H_MAX_SALDATURE} mm",
                f"lato saldature {H_SALDATURE} > {H_MAX_SALDATURE}")
    if ponticelli:
        e.avvisi.append(f"ponticelli isolati lato componenti: {len(ponticelli)}")
    else:
        e.ok.append("nessun ponticello isolato sul lato componenti")

    # informativo: piazzole adiacenti di net diverse (attenzione allo stagno)
    net_foro = {}
    for g, ns in inv.items():
        pass
    for h in occupati:
        g = trova(h)
        if g in inv:
            net_foro[h] = inv[g][0]
    vicine = 0
    for h, n in net_foro.items():
        for h2, n2 in net_foro.items():
            if h < h2 and adiacenti(h, h2) and n != n2:
                vicine += 1
    e.avvisi.append(f"{vicine} coppie di piazzole adiacenti di net diverse NON vanno unite: "
                    "stagnare con attenzione e controllare col tester")
    return e, net_foro, archi


# =============================================================================
# USCITE
# =============================================================================

def mappa_ascii(comp, net_foro):
    cella = {}
    for c in comp:
        for p, h in c["pin"].items():
            if c["tipo"] == "R":
                cella[h] = c["ref"] + ("*" if p == "corpo" else "")
            elif c["tipo"] == "filo":
                cella[h] = "~" + c["net_nome"][:6]
            elif c["tipo"] == "J2x4":
                cella[h] = "J1." + p + ("x" if c.get("chiave") == p else "")
            elif c["tipo"] == "TO92":
                cella[h] = c["ref"] + p
            else:
                cella[h] = c["ref"] + "." + p
    for f in FISSAGGI:
        for i, col in enumerate(COLONNE):
            for r in range(1, N_RIGHE + 1):
                h = f"{col}{r}"
                if math.hypot(_xy(h)[0] - f["xy"][0], _xy(h)[1] - f["xy"][1]) < 0.6:
                    cella[h] = "FISS"
    righe = ["        " + "".join(f"{c:^9}" for c in COLONNE) + "   (vista lato componenti)"]
    for r in range(N_RIGHE, 0, -1):
        s = f"  {r:>2}  |"
        for col in COLONNE:
            h = f"{col}{r}"
            if h in cella:
                t = cella[h]
            elif r in RIGHE_RISERVATE:
                t = "//"
            elif h in net_foro:
                t = "-" + net_foro[h][:6]
            else:
                t = "."
            s += f"{t:^9}"
        righe.append(s + "|" + ("  <- posteriore (USB-C TP4056)" if r == N_RIGHE else
                                "  <- anteriore (encoder, SuperMini)" if r == 1 else ""))
    righe.append("  legenda: R1* corpo della resistenza in piedi, R1 piedino ripiegato, ~NET filo esterno, "
                 "-NET solo pista, J1.5x chiave, // riga riservata")
    return "\n".join(righe)


def _t(x, y, testo, size, ancora="middle", colore="#000", peso="normal", extra=""):
    return (f'<text x="{x:.3f}" y="{y:.3f}" font-size="{size:.3f}" text-anchor="{ancora}" '
            f'font-family="Arial, Helvetica, sans-serif" font-weight="{peso}" fill="{colore}" {extra}>'
            f'{escape(testo)}</text>')


def disegna_scheda(lato, comp, net_foro, archi, s, ox, oy, dettagli):
    """Restituisce elementi SVG in coordinate pagina (mm). s = scala."""
    spec = lato == "saldature"

    def X(x):
        return ox + s * ((LARGH - x) if spec else x)

    def Y(y):
        return oy + s * (LUNG - y)

    el = []
    lw = 0.06 * s
    el.append(f'<rect x="{X(LARGH) if spec else X(0):.3f}" y="{Y(LUNG):.3f}" width="{s * LARGH:.3f}" '
              f'height="{s * LUNG:.3f}" fill="{"#e9dcc0" if not spec else "#d9c9a3"}" stroke="#555" stroke-width="{lw:.3f}"/>')
    # righe riservate
    yr0 = min(_xy(f"A{r}")[1] for r in RIGHE_RISERVATE) - PASSO / 2
    el.append(f'<rect x="{min(X(0), X(LARGH)):.3f}" y="{Y(LUNG):.3f}" width="{s * LARGH:.3f}" '
              f'height="{s * (LUNG - yr0):.3f}" fill="#999" fill-opacity="0.18"/>')
    # zone
    z = zona_critica_rett()
    el.append(f'<rect x="{min(X(z[1]), X(z[3])):.3f}" y="{Y(z[4]):.3f}" width="{s * (z[3] - z[1]):.3f}" '
              f'height="{s * (z[4] - z[2]):.3f}" fill="#ff9900" fill-opacity="0.12" stroke="#ff9900" '
              f'stroke-width="{lw:.3f}" stroke-dasharray="{0.4 * s:.3f},{0.25 * s:.3f}"/>')
    z = zona_chip_rett()
    el.append(f'<rect x="{min(X(z[1]), X(z[3])):.3f}" y="{Y(z[4]):.3f}" width="{s * (z[3] - z[1]):.3f}" '
              f'height="{s * (z[4] - z[2]):.3f}" fill="none" stroke="#c00" stroke-width="{lw:.3f}" '
              f'stroke-dasharray="{0.6 * s:.3f},{0.3 * s:.3f}"/>')
    # etichette coordinate
    fs = 0.9 * s if dettagli else 1.1
    for col in COLONNE:
        x = _xy(col + "1")[0]
        el.append(_t(X(x), Y(LUNG) - 0.4 * s - (0 if dettagli else 0.3), col, fs, peso="bold"))
        el.append(_t(X(x), Y(-1.5 if dettagli else 0) + 0.4 * s + fs, col, fs, peso="bold"))
    for r in range(1, N_RIGHE + 1):
        y = _xy(f"A{r}")[1]
        el.append(_t(min(X(0), X(LARGH)) - 0.5 * s, Y(y) + fs * 0.35, str(r), fs, ancora="end"))
        el.append(_t(max(X(0), X(LARGH)) + 0.5 * s, Y(y) + fs * 0.35, str(r), fs, ancora="start"))

    # piste (solo lato saldature)
    if spec:
        for a, b, net in archi:
            (xa, ya), (xb, yb) = _xy(a), _xy(b)
            el.append(f'<line x1="{X(xa):.3f}" y1="{Y(ya):.3f}" x2="{X(xb):.3f}" y2="{Y(yb):.3f}" '
                      f'stroke="{COLORI.get(net, "#000")}" stroke-width="{1.05 * s:.3f}" stroke-linecap="round"/>')
    # fori
    for col in COLONNE:
        for r in range(1, N_RIGHE + 1):
            h = f"{col}{r}"
            x, y = _xy(h)
            if spec:
                net = net_foro.get(h)
                fill = COLORI[net] if net else "#c98b4a"
                el.append(f'<circle cx="{X(x):.3f}" cy="{Y(y):.3f}" r="{0.85 * s:.3f}" fill="{fill}" '
                          f'stroke="#7a4a1a" stroke-width="{0.03 * s:.3f}"/>')
            el.append(f'<circle cx="{X(x):.3f}" cy="{Y(y):.3f}" r="{0.45 * s:.3f}" fill="#fff" '
                      f'stroke="#666" stroke-width="{0.03 * s:.3f}"/>')
    # fori di fissaggio
    for f in FISSAGGI:
        fx, fy = f["xy"]
        el.append(f'<circle cx="{X(fx):.3f}" cy="{Y(fy):.3f}" r="{D_FORO_FISS / 2 * s:.3f}" fill="#222"/>')
        el.append(f'<circle cx="{X(fx):.3f}" cy="{Y(fy):.3f}" r="{R_TESTA_VITE * s:.3f}" fill="none" '
                  f'stroke="#222" stroke-width="{lw:.3f}" stroke-dasharray="{0.3 * s:.3f},{0.2 * s:.3f}"/>')
        if dettagli:
            el.append(_t(X(fx), Y(fy) + 0.25 * s, f["nome"].split()[0], 0.6 * s, colore="#fff", peso="bold"))

    # componenti
    for c in comp:
        t = c["tipo"]
        if spec:
            if dettagli:
                for p, h in c["pin"].items():
                    x, y = _xy(h)
                    if t == "filo":
                        lab = c["net_nome"]
                    elif t == "R":
                        lab = c["ref"]
                    elif t == "J2x4":
                        lab = "J1." + p
                    else:
                        lab = f"{c['ref']}{p}"
                    el.append(_t(X(x), Y(y) - 0.95 * s, lab, 0.45 * s, colore="#000",
                                 extra='stroke="#fff" stroke-width="0.25" paint-order="stroke"'))
            continue
        col = "#333"
        for sg in corpi(c):
            if t == "filo":
                net = c["net_nome"]
                net = "GND" if net.startswith("GND") else net
                net = {"GPIO4": "ENC_A", "GPIO5": "ENC_B", "GPIO7": "PULS"}.get(net, net)
                el.append(f'<circle cx="{X(sg[1]):.3f}" cy="{Y(sg[2]):.3f}" r="{0.75 * s:.3f}" fill="none" '
                          f'stroke="{COLORI.get(net, "#000")}" stroke-width="{0.25 * s:.3f}"/>')
                if dettagli:
                    el.append(_t(X(sg[1]), Y(sg[2]) - 0.95 * s, c["net_nome"], 0.5 * s, peso="bold",
                                 extra='stroke="#fff" stroke-width="0.25" paint-order="stroke"'))
                continue
            if sg[0] == "C":
                fill = {"R": "#d2b48c", "C_el": "#2b4c7e"}.get(t, "#aaa")
                el.append(f'<circle cx="{X(sg[1]):.3f}" cy="{Y(sg[2]):.3f}" r="{sg[3] * s:.3f}" fill="{fill}" '
                          f'fill-opacity="0.75" stroke="{col}" stroke-width="{lw:.3f}"/>')
            else:
                x0, y0, x1, y1 = sg[1:]
                fill = {"TO92": "#222", "C_cer": "#e3a32b", "J2x4": "#111"}.get(t, "#aaa")
                el.append(f'<rect x="{min(X(x0), X(x1)):.3f}" y="{Y(y1):.3f}" width="{(x1 - x0) * s:.3f}" '
                          f'height="{(y1 - y0) * s:.3f}" fill="{fill}" fill-opacity="0.55" stroke="{col}" '
                          f'stroke-width="{lw:.3f}" rx="{0.3 * s:.3f}"/>')
        if t == "R":
            (xa, ya), (xb, yb) = _xy(c["pin"]["corpo"]), _xy(c["pin"]["filo"])
            el.append(f'<line x1="{X(xa):.3f}" y1="{Y(ya):.3f}" x2="{X(xb):.3f}" y2="{Y(yb):.3f}" '
                      f'stroke="#555" stroke-width="{0.12 * s:.3f}"/>')
            if dettagli:
                el.append(_t(X(xa), Y(ya) + 0.1 * s, c["ref"], 0.6 * s, peso="bold"))
                el.append(_t(X(xa), Y(ya) + 0.7 * s, c["valore"], 0.45 * s))
        elif t == "TO92":
            cx, cy = _xy(c["centro"])
            x0, y0, x1, y1 = corpi(c)[0][1:]
            p = c["piatto"]
            # lato piatto in evidenza
            seg = {"N": (x0, y1, x1, y1), "S": (x0, y0, x1, y0), "E": (x1, y0, x1, y1), "W": (x0, y0, x0, y1)}[p]
            el.append(f'<line x1="{X(seg[0]):.3f}" y1="{Y(seg[1]):.3f}" x2="{X(seg[2]):.3f}" y2="{Y(seg[3]):.3f}" '
                      f'stroke="#fff" stroke-width="{0.2 * s:.3f}"/>')
            if dettagli:
                for pin, h in c["pin"].items():
                    x, y = _xy(h)
                    el.append(_t(X(x), Y(y) + 0.2 * s, pin, 0.6 * s, colore="#000", peso="bold",
                                 extra='stroke="#ff0" stroke-width="0.6" paint-order="stroke"'))
                dx = {"E": -1.3, "W": 1.3}.get(p, 0)
                dy = {"N": -1.0, "S": 1.0}.get(p, 0)
                el.append(_t(X(cx + dx), Y(cy + dy) + 0.2 * s, c["ref"], 0.6 * s, colore="#fff", peso="bold"))
        elif t == "C_el":
            xp, yp = _xy(c["pin"]["+"])
            xm, ym = _xy(c["pin"]["-"])
            if dettagli:
                el.append(_t(X(xp), Y(yp) + 0.3 * s, "+", 0.9 * s, colore="#fff", peso="bold"))
                el.append(_t(X(xm), Y(ym) + 0.3 * s, "-", 0.9 * s, colore="#fff", peso="bold"))
                el.append(_t(X((xp + xm) / 2), Y((yp + ym) / 2) - 1.0 * s, "C1 47uF", 0.5 * s, colore="#fff"))
        elif t == "C_cer" and dettagli:
            x0, y0, x1, y1 = corpi(c)[0][1:]
            el.append(_t(X((x0 + x1) / 2), Y((y0 + y1) / 2) + 0.2 * s, "C2", 0.55 * s, peso="bold"))
        elif t == "J2x4" and dettagli:
            for p, h in c["pin"].items():
                x, y = _xy(h)
                lab = "x" if c.get("chiave") == p else p
                el.append(_t(X(x), Y(y) + 0.25 * s, lab, 0.65 * s, colore="#ff0", peso="bold"))
            el.append(_t(X(_xy("D1")[0] + 1.27), Y(-1.0) + 0.1 * s,
                         f"J1 ({c['variante']})", 0.5 * s, colore="#fff"))
    if dettagli:
        z = zona_critica_rett()
        el.append(_t(X((z[1] + z[3]) / 2), Y(z[2]) - 0.25 * s, f"<={ZONA_CRITICA['h_max']:g} mm", 0.55 * s, colore="#b36b00"))
        z = zona_chip_rett()
        el.append(_t(X((z[1] + z[3]) / 2), Y(z[4]) + 0.75 * s, "chip TP4056 (sotto): niente elettrolitico",
                     0.5 * s, colore="#c00"))
        el.append(_t(X(LARGH / 2), Y((_xy("A12")[1] + _xy("A13")[1]) / 2) + 0.2 * s, "righe 12-13 riservate ai fori del TP4056",
                     0.5 * s, colore="#333", peso="bold", extra='stroke="#fff" stroke-width="0.8" paint-order="stroke"'))
    return el


def svg_pagina(lato, comp, net_foro, archi, percorso):
    spec = lato == "saldature"
    PW, PH = 190.0, 40.0 + 4 * LUNG + 18.0
    s_big = 4.0
    ox1, oy1 = 14.0, 40.0
    ox4, oy4 = 70.0, 40.0
    el = [f'<?xml version="1.0" encoding="UTF-8"?>',
          f'<svg xmlns="http://www.w3.org/2000/svg" width="{PW}mm" height="{PH}mm" viewBox="0 0 {PW} {PH}">',
          f'<rect x="0" y="0" width="{PW}" height="{PH}" fill="#fff"/>']
    titolo = ("LATO SALDATURE - VISTA SPECCHIATA (schedina girata attorno all'asse anteriore-posteriore)"
              if spec else "LATO COMPONENTI - vista dall'alto")
    el.append(_t(8, 9, "Schedina millefori di interfaccia - YouTubeController", 5, ancora="start", peso="bold"))
    el.append(_t(8, 16, titolo, 3.6, ancora="start", colore="#c00" if spec else "#000", peso="bold"))
    el.append(_t(8, 22, "Stampare al 100% (senza adattare alla pagina): la barra sotto deve misurare 10 mm. "
                 "Anteriore (J1, encoder) in basso.", 2.6, ancora="start"))
    if spec:
        el.append(_t(8, 26.5, "Colonne in ordine H..A: e' la schedina vista da sotto. Linee colorate = ponticelli "
                     "di stagno o filo nudo tra piazzole adiacenti.", 2.6, ancora="start"))
    else:
        el.append(_t(8, 26.5, "Corpi in pianta: cerchio beige = resistenza in piedi (il corpo sta su quel foro), "
                     "nero = TO-92 (riga bianca = faccia piatta), cerchi colorati = fili.", 2.6, ancora="start"))
    el.append(_t(ox1 + LARGH / 2, oy1 - 6.5, "scala 1:1", 3, peso="bold"))
    el.append(_t(ox4 + 4 * LARGH / 2, oy4 - 6.5, "ingrandita 4:1", 3, peso="bold"))
    el += disegna_scheda(lato, comp, net_foro, archi, 1.0, ox1, oy1, False)
    el += disegna_scheda(lato, comp, net_foro, archi, s_big, ox4, oy4, True)
    # barra di controllo 10 mm
    yb = oy1 + LUNG + 7
    el.append(f'<line x1="{ox1}" y1="{yb}" x2="{ox1 + 10}" y2="{yb}" stroke="#000" stroke-width="0.4"/>')
    el.append(f'<line x1="{ox1}" y1="{yb - 1.2}" x2="{ox1}" y2="{yb + 1.2}" stroke="#000" stroke-width="0.3"/>')
    el.append(f'<line x1="{ox1 + 10}" y1="{yb - 1.2}" x2="{ox1 + 10}" y2="{yb + 1.2}" stroke="#000" stroke-width="0.3"/>')
    el.append(_t(ox1 + 12, yb + 1, "10 mm", 2.4, ancora="start"))
    el.append(_t(ox4 + 2 * LARGH, oy4 + 4 * LUNG + 13, "ANTERIORE: J1 (connettore scocca), verso encoder e SuperMini",
                 2.6, peso="bold"))
    # legenda / elenco
    yl = yb + 7
    x = 6.0
    if spec:
        el.append(_t(x, yl, "Legenda piste (net)", 3, ancora="start", peso="bold"))
        yl += 4.2
        for net, col in COLORI.items():
            el.append(f'<rect x="{x}" y="{yl - 2.3}" width="6" height="2.6" fill="{col}"/>')
            el.append(_t(x + 7.5, yl, f"{net}: {DESCR_NET[net]}", 2.2, ancora="start"))
            yl += 3.6
        el.append(f'<rect x="{x}" y="{yl - 2.3}" width="6" height="2.6" fill="#c98b4a"/>')
        el.append(_t(x + 7.5, yl, "piazzola non usata", 2.2, ancora="start"))
    else:
        el.append(_t(x, yl, "Componenti", 3, ancora="start", peso="bold"))
        yl += 4.2
        for c in comp:
            if c["tipo"] == "filo":
                continue
            el.append(_t(x, yl, f"{c['ref']}: {c['valore']}", 2.3, ancora="start"))
            yl += 3.4
        el.append(_t(x, yl + 1, "Fili: vedi README (tabella fili esterni)", 2.3, ancora="start"))
        yl += 4.4
        el.append(_t(x, yl, "Arancio tratteggiato: zona critica", 2.3, ancora="start", colore="#b36b00"))
        yl += 3.4
        el.append(_t(x, yl, "Rosso tratteggiato: chip TP4056 sotto", 2.3, ancora="start", colore="#c00"))
    el.append("</svg>")
    with open(percorso, "w", encoding="utf-8") as fh:
        fh.write("\n".join(el))


def main():
    ap = argparse.ArgumentParser(description="Schedina millefori: disposizione, verifica, SVG")
    ap.add_argument("--connettore", choices=["angolato", "diritto"], default="angolato")
    ap.add_argument("--senza-chiave", action="store_true", help="J1 pin 5 = terzo GND invece di chiave")
    ap.add_argument("--pinout-q1", choices=["EBC", "ECB"], default="EBC")
    ap.add_argument("--pinout-q2", choices=["EBC", "ECB"], default="EBC")
    ap.add_argument("--senza-svg", action="store_true")
    args = ap.parse_args()

    comp, tracce, ponticelli, chiave = costruisci(args)
    esito, net_foro, archi = verifica(comp, tracce, ponticelli, chiave)

    print(f"Schedina {len(COLONNE)}x{N_RIGHE} fori ({LARGH} x {LUNG} mm), connettore {args.connettore}, "
          f"chiave {'si' if chiave else 'no'}, Q1 {args.pinout_q1}, Q2 {args.pinout_q2}")
    print(mappa_ascii(comp, net_foro))
    print()
    print(f"Ponticelli sul retro: {len(archi)}; ponticelli isolati lato componenti: {len(ponticelli)}")
    for m in esito.ok:
        print("  OK      ", m)
    for m in esito.avvisi:
        print("  AVVISO  ", m)
    for m in esito.errori:
        print("  ERRORE  ", m)

    if esito.errori and not args.senza_svg:
        print("  (SVG non rigenerati: la variante non supera la verifica)")
    elif not args.senza_svg:
        cartella = os.path.dirname(os.path.abspath(__file__))
        for lato in ("componenti", "saldature"):
            p = os.path.join(cartella, f"lato_{lato}.svg")
            svg_pagina(lato, comp, net_foro, archi, p)
            try:
                ET.parse(p)
                print(f"  OK       {os.path.basename(p)} scritto, XML valido")
            except ET.ParseError as ex:
                esito.errori.append(f"{p}: XML non valido ({ex})")
                print(f"  ERRORE   {os.path.basename(p)}: XML non valido ({ex})")

    print()
    if esito.errori:
        print(f"VERIFICA FALLITA: {len(esito.errori)} errori")
        sys.exit(1)
    print("VERIFICA OK")


if __name__ == "__main__":
    main()
