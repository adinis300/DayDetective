"""
Game screen — handles both Standard and Time Attack modes.
"""
import random, datetime
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout     import BoxLayout
from kivy.uix.gridlayout    import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label         import Label
from kivy.uix.button        import Button
from kivy.uix.widget        import Widget
from kivy.uix.popup         import Popup
from kivy.graphics          import Color, RoundedRectangle, Rectangle
from kivy.animation         import Animation
from kivy.clock             import Clock
from kivy.metrics           import dp, sp
from kivy.app               import App

import theme, store
from widgets import PillButton, DayButton, ParticleWidget, StatBadge, HeartsWidget, CardMixin

LIVES  = 3
TIME   = 120
DAYS   = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
D_START = datetime.date(1950, 1, 1)
D_END   = datetime.date(2060, 12, 31)

def _random_date():
    delta = (D_END - D_START).days
    return D_START + datetime.timedelta(days=random.randint(0, delta))

def _fmt(d):  return d.strftime('%d %b %Y')
def _day(d):  return d.strftime('%A')


# ──────────────────────────────────────────────────────────────────
#  Date display card
# ──────────────────────────────────────────────────────────────────
class DateCard(BoxLayout, CardMixin):
    def __init__(self, **kw):
        super().__init__(orientation='vertical',
                         padding=[dp(16), dp(18)],
                         spacing=dp(6),
                         size_hint=(1, None),
                         height=dp(120), **kw)
        self.card_color = theme.CARD
        self.bind_card()

        self._prompt = Label(
            text='What day of the week falls on…',
            font_size=sp(14), color=theme.SUB,
            italic=True, size_hint_y=None, height=dp(22))

        self._date_lbl = Label(
            text='', font_size=sp(36), bold=True,
            color=theme.TEXT, size_hint_y=None, height=dp(52),
            font_name='RobotoMono')

        self.add_widget(self._prompt)
        self.add_widget(self._date_lbl)

    def set_date(self, text):
        self._date_lbl.text  = text
        self._date_lbl.color = theme.TEXT
        anim = Animation(font_size=sp(42), duration=0.1) + \
               Animation(font_size=sp(36), duration=0.1)
        anim.start(self._date_lbl)

    def flash_wrong(self):
        anim = Animation(color=theme.RED, duration=0.12) + \
               Animation(color=theme.TEXT, duration=0.3)
        anim.start(self._date_lbl)


# ──────────────────────────────────────────────────────────────────
#  Game Over popup
# ──────────────────────────────────────────────────────────────────
class GameOverPopup(Popup):
    def __init__(self, score, mode, on_play_again, on_home, on_leaderboard, **kw):
        content = BoxLayout(orientation='vertical',
                            padding=dp(28), spacing=dp(16))

        is_time = mode == 'time'
        header  = "TIME'S UP!" if is_time else 'GAME  OVER'
        h_color = theme.AMBER if is_time else theme.RED

        content.add_widget(Label(text=header, font_size=sp(30),
                                 bold=True, color=h_color,
                                 size_hint_y=None, height=dp(44)))
        content.add_widget(Label(text=f'Final Score:  {score}',
                                 font_size=sp(22), bold=True, color=theme.GOLD,
                                 size_hint_y=None, height=dp(36)))

        rank_text = _rank(score)
        content.add_widget(Label(text=rank_text, font_size=sp(14),
                                 color=theme.SUB, italic=True,
                                 size_hint_y=None, height=dp(24)))

        content.add_widget(Widget())

        btn_row = BoxLayout(orientation='horizontal',
                            spacing=dp(10),
                            size_hint_y=None, height=dp(52))

        pa = PillButton(text='Play Again', bg_color=theme.ACCENT)
        lb = PillButton(text='🏆 Scores',  bg_color=theme.CARD2)
        hm = PillButton(text='← Home',    bg_color=theme.CARD2)
        lb.color = theme.GOLD
        hm.color = theme.SUB

        btn_row.add_widget(pa)
        btn_row.add_widget(lb)
        btn_row.add_widget(hm)
        content.add_widget(btn_row)

        super().__init__(
            title='',
            content=content,
            size_hint=(0.9, None),
            height=dp(340),
            background_color=theme.CARD,
            separator_height=0,
            **kw)

        pa.bind(on_release=lambda *_: (self.dismiss(), on_play_again()))
        lb.bind(on_release=lambda *_: (self.dismiss(), on_leaderboard()))
        hm.bind(on_release=lambda *_: (self.dismiss(), on_home()))

        with self.canvas.before:
            Color(*theme.CARD)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size,
                                        radius=[dp(18)])
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *_):
        self._bg.pos  = self.pos
        self._bg.size = self.size


