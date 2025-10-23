#!/usr/bin/env python3
from PIL import Image
from pathlib import Path
import shutil
from datetime import datetime
import sys

def main():
    if len(sys.argv) < 2:
        print('Usage: optimize_single_image.py <basename> [dir]')
        return
    name = sys.argv[1]
    root = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('assets/images')
    orig = root / (name + '.jpg')
    if not orig.exists():
        orig = root / (name + '.jpeg')
    if not orig.exists():
        print('Original not found:', orig)
        return

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = root / '.image_backups' / timestamp
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(orig, backup / orig.name)

    with Image.open(orig) as im:
        rgb = im.convert('RGB')
        opt_jpeg = root / (name + '.opt.jpg')
        rgb.save(opt_jpeg, format='JPEG', quality=82, optimize=True, progressive=True)
        opt_jpeg.replace(orig)
        webp = root / (name + '.webp')
        rgb.save(webp, format='WEBP', quality=82)

    print('Optimized and created webp at', webp)
    print('Backup at', backup)

if __name__ == '__main__':
    main()
