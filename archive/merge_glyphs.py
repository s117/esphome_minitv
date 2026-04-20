#!/usr/bin/env python3
"""
Extract selected glyphs from multiple font files and merge into a single TTF.
Reads configuration from glyph_select.yaml (or a path passed as argument).

Dependencies:
    pip install fonttools pyyaml
"""

import os
import sys
import tempfile
import argparse
import yaml
from fontTools.ttLib import TTFont
from fontTools import subset as ft_subset
from fontTools.merge import Merger


def is_variable_font(font_path: str) -> bool:
    font = TTFont(font_path, lazy=True)
    result = "fvar" in font
    font.close()
    return result


def instantiate_to_static(font_path: str, tmp_dir: str) -> str:
    """Pin all axes of a variable font to their defaults, producing a static TTF."""
    from fontTools.varLib import instancer

    font = TTFont(font_path)
    axes = {axis.axisTag: axis.defaultValue for axis in font["fvar"].axes}
    print(f"  -> Variable font: pinning axes {axes}")
    instancer.instantiateVariableFont(font, axes, inplace=True)
    static_path = os.path.join(tmp_dir, os.path.basename(font_path) + ".static.ttf")
    font.save(static_path)
    return static_path


def normalize_upem(font_path: str, target_upem: int, tmp_dir: str, index: int) -> str:
    """Rescale a font's unitsPerEm to target_upem (no-op if already matching)."""
    from fontTools.ttLib.scaleUpem import scale_upem

    font = TTFont(font_path)
    current = font["head"].unitsPerEm
    if current == target_upem:
        font.close()
        return font_path
    print(f"  -> Rescaling UPM {current} -> {target_upem}")
    scale_upem(font, target_upem)
    out_path = os.path.join(tmp_dir, f"normalized_{index}.ttf")
    font.save(out_path)
    return out_path


def subset_font(font_path: str, unicodes: list[int], tmp_dir: str, index: int) -> str:
    """Subset font to the given unicode codepoints and save to a temp file."""
    options = ft_subset.Options()
    options.layout_features = ["*"]
    options.name_IDs = []          # drop name table to avoid merge conflicts
    options.notdef_outline = False
    options.hinting = False
    options.ignore_missing_unicodes = True

    font = ft_subset.load_font(font_path, options)
    subsetter = ft_subset.Subsetter(options=options)
    subsetter.populate(unicodes=unicodes)
    subsetter.subset(font)

    out_path = os.path.join(tmp_dir, f"subset_{index}.ttf")
    ft_subset.save_font(font, out_path, options)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge selected glyphs from multiple font files into one TTF"
    )
    parser.add_argument(
        "config",
        nargs="?",
        default="glyph_select.yaml",
        help="Path to YAML config file (default: glyph_select.yaml)",
    )
    args = parser.parse_args()

    config_path = args.config
    config_dir = os.path.dirname(os.path.abspath(config_path))

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    output_path = os.path.join(config_dir, config["output_path"])
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    glyph_sets = config["glyph_set"]
    total = len(glyph_sets)

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Resolve font paths and detect variable fonts up front so we can
        # determine a common UPM before subsetting.
        resolved_paths = []
        for entry in glyph_sets:
            fp = os.path.join(config_dir, entry["file_path"])
            if not os.path.isfile(fp):
                print(f"ERROR: font not found: {fp}", file=sys.stderr)
                sys.exit(1)
            resolved_paths.append(fp)

        # Pick the largest UPM as the common target to avoid precision loss.
        upems = []
        for fp in resolved_paths:
            f = TTFont(fp, lazy=True)
            upems.append(f["head"].unitsPerEm)
            f.close()
        target_upem = max(upems)
        if len(set(upems)) > 1:
            print(f"UPM values {upems} differ — normalising all to {target_upem}")

        subset_paths = []

        for i, (entry, font_path) in enumerate(zip(glyph_sets, resolved_paths)):
            glyph_chars: list[str] = entry["glyphs"]
            unicodes = [ord(g[0]) for g in glyph_chars if g]
            print(f"[{i + 1}/{total}] {entry['file_path']}  ({len(unicodes)} glyphs)")

            if is_variable_font(font_path):
                font_path = instantiate_to_static(font_path, tmp_dir)

            font_path = normalize_upem(font_path, target_upem, tmp_dir, i)
            subset_path = subset_font(font_path, unicodes, tmp_dir, i)
            subset_paths.append(subset_path)

        print(f"Merging {len(subset_paths)} subset(s) ...")
        merger = Merger()
        merged = merger.merge(subset_paths)
        merged.save(output_path)

    print(f"Done -> {output_path}")


if __name__ == "__main__":
    main()
