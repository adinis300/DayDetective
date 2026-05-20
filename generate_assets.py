"""
Run this once to generate placeholder icon + presplash.
Requires: pip install pillow
"""
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Run:  pip install pillow  then try again.")
    raise

import os, math

OUT = os.path.join(os.path.dirname(__file__), 'assets')
os.makedirs(OUT, exist_ok=True)

BG     = (8,   9,  16)
ACCENT = (108, 99, 255)
GOLD   = (255, 209, 102)
TEXT   = (238, 238, 245)

# ── ICON 512×512 ──────────────────────────────────────────────────
img = Image.new('RGBA', (512, 512), BG + (255,))
d   = ImageDraw.Draw(img)

# Outer circle (accent)
d.ellipse([40, 40, 472, 472], fill=ACCENT)

# Inner circle (dark)
d.ellipse([80, 80, 432, 432], fill=BG)

# Magnifying glass body
d.ellipse([160, 130, 300, 270], outline=GOLD, width=20)

# Handle
d.line([(285, 255), (360, 340)], fill=GOLD, width=20)

# Calendar grid dots
for row in range(3):
    for col in range(3):
        cx = 180 + col * 40
        cy = 155 + row * 35
        d.ellipse([cx-6, cy-6, cx+6, cy+6], fill=GOLD)

img.save(os.path.join(OUT, 'icon.png'))
print("icon.png  ✓")

# ── PRESPLASH 1080×1920 ───────────────────────────────────────────
splash = Image.new('RGB', (1080, 1920), BG)
sd     = ImageDraw.Draw(splash)

# Central glow circle
for r in range(180, 0, -10):
    alpha = int(255 * (1 - r/180) * 0.15)
    col = tuple(min(255, int(c + alpha)) for c in ACCENT[:3])
    sd.ellipse([540-r, 900-r, 540+r, 900+r], fill=col)

# Magnifying glass (large)
sd.ellipse([390, 750, 650, 1010], outline=ACCENT, width=18)
sd.line([(630, 990), (740, 1100)], fill=ACCENT, width=18)

# Title text (basic, no custom font needed)
try:
    font_big = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 72)
    font_sub = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 34)
except:
    font_big = ImageFont.load_default()
    font_sub = font_big

sd.text((540, 1150), 'DAY DETECTIVE', fill=TEXT, font=font_big, anchor='mm')
sd.text((540, 1240), 'The Day of the Week Quiz', fill=tuple(int(c*180/255) for c in TEXT), font=font_sub, anchor='mm')

splash.save(os.path.join(OUT, 'presplash.png'))
print("presplash.png  ✓")
print("\nAll assets generated in assets/ folder.")
