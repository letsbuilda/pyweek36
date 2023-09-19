import arcade
from .constants import (
    PLAYER_MOVE_FORCE_IN_AIR,
    SCREEN_HEIGHT,
    SCREEN_TITLE,
    SCREEN_WIDTH,
    PLAYER_MOVE_FORCE_ON_GROUND,
    PLAYER_JUMP_IMPULSE
)
from sprites import PlayerSprite
from typing import Optional


class GameWindow(arcade.Window):
    """Our Game Window"""

    def __init__(self, width, height, title):
        """Create the variables"""
        super().__init__(width, height, title)

        self.physics_engine: Optional[arcade.PymunkPhysicsEngine] = None

        self.player_list: Optional[arcade.SpriteList] = None
        self.wall_list: Optional[arcade.SpriteList] = None
        self.bullet_list: Optional[arcade.SpriteList] = None
        # We can always add more sprite lists here.

        self.left_pressed: bool = False
        self.right_pressed: bool = False

    def setup(self):
        """Set up everything with the game"""
        self.player_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()

        self.player_sprite = PlayerSprite()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.UP:
            if self.physics_engine.is_on_ground(self.player_sprite):
                impulse = (0, PLAYER_JUMP_IMPULSE)
                self.physics_engine.apply_impulse(self.player_sprite, impulse)

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False

    def on_update(self, delta_time):
        """Movement and game logic"""
        is_on_ground = self.physics_engine.is_on_ground(self.player_sprite)
        if self.left_pressed and not self.right_pressed:
            if is_on_ground:
                force = (-PLAYER_MOVE_FORCE_ON_GROUND, 0)
            else:
                force = (-PLAYER_MOVE_FORCE_IN_AIR, 0)
            self.physics_engine.apply_force(self.player_sprite, force)
            self.physics_engine.set_friction(self.player_sprite, 0)
        elif self.right_pressed and not self.left_pressed:
            if is_on_ground:
                force = (PLAYER_MOVE_FORCE_ON_GROUND, 0)
            else:
                force = (PLAYER_MOVE_FORCE_IN_AIR, 0)
            self.physics_engine.apply_force(self.player_sprite, force)
            self.physics_engine.set_friction(self.player_sprite, 0)
        else:
            self.physics_engine.set_friction(self.player_sprite, 1.0)

    def on_draw(self):
        """Draw everything"""
        self.clear()


def setup_game():
    """Sets up window."""
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    setup_game()
