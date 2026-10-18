# -*- coding: utf-8 -*-
"""Static checks for the multi-page build."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = sorted(ROOT.rglob("index.html")) + [ROOT / "404.html"]
HREF = re.compile(r'(?:href|src)="([^"]+)"')
TITLE = re.compile(r"<title>(.*?)</title>", re.S)
DESC = re.compile(r'<meta name="description" content="([^"]*)"')
CANON = re.compile(r'<link rel="canonical" href="([^"]*)"')
H1 = re.compile(r"<h1[\s>]", re.I)
ID = re.compile(r'\sid="([^"]+)"')

issues: list[str] = []
canonicals: dict[str, str] = {}
ids: dict[str, str] = {}
for page in PAGES:
    rel = page.relative_to(ROOT)
    text = page.read_text(encoding="utf-8")
    if len(H1.findall(text)) != 1:
        issues.append(f"{rel}: H1 count = {len(H1.findall(text))}")
    title = TITLE.search(text)
    desc = DESC.search(text)
    canon = CANON.search(text)
    if not title or not title.group(1).strip():
        issues.append(f"{rel}: missing title")
    if not desc or len(desc.group(1).strip()) < 50:
        issues.append(f"{rel}: missing/short description")
    if not canon:
        issues.append(f"{rel}: missing canonical")
    else:
        key = canon.group(1)
        if key in canonicals:
            issues.append(f"{rel}: duplicate canonical with {canonicals[key]}")
        canonicals[key] = str(rel)
    for match in HREF.findall(text):
        target = match.strip()
        if not target or target.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:", "javascript:")):
            continue
        target = target.split("#", 1)[0].split("?", 1)[0]
        if not target:
            continue
        resolved = (page.parent / target).resolve()
        if target.endswith("/"):
            resolved = resolved / "index.html"
        if not resolved.exists():
            issues.append(f"{rel}: broken link {match}")
    page_ids: set[str] = set()
    for item in ID.findall(text):
        if item in page_ids:
            issues.append(f"{rel}: duplicate id {item}")
        page_ids.add(item)

print(f"checked {len(PAGES)} pages")
if issues:
    print("\n".join(issues[:80]))
    sys.exit(1)
print("OK: links, titles, descriptions, canonicals, H1s, ids")
