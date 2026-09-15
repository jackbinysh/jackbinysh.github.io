#!/usr/bin/env python3
"""Pad research images to 16:9 with macOS sips, keeping originals intact.

Run from any directory. Optional project folder names limit the selection:
  python3 scripts/prepare_research_thumbnails.py OddElasticity
"""

import argparse
import math
from pathlib import Path
import struct
import subprocess


def png_size(path):
    with path.open("rb") as image:
        header = image.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Expected PNG: {path}")
    return struct.unpack(">II", header[16:24])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("projects", nargs="*")
    parser.add_argument("--occupancy", type=float, default=0.92,
                        help="Maximum fraction of canvas width/height occupied (default: 0.92)")
    args = parser.parse_args()
    if not 0 < args.occupancy <= 1:
        parser.error("--occupancy must be greater than 0 and at most 1")

    research = Path(__file__).resolve().parents[1] / "content" / "research"
    sources = ([research / name / "featured.png" for name in args.projects]
               if args.projects else sorted(research.glob("*/featured.png")))
    for source in sources:
        width, height = png_size(source)
        unit = math.ceil(max(width / 16, height / 9) / args.occupancy)
        canvas_width, canvas_height = 16 * unit, 9 * unit
        target = source.with_name("thumbnail.png")
        subprocess.run([
            "sips", "--padToHeightWidth", str(canvas_height), str(canvas_width),
            "--padColor", "FFFFFF", str(source), "--out", str(target),
        ], check=True, capture_output=True, text=True)
        if png_size(target) != (canvas_width, canvas_height):
            raise RuntimeError(f"Unexpected output dimensions: {target}")
        print(f"{source.parent.name}: {width}x{height} → {canvas_width}x{canvas_height}")


if __name__ == "__main__":
    main()
