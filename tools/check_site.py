"""Lightweight static checks for the prototype: ids, local links, assets."""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlparse

from lxml import html

ROOT = Path(__file__).resolve().parents[1]
PAGES = sorted(ROOT.glob("*.html"))
ALLOWED_EXTERNAL = ("http://", "https://", "mailto:", "tel:", "javascript:", "data:")


def local_target(page: Path, href: str) -> tuple[Path | None, str]:
    href = href.strip()
    if not href or href.startswith(ALLOWED_EXTERNAL):
        return None, ""
    parsed = urlparse(href)
    target = (page.parent / unquote(parsed.path)).resolve() if parsed.path else page
    return target, unquote(parsed.fragment)


def main() -> int:
    errors: list[str] = []
    ids: dict[Path, set[str]] = {}

    for page in PAGES:
        try:
            tree = html.fromstring(page.read_bytes())
        except Exception as exc:  # noqa: BLE001 - report and continue
            errors.append(f"{page.name}: parse error: {exc}")
            continue
        page_ids = tree.xpath("//*[@id]/@id")
        duplicates = [key for key, count in Counter(page_ids).items() if count > 1]
        if duplicates:
            errors.append(f"{page.name}: duplicate ids: {duplicates}")
        ids[page] = set(page_ids)
        if not tree.xpath("//h1"):
            errors.append(f"{page.name}: no h1")

        for attr in ("href", "src"):
            for node in tree.xpath(f"//*[@{attr}]"):
                value = node.get(attr)
                if not value or value.startswith(ALLOWED_EXTERNAL):
                    continue
                target, fragment = local_target(page, value)
                if target is None:
                    continue
                if not target.exists():
                    errors.append(f"{page.name}: missing {attr} target {value!r}")
                    continue
                if attr == "href" and fragment and target.suffix.lower() == ".html":
                    if target in ids and target != page:
                        continue
                    target_tree = html.fromstring(target.read_bytes())
                    target_ids = {item for item in target_tree.xpath("//*[@id]/@id")}
                    if fragment not in target_ids:
                        errors.append(f"{page.name}: missing anchor {value!r}")

        for node in tree.xpath("//*[@aria-labelledby]"):
            for ref in node.get("aria-labelledby", "").split():
                if ref not in ids[page]:
                    errors.append(f"{page.name}: aria-labelledby points to missing #{ref}")

    # Sitemap URLs should match local pages where they are same-site.
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    for page in PAGES:
        if page.name in {"404.html"}:
            continue
        if f"/{page.name}" not in sitemap and page.name != "index.html":
            errors.append(f"sitemap.xml: {page.name} is not listed")

    if errors:
        print("FAILED")
        for error in errors:
            print(" -", error)
        return 1

    print(f"OK: {len(PAGES)} pages, ids/links/assets checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
