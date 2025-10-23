#!/usr/bin/env python3
"""
Optimize images (JPEG/PNG/GIF) in-place with backups.
Creates a timestamped backup directory `.image_backups/<timestamp>/...` and writes optimized files over originals.
Prints a summary of per-file savings and totals.

Usage:
  python scripts/optimize_images.py assets/images --quality 82 --convert-webp

"""
import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image
except Exception:
    print("Pillow is required. Run: python -m pip install --user --upgrade Pillow")
    sys.exit(2)

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif'}


def optimize_image(path: Path, tmp_path: Path, quality: int, convert_webp: bool):
    ext = path.suffix.lower()
    size_before = path.stat().st_size
    saved_webp = False
    try:
        with Image.open(path) as im:
            # Convert animated gifs: skip optimization to avoid breaking animations
            if ext == '.gif' and getattr(im, 'is_animated', False):
                # just copy as-is
                return size_before, size_before, False

            # Use RGB for JPEGs
            if ext in ('.jpg', '.jpeg'):
                img = im.convert('RGB')
                img.save(tmp_path, format='JPEG', quality=quality, optimize=True, progressive=True)
            elif ext == '.png':
                # For PNGs, try to save with optimize flag
                img = im.convert('RGBA') if im.mode in ('RGBA', 'LA') else im.convert('RGB')
                img.save(tmp_path, format='PNG', optimize=True)
            elif ext == '.gif':
                im.save(tmp_path, format='GIF', optimize=True)
            else:
                # Unsupported, copy
                shutil.copy2(path, tmp_path)

            size_after = tmp_path.stat().st_size

            # Optionally try to write a WebP variant (if libwebp is available in Pillow build)
            if convert_webp:
                try:
                    webp_path = tmp_path.with_suffix('.webp')
                    img.save(webp_path, format='WEBP', quality=quality)
                    webp_size = webp_path.stat().st_size
                    # If webp is smaller than optimized file, keep it as an extra file (don't replace original)
                    saved_webp = True
                except Exception:
                    saved_webp = False

            # Replace original with optimized
            os.replace(str(tmp_path), str(path))
            return size_before, size_after, saved_webp

    except Exception as e:
        print(f"Failed to optimize {path}: {e}")
        # If any failure, ensure tmp removed and keep original
        if tmp_path.exists():
            tmp_path.unlink()
        return size_before, size_before, False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', help='Root directory to scan for images')
    parser.add_argument('--quality', type=int, default=82, help='JPEG/WebP quality (default: 82)')
    parser.add_argument('--convert-webp', action='store_true', help='Attempt to create WebP variants')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without writing')
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f"Path not found: {root}")
        sys.exit(1)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_root = root.parent / f'.image_backups/{timestamp}'
    backup_root.mkdir(parents=True, exist_ok=True)

    results = []
    total_before = 0
    total_after = 0

    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            p = Path(dirpath) / fn
            if p.suffix.lower() not in IMAGE_EXTS:
                continue
            rel = p.relative_to(root)
            backup_path = backup_root / rel
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, backup_path)

            tmp_path = p.with_suffix(p.suffix + '.opt')
            if args.dry_run:
                size_before = p.stat().st_size
                print(f"DRY: would optimize {p} ({size_before} bytes)")
                continue

            size_before, size_after, webp = optimize_image(p, tmp_path, args.quality, args.convert_webp)
            results.append((str(p), size_before, size_after, webp))
            total_before += size_before
            total_after += size_after

    # Print summary
    print('\nOptimization summary:')
    for path, before, after, webp in results:
        saved = before - after
        pct = (saved / before * 100) if before else 0
        webp_note = ' +webp' if webp else ''
        print(f"{path}: {before} -> {after} (saved {saved} bytes, {pct:.1f}%){webp_note}")

    print('\nTotals:')
    total_saved = total_before - total_after
    total_pct = (total_saved / total_before * 100) if total_before else 0
    print(f"Before: {total_before} bytes\nAfter:  {total_after} bytes\nSaved:  {total_saved} bytes ({total_pct:.1f}%)")
    print(f"Backups created under: {backup_root}")

if __name__ == '__main__':
    main()
