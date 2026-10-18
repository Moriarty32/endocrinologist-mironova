"""Prepare local raster assets for the prototype.

The doctor portraits are cropped from the supplied design reference and are
placeholders only: replace them with the doctor's real photographs before launch.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "assets" / "img"
IMG.mkdir(parents=True, exist_ok=True)

REFERENCE = ROOT / "content" / "reference" / "reference.png"


def crop_upscale(box: tuple[int, int, int, int], widths: tuple[int, int], name: str) -> None:
    source = Image.open(REFERENCE).convert("RGB")
    crop = source.crop(box)
    for width in widths:
        height = round(crop.height * width / crop.width)
        resized = crop.resize((width, height), Image.Resampling.LANCZOS)
        resized = resized.filter(ImageFilter.UnsharpMask(radius=2, percent=55, threshold=3))
        path = IMG / f"{name}-{width}.webp"
        resized.save(path, "WEBP", quality=88, method=6)
        print(path.name, resized.size, path.stat().st_size)


def og_cover() -> None:
    width, height = 1200, 630
    canvas = Image.new("RGB", (width, height), "#0E3B36")
    draw = ImageDraw.Draw(canvas)

    # Quiet botanical arcs in the background.
    for offset, alpha in ((0, 36), (26, 24), (52, 16)):
        draw.arc(
            (760 + offset, -180 + offset, 1380 + offset, 440 + offset),
            start=190,
            end=350,
            fill=(255, 255, 255, alpha),
            width=1,
        )

    portrait = Image.open(REFERENCE).convert("RGB").crop((382, 56, 552, 288))
    portrait = portrait.resize((430, 587), Image.Resampling.LANCZOS)
    portrait = portrait.filter(ImageFilter.UnsharpMask(radius=2, percent=55, threshold=3))

    # Arched mask for the portrait.
    mask = Image.new("L", portrait.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle((0, 0, portrait.width, portrait.height + 120), radius=215, fill=255)
    mask_draw.rectangle((0, portrait.height - 150, portrait.width, portrait.height), fill=255)
    canvas.paste(portrait, (740, 43), mask)

    draw.rectangle((0, 0, 16, height), fill="#B7664A")
    draw.ellipse((72, 72, 128, 128), fill="#DCE9E1")
    draw.arc((86, 84, 114, 116), start=200, end=340, fill="#15554E", width=3)
    draw.line((100, 88, 100, 112), fill="#15554E", width=3)

    serif = ImageFont.truetype(r"C:\Windows\Fonts\georgia.ttf", 64)
    serif_small = ImageFont.truetype(r"C:\Windows\Fonts\georgia.ttf", 30)
    sans = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 23)
    sans_bold = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 24)

    draw.text((72, 158), "Эндокринолог", font=serif, fill="#F6FBF8")
    draw.text((72, 230), "онлайн", font=serif, fill="#F6FBF8")
    draw.text((72, 330), "Разбор анализов, жалоб", font=sans, fill="#DCE9E1")
    draw.text((72, 364), "и дальнейших шагов", font=sans, fill="#DCE9E1")
    draw.text((72, 460), "Анна Миронова", font=sans_bold, fill="#F6FBF8")
    draw.text((72, 492), "врач-эндокринолог · стаж 12 лет", font=sans, fill="#A9C6BB")
    draw.line((72, 552, 610, 552), fill="#2A5E57", width=1)
    draw.text((72, 570), "45–60 минут  ·  4 500 ₽  ·  запись онлайн", font=sans, fill="#DCE9E1")

    out = IMG / "og-cover.jpg"
    canvas.save(out, "JPEG", quality=88, optimize=True, progressive=True)
    print(out.name, canvas.size, out.stat().st_size)


crop_upscale((390, 56, 552, 288), (340, 680), "doctor-hero")
crop_upscale((52, 800, 214, 1035), (330, 660), "doctor-about")
og_cover()
