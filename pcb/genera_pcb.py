#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera il PCB YouTubeController (interfaccia SuperMini + anello + motore + TP4056) per KiCad 10.

  python genera_pcb.py            -> scrive pcb/kicad/youtube_controller.kicad_pcb (+ .kicad_pro)
                                      con posizionamento e piste (router a griglia integrato)

Solo libreria standard. Sistema di coordinate:
  - "doc": x verso destra, y dal FRONTE (USB-C, y=0) al RETRO (y=60), vista dall'alto = lato componenti,
    come in firmware/millefori/ (A1 = (3,49; 5,87), passo 2,54);
  - KiCad: x = x_doc, y = -y_doc (cosi' il fronte sta in basso sullo schermo e le coordinate
    di Gerber/CPL (Y verso l'alto) risultano positive e uguali a quelle "doc").
"""
import heapq
import math
import os
import sys
import uuid

QUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(QUI, "kicad")

# ---------------------------------------------------------------------------
# Parametri
# ---------------------------------------------------------------------------
W_BRD, L_BRD = 22.54, 60.0
PASSO = 2.54
A1 = (3.49, 5.87)                  # centro foro A1 (doc)
M3 = [(2.0, 2.0), (2.0, 58.0)]     # fori M3 (doc)
D_M3 = 3.2

CLR = 0.20                         # distanza di progetto (minimo JLCPCB 0,127)
W_SIG, W_PWR = 0.25, 0.50
VIA_D, VIA_DRILL = 0.60, 0.30
EDGE = 0.35                        # rame - bordo scheda
GRID = 0.127
OX, OY = 0.061, -0.028             # origine della griglia: i fori SuperMini cadono sui nodi
NX, NY = 178, 474
JY0 = 473                          # indice riga del nodo y = OY

# antenna (doc): L = x 7,0..17,8 y 24,2..32,5  +  x 4,8..7,0 y 27,2..32,5
ANT_POLY = [(7.0, 24.2), (17.8, 24.2), (17.8, 32.5), (4.8, 32.5), (4.8, 27.2), (7.0, 27.2)]


def K(x, y):
    """doc -> KiCad"""
    return (x, -y)


def hole(col, riga):
    """foro della griglia millefori (col 0..7 = A..H, riga 1..20) in coordinate doc"""
    return (A1[0] + col * PASSO, A1[1] + (riga - 1) * PASSO)


def U():
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Footprint (coordinate locali KiCad: y verso il basso)
# pad: (nome, tipo, x, y, w, h, drill)  tipo: smd | tht | thts (quadrato) | npth
# ---------------------------------------------------------------------------
FP = {
    "R_0805": dict(attr="smd", lcsc_pkg="R_0805_2012Metric", pads=[("1", "smd", -0.9125, 0, 1.025, 1.40, 0), ("2", "smd", 0.9125, 0, 1.025, 1.40, 0)],
                   body=(-1.0, -0.6, 1.0, 0.6)),
    "C_0805": dict(attr="smd", lcsc_pkg="C_0805_2012Metric", pads=[("1", "smd", -0.9125, 0, 1.025, 1.40, 0), ("2", "smd", 0.9125, 0, 1.025, 1.40, 0)],
                   body=(-1.0, -0.6, 1.0, 0.6)),
    "C_1206": dict(attr="smd", lcsc_pkg="C_1206_3216Metric", pads=[("1", "smd", -1.475, 0, 1.05, 1.75, 0), ("2", "smd", 1.475, 0, 1.05, 1.75, 0)],
                   body=(-1.6, -0.8, 1.6, 0.8)),
    "SOT-23": dict(attr="smd", lcsc_pkg="SOT-23", pads=[("1", "smd", -0.95, 1.0, 0.70, 1.00, 0), ("2", "smd", 0.95, 1.0, 0.70, 1.00, 0),
                                                       ("3", "smd", 0.0, -1.0, 0.70, 1.00, 0)],
                   body=(-1.45, -0.65, 1.45, 0.65)),
    "D_SMA": dict(attr="smd", lcsc_pkg="D_SMA", pads=[("1", "smd", -2.0, 0, 2.50, 1.80, 0), ("2", "smd", 2.0, 0, 2.50, 1.80, 0)],
                  body=(-2.15, -1.3, 2.15, 1.3)),
    "M3_HOLE": dict(attr="th", pads=[("", "npth", 0, 0, D_M3, D_M3, D_M3)], body=(-1.6, -1.6, 1.6, 1.6)),
}


def header_fp(n_col, n_row):
    pads = []
    k = 1
    for r in range(n_row):
        for c in range(n_col):
            pads.append((str(k), "thts" if k == 1 else "tht", c * PASSO, r * PASSO, 1.7, 1.7, 1.0))
            k += 1
    return pads


# ---------------------------------------------------------------------------
# Componenti: ref -> (footprint, valore, x_doc, y_doc, rot)
# ---------------------------------------------------------------------------
# rot in gradi antiorari come in KiCad (vista dall'alto)
sys.path.insert(0, QUI)
from netlist_pcb import PARTI, NETS, POWER_NETS  # noqa: E402

# SuperMini: 2 file da 9 fori, origine = foro B1; coordinate locali KiCad (y verso il basso = verso il fronte)
HEADERS = {
    "SM_SUPERMINI": [("B%d" % (r + 1), "thts" if r == 0 else "tht", 0, -r * PASSO, 1.7, 1.7, 1.0) for r in range(9)] +
                    [("H%d" % (r + 1), "tht", 15.24, -r * PASSO, 1.7, 1.7, 1.0) for r in range(9)],
    # J1 2x5: pin 1,2 sulla riga anteriore; dispari a sinistra, pari a destra; le righe vanno verso il retro
    "HDR_2x5": [(str(2 * r + c + 1), "thts" if (r == 0 and c == 0) else "tht", c * PASSO, -r * PASSO, 1.7, 1.7, 1.0)
                for r in range(5) for c in range(2)],
    "HDR_1x4": [(str(c + 1), "thts" if c == 0 else "tht", c * PASSO, 0, 1.7, 1.7, 1.0) for c in range(4)],
}

# parti fisse (origine del footprint = piazzola/foro di riferimento)
PLACE = {
    "SM": ("SM_SUPERMINI", "ESP32-S3 SuperMini", *hole(1, 1), 0),
    "J1": ("HDR_2x5", "scocca 2x5 P2.54", *hole(0, 13), 0),          # pin 1 = (3,49; 36,35)
    "J2": ("HDR_1x4", "TP4056 1x4 P2.54", 8.0, 57.0, 0),
    "H1": ("M3_HOLE", "M3", *M3[0], 0),
    "H2": ("M3_HOLE", "M3", *M3[1], 0),
}
SOLID = [("J1", "10")]
SILK = []
ROUTE_ORDER = []
POS_FILE = os.path.join(QUI, "layout_pcb.py")
if os.path.exists(POS_FILE):
    exec(open(POS_FILE, encoding="utf-8").read())      # definisce MOV = {ref: (x, y, rot)}
    for ref, (x, y, rot) in MOV.items():
        PLACE[ref] = (PARTI[ref][0], PARTI[ref][1], x, y, rot)
exec(open(os.path.join(QUI, "etichette_pcb.py"), encoding="utf-8").read())   # SILK, ROUTE_ORDER


# ---------------------------------------------------------------------------
# Geometria
# ---------------------------------------------------------------------------
def rotpt(px, py, rot):
    t = math.radians(rot)
    c, s = round(math.cos(t), 6), round(math.sin(t), 6)
    return (px * c + py * s, -px * s + py * c)


class Pad:
    pass


def costruisci_pad():
    """ritorna lista di Pad con coordinate KiCad assolute"""
    pads = []
    for ref, (fpn, val, xd, yd, rot) in PLACE.items():
        fx, fy = K(xd, yd)
        spec = FP[fpn] if fpn in FP else None
        plist = spec["pads"] if spec else HEADERS[fpn]
        for (nome, tipo, px, py, w, h, dr) in plist:
            gx, gy = rotpt(px, py, rot)
            p = Pad()
            p.ref, p.nome, p.tipo = ref, nome, tipo
            p.x, p.y = fx + gx, fy + gy
            if int(round(rot)) % 180 == 90:
                w, h = h, w
            p.w, p.h, p.drill = w, h, dr
            p.net = None
            p.layers = (0, 1) if tipo in ("tht", "thts", "npth") else (0,)
            p.round = tipo in ("tht",)
            pads.append(p)
    for n, lst in NETS.items():
        for (ref, nome) in lst:
            ok = False
            for p in pads:
                if p.ref == ref and p.nome == str(nome):
                    p.net = n
                    ok = True
            if not ok:
                raise SystemExit("pad inesistente: %s.%s" % (ref, nome))
    return pads


# ---------------------------------------------------------------------------
# Router a griglia (2 strati, A*)
# ---------------------------------------------------------------------------
def nx_of(x):
    return (x - OX) / GRID


def ny_of(y):
    return (y - OY) / GRID + JY0


def node_xy(ix, iy):
    return (OX + GRID * ix, OY + GRID * (iy - JY0))


class Item:
    def __init__(self, net, layers, kind, geom, hw=0.0, clr=None, ispad=False):
        self.net, self.layers, self.kind, self.geom, self.hw, self.clr, self.ispad = net, layers, kind, geom, hw, clr, ispad


def fill_rect(buf, x0, y0, x1, y1):
    ia, ib = max(0, int(math.ceil(nx_of(x0) - 1e-9))), min(NX - 1, int(math.floor(nx_of(x1) + 1e-9)))
    ja, jb = max(0, int(math.ceil(ny_of(y0) - 1e-9))), min(NY - 1, int(math.floor(ny_of(y1) + 1e-9)))
    if ib < ia:
        return
    seg = b"\x01" * (ib - ia + 1)
    for j in range(ja, jb + 1):
        buf[j * NX + ia: j * NX + ib + 1] = seg


def fill_disk(buf, cx, cy, r):
    ja, jb = max(0, int(math.ceil(ny_of(cy - r) - 1e-9))), min(NY - 1, int(math.floor(ny_of(cy + r) + 1e-9)))
    for j in range(ja, jb + 1):
        y = OY + GRID * (j - JY0)
        d2 = r * r - (y - cy) ** 2
        if d2 < 0:
            continue
        dx = math.sqrt(d2)
        ia, ib = max(0, int(math.ceil(nx_of(cx - dx) - 1e-9))), min(NX - 1, int(math.floor(nx_of(cx + dx) + 1e-9)))
        if ib >= ia:
            buf[j * NX + ia: j * NX + ib + 1] = b"\x01" * (ib - ia + 1)


def mark(buf, it, e):
    if it.kind == "rect":
        x0, y0, x1, y1 = it.geom
        fill_rect(buf, x0 - e, y0 - e, x1 + e, y1 + e)
    else:
        cx, cy, r = it.geom
        fill_disk(buf, cx, cy, r + e)


class Router:
    def __init__(self, pads):
        self.pads = pads
        self.items = []
        self.tracks = []     # (net, layer, [(x,y)...], w)
        self.vias = []       # (net, x, y)
        for p in pads:
            if p.tipo == "npth":
                self.items.append(Item("__hole", (0, 1), "disk", (p.x, p.y, p.w / 2 + 0.35), clr=0))
            else:
                g = ("disk", (p.x, p.y, p.w / 2)) if p.round else ("rect", (p.x - p.w / 2, p.y - p.h / 2, p.x + p.w / 2, p.y + p.h / 2))
                self.items.append(Item(p.net or ("__nc_" + p.ref + p.nome), p.layers, g[0], g[1], ispad=True))
        for (mx, my) in M3:
            x, y = K(mx, my)
            self.items.append(Item("__m3", (0, 1), "disk", (x, y, 2.9), clr=0.0))
        xs = [K(*p)[0] for p in ANT_POLY]
        # antenna: due rettangoli
        self.items.append(Item("__ant", (0, 1), "rect", (7.0, -32.5, 17.8, -24.2), clr=0.02))
        self.items.append(Item("__ant", (0, 1), "rect", (4.8, -32.5, 7.0, -27.2), clr=0.02))

    # -- mappe ----------------------------------------------------------
    def mappe(self, net, w):
        bl = [bytearray(NX * NY), bytearray(NX * NY)]
        vb = bytearray(NX * NY)
        for it in self.items:
            if it.net == net:
                if it.ispad:
                    mark(vb, it, 0.5 if it.ispad == "via" else VIA_D / 2 + 0.05)      # via mai dentro le piazzole
                continue
            c = CLR if it.clr is None else it.clr
            for L in it.layers:
                mark(bl[L], it, c + w / 2 + it.hw)
                mark(vb, it, c + VIA_D / 2 + it.hw)
        # bordo scheda
        for buf, ee in ((bl[0], EDGE + w / 2), (bl[1], EDGE + w / 2), (vb, EDGE + VIA_D / 2)):
            fill_rect(buf, -5, -70, ee - 0.0001, 10)                       # x < ee
            fill_rect(buf, W_BRD - ee + 0.0001, -70, W_BRD + 5, 10)
            fill_rect(buf, -5, -L_BRD - 5, W_BRD + 5, -L_BRD + ee - 0.0001)
            fill_rect(buf, -5, -ee + 0.0001, W_BRD + 5, 10)
        return bl, vb

    def access(self, p, bl, w):
        res = []
        for L in p.layers:
            if p.round:
                r = p.w / 2 - 0.05
                mk = lambda x, y: (x - p.x) ** 2 + (y - p.y) ** 2 <= r * r
            else:
                mk = lambda x, y: abs(x - p.x) <= p.w / 2 - 0.02 and abs(y - p.y) <= p.h / 2 - 0.02
            ia, ib = int(nx_of(p.x - p.w / 2)) - 1, int(nx_of(p.x + p.w / 2)) + 2
            ja, jb = int(ny_of(p.y - p.h / 2)) - 1, int(ny_of(p.y + p.h / 2)) + 2
            for j in range(ja, jb + 1):
                for i in range(ia, ib + 1):
                    if 0 <= i < NX and 0 <= j < NY:
                        x, y = node_xy(i, j)
                        if mk(x, y) and not bl[L][j * NX + i]:
                            res.append((L, i, j))
        return res

    # -- A* -------------------------------------------------------------
    def astar(self, sources, goals_fn, h_target, bl, vb, w, gnd_mode=False):
        N = NX * NY
        INF = 1e18
        g = {}
        prev = {}
        pq = []
        for s in sources:
            k = s[0] * N + s[2] * NX + s[1]
            g[k] = 0.0
            heapq.heappush(pq, (self.h(s, h_target), 0.0, k))
        DIRS = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
                (1, 1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142), (-1, -1, 1.4142)]
        done = set()
        while pq:
            f, gc, k = heapq.heappop(pq)
            if k in done:
                continue
            done.add(k)
            L, rem = divmod(k, N)
            iy, ix = divmod(rem, NX)
            if goals_fn(L, ix, iy):
                path = [k]
                while path[-1] in prev:
                    path.append(prev[path[-1]])
                path.reverse()
                return path
            mult = 1.0 if L == 0 else 1.35
            for dx, dy, c in DIRS:
                jx, jy = ix + dx, iy + dy
                if jx < 0 or jy < 0 or jx >= NX or jy >= NY:
                    continue
                if bl[L][jy * NX + jx]:
                    continue
                if dx and dy:
                    # niente diagonali che sfiorano ostacoli
                    if bl[L][iy * NX + jx] or bl[L][jy * NX + ix]:
                        continue
                k2 = L * N + jy * NX + jx
                if k2 in done:
                    continue
                ng = gc + c * mult
                if ng < g.get(k2, INF):
                    g[k2] = ng
                    prev[k2] = k
                    heapq.heappush(pq, (ng + self.h((L, jx, jy), h_target), ng, k2))
            # via
            if not vb[iy * NX + ix] and not bl[1 - L][iy * NX + ix]:
                k2 = (1 - L) * N + iy * NX + ix
                if k2 not in done:
                    ng = gc + 14.0
                    if ng < g.get(k2, INF):
                        g[k2] = ng
                        prev[k2] = k
                        heapq.heappush(pq, (ng + self.h((1 - L, ix, iy), h_target), ng, k2))
        return None

    @staticmethod
    def h(s, t):
        if t is None:
            return 0.0
        dx, dy = abs(s[1] - t[0]), abs(s[2] - t[1])
        return (max(dx, dy) + 0.4142 * min(dx, dy)) * 0.95

    # -- una net --------------------------------------------------------
    def route_net(self, net, w):
        pads = [p for p in self.pads if p.net == net]
        gnd = (net == "GND")
        if gnd:
            pads = [p for p in pads if p.tipo == "smd"]
        if not gnd and len(pads) < 2:
            return True
        bl, vb = self.mappe(net, w)
        N = NX * NY
        ok = True
        if gnd:
            for p in pads:
                src = self.access(p, bl, w)
                tgt = (nx_of(p.x), ny_of(p.y))
                path = self.astar(src, lambda L, i, j: L == 0 and not vb[j * NX + i] and not self._in_any_pad(i, j),
                                  None, bl, vb, w)
                if not path:
                    print("  GND: nessun via per", p.ref, p.nome)
                    ok = False
                    continue
                self.emit(net, path, w, add_final_via=True)
                bl, vb = self.mappe(net, w)
            return ok
        tree = set()
        first = pads[0]
        for a in self.access(first, bl, w):
            tree.add(a)
        if not tree:
            print("  nessun nodo di accesso per", first.ref, first.nome)
            return False
        rest = pads[1:]
        acc = {}
        for p in rest:
            acc[id(p)] = set(self.access(p, bl, w))
            if not acc[id(p)]:
                print("  nessun nodo di accesso per", p.ref, p.nome, "(w=%.2f)" % w)
                return False
        goalmap = {}
        while rest:
            goalmap = {}
            for p in rest:
                for a in acc[id(p)]:
                    goalmap[a[0] * N + a[2] * NX + a[1]] = p
            cx = sum(p.x for p in rest) / len(rest)
            cy = sum(p.y for p in rest) / len(rest)
            path = self.astar(list(tree), lambda L, i, j: (L * N + j * NX + i) in goalmap, None, bl, vb, w)
            if not path:
                return False
            endp = goalmap[path[-1]]
            self.emit(net, path, w)
            for k in path:
                L, rem = divmod(k, N)
                j, i = divmod(rem, NX)
                tree.add((L, i, j))
            for a in acc[id(endp)]:
                tree.add(a)
            rest.remove(endp)
            # le mappe non cambiano per la stessa net (le sue piste non sono ostacoli)
        return True

    def _in_any_pad(self, i, j):
        x, y = node_xy(i, j)
        for p in self.pads:
            if p.tipo == "npth":
                continue
            if p.round:
                if (x - p.x) ** 2 + (y - p.y) ** 2 <= (p.w / 2 + VIA_D / 2) ** 2:
                    return True
            else:
                if abs(x - p.x) <= p.w / 2 + VIA_D / 2 and abs(y - p.y) <= p.h / 2 + VIA_D / 2:
                    return True
        return False

    def emit(self, net, path, w, add_final_via=False):
        N = NX * NY
        pts = []
        for k in path:
            L, rem = divmod(k, N)
            j, i = divmod(rem, NX)
            pts.append((L, i, j))
        # spezza a ogni cambio di strato
        cur = [pts[0]]
        runs = []
        for a in pts[1:]:
            if a[0] != cur[-1][0]:
                runs.append(cur)
                self.vias.append((net, node_xy(a[1], a[2])))
                self.items.append(Item(net, (0, 1), "disk", (*node_xy(a[1], a[2]), VIA_D / 2), ispad="via"))
                cur = [a]
            else:
                cur.append(a)
        runs.append(cur)
        if add_final_via:
            L, i, j = pts[-1]
            self.vias.append((net, node_xy(i, j)))
            self.items.append(Item(net, (0, 1), "disk", (*node_xy(i, j), VIA_D / 2), ispad="via"))
        for run in runs:
            L = run[0][0]
            # semplifica i tratti collineari
            poly = [run[0]]
            for a in run[1:]:
                if len(poly) >= 2:
                    p0, p1 = poly[-2], poly[-1]
                    if (p1[1] - p0[1], p1[2] - p0[2]) == (a[1] - p1[1], a[2] - p1[2]):
                        poly[-1] = a
                        continue
                poly.append(a)
            xy = [node_xy(a[1], a[2]) for a in poly]
            if len(xy) >= 2:
                self.tracks.append((net, L, xy, w))
            for (a, b) in zip(run[:-1], run[1:]):
                pass
            # ostacoli: dischi lungo i nodi del percorso
            for a in run:
                x, y = node_xy(a[1], a[2])
                self.items.append(Item(net, (L,), "disk", (x, y, w / 2)))
            # tra due nodi adiacenti la copertura e' continua (passo 0,127 < raggio)


# ---------------------------------------------------------------------------
# Scrittura del file KiCad
# ---------------------------------------------------------------------------
def fmt(v):
    s = ("%.4f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def scrivi(pads, router, nets_idx, path):
    L = []
    a = L.append
    a('(kicad_pcb (version 20240108) (generator "genera_pcb.py") (generator_version "8.0")')
    a('  (general (thickness 1.6) (legacy_teardrops no))')
    a('  (paper "A4")')
    a('  (layers (0 "F.Cu" signal) (31 "B.Cu" signal) (32 "B.Adhes" user "B.Adhesive") (33 "F.Adhes" user "F.Adhesive")')
    a('    (34 "B.Paste" user) (35 "F.Paste" user) (36 "B.SilkS" user "B.Silkscreen") (37 "F.SilkS" user "F.Silkscreen")')
    a('    (38 "B.Mask" user) (39 "F.Mask" user) (40 "Dwgs.User" user "User.Drawings") (41 "Cmts.User" user "User.Comments")')
    a('    (44 "Edge.Cuts" user) (45 "Margin" user) (46 "B.CrtYd" user "B.Courtyard") (47 "F.CrtYd" user "F.Courtyard")')
    a('    (48 "B.Fab" user "B.Fabrication") (49 "F.Fab" user "F.Fabrication"))')
    a('  (setup (pad_to_mask_clearance 0) (allow_soldermask_bridges_in_footprints no)')
    a('    (pcbplotparams (layerselection 0x00010fc_ffffffff) (plot_on_all_layers_selection 0x0000000_00000000) (disableapertmacros no)')
    a('      (usegerberextensions no) (usegerberattributes yes) (usegerberadvancedattributes yes) (creategerberjobfile yes)')
    a('      (dashed_line_dash_ratio 12.0) (dashed_line_gap_ratio 3.0) (svgprecision 4) (plotframeref no) (viasonmask no) (mode 1)')
    a('      (useauxorigin no) (hpglpennumber 1) (hpglpenspeed 20) (hpglpendiameter 15.0) (pdf_front_fp_property_popups yes)')
    a('      (pdf_back_fp_property_popups yes) (dxfpolygonmode yes) (dxfimperialunits yes) (dxfusepcbnewfont yes) (psnegative no)')
    a('      (psa4output no) (plotreference yes) (plotvalue yes) (plotfptext yes) (plotinvisibletext no) (sketchpadsonfab no)')
    a('      (subtractmaskfromsilk no) (outputformat 1) (mirror no) (drillshape 0) (scaleselection 1) (outputdirectory "")))')
    a('  (net 0 "")')
    for n, i in nets_idx.items():
        a('  (net %d "%s")' % (i, n))

    def netref(n):
        if n is None or n not in nets_idx:
            return ""
        return '(net %d "%s")' % (nets_idx[n], n)

    for ref, (fpn, val, xd, yd, rot) in PLACE.items():
        spec = FP.get(fpn)
        plist = spec["pads"] if spec else HEADERS[fpn]
        attr = (spec or {"attr": "th"})["attr"]
        x, y = K(xd, yd)
        a('  (footprint "YTC:%s" (layer "F.Cu") (uuid "%s") (at %s %s %s)' % (fpn, U(), fmt(x), fmt(y), fmt(rot) if rot else "0"))
        if attr == "smd":
            a('    (attr smd)')
        elif fpn == "M3_HOLE":
            a('    (attr through_hole exclude_from_pos_files exclude_from_bom)')
        else:
            a('    (attr through_hole exclude_from_pos_files exclude_from_bom)')
        a('    (property "Reference" "%s" (at 0 -2.2 0) (layer "F.Fab") (uuid "%s") (effects (font (size 0.8 0.8) (thickness 0.12))))' % (ref, U()))
        a('    (property "Value" "%s" (at 0 2.2 0) (layer "F.Fab") (uuid "%s") (effects (font (size 0.8 0.8) (thickness 0.12))))' % (val, U()))
        if spec and "body" in spec:
            x0, y0, x1, y1 = spec["body"]
            a('    (fp_rect (start %s %s) (end %s %s) (stroke (width 0.1) (type default)) (fill none) (layer "F.Fab") (uuid "%s"))' %
              (fmt(x0), fmt(y0), fmt(x1), fmt(y1), U()))
        for (nome, tipo, px, py, w, h, dr) in plist:
            pp = [q for q in pads if q.ref == ref and q.nome == nome][0]
            n = netref(pp.net)
            rr = fmt(rot) if rot else "0"
            if tipo == "smd":
                a('    (pad "%s" smd roundrect (at %s %s %s) (size %s %s) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.2) %s (uuid "%s"))' %
                  (nome, fmt(px), fmt(py), rr, fmt(w), fmt(h), n, U()))
            elif tipo == "npth":
                a('    (pad "" np_thru_hole circle (at 0 0) (size %s %s) (drill %s) (layers "*.Cu" "*.Mask") (uuid "%s"))' % (fmt(w), fmt(h), fmt(dr), U()))
            else:
                shape = "rect" if tipo == "thts" else "circle"
                a('    (pad "%s" thru_hole %s (at %s %s %s) (size %s %s) (drill %s) (layers "*.Cu" "*.Mask") (remove_unused_layers no) %s%s (uuid "%s"))' %
                  (nome, shape, fmt(px), fmt(py), rr, fmt(w), fmt(h), fmt(dr), n, " (zone_connect 2)" if (ref, nome) in SOLID else "", U()))
        a('  )')
    # piste
    def netid(n):
        return "(net %d)" % nets_idx[n]

    for (net, Lr, xy, w) in router.tracks:
        for p0, p1 in zip(xy[:-1], xy[1:]):
            a('  (segment (start %s %s) (end %s %s) (width %s) (layer "%s") %s (uuid "%s"))' %
              (fmt(p0[0]), fmt(p0[1]), fmt(p1[0]), fmt(p1[1]), fmt(w), "F.Cu" if Lr == 0 else "B.Cu", netid(net), U()))
    for (net, (x, y)) in router.vias:
        a('  (via (at %s %s) (size %s) (drill %s) (layers "F.Cu" "B.Cu") %s (uuid "%s"))' % (fmt(x), fmt(y), fmt(VIA_D), fmt(VIA_DRILL), netid(net), U()))
    # contorno
    a('  (gr_rect (start 0 0) (end %s %s) (stroke (width 0.1) (type default)) (fill none) (layer "Edge.Cuts") (uuid "%s"))' %
      (fmt(W_BRD), fmt(-L_BRD), U()))
    # serigrafia
    for (txt, xd, yd, rot, sz) in SILK:
        x, y = K(xd, yd)
        a('  (gr_text "%s" (at %s %s %s) (layer "F.SilkS") (uuid "%s") (effects (font (size %s %s) (thickness 0.15)) (justify left)))' %
          (txt, fmt(x), fmt(y), fmt(rot), U(), fmt(sz), fmt(sz)))
    for (x0, y0, x1, y1) in RECTS:
        a('  (gr_rect (start %s %s) (end %s %s) (stroke (width 0.15) (type default)) (fill none) (layer "F.SilkS") (uuid "%s"))' %
          (fmt(x0), fmt(-y0), fmt(x1), fmt(-y1), U()))
    # zona di massa su B.Cu
    gi = nets_idx["GND"]
    a('  (zone (net %d) (net_name "GND") (layer "B.Cu") (uuid "%s") (hatch edge 0.5)' % (gi, U()))
    a('    (connect_pads (clearance 0.25)) (min_thickness 0.25) (filled_areas_thickness no)')
    a('    (fill yes (thermal_gap 0.3) (thermal_bridge_width 0.4) (island_removal_mode 0))')
    a('    (polygon (pts (xy 0 0) (xy %s 0) (xy %s %s) (xy 0 %s))))' % (fmt(W_BRD), fmt(W_BRD), fmt(-L_BRD), fmt(-L_BRD)))
    # antenna: keepout su entrambi gli strati
    pts = " ".join("(xy %s %s)" % (fmt(x), fmt(-y)) for (x, y) in ANT_POLY)
    a('  (zone (net 0) (net_name "") (layers "F.Cu" "B.Cu") (uuid "%s") (name "KEEPOUT_ANTENNA") (hatch edge 0.5)' % U())
    a('    (connect_pads (clearance 0)) (min_thickness 0.25) (filled_areas_thickness no)')
    a('    (keepout (tracks not_allowed) (vias not_allowed) (pads allowed) (copperpour not_allowed) (footprints allowed))')
    a('    (fill (thermal_gap 0.5) (thermal_bridge_width 0.5))')
    a('    (polygon (pts %s)))' % pts)
    a(')')
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")


PRO = """{
  "board": {
    "design_settings": {
      "defaults": {"board_outline_line_width": 0.1, "copper_line_width": 0.2, "copper_text_size_h": 1.5, "copper_text_size_v": 1.5,
        "copper_text_thickness": 0.3, "other_line_width": 0.1, "silk_line_width": 0.15, "silk_text_size_h": 1.0,
        "silk_text_size_v": 1.0, "silk_text_thickness": 0.15},
      "rules": {"min_clearance": 0.127, "min_copper_edge_clearance": 0.3, "min_hole_clearance": 0.25, "min_hole_to_hole": 0.5,
        "min_microvia_diameter": 0.2, "min_microvia_drill": 0.1, "min_resolved_spokes": 2, "min_silk_clearance": 0.0,
        "min_through_hole_diameter": 0.3, "min_track_width": 0.127, "min_via_annular_width": 0.13, "min_via_diameter": 0.5,
        "use_height_for_length_calcs": true},
      "rule_severities": {"lib_footprint_issues": "ignore", "lib_footprint_mismatch": "ignore", "silk_over_copper": "ignore", "silk_overlap": "ignore", "silk_edge_clearance": "ignore"}
    }
  },
  "meta": {"filename": "youtube_controller.kicad_pro", "version": 3},
  "net_settings": {
    "classes": [{"name": "Default", "clearance": 0.15, "track_width": 0.25, "via_diameter": 0.6, "via_drill": 0.3,
                 "microvia_diameter": 0.3, "microvia_drill": 0.1, "diff_pair_gap": 0.25, "diff_pair_width": 0.2, "diff_pair_via_gap": 0.25,
                 "wire_width": 6, "bus_width": 12, "line_style": 0, "pcb_color": "rgba(0, 0, 0, 0.000)", "schematic_color": "rgba(0, 0, 0, 0.000)"}],
    "meta": {"version": 3},
    "net_colors": null,
    "netclass_assignments": null,
    "netclass_patterns": []
  },
  "sheets": [],
  "text_variables": {}
}
"""


def main():
    pads = costruisci_pad()
    nets = list(NETS.keys())
    nets_idx = {n: i + 1 for i, n in enumerate(nets)}
    R = Router(pads)
    ordine = ROUTE_ORDER
    falliti = []
    for net in ordine:
        wid = [W_PWR, 0.35, W_SIG] if net in POWER_NETS else [W_SIG]
        ok = False
        for w in wid:
            # annulla tracce parziali di tentativi precedenti
            n_t, n_v, n_i = len(R.tracks), len(R.vias), len(R.items)
            ok = R.route_net(net, w)
            if ok:
                print("OK  %-8s w=%.2f" % (net, w))
                break
            del R.tracks[n_t:], R.vias[n_v:], R.items[n_i:]
        if not ok:
            print("FALLITO", net)
            falliti.append(net)
    os.makedirs(OUT, exist_ok=True)
    scrivi(pads, R, nets_idx, os.path.join(OUT, "youtube_controller.kicad_pcb"))
    with open(os.path.join(OUT, "youtube_controller.kicad_pro"), "w", encoding="utf-8") as f:
        f.write(PRO)
    print("tracce %d, via %d, falliti: %s" % (len(R.tracks), len(R.vias), falliti))
    return 1 if falliti else 0


if __name__ == "__main__":
    sys.exit(main())
