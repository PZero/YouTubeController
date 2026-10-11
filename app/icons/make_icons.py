#!/usr/bin/env python3
"""Genera le icone della PWA: icon.svg (sorgente vettoriale) e tutte le PNG.

Solo libreria standard (nessun Pillow/cairosvg): la stessa geometria viene scritta
come SVG e rasterizzata qui (pittore su griglia 2048 px, poi media per area = antialias).

Uso (dalla radice del repo):  python app/icons/make_icons.py
Disegno: scatola del controller vista dall'alto con manopola zigrinata (tacca
indicatrice + freccia di rotazione) e pulsante tondo rosso con triangolo "play".
Sfondo pieno (iOS riempie di nero le trasparenze).
"""
import math
import os
import struct
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
U = 512  # unita' di disegno (viewBox 0 0 512 512)

BG = '#0f1115'
BOX = '#262b33'
BOX_EDGE = '#343a44'
KNOB = '#c9ced6'
KNOB_CAP = '#e8eaed'
DARK = '#16181d'
ARC = '#0a84ff'
BTN = '#ff453a'
WHITE = '#ffffff'

KX, KY = 190, 262        # centro manopola
BX, BY = 362, 262        # centro pulsante
N_TEETH = 20


def shapes(scale=1.0, cx=256, cy=256):
    """Lista di primitive (in unita' 512) dal fondo verso l'alto.
    scale<1 restringe il soggetto attorno al centro (versione maskable)."""
    def P(x, y):
        return (cx + (x - 256) * scale, cy + (y - 256) * scale)

    def S(v):
        return v * scale

    out = []
    # scatola (vista dall'alto, leggero bordo per dare volume)
    x0, y0 = P(48, 150)
    x1, y1 = P(464, 374)
    out.append(('rrect', BOX_EDGE, x0, y0, x1, y1, S(52)))
    x0, y0 = P(56, 150)
    x1, y1 = P(456, 362)
    out.append(('rrect', BOX, x0, y0, x1, y1, S(46)))
    # freccia di rotazione attorno alla manopola (arco in alto, punta a destra)
    kx, ky = P(KX, KY)
    out.append(('arc', ARC, kx, ky, S(104), S(12), -158, -52))
    a = math.radians(-52)
    tipx, tipy = kx + S(104) * math.cos(a), ky + S(104) * math.sin(a)
    tx, ty = -math.sin(a), math.cos(a)          # tangente (verso orario)
    nx, ny = math.cos(a), math.sin(a)           # normale radiale
    L, W = S(30), S(22)
    out.append(('poly', ARC, [
        (tipx + tx * L, tipy + ty * L),
        (tipx + nx * W, tipy + ny * W),
        (tipx - nx * W, tipy - ny * W),
    ]))
    # manopola zigrinata: disco + denti (dischi piccoli sul bordo)
    out.append(('circle', KNOB, kx, ky, S(70)))
    for i in range(N_TEETH):
        t = 2 * math.pi * i / N_TEETH
        out.append(('circle', KNOB, kx + S(70) * math.cos(t), ky + S(70) * math.sin(t), S(9)))
    out.append(('circle', KNOB_CAP, kx, ky, S(54)))
    # tacca indicatrice
    out.append(('capsule', DARK, kx, ky - S(46), kx, ky - S(18), S(6)))
    # pulsante
    bx, by = P(BX, BY)
    out.append(('circle', DARK, bx, by, S(52)))
    out.append(('circle', BTN, bx, by, S(46)))
    r = S(22)
    out.append(('poly', WHITE, [
        (bx - r * 0.55, by - r * 0.85),
        (bx - r * 0.55, by + r * 0.85),
        (bx + r * 0.95, by),
    ]))
    return out


# ---------------------------------------------------------------- SVG
def to_svg(prims):
    f = lambda v: f'{v:.2f}'.rstrip('0').rstrip('.')
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {U} {U}" width="{U}" height="{U}">',
             f'<rect width="{U}" height="{U}" fill="{BG}"/>']
    for p in prims:
        k, col = p[0], p[1]
        if k == 'rrect':
            _, _, x0, y0, x1, y1, r = p
            parts.append(f'<rect x="{f(x0)}" y="{f(y0)}" width="{f(x1-x0)}" height="{f(y1-y0)}" rx="{f(r)}" fill="{col}"/>')
        elif k == 'circle':
            _, _, x, y, r = p
            parts.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{col}"/>')
        elif k == 'poly':
            pts = ' '.join(f'{f(x)},{f(y)}' for x, y in p[2])
            parts.append(f'<polygon points="{pts}" fill="{col}"/>')
        elif k == 'capsule':
            _, _, xa, ya, xb, yb, r = p
            parts.append(f'<line x1="{f(xa)}" y1="{f(ya)}" x2="{f(xb)}" y2="{f(yb)}" stroke="{col}" stroke-width="{f(2*r)}" stroke-linecap="round"/>')
        elif k == 'arc':
            _, _, x, y, r, w, a0, a1 = p
            sx, sy = x + r * math.cos(math.radians(a0)), y + r * math.sin(math.radians(a0))
            ex, ey = x + r * math.cos(math.radians(a1)), y + r * math.sin(math.radians(a1))
            large = 1 if (a1 - a0) % 360 > 180 else 0
            parts.append(f'<path d="M{f(sx)} {f(sy)}A{f(r)} {f(r)} 0 {large} 1 {f(ex)} {f(ey)}" fill="none" stroke="{col}" stroke-width="{f(w)}" stroke-linecap="round"/>')
    parts.append('</svg>')
    return '\n'.join(parts) + '\n'


