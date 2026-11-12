#!/usr/bin/env python3
"""Make the coolest art (make.fun coolest-art-01).

Writes one piece of art to /output/entry.png: a phoenix of molten gold
and crimson rising above a neon cyberpunk city at dusk.

The artwork is held in this repository as art.png (a whole PNG, 1024x1024,
under 1 MiB). This program copies it byte-for-byte to /output/entry.png,
so two runs always write the same bytes. Standard library only, no
network, no randomness, no wall-clock use.
"""

import hashlib
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "art.png")
OUTPUT_DIR = "/output"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "entry.png")

MAX_BYTES = 1 * 1024 * 1024
MAX_DIMENSION = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def png_dimensions(data):
    """Read (width, height) from a PNG IHDR chunk. Raises on bad data."""
    if len(data) < 33 or data[:8] != PNG_MAGIC:
        raise ValueError("not a PNG file")
    if data[12:16] != b"IHDR":
        raise ValueError("PNG has no IHDR chunk")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def main():
    with open(SOURCE, "rb") as f:
        data = f.read()
    if len(data) > MAX_BYTES:
        raise ValueError("art.png is over 1 MiB: %d bytes" % len(data))
    width, height = png_dimensions(data)
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise ValueError(
            "art.png is over 1024x1024: %dx%d" % (width, height)
        )
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_PATH, "wb") as f:
        f.write(data)
    with open(OUTPUT_PATH, "rb") as f:
        written = f.read()
    if hashlib.sha256(written).hexdigest() != hashlib.sha256(data).hexdigest():
        raise ValueError("output does not match source bytes")
    digest = hashlib.sha256(data).hexdigest()
    print("wrote %s (%dx%d, %d bytes, sha256 %s)"
          % (OUTPUT_PATH, width, height, len(data), digest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
