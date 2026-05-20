"""
Home screen — animated title, two mode cards, leaderboard button, music toggle.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout     import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label         import Label
from kivy.uix.button        import Button
from kivy.uix.widget        import Widget
from kivy.graphics          import Color, RoundedRectangle, Line
from kivy.animation         import Animation
from kivy.clock             import Clock
from kivy.app               import App
from kivy.metrics           import dp, sp
import math
import theme
from widgets import PillButton, ParticleWidget, CardMixin


class ModeCard(BoxLayout, CardMixin):
    """A tappable mode selection card."""
    def __init__(self, icon, title, desc, color, on_press_cb, **kw):
        super().__init__(orientation='vertical',
                         padding=dp(24), spacing=dp(12), **kw)
        self.card_color = theme.CARD
        self.bind_card()
        self._color = color
        self._cb    = on_press_cb
        self._draw_border()
        self.bind(pos=self._draw_border, size=self._draw_border)

        # Icon
        self.add_widget(Label(text=icon, font_size=sp(44),
                              size_hint_y=None, height=dp(56),
                              color=color))
        # Title
        self.add_widget(Label(text=title, font_size=sp(22),
                              bold=True, color=theme.TEXT,
                              size_hint_y=None, height=dp(32)))
        # Desc
        self.add_widget(Label(text=desc, font_size=sp(14),
                              color=theme.SUB, halign='center',
                              size_hint_y=None, height=dp(54),
                              text_size=(dp(180), None)))
        # Spacer
        self.add_widget(Widget())
        # Play button
        btn = PillButton(text='PLAY', bg_color=color,
                         size_hint=(1, None), height=dp(52))
        btn.bind(on_release=lambda *_: on_press_cb())
        self.add_widget(btn)

    def _draw_border(self, *_):
        self.canvas.after.clear()
        with self.canvas.after:
            Color(*self._color, 0.5)
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height,
                                    dp(theme.RADIUS)), width=1.5)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            Animation(card_color=theme.CARD2, duration=0.08).start(self)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        Animation(card_color=theme.CARD, duration=0.2).start(self)
        return super().on_touch_up(touch)


class HomeScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._anim_t = 0
        self._build()

    def _build(self):
        root = RelativeLayout()

        # ── Particle background ──
        self._particles = ParticleWidget(size_hint=(1,1))
        root.add_widget(self._particles)

        # ── Main vertical layout ──
        layout = BoxLayout(orientation='vertical',
                           padding=[dp(20), dp(36), dp(20), dp(28)],
                           spacing=dp(16),
                           size_hint=(1,1))

        # Title area
        title_box = BoxLayout(orientation='vertical',
                              size_hint_y=None, height=dp(90),
                              spacing=dp(4))
        self._title_lbl = Label(
            text='DAY  DETECTIVE',
            font_size=sp(theme.F_TITLE),
            bold=True, color=theme.ACCENT,
            size_hint_y=None, height=dp(52))
        sub_lbl = Label(
            text='The Day of the Week Quiz',
            font_size=sp(theme.F_LABEL + 1),
            color=theme.SUB,
            size_hint_y=None, height=dp(22))
        title_box.add_widget(self._title_lbl)
        title_box.add_widget(sub_lbl)
        layout.add_widget(title_box)

        # Mode cards row
        cards_row = BoxLayout(orientation='horizontal',
                              spacing=dp(14),
                              size_hint_y=None, height=dp(280))

        self._std_card = ModeCard(
            icon='🕐', title='Standard Mode',
            desc='Answer as many dates\nas you can.\n3 lives — don\'t mess up!',
            color=theme.ACCENT,
            on_press_cb=lambda: self._start('standard'),
            size_hint_x=0.5)

        self._time_card = ModeCard(
            icon='⏱', title='Time Attack',
            desc='Score as high as\npossible in 2 minutes.\nNo lives — just speed!',
            color=theme.AMBER,
            on_press_cb=lambda: self._start('time'),
            size_hint_x=0.5)

        cards_row.add_widget(self._std_card)
        cards_row.add_widget(self._time_card)
        layout.add_widget(cards_row)

        # Bottom row: Leaderboard + Music
        bottom = BoxLayout(orientation='horizontal',
                           spacing=dp(12),
                           size_hint_y=None, height=dp(54))

        lb_btn = PillButton(text='🏆   Leaderboard',
                            bg_color=theme.CARD2,
                            size_hint_x=0.7)
        lb_btn.color = theme.GOLD
        lb_btn.bind(on_release=lambda *_: self._open_leaderboard())

        self._music_btn = PillButton(text='🔊  Music',
                                     bg_color=theme.CARD2,
                                     size_hint_x=0.3)
        self._music_btn.color = theme.SUB
        self._music_btn.bind(on_release=lambda *_: self._toggle_music())

        bottom.add_widget(lb_btn)
        bottom.add_widget(self._music_btn)
        layout.add_widget(bottom)

        # Version
        layout.add_widget(Label(text='v2.1', font_size=sp(11),
                                color=theme.MUTED,
                                size_hint_y=None, height=dp(18)))

        root.add_widget(layout)
        self.add_widget(root)

        Clock.schedule_interval(self._pulse_title, 0.05)

    def _pulse_title(self, dt):
        self._anim_t += dt
        # Gentle opacity pulse on title
        a = 0.85 + 0.15 * math.sin(self._anim_t * 1.6)
        self._title_lbl.color = (*theme.ACCENT[:3], a)

    def _start(self, mode):
        sm = self.manager
        sm.current = f'game_{mode}'

    def _open_leaderboard(self):
        lb = self.manager.get_screen('leaderboard')
        lb.active_tab = 'standard'
        lb.refresh()
        self.manager.current = 'leaderboard'

    def _toggle_music(self):
        app = App.get_running_app()
        playing = app.toggle_music()
        self._music_btn.text = '🔊  Music' if playing else '🔇  Muted'
