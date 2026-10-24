# -*- coding: utf-8 -*-
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
missing = []
for css_path in sorted(root.glob("*.css")):
    css = css_path.name
    text = css_path.read_text(encoding="utf-8")
    for raw in re.findall(r"url\(([^)]+)\)", text):
        value = raw.strip("\"' ")
        if value.startswith("data:"):
            continue
        target = css_path.parent / value.split("?", 1)[0]
        if not target.exists():
            missing.append((css, value))
print("CSS assets checked")
if missing:
    print("\n".join(f"{css}: {value}" for css, value in missing))
    raise SystemExit(1)
print("OK")
