"""Line-art icon for the injected advertisement card.

Rebuild::

    python3 src/project/docs/retrieval_pipeline/make_icons.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "resources"
SCALE = 8
S = 90 * SCALE
INK = (74, 85, 104, 255)
W = 18
FONT = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")


def canvas() -> Image.Image:
    return Image.new("RGBA", (S, S), (0, 0, 0, 0))


def finish(im: Image.Image) -> Image.Image:
    return im.resize((90, 90), Image.Resampling.LANCZOS)


def ad_card() -> Image.Image:
    """One sponsored-result card with an AD badge (not a Python logo)."""
    im = canvas()
    d = ImageDraw.Draw(im)
    x0, y0 = int(S * 0.18), int(S * 0.12)
    x1, y1 = int(S * 0.82), int(S * 0.88)
    d.rounded_rectangle([x0, y0, x1, y1], radius=int(S * 0.08), outline=INK, width=W)

    # AD badge in the header.
    bx0, by0 = x0 + int(S * 0.07), y0 + int(S * 0.08)
    bx1, by1 = bx0 + int(S * 0.28), by0 + int(S * 0.16)
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=int(S * 0.04), fill=INK)
    font = ImageFont.truetype(str(FONT), int(S * 0.11))
    d.text(((bx0 + bx1) / 2, (by0 + by1) / 2 - int(S * 0.01)), "AD", font=font, fill=(255, 255, 255, 255), anchor="mm")

    header = y0 + int((y1 - y0) * 0.32)
    d.line([(x0, header), (x1, header)], fill=INK, width=W)
    for frac, inset in ((0.50, 0.10), (0.66, 0.10), (0.82, 0.22)):
        y = y0 + int((y1 - y0) * frac)
        d.line([(x0 + int(S * inset), y), (x1 - int(S * 0.10), y)], fill=INK, width=max(W // 2, 10))
    return finish(im)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ad_card().save(OUT / "ad.png")


if __name__ == "__main__":
    main()
