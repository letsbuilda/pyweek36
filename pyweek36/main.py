"""Runner for the game."""

import arcade
from .gui import GameGUI


def main():
    """Main method"""
    window = GameGUI()
    window.setup()
    arcade.run()
