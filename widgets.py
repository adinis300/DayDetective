"""
Reusable custom widgets used across screens.
"""
from kivy.uix.button        import Button
from kivy.uix.label         import Label
from kivy.uix.boxlayout     import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget        import Widget
from kivy.graphics          import Color, RoundedRectangle, Rectangle, Line, Ellipse
from kivy.properties        import StringProperty, ColorProperty, NumericProperty
from kivy.animation         import Animation
from kivy.clock             import Clock
from kivy.metrics           import dp, sp
import theme, math, random


# ──────────────────────────────────────────────────────────────────
#  Rounded card background mixin
# ──────────────────────────────────────────────────────────────────
class CardMixin:
    card_color  = ColorProperty(theme.CARD)
    radius_val  = NumericProperty(dp(theme.RADIUS))

    def _draw_card(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.card_color)
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[self.radius_val])

    def bind_card(self):
        self.bind(pos=self._draw_card, size=self._draw_card,
                  card_color=self._draw_card)
        self._draw_card()


# ──────────────────────────────────────────────────────────────────
#  Pill button (primary)
# ──────────────────────────────────────────────────────────────────
class PillButton(Button):
    bg_color   = ColorProperty(theme.ACCENT)
    text_color = ColorProperty(theme.WHITE)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.background_color = (0,0,0,0)
        self.background_normal = ''
        self.color = self.text_color
        self.font_size = sp(theme.F_BTN)
        self.bold  = True
        self.size_hint_y = None
        self.height = dp(54)
        self.bind(pos=self._draw, size=self._draw, bg_color=self._draw)
        self._draw()

    def _draw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[dp(27)])

    def on_press(self):
        Animation(bg_color=theme.ACCENT2, duration=0.08).start(self)

    def on_release(self):
        Animation(bg_color=self.orig_color if hasattr(self,'orig_color') else self.bg_color,
                  duration=0.15).start(self)


# ──────────────────────────────────────────────────────────────────
#  Day answer button (7 of these)
# ──────────────────────────────────────────────────────────────────
class DayButton(Button):
    normal_color  = ColorProperty(theme.CARD2)
    text_color    = ColorProperty(theme.TEXT)
    current_color = ColorProperty(theme.CARD2)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.background_color  = (0,0,0,0)
        self.background_normal = ''
        self.color     = self.text_color
        self.font_size = sp(theme.F_BTN)
        self.bold      = True
        self.size_hint_y = None
        self.height    = dp(58)
        self.bind(pos=self._draw, size=self._draw, current_color=self._draw)
        self._draw()

    def _draw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.current_color)
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[dp(12)])

    def reset(self):
        self.current_color = self.normal_color
        self.color         = self.text_color
        self.disabled      = False

    def mark_correct(self):
        Animation(current_color=theme.GREEN, duration=0.2).start(self)
        self.color    = (0.03, 0.04, 0.06, 1)
        self.disabled = True

    def mark_wrong(self):
        Animation(current_color=theme.RED, duration=0.2).start(self)
        self.disabled = True

    def mark_dim(self):
        self.color    = theme.MUTED
        self.disabled = True

    def on_press(self):
        if not self.disabled:
            Animation(current_color=theme.ACCENT, duration=0.08).start(self)


# ──────────────────────────────────────────────────────────────────
#  Particle canvas (purely decorative background layer)
# ──────────────────────────────────────────────────────────────────
class ParticleWidget(Widget):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._pts = []
        self._ids = []
        Clock.schedule_interval(self._tick, 0.08)
        self.bind(size=self._init_particles)

    def _init_particles(self, *_):
        n = 60
        w, h = self.width or 400, self.height or 700
        self._pts = [
            [random.uniform(0, w), random.uniform(0, h),
             random.uniform(0.008, 0.025) * w,
             random.uniform(0.05, 0.35),
             random.uniform(0.08, 0.7)]
            for _ in range(n)
        ]

    def _tick(self, dt):
        if not self._pts:
            return
        w, h = self.width, self.height
        self.canvas.before.clear()
        with self.canvas.before:
            for p in self._pts:
                p[1] += p[3]
                if p[1] > h:
                    p[1] = 0
                    p[0] = random.uniform(0, w)
                a = p[4]
                Color(a * 0.55, a * 0.55, min(1, a * 0.8), a * 0.6)
                r = p[2]
                Ellipse(pos=(p[0] - r, p[1] - r), size=(r*2, r*2))


# ──────────────────────────────────────────────────────────────────
#  Stat badge (label + value)
# ──────────────────────────────────────────────────────────────────
class StatBadge(BoxLayout, CardMixin):
    label_text = StringProperty('')
    value_text = StringProperty('0')

    def __init__(self, label='', value='0', **kw):
        super().__init__(orientation='vertical', padding=dp(12),
                         spacing=dp(4), size_hint=(None, None),
                         width=dp(90), height=dp(64), **kw)
        self.card_color = theme.CARD2
        self.bind_card()

        self._lbl = Label(text=label, font_size=sp(theme.F_LABEL),
                          color=theme.MUTED, size_hint_y=None, height=dp(18),
                          bold=False)
        self._val = Label(text=value, font_size=sp(20),
                          color=theme.GOLD, bold=True,
                          size_hint_y=None, height=dp(28))
        self.add_widget(self._lbl)
        self.add_widget(self._val)

    def set_value(self, v, color=None):
        self._val.text  = str(v)
        if color:
            self._val.color = color


# ──────────────────────────────────────────────────────────────────
#  Heart lives display
# ──────────────────────────────────────────────────────────────────
class HeartsWidget(BoxLayout, CardMixin):
    def __init__(self, lives=3, **kw):
        super().__init__(orientation='horizontal',
                         padding=[dp(12), dp(10)],
                         spacing=dp(6),
                         size_hint=(None, None),
                         width=dp(110), height=dp(64), **kw)
        self.card_color = theme.CARD2
        self.bind_card()
        self._max   = lives
        self._lives = lives
        self._lbls  = []
        for _ in range(lives):
            lbl = Label(text='♥', font_size=sp(26), color=theme.ACCENT2,
                        size_hint=(None, None), width=dp(26), height=dp(36))
            self.add_widget(lbl)
            self._lbls.append(lbl)

    def set_lives(self, n):
        self._lives = n
        for i, lbl in enumerate(self._lbls):
            lbl.color = theme.ACCENT2 if i < n else theme.MUTED
