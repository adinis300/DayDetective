"""
Shared design tokens — colours, fonts, spacing.
All colours are RGBA tuples (0-1 range) for Kivy.
"""
from kivy.utils import get_color_from_hex as H

# ── Palette ──────────────────────────────────────────────────────
BG        = H('#080910')
CARD      = H('#10111c')
CARD2     = H('#181929')
BORDER    = H('#21223a')
ACCENT    = H('#6c63ff')
ACCENT2   = H('#ff6584')
GREEN     = H('#3ecf8e')
RED       = H('#ff5068')
GOLD      = H('#ffd166')
AMBER     = H('#ffaa33')
TEXT      = H('#eeeef5')
SUB       = H('#8888aa')
MUTED     = H('#44445a')
TIMER_OK  = H('#3ecf8e')
TIMER_LO  = H('#ff6584')
WHITE     = H('#ffffff')

# ── Typography (sp values) ────────────────────────────────────────
F_TITLE   = 34
F_TITLE2  = 26
F_DATE    = 40
F_BODY    = 17
F_BTN     = 18
F_LABEL   = 13
F_SMALL   = 12

# ── Spacing (dp values) ──────────────────────────────────────────
PAD_LG    = 28
PAD_MD    = 18
PAD_SM    = 10
RADIUS    = 14
