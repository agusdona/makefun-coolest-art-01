# The Whale That Carried Home -- coolest-art-01, round 6.
# A humpback whale glides through a deep indigo night sky, carrying a small
# cottage with warm glowing windows on its back, sailing above soft clouds
# toward a pale moon, trailing stardust. Pure Python, standard library only.
# Deterministic: fixed seed, no network, no timestamps in the PNG.
import math
import os
import random
import struct
import zlib

W = H = 1024
SEED = 20261112


# ---------------- PNG encoder (stdlib only) ----------------
def _chunk(typ, data):
    c = struct.pack(">I", len(data)) + typ + data
    return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)


def png_bytes(rgb):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)  # filter: none
        raw += rgb[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 6))
            + _chunk(b"IEND", b""))


# ---------------- Canvas ----------------
class Canvas:
    def __init__(self):
        self.p = bytearray(W * H * 3)

    def set(self, x, y, r, g, b):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.p[i] = r
            self.p[i + 1] = g
            self.p[i + 2] = b

    def blend(self, x, y, r, g, b, a):
        if 0 <= x < W and 0 <= y < H and a > 0:
            i = (y * W + x) * 3
            p = self.p
            if a >= 1:
                p[i] = r
                p[i + 1] = g
                p[i + 2] = b
            else:
                p[i] = int(p[i] * (1 - a) + r * a)
                p[i + 1] = int(p[i + 1] * (1 - a) + g * a)
                p[i + 2] = int(p[i + 2] * (1 - a) + b * a)

    def vgrad(self, top, bot):
        for y in range(H):
            t = y / (H - 1)
            r = int(top[0] + (bot[0] - top[0]) * t)
            g = int(top[1] + (bot[1] - top[1]) * t)
            b = int(top[2] + (bot[2] - top[2]) * t)
            base = y * W * 3
            self.p[base:base + W * 3] = bytes((r, g, b)) * W

    def _span(self, y, x0, x1, r, g, b, a):
        if y < 0 or y >= H or x1 < x0:
            return
        x0 = max(0, x0)
        x1 = min(W - 1, x1)
        if x1 < x0:
            return
        p = self.p
        if a >= 1:
            fill = bytes((r, g, b)) * (x1 - x0 + 1)
            base = (y * W + x0) * 3
            p[base:base + (x1 - x0 + 1) * 3] = fill
        else:
            ia = 1 - a
            for x in range(x0, x1 + 1):
                i = (y * W + x) * 3
                p[i] = int(p[i] * ia + r * a)
                p[i + 1] = int(p[i + 1] * ia + g * a)
                p[i + 2] = int(p[i + 2] * ia + b * a)

    def ellipse(self, cx, cy, rx, ry, col, alpha=1.0):
        r, g, b = col
        for y in range(max(0, cy - ry), min(H, cy + ry + 1)):
            dy = (y - cy) / ry
            dx = rx * math.sqrt(max(0.0, 1 - dy * dy))
            self._span(y, int(cx - dx), int(cx + dx), r, g, b, alpha)

    def disc(self, cx, cy, rad, col, alpha=1.0):
        self.ellipse(cx, cy, rad, rad, col, alpha)

    def glow(self, cx, cy, rad, col, steps=5, a=0.09):
        # Soft radial glow: stacked discs, faintest outside, brightest centre.
        for s in range(steps, 0, -1):
            self.disc(cx, cy, int(rad * s / steps), col, a)

    def soft_ellipse(self, cx, cy, rx, ry, col, steps=3, a=0.15):
        # A puff with soft edges: stacked ellipses, faintest outside.
        for s in range(steps, 0, -1):
            self.ellipse(cx, cy, int(rx * s / steps), int(ry * s / steps),
                         col, a)

    def poly(self, pts, col, alpha=1.0):
        # Scanline fill of a simple polygon.
        r, g, b = col
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(H, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if y0 == y1:
                    continue
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            if len(xs) >= 2:
                xs.sort()
                self._span(y, int(xs[0]), int(xs[-1]), r, g, b, alpha)

    def sparkle(self, cx, cy, rad, col):
        # A four-point star: bright core plus thin cross arms.
        self.disc(cx, cy, max(1, rad // 3), col)
        for d in range(1, rad + 1):
            a = 0.9 * (1 - d / (rad + 1))
            self.blend(cx + d, cy, *col, a)
            self.blend(cx - d, cy, *col, a)
            self.blend(cx, cy + d, *col, a)
            self.blend(cx, cy - d, *col, a)


# ---------------- Sky, stars, moon ----------------
SKY_TOP = (9, 11, 40)
SKY_BOT = (40, 46, 100)
MOON = (246, 226, 170)
MOON_GLOW = (250, 232, 185)


def sky(c):
    c.vgrad(SKY_TOP, SKY_BOT)


def stars(c, rng):
    # Scattered stars, denser and brighter near the top.
    for _ in range(210):
        x = rng.randint(8, W - 8)
        y = rng.randint(8, 760)
        bright = rng.random()
        if bright < 0.55:
            col = (235, 238, 255)
            rad = 1
        elif bright < 0.85:
            col = (255, 244, 210)
            rad = 2
        else:
            col = (255, 255, 255)
            rad = 3
        if rng.random() < 0.10:
            c.sparkle(x, y, rad + 3, col)
        else:
            c.disc(x, y, rad, col, 0.9)


def moon(c):
    c.glow(800, 195, 185, MOON_GLOW, steps=6, a=0.07)
    c.disc(800, 195, 92, MOON)
    # Soft shading on the lower-left limb.
    c.disc(770, 225, 78, (232, 210, 152), 0.35)
    # Craters: faint, slightly darker discs.
    c.disc(775, 165, 14, (228, 205, 148), 0.5)
    c.disc(825, 215, 10, (228, 205, 148), 0.5)
    c.disc(805, 160, 7, (228, 205, 148), 0.45)
    c.disc(760, 200, 6, (228, 205, 148), 0.4)

# ---------------- The whale ----------------
WHALE_BODY = (64, 96, 160)
WHALE_BELLY = (110, 140, 190)
WHALE_BACK = (140, 168, 215)
WHALE_DARK = (38, 56, 100)
HOUSE_WALL = (74, 52, 40)
HOUSE_ROOF = (48, 34, 30)
WINDOW = (255, 196, 110)
CLOUD = (150, 155, 205)
CLOUD_DARK = (58, 63, 108)


def whale(c, rng):
    # Silhouette: tapered snout, thick mid-body, narrow tail stalk, fluke.
    body = [
        (815, 540), (790, 495), (760, 470), (650, 428), (550, 415),
        (420, 418), (320, 432), (240, 470), (210, 500),
        (130, 458), (185, 540), (130, 622),
        (210, 585), (240, 600), (320, 645), (430, 665), (550, 670),
        (660, 655), (760, 620), (805, 580),
    ]
    c.poly(body, WHALE_BODY)
    # Belly: a low, lighter lens along the underside.
    c.ellipse(520, 618, 190, 50, WHALE_BELLY)
    # Pectoral fin, swept back.
    c.poly([(450, 638), (495, 658), (405, 705), (420, 655)], (48, 70, 125))
    # Gentle eye and its sparkle.
    c.disc(752, 522, 9, (12, 16, 30))
    c.disc(749, 519, 2, (255, 255, 255))
    # Mouth: a soft smile curving back from the snout.
    for i in range(13):
        t = i / 12.0
        x = int(800 - 95 * t)
        y = int(562 + 22 * t * t)
        c.disc(x, y, 2, (30, 46, 85), 0.7)
    # Blowhole spray: a fountain of stardust above the head.
    for _ in range(26):
        ang = rng.uniform(-2.3, -0.85)
        dist = rng.uniform(18, 95)
        x = 692 + int(math.cos(ang) * dist)
        y = 448 + int(math.sin(ang) * dist)
        rad = 1 if rng.random() < 0.6 else 2
        col = (255, 244, 210) if rng.random() < 0.7 else (255, 255, 255)
        c.disc(x, y, rad, col, 0.95)


def house(c, rng):
    # Warm glow the cottage throws on the whale's back.
    c.glow(455, 408, 78, (255, 190, 100), steps=5, a=0.06)
    # Walls, sunk a little into the back so it sits firmly.
    c.poly([(410, 345), (500, 345), (500, 425), (410, 425)], HOUSE_WALL)
    # Gabled roof.
    c.poly([(398, 348), (512, 348), (455, 293)], HOUSE_ROOF)
    # Door with a brass knob.
    c.poly([(447, 382), (466, 382), (466, 425), (447, 425)], (40, 28, 24))
    c.disc(463, 400, 2, (255, 210, 130))
    # Windows, lit warm, with crossbars.
    c.glow(430, 368, 34, WINDOW, steps=4, a=0.10)
    c.glow(482, 368, 34, WINDOW, steps=4, a=0.10)
    c.poly([(420, 358), (441, 358), (441, 379), (420, 379)], WINDOW)
    c.poly([(472, 358), (493, 358), (493, 379), (472, 379)], WINDOW)
    c.poly([(429, 358), (432, 358), (432, 379), (429, 379)], HOUSE_WALL)
    c.poly([(420, 367), (441, 367), (441, 370), (420, 370)], HOUSE_WALL)
    c.poly([(481, 358), (484, 358), (484, 379), (481, 379)], HOUSE_WALL)
    c.poly([(472, 367), (493, 367), (493, 370), (472, 370)], HOUSE_WALL)
    # Chimney, and smoke drifting back as the whale flies right.
    c.poly([(484, 300), (499, 300), (499, 348), (484, 348)], (60, 44, 36))
    for i in range(5):
        c.disc(478 - i * 9, 292 - i * 12, 7 - i, (200, 200, 220),
               0.16 - i * 0.02)


def clouds(c, rng):
    # A soft sea of cloud below the whale.
    for _ in range(18):
        x = rng.randint(-40, W + 40)
        y = rng.randint(890, 1010)
        rx = rng.randint(110, 230)
        ry = rng.randint(30, 60)
        col = CLOUD if rng.random() < 0.6 else CLOUD_DARK
        c.soft_ellipse(x, y, rx, ry, col, steps=5, a=0.09)
    # Mid wisps.
    for _ in range(6):
        x = rng.randint(0, W)
        y = rng.randint(770, 850)
        c.soft_ellipse(x, y, rng.randint(70, 150), rng.randint(14, 24),
                       CLOUD, steps=5, a=0.06)
    # Two faint wisps under the whale, for depth.
    c.soft_ellipse(430, 700, 190, 20, CLOUD, steps=5, a=0.05)
    c.soft_ellipse(560, 715, 150, 16, CLOUD, steps=5, a=0.05)


def trail(c, rng):
    # Stardust the whale leaves behind its tail, fading with distance.
    for _ in range(70):
        x = rng.randint(10, 130)
        t = (x - 10) / 120.0
        y = rng.randint(470, 625)
        rad = 1 + int(2 * t)
        col = (255, 230, 160) if rng.random() < 0.6 else (255, 255, 255)
        c.disc(x, y, rad, col, 0.3 + 0.6 * t)
    for _ in range(6):
        x = rng.randint(60, 130)
        y = rng.randint(490, 600)
        c.sparkle(x, y, 6, (255, 240, 190))


# ---------------- Render ----------------
def render():
    rng = random.Random(SEED)
    c = Canvas()
    sky(c)
    stars(c, rng)
    moon(c)
    clouds(c, rng)
    whale(c, rng)
    house(c, rng)
    trail(c, rng)
    return png_bytes(c.p)


def main():
    data = render()
    out = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if out:
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, "entry.png"), "wb") as f:
            f.write(data)
    elif os.path.isdir("/output"):
        with open("/output/entry.png", "wb") as f:
            f.write(data)
    # Also drop art.png beside this script and in the working directory
    # (best effort: /bot is read-only inside the grader's container).
    here = os.path.dirname(os.path.abspath(__file__))
    for path in (os.path.join(here, "art.png"), "art.png"):
        try:
            with open(path, "wb") as f:
                f.write(data)
        except OSError:
            pass


if __name__ == "__main__":
    main()
