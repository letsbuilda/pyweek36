import arcade
from .constants import SCREEN_HEIGHT, SCREEN_TITLE, SCREEN_WIDTH

class GameWindow(arcade.Window):
    """Our Game Window"""

    def __init__(self, width, height, title):
        """ Create the variables """
        super().__init__(width, height, title)

    def setup(self):
        """ Set up everything with the game """
        pass

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        pass

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """
        pass

    def on_update(self, delta_time):
        """ Movement and game logic """
        pass

    def on_draw(self):
        """ Draw everything """
        self.clear()


def setup_game():
    """ Sets up window. """
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()