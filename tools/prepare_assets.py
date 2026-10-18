"""Prepare local raster assets for the prototype.

The doctor portrait is the image supplied for the site. The open-graph cover is
assembled from the same source. Both are local files; this script has no
dependency on the design-reference attachment folder.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "assets" / "img"
IMG.mkdir(parents=True, exist_ok=True)

PORTRAIT = ROOT / "content" / "reference" / "doctor-portrait.png"


def save_width(source: Image.Image, box: tuple[int, int, int, int], width: int, name: str) -> None:
    crop = source.crop(box)
    height = round(crop.height * width / crop.width)
    resized = crop.resize((width, height), Image.Resampling.LANCZOS)
    resized = resized.filter(ImageFilter.UnsharpMask(radius=1.2, percent=35, threshold=3))
    path = IMG / f"{name}-{width}.webp"
    resized.save(path, "WEBP", quality=90, method=6)
    print(path.name, resized.size, path.stat().st_size)


def save_fixed(source: Image.Image, box: tuple[int, int, int, int], size: tuple[int, int], name: str) -> None:
    crop = source.crop(box).resize(size, Image.Resampling.LANCZOS)
    path = IMG / f"{name}.webp"
    crop.save(path, "WEBP", quality=90, method=6)
    print(path.name, crop.size, path.stat().st_size)


def og_cover(portrait: Image.Image) -> None:
    width, height = 1200, 630
    canvas = Image.new("RGB", (width, height), "#0E3B36")
    draw = ImageDraw.Draw(canvas)

    for offset, alpha in ((0, 36), (26, 24), (52, 16)):
        draw.arc(
            (760 + offset, -180 + offset, 1380 + offset, 440 + offset),
            start=190,
            end=350,
            fill=(255, 255, 255, alpha),
            width=1,
        )

    # 842×1150 crop: face and upper body, matching the portrait panel ratio.
    portrait_crop = portrait.crop((140, 0, 982, 1150)).resize((430, 587), Image.Resampling.LANCZOS)
    portrait_crop = portrait_crop.filter(ImageFilter.UnsharpMask(radius=1.2, percent=35, threshold=3))

    mask = Image.new("L", portrait_crop.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle((0, 0, portrait_crop.width, portrait_crop.height + 120), radius=215, fill=255)
    mask_draw.rectangle((0, portrait_crop.height - 150, portrait_crop.width, portrait_crop.height), fill=255)
    canvas.paste(portrait_crop, (740, 43), mask)

    draw.rectangle((0, 0, 16, height), fill="#B7664A")
    draw.ellipse((72, 72, 128, 128), fill="#DCE9E1")
    draw.arc((86, 84, 114, 116), start=200, end=340, fill="#15554E", width=3)
    draw.line((100, 88, 100, 112), fill="#15554E", width=3)

    serif = ImageFont.truetype(r"C:\Windows\Fonts\georgia.ttf", 64)
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


portrait = Image.open(PORTRAIT).convert("RGB")
full = (0, 0, portrait.width, portrait.height)

# 4:5-friendly page portraits.
save_width(portrait, full, 330, "doctor-about")
save_width(portrait, full, 660, "doctor-about")
save_width(portrait, full, 340, "doctor-hero")
save_width(portrait, full, 680, "doctor-hero")

# 0.7 hero card for tablet/mobile; crop sides, keep face and stethoscope.
save_fixed(portrait, (141, 0, 981, 1200), (490, 700), "doctor-hero-clinic")

og_cover(portrait)
