#!/usr/bin/env python3
"""Generate responsive image variants from a source image.

Usage:
  python scripts/generate_responsive_images.py <source> --sizes 1200 800 400 --formats webp jpg

This script will read the source image (WebP/JPEG/PNG) and write out sized files
with names like <basename>-1200.webp, <basename>-800.webp, <basename>-400.webp and
JPEG fallbacks when requested.
"""
import argparse
from pathlib import Path
from PIL import Image


def generate_variants(source: Path, sizes, formats):
    im = Image.open(source)
    base = source.stem
    out_dir = source.parent

    for w in sizes:
        if im.width <= w:
            # If source is smaller than requested size, use source width
            target_w = im.width
        else:
            target_w = w
        ratio = target_w / float(im.width)
        target_h = int(im.height * ratio)
        resized = im.resize((target_w, target_h), Image.LANCZOS)

        for fmt in formats:
            out_ext = fmt.lower()
            out_name = f"{base}-{target_w}.{out_ext}"
            out_path = out_dir / out_name
            save_kwargs = {}
            if out_ext in ("jpg", "jpeg"):
                save_kwargs.update(format="JPEG", quality=85, optimize=True, progressive=True)
                if resized.mode in ("RGBA", "LA"):
                    bg = Image.new("RGB", resized.size, (255, 255, 255))
                    bg.paste(resized, mask=resized.split()[3])
                    bg.save(out_path, **save_kwargs)
                else:
                    resized.convert("RGB").save(out_path, **save_kwargs)
            elif out_ext == "webp":
                save_kwargs.update(format="WEBP", quality=80, method=6)
                resized.save(out_path, **save_kwargs)
            else:
                # fallback to PNG
                resized.save(out_path, format="PNG", optimize=True)
            print(f"Wrote {out_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Source image path")
    parser.add_argument("--sizes", nargs="+", type=int, default=[1200, 800, 400])
    parser.add_argument("--formats", nargs="+", default=["webp", "jpg"], help="Output formats (webp, jpg, png)")
    args = parser.parse_args()

    src = Path(args.source)
    if not src.exists():
        print(f"Source not found: {src}")
        return

    generate_variants(src, args.sizes, args.formats)


if __name__ == "__main__":
    main()