# ---------------------------------------------------------------- raster
HI = 2048  # griglia di lavoro


def rgb(h):
    return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))


def render(prims):
    k = HI / U
    buf = bytearray(bytes(rgb(BG)) * (HI * HI))

    def paint(col, x0, y0, x1, y1, inside):
        c = bytes(rgb(col))
        for j in range(max(0, int(y0 * k)), min(HI, int(y1 * k) + 2)):
            y = (j + 0.5) / k
            row = j * HI
            for i in range(max(0, int(x0 * k)), min(HI, int(x1 * k) + 2)):
                if inside((i + 0.5) / k, y):
                    o = (row + i) * 3
                    buf[o:o + 3] = c

    for p in prims:
        kind, col = p[0], p[1]
        if kind == 'rrect':
            _, _, x0, y0, x1, y1, r = p
            def ins(x, y, x0=x0, y0=y0, x1=x1, y1=y1, r=r):
                dx = max(x0 + r - x, 0, x - (x1 - r))
                dy = max(y0 + r - y, 0, y - (y1 - r))
                return dx * dx + dy * dy <= r * r
            paint(col, x0, y0, x1, y1, ins)
        elif kind == 'circle':
            _, _, cx, cy, r = p
            paint(col, cx - r, cy - r, cx + r, cy + r,
                  lambda x, y, cx=cx, cy=cy, r=r: (x - cx) ** 2 + (y - cy) ** 2 <= r * r)
        elif kind == 'capsule':
            _, _, xa, ya, xb, yb, r = p
            def ins(x, y, xa=xa, ya=ya, xb=xb, yb=yb, r=r):
                vx, vy = xb - xa, yb - ya
                t = max(0, min(1, ((x - xa) * vx + (y - ya) * vy) / (vx * vx + vy * vy)))
                return (x - xa - t * vx) ** 2 + (y - ya - t * vy) ** 2 <= r * r
            paint(col, min(xa, xb) - r, min(ya, yb) - r, max(xa, xb) + r, max(ya, yb) + r, ins)
        elif kind == 'poly':
            pts = p[2]
            def ins(x, y, pts=pts):
                s = []
                for a in range(3):
                    (x1, y1), (x2, y2) = pts[a], pts[(a + 1) % 3]
                    s.append((x2 - x1) * (y - y1) - (y2 - y1) * (x - x1))
                return all(v >= 0 for v in s) or all(v <= 0 for v in s)
            xs, ys = [q[0] for q in pts], [q[1] for q in pts]
            paint(col, min(xs), min(ys), max(xs), max(ys), ins)
        elif kind == 'arc':
            _, _, cx, cy, r, w, a0, a1 = p
            ends = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in (a0, a1)]
            def ins(x, y, cx=cx, cy=cy, r=r, w=w, a0=a0, a1=a1, ends=ends):
                ang = math.degrees(math.atan2(y - cy, x - cx))
                if a0 <= ang <= a1 and abs(math.hypot(x - cx, y - cy) - r) <= w / 2:
                    return True
                return any((x - ex) ** 2 + (y - ey) ** 2 <= (w / 2) ** 2 for ex, ey in ends)
            paint(col, cx - r - w, cy - r - w, cx + r + w, cy + r + w, ins)
    return buf


def downsample(buf, n):
    sums = [0] * (n * n * 3)
    cnt = [0] * (n * n)
    xmap = [i * n // HI for i in range(HI)]
    for j in range(HI):
        ty = (j * n // HI) * n
        row = j * HI * 3
        for i in range(HI):
            t = ty + xmap[i]
            o = row + i * 3
            t3 = t * 3
            sums[t3] += buf[o]
            sums[t3 + 1] += buf[o + 1]
            sums[t3 + 2] += buf[o + 2]
            cnt[t] += 1
    out = bytearray()
    for y in range(n):
        out.append(0)  # filtro PNG: nessuno
        for x in range(n):
            t = y * n + x
            c = cnt[t]
            out += bytes((sums[t * 3] // c, sums[t * 3 + 1] // c, sums[t * 3 + 2] // c))
    return out


def write_png(path, n, raw):
    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    data = (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', n, n, 8, 2, 0, 0, 0))  # RGB, niente alfa
            + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
            + chunk(b'IEND', b''))
    with open(path, 'wb') as fh:
        fh.write(data)


def main():
    normal = shapes()
    with open(os.path.join(HERE, 'icon.svg'), 'w', encoding='utf-8') as fh:
        fh.write(to_svg(normal))
    hi = render(normal)
    for n, name in [(180, 'apple-touch-icon.png'), (167, 'apple-touch-icon-167.png'),
                    (152, 'apple-touch-icon-152.png'), (192, 'icon-192.png'),
                    (512, 'icon-512.png'), (32, 'favicon-32.png')]:
        write_png(os.path.join(HERE, name), n, downsample(hi, n))
        print('scritto', name)
    # maskable: soggetto ridotto al 78% per stare nella zona sicura (cerchio dell'80% centrale)
    hi = render(shapes(scale=0.78))
    write_png(os.path.join(HERE, 'icon-maskable-512.png'), 512, downsample(hi, 512))
    print('scritto icon-maskable-512.png')


if __name__ == '__main__':
    main()
