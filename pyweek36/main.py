"""
Example of Pymunk Physics Engine Platformer
"""

import math

import arcade
from arcade import SpriteList, PymunkPhysicsEngine

from .constants import *
from .sprites import BulletSprite, PlayerSprite


class GameWindow(arcade.Window):
    """Main Window"""

    def __init__(self, width, height, title):
        """Create the variables"""

        super().__init__(width, height, title)

        self.player_sprite: PlayerSprite = PlayerSprite(self)
        self.block_list: SpriteList = SpriteList()
        self.bullet_list: SpriteList = SpriteList()

        self.global_time: float = 0
        self.last_pressed: dict[int, float] = {}
        self.pressed_keys: set[int] = set()
        k = arcade.key
        self.control_map: dict[int, InputType] = (
            dict.fromkeys([k.UP, k.W, k.SPACE], InputType.UP)
            | dict.fromkeys([k.DOWN, k.S], InputType.DOWN)
            | dict.fromkeys([k.LEFT, k.A], InputType.LEFT)
            | dict.fromkeys([k.RIGHT, k.D], InputType.RIGHT)
        )
        self.physics_engine: PymunkPhysicsEngine | None = None

    def load_tilemap(self, map_name):
        tile_map = arcade.tilemap.TileMap(
            ASSETS_DIR / "tiled" / map_name,
            SPRITE_SCALING_TILES,
            hit_box_algorithm="Detailed",
        )

        self.physics_engine = PymunkPhysicsEngine(
            damping=DEFAULT_DAMPING,
            gravity=(0, -GRAVITY),
        )

        # Player sprite
        grid_x = 1
        grid_y = 3
        self.player_sprite.position = (
            SPRITE_SIZE * (grid_x + 0.5),
            SPRITE_SIZE * (grid_y + 0.5),
        )
        self.physics_engine.add_sprite(
            self.player_sprite,
            friction=PLAYER_FRICTION,
            mass=PLAYER_MASS,
            damping=PLAYER_DAMPING,
            moment=arcade.PymunkPhysicsEngine.MOMENT_INF,
            collision_type="player",
        )

        # Walls
        self.block_list = tile_map.sprite_lists["Map"]
        self.physics_engine.add_sprite_list(
            self.block_list,
            friction=WALL_FRICTION,
            collision_type="wall",
            body_type=arcade.PymunkPhysicsEngine.STATIC,
        )

        # Bullets
        self.bullet_list.clear()

        def wall_hit_handler(bullet_sprite, _wall_sprite, _arbiter, _space, _data):
            """Called for bullet/wall collision"""
            bullet_sprite.remove_from_sprite_lists()

        self.physics_engine.add_collision_handler(
            "bullet", "wall", post_handler=wall_hit_handler
        )

    def setup(self):
        """Set up everything with the game"""

        arcade.set_background_color(arcade.color.AMAZON)

        self.load_tilemap("map.tmx")

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        if (type_ := self.control_map.get(key)) is None:
            return
        self.last_pressed[type_] = self.global_time
        self.pressed_keys.add(type_)

    def on_key_release(self, key, modifiers):
        """Called whenever a key is released."""
        if (type_ := self.control_map.get(key)) is None:
            return
        self.pressed_keys.remove(type_)

    def is_buffered(self, key, consume_input=True):
        if self.last_pressed.get(key, -1) + INPUT_BUFFER_DURATION > self.global_time:
            if consume_input:
                self.last_pressed[key] = -1
            return True
        else:
            return False

    def on_mouse_press(self, x, y, button, modifiers):
        """Called whenever the mouse button is clicked."""

        bullet = BulletSprite(20, 5, arcade.color.DARK_YELLOW)
        self.bullet_list.append(bullet)

        # Position the bullet at the player's current location
        start_x, start_y = bullet.position = self.player_sprite.position

        # NOTE: Add self.view_bottom and self.view_left if scrolling
        angle = math.atan2(y - start_y, x - start_x)
        bullet.angle = math.degrees(angle)

        self.physics_engine.add_sprite(
            bullet,
            mass=BULLET_MASS,
            damping=1.0,
            friction=0.6,
            collision_type="bullet",
            gravity=(0, -BULLET_GRAVITY),
            elasticity=0.9,
        )

        # Add force to bullet
        self.physics_engine.apply_force(bullet, (BULLET_MOVE_FORCE, 0))

    def on_update(self, delta_time):
        """Movement and game logic"""

        self.global_time += delta_time
        self.player_sprite.on_update(delta_time)

        # Move items in the physics engine
        self.physics_engine.step()

    def on_draw(self):
        """Draw everything"""
        self.clear()
        self.block_list.draw()
        self.bullet_list.draw()
        self.player_sprite.draw()
        # self.player_sprite.draw_hit_boxes(color=arcade.color.RED, line_thickness=5)


def main():
    """Main function"""
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()
