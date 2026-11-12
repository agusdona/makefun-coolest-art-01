# The Lantern Crab

A hermit crab in a vintage brass diving helmet, holding a glowing lantern
high above a moonlit beach. Fireflies drift through the dark blue night
air, a crescent moon hangs in a starry sky, and the lantern's warm golden
light spills across the wet sand and the gentle waves at the shoreline.

The artwork is held in this repository as `art.png` (1024x1024, under
1 MiB). It is a small, brave light-keeper: one crab, one lantern, one
quiet night — a moment of warmth against the vast dark sea.

## How it works

`main.py` writes the artwork. It reads `art.png`, checks that it is a
real PNG no larger than 1 MiB and no bigger than 1024x1024, then copies
it byte-for-byte to `/output/entry.png` and prints the title, dimensions,
byte size, and SHA-256 of what it wrote. Standard library only, no
network, no randomness — two runs always write the same bytes.

Run it with:

```sh
python3 main.py
```
