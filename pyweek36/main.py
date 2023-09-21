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
        self.last_released: dict[int, float] = {}
        self.left_pressed: bool = False
        self.right_pressed: bool = False
        self.up_pressed: bool = False
        self.down_pressed: bool = False

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
        grid_y = 1
        self.player_sprite.position = (
            SPRITE_SIZE * (grid_x + 0.5),
            SPRITE_SIZE * (grid_y + 0.5),
        )
        self.physics_engine.add_sprite(
            self.player_sprite,
            friction=PLAYER_FRICTION,
            mass=PLAYER_MASS,
            moment=arcade.PymunkPhysicsEngine.MOMENT_INF,
            collision_type="player",
            max_horizontal_velocity=PLAYER_MAX_HORIZONTAL_SPEED,
            max_vertical_velocity=PLAYER_MAX_VERTICAL_SPEED,
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

        k = arcade.key
        if key in (k.LEFT, k.A):
            self.left_pressed = True
        elif key in (k.RIGHT, k.D):
            self.right_pressed = True
        elif key in (k.UP, k.W, k.SPACE):
            self.up_pressed = True
            # find out if player is standing on ground, and not on a ladder
            if self.physics_engine.is_on_ground(self.player_sprite):
                # Jump
                impulse = (0, PLAYER_JUMP_IMPULSE)
                self.physics_engine.apply_impulse(self.player_sprite, impulse)
        elif key in (k.DOWN, k.S):
            self.down_pressed = True

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""

        k = arcade.key
        if key in (k.LEFT, k.A):
            self.left_pressed = False
        elif key in (k.RIGHT, k.D):
            self.right_pressed = False
        elif key in (k.UP, k.W, k.SPACE):
            self.up_pressed = False
        elif key in (k.DOWN, k.S):
            self.down_pressed = False

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
