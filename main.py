"""
Day Detective — Kivy Android App
Entry point
"""
from kivy.config import Config
Config.set('graphics', 'resizable', '1')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window
from kivy.utils import platform
from kivy.core.audio import SoundLoader

from screens.home   import HomeScreen
from screens.game   import GameScreen
from screens.leaderboard import LeaderboardScreen
import store

Window.clearcolor = (0.031, 0.035, 0.063, 1)   # #080910

class DayDetectiveApp(App):
    def build(self):
        self.title = 'Day Detective'
        self.icon  = 'assets/icon.png'

        # Global music player — pass around via app reference
        self.music = None
        self._load_music()

        sm = ScreenManager(transition=FadeTransition(duration=0.25))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(GameScreen(name='game_standard', mode='standard'))
        sm.add_widget(GameScreen(name='game_time',     mode='time'))
        sm.add_widget(LeaderboardScreen(name='leaderboard'))
        self.sm = sm
        return sm

    def _load_music(self):
        import os
        path = os.path.join(os.path.dirname(__file__), 'assets', 'music.mp3')
        if os.path.exists(path):
            self.music = SoundLoader.load(path)
            if self.music:
                self.music.loop   = True
                self.music.volume = 0.6
                self.music.play()

    def toggle_music(self):
        if not self.music:
            return False
        if self.music.state == 'play':
            self.music.stop()
            return False
        else:
            self.music.play()
            return True

    @property
    def music_playing(self):
        return self.music and self.music.state == 'play'


if __name__ == '__main__':
    DayDetectiveApp().run()
