"""Generate a simple JARVIS .ico for the Windows app."""

from __future__ import annotations

from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow not installed — skip icon")
    raise SystemExit(0)

OUT = Path(__file__).resolve().parent / "jarvis.ico"
SIZES = [16, 24, 32, 48, 64, 128, 256]


def make(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # rounded square background
    margin = max(1, size // 16)
    d.rounded_rectangle(
        [margin, margin, size - margin - 1, size - margin - 1],
        radius=size // 5,
        fill=(15, 23, 42, 255),
        outline=(59, 130, 246, 255),
        width=max(1, size // 24),
    )
    # letter J
    try:
        font = ImageFont.truetype("segoeui.ttf", size // 2)
    except Exception:
        font = ImageFont.load_default()
    text = "J"
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(
        ((size - tw) / 2, (size - th) / 2 - size // 20),
        text,
        fill=(96, 165, 250, 255),
        font=font,
    )
    return img


def main() -> None:
    images = [make(s) for s in SIZES]
    images[0].save(
        OUT,
        format="ICO",
        sizes=[(s, s) for s in SIZES],
        append_images=images[1:],
    )
    print(f"Icon written: {OUT}")


if __name__ == "__main__":
    main()
