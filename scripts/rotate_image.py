#!/usr/bin/env python3
"""Rotate images for a given base name (e.g. it-in-the-d-podcast-04172025).

Backs up existing files under assets/images/.image_backups/<timestamp>/
and rotates matching files (jpg/jpeg/png/webp) 90 degrees clockwise by default.

Usage:
  py -3 scripts\rotate_image.py it-in-the-d-podcast-04172025 --dir assets/images
"""
import argparse
import shutil
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image
except Exception:
    print("Pillow is required. Run: python -m pip install --user --upgrade Pillow")
    raise


IMAGE_EXTS = ['.jpg', '.jpeg', '.png', '.webp']


def rotate_file(p: Path, degrees: int, backup_root: Path):
    backup_root.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, backup_root / p.name)
    with Image.open(p) as im:
        rotated = im.rotate(-degrees, expand=True)
        # Keep WEBP format when saving webp; otherwise use original format if available
        fmt = 'WEBP' if p.suffix.lower() == '.webp' else (im.format or None)
        # Pillow will infer format from filename if fmt is None
        rotated.save(p, format=fmt)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('basename', help='Base filename without extension (e.g. it-in-the-d-podcast-04172025)')
    parser.add_argument('--dir', default='assets/images', help='Directory containing images')
    parser.add_argument('--degrees', type=int, default=90, help='Degrees to rotate clockwise (default: 90)')
    args = parser.parse_args()

    root = Path(args.dir)
    if not root.exists():
        print(f'Directory not found: {root}')
        return

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_root = root / '.image_backups' / timestamp

    found = False
    for ext in IMAGE_EXTS:
        p = root / (args.basename + ext)
        # handle case where a .jpeg.webp or .jpg.webp exists (double suffix) as well
        double = root / (args.basename + ext + '.webp')
        candidates = [p, double]
        for cand in candidates:
            if cand.exists():
                found = True
                try:
                    rotate_file(cand, args.degrees, backup_root)
                    print(f'Rotated: {cand}')
                except Exception as e:
                    print(f'Failed to rotate {cand}: {e}')

    if not found:
        print('No matching files found for', args.basename)
    else:
        print('Backups at', backup_root)


if __name__ == '__main__':
    main()
