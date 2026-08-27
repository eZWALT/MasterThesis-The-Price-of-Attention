"""Slate line-art icons for trajectory Gold/Silver tables.

90x90 RGBA, stroke matched to filter.png / dedup.png. Rebuild::

    python3 src/project/docs/trajectory_pipeline/make_icons.py
"""

from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

OUT = Path(__file__).resolve().parent / "resources"
SCALE = 8
S = 90 * SCALE
INK = (74, 85, 104, 255)
W = 18


def canvas() -> Image.Image:
    return Image.new("RGBA", (S, S), (0, 0, 0, 0))


def finish(im: Image.Image) -> Image.Image:
    return im.resize((90, 90), Image.Resampling.LANCZOS)


def database() -> Image.Image:
    im = canvas()
    d = ImageDraw.Draw(im)
    left, right = int(S * 0.24), int(S * 0.76)
    top, bot = int(S * 0.18), int(S * 0.84)
    eh = int(S * 0.18)
    d.line([(left, top + eh // 2), (left, bot - eh // 2)], fill=INK, width=W)
    d.line([(right, top + eh // 2), (right, bot - eh // 2)], fill=INK, width=W)
    d.ellipse([left, top, right, top + eh], outline=INK, width=W)
    bottom = canvas()
    bd = ImageDraw.Draw(bottom)
    bd.ellipse([left, bot - eh, right, bot], outline=INK, width=W)
    eraser = Image.new("L", (S, S), 0)
    ImageDraw.Draw(eraser).rectangle([0, 0, S, bot - eh // 2], fill=255)
    r, g, b, a = bottom.split()
    bottom = Image.merge("RGBA", (r, g, b, ImageChops.subtract(a, eraser)))
    return finish(Image.alpha_composite(im, bottom))


def table() -> Image.Image:
    im = canvas()
    d = ImageDraw.Draw(im)
    m = int(S * 0.20)
    x0, y0, x1, y1 = m, m, S - m, S - m
    d.rounded_rectangle([x0, y0, x1, y1], radius=int(S * 0.08), outline=INK, width=W)
    header = y0 + int((y1 - y0) * 0.28)
    d.line([(x0, header), (x1, header)], fill=INK, width=W)
    col1 = x0 + (x1 - x0) // 3
    col2 = x0 + 2 * (x1 - x0) // 3
    d.line([(col1, header), (col1, y1)], fill=INK, width=W)
    d.line([(col2, header), (col2, y1)], fill=INK, width=W)
    row = header + (y1 - header) // 2
    d.line([(x0, row), (x1, row)], fill=INK, width=W)
    return finish(im)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    database().save(OUT / "database.png")
    table().save(OUT / "table.png")


if __name__ == "__main__":
    main()
