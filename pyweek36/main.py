"""RunnerZ for the game."""

import arcade
from .constants import MUSIC_PATH
from .gui import GameGUI

from threading import Thread


background_music = arcade.Sound(MUSIC_PATH)
music_id = background_music.play(volume=0.5)


# Game music theme thread plays infinitely
def play_music():
    # If music is not playing, play it
    global background_music, music_id
    if not background_music.is_playing(music_id):
        music_id = background_music.play(volume=0.5)


def main():
    """Main method"""
    window = GameGUI()
    window.setup()

    # Start the background music
    music_thread = Thread(target=play_music)
    music_thread.start()

    arcade.run()
