"""Runner for the game."""

import arcade
from .constants import MUSIC_PATH
from .gui import GameGUI


def main():
    """Main method"""
    window = GameGUI()
    window.setup()

    # Load music from path
    music = arcade.Sound(MUSIC_PATH)
    music.play(volume=0.5)

    arcade.run()