def _rank(s):
    if s == 0:  return 'Better luck next time.'
    if s < 4:   return 'Rookie Detective'
    if s < 9:   return 'Seasoned Investigator'
    if s < 15:  return 'Calendar Virtuoso'
    return 'Legendary Day Oracle 🏆'


# ──────────────────────────────────────────────────────────────────
#  Game Screen
# ──────────────────────────────────────────────────────────────────
class GameScreen(Screen):
    def __init__(self, mode='standard', **kw):
        super().__init__(**kw)
        self.mode     = mode
        self.score    = 0
        self.streak   = 0
        self.lives    = LIVES
        self.time_left = TIME
        self.answered  = False
        self._cur_date = None
        self._cur_ans  = None
        self._timer_ev = None
        self._build()

    # ── BUILD ─────────────────────────────────
    def _build(self):
        root = RelativeLayout()

        self._particles = ParticleWidget(size_hint=(1,1))
        root.add_widget(self._particles)

        layout = BoxLayout(orientation='vertical',
                           padding=[dp(16), dp(14), dp(16), dp(16)],
                           spacing=dp(10),
                           size_hint=(1,1))

        # ── Top bar ──
        top = BoxLayout(orientation='horizontal',
                        size_hint_y=None, height=dp(48),
                        spacing=dp(10))

        back_btn = PillButton(text='← Home', bg_color=theme.CARD2,
                              size_hint_x=None, width=dp(110),
                              height=dp(42))
        back_btn.color = theme.SUB
        back_btn.bind(on_release=lambda *_: self._go_home())

        mode_lbl = Label(
            text=('🕐  Standard Mode' if self.mode=='standard' else '⏱  Time Attack'),
            font_size=sp(20), bold=True,
            color=(theme.ACCENT if self.mode=='standard' else theme.AMBER))

        self._music_btn = PillButton(text='🔊', bg_color=theme.CARD2,
                                     size_hint_x=None, width=dp(52),
                                     height=dp(42))
        self._music_btn.color = theme.SUB
        self._music_btn.bind(on_release=lambda *_: self._toggle_music())

        top.add_widget(back_btn)
        top.add_widget(mode_lbl)
        top.add_widget(self._music_btn)
        layout.add_widget(top)

        # ── HUD ──
        hud = BoxLayout(orientation='horizontal',
                        size_hint_y=None, height=dp(68),
                        spacing=dp(10))

        if self.mode == 'standard':
            self._hearts = HeartsWidget(lives=LIVES)
            hud.add_widget(self._hearts)
        else:
            from kivy.uix.boxlayout import BoxLayout as BL
            timer_box = BL(orientation='vertical',
                           padding=[dp(10), dp(6)],
                           size_hint=(None, None),
                           width=dp(110), height=dp(68))
            with timer_box.canvas.before:
                Color(*theme.CARD2)
                self._timer_bg = RoundedRectangle(
                    pos=timer_box.pos, size=timer_box.size,
                    radius=[dp(theme.RADIUS)])
            timer_box.bind(pos=lambda i,_: setattr(self._timer_bg,'pos',i.pos),
                           size=lambda i,_: setattr(self._timer_bg,'size',i.size))
            timer_box.add_widget(Label(text='TIME', font_size=sp(11),
                                       color=theme.MUTED, bold=False,
                                       size_hint_y=None, height=dp(18)))
            self._timer_lbl = Label(text='2:00', font_size=sp(26),
                                    bold=True, color=theme.TIMER_OK,
                                    size_hint_y=None, height=dp(36))
            timer_box.add_widget(self._timer_lbl)
            hud.add_widget(timer_box)

        self._score_badge  = StatBadge('SCORE',  '0')
        self._streak_badge = StatBadge('STREAK', '0')
        hud.add_widget(self._score_badge)
        hud.add_widget(self._streak_badge)

        hud.add_widget(Widget())  # spacer

        lb_btn = PillButton(text='🏆', bg_color=theme.CARD2,
                            size_hint_x=None, width=dp(56), height=dp(56))
        lb_btn.color = theme.GOLD
        lb_btn.bind(on_release=lambda *_: self._open_leaderboard())
        hud.add_widget(lb_btn)

        layout.add_widget(hud)

        # ── Date card ──
        self._date_card = DateCard()
        layout.add_widget(self._date_card)

        # ── Day buttons — 4 on top row, 3 centred below ──
        self._day_btns = []

        top_row = GridLayout(cols=4, spacing=dp(10),
                             size_hint_y=None, height=dp(58))
        for day in DAYS[:4]:
            b = DayButton(text=day)
            b.bind(on_release=lambda btn, d=day: self._guess(d))
            top_row.add_widget(b)
            self._day_btns.append(b)

        bot_row = BoxLayout(orientation='horizontal',
                            spacing=dp(10),
                            size_hint_y=None, height=dp(58))
        bot_row.add_widget(Widget(size_hint_x=0.5/3))
        for day in DAYS[4:]:
            b = DayButton(text=day, size_hint_x=1)
            b.bind(on_release=lambda btn, d=day: self._guess(d))
            bot_row.add_widget(b)
            self._day_btns.append(b)
        bot_row.add_widget(Widget(size_hint_x=0.5/3))

        layout.add_widget(top_row)
        layout.add_widget(bot_row)

        # ── Feedback area ──
        self._status_lbl = Label(text='', font_size=sp(18), bold=True,
                                 color=theme.GREEN,
                                 size_hint_y=None, height=dp(30))
        self._explain_lbl = Label(text='', font_size=sp(13),
                                  color=theme.SUB,
                                  size_hint_y=None, height=dp(22))
        layout.add_widget(self._status_lbl)
        layout.add_widget(self._explain_lbl)

        # ── Next button ──
        self._next_btn = PillButton(text='Next Date  →',
                                    bg_color=theme.ACCENT,
                                    size_hint=(0.7, None),
                                    pos_hint={'center_x': 0.5})
        self._next_btn.bind(on_release=lambda *_: self._next_round())
        self._next_btn.opacity = 0
        self._next_btn.disabled = True
        layout.add_widget(self._next_btn)

        layout.add_widget(Widget())  # bottom spacer

        root.add_widget(layout)
        self.add_widget(root)

    # ── SCREEN LIFECYCLE ──────────────────────
    def on_enter(self, *args):
        self._restart()

    def on_leave(self, *args):
        self._cancel_timer()

    # ── TIMER ─────────────────────────────────
    def _start_timer(self):
        self._cancel_timer()
        self._timer_ev = Clock.schedule_interval(self._tick_timer, 1)

    def _tick_timer(self, dt):
        self.time_left -= 1
        m, s = divmod(self.time_left, 60)
        self._timer_lbl.text  = f'{m}:{s:02d}'
        self._timer_lbl.color = theme.TIMER_LO if self.time_left <= 20 else theme.TIMER_OK
        if self.time_left <= 0:
            self._cancel_timer()
            self._time_up()

    def _cancel_timer(self):
        if self._timer_ev:
            Clock.unschedule(self._timer_ev)
            self._timer_ev = None

    def _time_up(self):
        for b in self._day_btns: b.disabled = True
        self._next_btn.opacity  = 0
        self._next_btn.disabled = True
        store.add_score(self.mode, self.score)
        Clock.schedule_once(lambda dt: self._show_game_over(time_up=True), 0.4)

    # ── GAME LOGIC ────────────────────────────
    def _next_round(self):
        self.answered  = False
        self._cur_date = _random_date()
        self._cur_ans  = _day(self._cur_date)

        self._date_card.set_date(_fmt(self._cur_date))
        self._status_lbl.text  = ''
        self._explain_lbl.text = ''

        for b in self._day_btns: b.reset()

        anim = Animation(opacity=0, duration=0.15)
        anim.bind(on_complete=lambda *_: setattr(self._next_btn, 'disabled', True))
        anim.start(self._next_btn)

    def _guess(self, day):
        if self.answered: return
        self.answered = True
        correct = (day == self._cur_ans)

        for b in self._day_btns:
            if b.text == self._cur_ans:
                b.mark_correct()
            elif b.text == day and not correct:
                b.mark_wrong()
            else:
                b.mark_dim()

        if correct:
            self.score  += 1
            self.streak += 1
            note = f'   🔥 {self.streak} in a row!' if self.streak >= 3 else ''
            self._status_lbl.text  = '✓   Correct!'
            self._status_lbl.color = theme.GREEN
            self._explain_lbl.text = f'{_fmt(self._cur_date)} is a {self._cur_ans}.{note}'
        else:
            self.streak = 0
            self._status_lbl.text  = f'✗   Wrong — it was {self._cur_ans}'
            self._status_lbl.color = theme.RED
            self._explain_lbl.text = f'You guessed {day}.'
            self._date_card.flash_wrong()
            if self.mode == 'standard':
                self.lives -= 1
                self._hearts.set_lives(self.lives)

        self._score_badge.set_value(self.score)
        self._streak_badge.set_value(
            self.streak,
            color=theme.GOLD if self.streak >= 3 else theme.ACCENT)

        if self.mode == 'standard' and self.lives <= 0:
            store.add_score(self.mode, self.score)
            Clock.schedule_once(lambda dt: self._show_game_over(), 0.6)
        elif self.mode == 'time':
            Clock.schedule_once(lambda dt: self._next_round(), 0.85)
        else:
            anim = Animation(opacity=1, duration=0.2)
            anim.bind(on_complete=lambda *_: setattr(self._next_btn, 'disabled', False))
            anim.start(self._next_btn)

    def _show_game_over(self, time_up=False):
        popup = GameOverPopup(
            score=self.score, mode=self.mode,
            on_play_again=self._restart,
            on_home=self._go_home,
            on_leaderboard=self._open_leaderboard)
        popup.open()

    def _restart(self):
        self._cancel_timer()
        self.score     = 0
        self.streak    = 0
        self.lives     = LIVES
        self.time_left = TIME
        self.answered  = False

        self._score_badge.set_value(0)
        self._streak_badge.set_value(0)

        if self.mode == 'standard':
            self._hearts.set_lives(LIVES)
        else:
            self._timer_lbl.text  = '2:00'
            self._timer_lbl.color = theme.TIMER_OK
            self._start_timer()

        self._next_round()

    def _go_home(self):
        self._cancel_timer()
        self.manager.current = 'home'

    def _open_leaderboard(self):
        lb = self.manager.get_screen('leaderboard')
        lb.active_tab = self.mode
        lb.refresh()
        self.manager.current = 'leaderboard'

    def _toggle_music(self):
        app = App.get_running_app()
        playing = app.toggle_music()
        self._music_btn.text = '🔊' if playing else '🔇'
