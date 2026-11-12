# The Whale That Carried Home

A humpback whale glides through a deep indigo night sky, carrying a small
cottage with warm glowing windows on its back, sailing above a soft sea of
cloud toward a pale moon, trailing stardust behind its tail.

The idea is a quiet one: home is not a place you leave behind — it travels
with you. The whale is the journey, the cottage is the home, and the moon is
where they are headed. One big shape (the whale), one warm light (the
cottage), one pale disc (the moon): the whole picture reads at a glance, even
small.

## How it is made

`main.py` draws the picture from scratch in pure Python (standard library
only: `math`, `os`, `random`, `struct`, `zlib`). No image files, no network,
no fonts. It builds the scene on a 1024x1024 RGB canvas — a vertical indigo
gradient sky, scattered stars, a cratered moon with a soft glow, a whale
silhouette drawn as a polygon (tapered snout, thick mid-body, narrow tail
stalk, notched fluke) with a lighter belly, a swept pectoral fin, a gentle
eye and a dotted smile, a blowhole spray of stardust, a cottage with lit
windows and chimney smoke, a stardust trail, and a soft sea of cloud below —
then encodes it as a PNG with a small hand-written encoder.

## How to run

```sh
python3 main.py
```

It writes `art.png` (1024x1024, about 43 KB) next to the script, and
`entry.png` into `$MAKEFUN_OUTPUT_DIR` (or `/output`) when that is set, as
the grader expects. The picture is fully deterministic: same seed, same
bytes, every run (verified by running it twice and comparing SHA-256).

## Verification

- `art.png` is a valid PNG, 1024x1024, 42,687 bytes (limit 1 MiB).
- Two consecutive runs produce byte-identical output (SHA-256
  `b6dda78403fb981a1983b8966057a0a716380ad05a1cd008ad260b003b3bd3fd`).
- Render time about 1.3 s (harness limit 60 s).
- Program uses only the Python standard library and no network.
