"""
Leaderboard screen — tabbed Standard / Time Attack.
"""
from kivy.uix.screenmanager  import Screen
from kivy.uix.boxlayout      import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview     import ScrollView
from kivy.uix.label          import Label
from kivy.uix.button         import Button
from kivy.uix.widget         import Widget
from kivy.graphics           import Color, RoundedRectangle, Line
from kivy.metrics            import dp, sp
from kivy.animation          import Animation

import theme, store
from widgets import PillButton, ParticleWidget, CardMixin

MEDALS = ['🥇', '🥈', '🥉', '4th', '5th']


class TabButton(Button):
    def __init__(self, text, color, active=False, **kw):
        super().__init__(text=text,
                         background_color=(0,0,0,0),
                         background_normal='',
                         size_hint_y=None, height=dp(52),
                         font_size=sp(15), bold=True,
                         **kw)
        self._active_color = color
        self.set_active(active)

    def set_active(self, active):
        self._is_active = active
        self.color = self._active_color if active else theme.MUTED
        self.canvas.after.clear()
        if active:
            with self.canvas.after:
                Color(*self._active_color)
                Line(points=[self.x+dp(8), self.y+2,
                             self.x+self.width-dp(8), self.y+2],
                     width=2)
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *_):
        self.set_active(self._is_active)


class EntryRow(BoxLayout, CardMixin):
    def __init__(self, rank_i, entry, **kw):
        super().__init__(orientation='horizontal',
                         padding=[dp(16), dp(14)],
                         spacing=dp(12),
                         size_hint_y=None, height=dp(62), **kw)
        self.card_color = theme.CARD2 if rank_i % 2 == 0 else theme.CARD
        self.bind_card()

        medal_col = theme.GOLD if rank_i == 0 else (theme.SUB if rank_i < 3 else theme.MUTED)

        self.add_widget(Label(
            text=MEDALS[rank_i], font_size=sp(22),
            color=medal_col,
            size_hint_x=None, width=dp(40)))

        self.add_widget(Label(
            text=str(entry['score']), font_size=sp(22),
            bold=True, color=theme.TEXT,
            halign='left', size_hint_x=0.4))

        self.add_widget(Widget())

        self.add_widget(Label(
            text=entry['date'], font_size=sp(13),
            color=theme.SUB,
            halign='right', size_hint_x=None, width=dp(110)))


class LeaderboardScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.active_tab = 'standard'
        self._built = False

    def on_enter(self, *args):
        if not self._built:
            self._build()
            self._built = True
        self.refresh()

    def _build(self):
        root = RelativeLayout()
        self._particles = ParticleWidget(size_hint=(1,1))
        root.add_widget(self._particles)

        layout = BoxLayout(orientation='vertical',
                           padding=[dp(16), dp(20), dp(16), dp(16)],
                           spacing=dp(14),
                           size_hint=(1,1))

        # Header row
        header = BoxLayout(orientation='horizontal',
                           size_hint_y=None, height=dp(52))

        back_btn = PillButton(text='← Back', bg_color=theme.CARD2,
                              size_hint_x=None, width=dp(110), height=dp(44))
        back_btn.color = theme.SUB
        back_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'home'))

        header.add_widget(back_btn)
        header.add_widget(Label(text='🏆  Leaderboard', font_size=sp(24),
                                bold=True, color=theme.GOLD))
        layout.add_widget(header)

        # Tab bar
        tab_bar = BoxLayout(orientation='horizontal',
                            size_hint_y=None, height=dp(52),
                            spacing=0)
        with tab_bar.canvas.before:
            Color(*theme.CARD2)
            self._tab_bg = RoundedRectangle(pos=tab_bar.pos,
                                            size=tab_bar.size,
                                            radius=[dp(10)])
        tab_bar.bind(
            pos=lambda i,_: setattr(self._tab_bg,'pos',i.pos),
            size=lambda i,_: setattr(self._tab_bg,'size',i.size))

        self._tab_std  = TabButton('🕐  Standard Mode', theme.ACCENT,  active=True)
        self._tab_time = TabButton('⏱  Time Attack',   theme.AMBER,   active=False)

        self._tab_std.bind(on_release=lambda *_: self._switch('standard'))
        self._tab_time.bind(on_release=lambda *_: self._switch('time'))

        tab_bar.add_widget(self._tab_std)
        tab_bar.add_widget(self._tab_time)
        layout.add_widget(tab_bar)

        # Scroll area for entries
        self._scroll = ScrollView(size_hint=(1,1))
        self._entries_box = BoxLayout(orientation='vertical',
                                      spacing=dp(6),
                                      size_hint_y=None)
        self._entries_box.bind(minimum_height=self._entries_box.setter('height'))
        self._scroll.add_widget(self._entries_box)
        layout.add_widget(self._scroll)

        root.add_widget(layout)
        self.add_widget(root)

    def _switch(self, mode):
        self.active_tab = mode
        self._tab_std.set_active(mode == 'standard')
        self._tab_time.set_active(mode == 'time')
        self.refresh()

    def refresh(self):
        if not self._built:
            return
        self._entries_box.clear_widgets()
        entries = store.load_lb(self.active_tab)

        color = theme.ACCENT if self.active_tab == 'standard' else theme.AMBER
        label = 'Standard Mode' if self.active_tab == 'standard' else 'Time Attack'

        self._entries_box.add_widget(
            Label(text=f'Top 5 — {label}',
                  font_size=sp(16), color=color, bold=True,
                  size_hint_y=None, height=dp(36), halign='center'))

        if not entries:
            self._entries_box.add_widget(
                Label(text='No scores yet — go play!',
                      font_size=sp(15), color=theme.SUB, italic=True,
                      size_hint_y=None, height=dp(80), halign='center'))
        else:
            for i, entry in enumerate(entries):
                self._entries_box.add_widget(EntryRow(i, entry))
