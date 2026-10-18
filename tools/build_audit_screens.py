# -*- coding: utf-8 -*-
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "audit" / "raw"
out = ROOT / "audit" / "screenshots"
out.mkdir(parents=True, exist_ok=True)

pairs = [
    ("audit-home-1440.png", "before-home-1440.jpg"),
    ("audit-home-1920.png", "before-home-1920.jpg"),
    ("audit-mobile-top.png", "before-home-390.jpg"),
    ("multi-service.png", "before-service-1440.jpg"),
    ("multi-prices.png", "before-prices-1440.jpg"),
    ("multi-about.png", "before-about-1440.jpg"),
    ("final-home-1440.png", "after-home-1440.jpg"),
    ("final-home-1920.png", "after-home-1920.jpg"),
    ("final-top-390.png", "after-home-390.jpg"),
    ("final-top-360.png", "after-home-360.jpg"),
    ("final-top-768.png", "after-home-768.jpg"),
    ("final-service-1440.png", "after-service-1440.jpg"),
    ("final-prices-1440.png", "after-prices-1440.jpg"),
    ("final-about-1440.png", "after-about-1440.jpg"),
    ("final-docs-1440.png", "after-docs-1440.jpg"),
]
for source, target in pairs:
    path = src / source
    if not path.exists():
        print("missing", source)
        continue
    image = Image.open(path).convert("RGB")
    if image.width > 1200:
        image = image.resize((1200, round(image.height * 1200 / image.width)), Image.LANCZOS)
    image.save(out / target, "JPEG", quality=82, optimize=True)
    print(target, image.size)
