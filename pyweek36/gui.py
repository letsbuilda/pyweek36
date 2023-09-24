"""
GUI for the game
"""

import arcade
from arcade.gui import UIManager

from .game import GameWindow
from .constants import *


class GameGUI(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=False)
        self.title = None
        self.v_box = None
        self.manager = None

    def open_level_selector(self):
        """Open level selector"""
        # Clear the window
        self.manager.clear()
        self.manager.enable()

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()

        levels = {
            int(i) if i != "1" else 10: file.stem
            for i, file in enumerate(LEVEL_DIR.iterdir())
            if file.suffix == ".tmx" and file.stem not in {"demo", "template"}
        }
        levels = sorted(levels.items())

        buttons = []
        for level, name in levels:
            button = arcade.gui.UIFlatButton(text=f"Level {level}", width=200)
            self.v_box.add(button.with_space_around(bottom=20))
            buttons.append(button)

            button.on_click = (lambda l: lambda event: self.start_game(l))(level)

        # Create a widget to hold the v_box widget, that will center the buttons
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x", anchor_y="center_y", child=self.v_box
            )
        )

    def start_game(self, level):
        """Start the game"""
        self.close()

        game = GameWindow(level, GameGUI)
        game.setup()
        arcade.run()

    def setup(self):
        """Set up the window"""

        # a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Set background color
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()

        # Add a title in big black letters
        self.title = arcade.gui.UILabel(
            text=SCREEN_TITLE, color=arcade.color.WHITE, font_size=36
        )
        self.v_box.add(self.title.with_space_around(bottom=20))

        # Create the buttons
        start_button = arcade.gui.UIFlatButton(text="Start", width=200)
        self.v_box.add(start_button.with_space_around(bottom=20))

        @start_button.event("on_click")
        def on_click_start(event):
            """Open level selector"""
            self.open_level_selector()

        quit_button = arcade.gui.UIFlatButton(text="Quit", width=200)
        self.v_box.add(quit_button.with_space_around(bottom=20))

        # use a decorator to handle on_click events
        @quit_button.event("on_click")
        def on_click_settings(event):
            """User closes window"""
            arcade.close_window()

        # Create a widget to hold the v_box widget, that will center the buttons
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x", anchor_y="center_y", child=self.v_box
            )
        )

    def on_draw(self):
        self.clear()
        try:
            self.manager.draw()
        except AttributeError:
            pass

    def on_key_press(self, symbol: int, modifiers: int):
        """Handle key presses"""
        if symbol in (arcade.key.ESCAPE, arcade.key.Q):
            self.setup()
