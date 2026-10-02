#!/usr/bin/env python3
"""
Parse a Paprika .paprikarecipes export into:
  1. <name>-library.md    - the whole collection as readable markdown
  2. <name>-index.xlsx    - one row per recipe, filterable

Usage:
    python parse_paprika.py "MacArthur Recipes Sep 26.paprikarecipes"
    python parse_paprika.py <file> --outdir /some/folder

Requires: openpyxl  (pip install openpyxl)
Photos are ignored, which is what keeps the outputs small.
"""

import argparse
import glob
import gzip
import json
import os
import sys
import tempfile
import zipfile
from collections import defaultdict


def load(path):
    """Unzip the export and return a list of recipe dicts, photos stripped."""
    recipes = []
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(path) as z:
            z.extractall(tmp)
        files = glob.glob(os.path.join(tmp, "**", "*.paprikarecipe"), recursive=True)
        if not files:
            sys.exit("No .paprikarecipe files inside that archive.")
        for f in files:
            try:
                with gzip.open(f) as fh:
                    d = json.loads(fh.read())
            except OSError:          # occasionally a member is not gzipped
                with open(f, "rb") as fh:
                    d = json.loads(fh.read())
            d.pop("photo_data", None)
            d.pop("photos", None)
            recipes.append(d)
    return recipes


def clean(s, inline=False):
    if not s:
        return ""
    s = str(s).replace("\r\n", "\n").replace("\r", "\n").strip()
    return s.replace("\n", " ") if inline else s


def category(r):
    c = r.get("categories") or []
    return c[0] if c else "Uncategorized"


def write_markdown(recipes, out):
    bycat = defaultdict(list)
    for r in recipes:
        bycat[category(r)].append(r)
    for c in bycat:
        bycat[c].sort(key=lambda r: clean(r.get("name")).lower())

    L = [
        "# Recipe Library",
        "",
        f"{len(recipes)} recipes exported from Paprika.",
        "",
        "Where a **Cook's note** appears, that is an annotation added by whoever "
        "cooked it -- usually the most useful line in the entry.",
        "",
        "## Contents",
        "",
    ]
    for c in sorted(bycat):
        L.append(f"- {c} ({len(bycat[c])})")
    L.append("\n---\n")

    for c in sorted(bycat):
        L.append(f"\n# {c}\n")
        for r in bycat[c]:
            L.append(f"## {clean(r.get('name'))}\n")

            meta = []
            if clean(r.get("source")):
                meta.append(f"**Source:** {clean(r.get('source'), True)}")
            if clean(r.get("servings")):
                meta.append(f"**Servings:** {clean(r.get('servings'), True)}")
            times = [
                f"{label} {clean(r.get(key), True)}"
                for key, label in (("prep_time", "prep"),
                                   ("cook_time", "cook"),
                                   ("total_time", "total"))
                if clean(r.get(key))
            ]
            if times:
                meta.append("**Time:** " + ", ".join(times))
            if meta:
                L.append(" - ".join(meta) + "\n")

            if clean(r.get("description")):
                L.append(f"**Cook's note:** {clean(r.get('description'))}\n")
            if clean(r.get("notes")):
                L.append(f"**Notes:** {clean(r.get('notes'))}\n")

            if clean(r.get("ingredients")):
                L.append("**Ingredients**\n")
                for line in clean(r.get("ingredients")).split("\n"):
                    line = line.strip()
                    L.append(f"- {line}" if line else "")
                L.append("")

            if clean(r.get("directions")):
                L.append("**Directions**\n")
                L.append(clean(r.get("directions")) + "\n")

            if clean(r.get("source_url")):
                L.append(f"[Original]({clean(r.get('source_url'), True)})\n")

            L.append("---\n")

    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


def write_index(recipes, out):
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Font, PatternFill
        from openpyxl.utils import get_column_letter
    except ImportError:
        sys.exit("openpyxl is needed for the spreadsheet: pip install openpyxl")

    recipes = sorted(recipes, key=lambda r: (category(r).lower(),
                                             clean(r.get("name")).lower()))
    wb = Workbook()
    ws = wb.active
    ws.title = "Recipe Index"
    ws.append(["Recipe", "Category", "Source", "Servings", "Total time",
               "Cook's note", "Ingredients", "Link"])

    for r in recipes:
        total = clean(r.get("total_time"), True) or " / ".join(
            x for x in (clean(r.get("prep_time"), True),
                        clean(r.get("cook_time"), True)) if x)
        ingredients = "; ".join(
            l.strip() for l in clean(r.get("ingredients")).split("\n") if l.strip()
        )[:600]
        ws.append([
            clean(r.get("name"), True),
            category(r),
            clean(r.get("source"), True),
            clean(r.get("servings"), True),
            total,
            clean(r.get("description"), True)[:500],
            ingredients,
            clean(r.get("source_url"), True),
        ])

    header_font = Font(name="Arial", bold=True, color="FFFFFF")
    header_fill = PatternFill("solid", fgColor="2F4F4F")
    for cell in ws[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(vertical="center")
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.font = Font(name="Arial", size=10)
            cell.alignment = Alignment(vertical="top")
    for i, w in enumerate([42, 16, 26, 20, 16, 60, 70, 30], start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[1].height = 20
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    wb.save(out)


def main():
    p = argparse.ArgumentParser(description="Parse a Paprika export.")
    p.add_argument("export", help="path to the .paprikarecipes file")
    p.add_argument("--outdir", help="where to write outputs (default: alongside the input)")
    args = p.parse_args()

    if not os.path.isfile(args.export):
        sys.exit(f"Not found: {args.export}")

    outdir = args.outdir or os.path.dirname(os.path.abspath(args.export))
    os.makedirs(outdir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(args.export))[0]

    print(f"Reading {args.export} ...")
    recipes = load(args.export)
    print(f"  {len(recipes)} recipes")

    md = os.path.join(outdir, f"{stem}-library.md")
    write_markdown(recipes, md)
    print(f"  wrote {md}  ({os.path.getsize(md):,} bytes)")

    xl = os.path.join(outdir, f"{stem}-index.xlsx")
    write_index(recipes, xl)
    print(f"  wrote {xl}  ({os.path.getsize(xl):,} bytes)")

    dated = sorted(clean(r.get("created"), True) for r in recipes if r.get("created"))
    if dated:
        print(f"  created dates span {dated[0]} to {dated[-1]}")
    annotated = sum(1 for r in recipes if clean(r.get("description")))
    print(f"  {annotated} recipes carry a cook's note")


if __name__ == "__main__":
    main()
