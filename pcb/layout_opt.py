#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Posizionamento automatico (simulated annealing, seme fisso) dei componenti SMD nella zona libera del retro.
   Scrive layout_pcb.py (MOV). Uso: python layout_opt.py [seme] [iterazioni]"""
import math, random, sys, os
QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
from netlist_pcb import PARTI, NETS

FPPADS = {  # (px,py,w,h) locali
    "R_0805": [(-0.9125, 0, 1.025, 1.4), (0.9125, 0, 1.025, 1.4)],
    "C_0805": [(-0.9125, 0, 1.025, 1.4), (0.9125, 0, 1.025, 1.4)],
    "C_1206": [(-1.475, 0, 1.05, 1.75), (1.475, 0, 1.05, 1.75)],
    "SOT-23": [(-0.95, 1.0, 0.7, 1.0), (0.95, 1.0, 0.7, 1.0), (0.0, -1.0, 0.7, 1.0)],
    "D_SMA": [(-2.0, 0, 2.5, 1.8), (2.0, 0, 2.5, 1.8)],
}
FIXED_PADS = {   # pad fissi: (net-ref) -> (x, y) doc
}
XMIN, XMAX, YMIN, YMAX = 7.7, 19.5, 33.4, 53.0
MARG = 0.55      # distanza minima tra i corpi (corpo = estensione delle piazzole)

def padpos(fp, rot, x, y, i):
    px, py, w, h = FPPADS[fp][i]
    t = math.radians(rot); c, s = round(math.cos(t), 6), round(math.sin(t), 6)
    gx, gy = px * c + py * s, -px * s + py * c      # KiCad (y giu')
    if int(rot) % 180 == 90: w, h = h, w
    return (x + gx, y - gy, w, h)                    # doc: y = y_doc

def box(fp, rot, x, y):
    ps = [padpos(fp, rot, x, y, i) for i in range(len(FPPADS[fp]))]
    return (min(p[0]-p[2]/2 for p in ps), min(p[1]-p[3]/2 for p in ps), max(p[0]+p[2]/2 for p in ps), max(p[1]+p[3]/2 for p in ps))

# punti fissi (doc) per l'attrazione
def hole(c, r): return (3.49 + c*2.54, 5.87 + (r-1)*2.54)
FIX = {}
for r in range(5):
    for c in range(2):
        FIX[("J1", str(2*r+c+1))] = (3.49 + c*2.54, 36.35 + r*2.54)
for c in range(4): FIX[("J2", str(c+1))] = (8.0 + c*2.54, 57.0)
smmap = {"H1":(21.27,5.87),"H2":(21.27,8.41),"H3":(21.27,10.95),"H7":(21.27,21.11),"H8":(21.27,23.65),"H9":(21.27,26.19),
         "B3":(6.03,10.95),"B4":(6.03,13.49)}
for k, v in smmap.items(): FIX[("SM", k)] = (v[0], min(v[1], 31.0))   # attrazione verso il bordo della zona libera

refs = list(PARTI.keys())
FIXBOX = [(2.5, 35.5, 7.7, 47.5), (7.5, 55.5, 17.8, 58.5)]   # J1 e J2 (J2 + margine)

def cost(st):
    boxes = {r: box(PARTI[r][0], *st[r][2:4] if False else (st[r][2], st[r][0], st[r][1])) for r in refs}
    pos = {}
    for r in refs:
        fp = PARTI[r][0]
        for i in range(len(FPPADS[fp])):
            pos[(r, str(i+1))] = padpos(fp, st[r][2], st[r][0], st[r][1], i)[:2]
    c = 0.0
    for net, lst in NETS.items():
        if net == "GND": w = 0.15
        elif net in ("VBAT", "LEDP"): w = 1.3
        else: w = 1.0
        pts = []
        for (r, p) in lst:
            k = (r, str(p))
            if k in pos: pts.append(pos[k])
            elif k in FIX: pts.append(FIX[k])
        if len(pts) > 1:
            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
            c += w * ((max(xs)-min(xs)) + 1.1*(max(ys)-min(ys)))
    rs = list(boxes)
    for i in range(len(rs)):
        a = boxes[rs[i]]
        if a[0] < XMIN: c += 400*(XMIN-a[0])
        if a[2] > XMAX: c += 400*(a[2]-XMAX)
        if a[1] < YMIN: c += 400*(YMIN-a[1])
        if a[3] > YMAX: c += 400*(a[3]-YMAX)
        for fb in FIXBOX:
            ox = min(a[2], fb[2]) - max(a[0], fb[0]); oy = min(a[3], fb[3]) - max(a[1], fb[1])
            if ox > -MARG and oy > -MARG: c += 300*(ox+MARG)*(oy+MARG)
        for j in range(i+1, len(rs)):
            b = boxes[rs[j]]
            ox = min(a[2], b[2]) - max(a[0], b[0]); oy = min(a[3], b[3]) - max(a[1], b[1])
            if ox > -MARG and oy > -MARG: c += 300*(ox+MARG)*(oy+MARG)
    return c

def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    iters = int(sys.argv[2]) if len(sys.argv) > 2 else 120000
    random.seed(seed)
    st = {r: [random.uniform(XMIN+2, XMAX-2), random.uniform(YMIN+2, YMAX-2), random.choice([0, 90, 180, 270])] for r in refs}
    cur = cost(st); best = cur; bst = {k: v[:] for k, v in st.items()}
    T0 = 20.0
    for it in range(iters):
        T = T0 * (1 - it/iters)**2 + 0.01
        r = random.choice(refs)
        old = st[r][:]
        m = random.random()
        if m < 0.6:
            st[r][0] += random.gauss(0, 1.2*T/T0 + 0.15); st[r][1] += random.gauss(0, 1.2*T/T0 + 0.15)
        elif m < 0.8:
            st[r][2] = (st[r][2] + random.choice([90, 180, 270])) % 360
        else:
            r2 = random.choice(refs); old2 = st[r2][:]
            st[r][0], st[r][1], st[r2][0], st[r2][1] = st[r2][0], st[r2][1], st[r][0], st[r][1]
            n = cost(st)
            if n < cur or random.random() < math.exp((cur-n)/T): cur = n
            else: st[r][:] = old; st[r2][:] = old2
            if cur < best: best = cur; bst = {k: v[:] for k, v in st.items()}
            continue
        n = cost(st)
        if n < cur or random.random() < math.exp((cur-n)/T): cur = n
        else: st[r][:] = old
        if cur < best: best = cur; bst = {k: v[:] for k, v in st.items()}
    # arrotonda alla griglia 0,127 (origine come il router) per avere pad quasi sui nodi
    out = []
    for r in refs:
        x, y, rot = bst[r]
        x = round((x - 0.061)/0.127)*0.127 + 0.061
        y = round((y - 5.87)/0.127)*0.127 + 5.87
        out.append("    %r: (%.3f, %.3f, %d)," % (r, x, y, rot))
    open(os.path.join(QUI, "layout_pcb.py"), "w", encoding="utf-8").write("# generato da layout_opt.py (seme %d, costo %.1f)\nMOV = {\n%s\n}\n" % (seed, best, "\n".join(out)))
    print("costo", round(best, 1))

main()
