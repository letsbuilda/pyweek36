"""
Example of Pymunk Physics Engine Platformer
"""

import math
from random import choice, random, sample
from time import perf_counter

import arcade
from arcade import PymunkPhysicsEngine, SpriteList, Camera
from pyglet.math import Vec2

from .constants import *
from .sprites import BulletSprite, PlayerSprite


class GameWindow(arcade.Window):
    """Main Window"""

    def __init__(self, width, height, title):
        """Create the variables"""

        super().__init__(width, height, title, False, True)

        self.player_sprite: PlayerSprite | None = None
        self.block_list: SpriteList = SpriteList()
        self.bullet_list: SpriteList = SpriteList()

        self.next_spread = None
        self.last_spread: float | None = None
        # Track the current state of what key is pressed
        self.global_time: float = 0
        self.last_pressed: dict[int, float] = {}
        self.pressed_inputs: set[int] = set()
        k = arcade.key
        self.control_map: dict[int, InputType] = (
            dict.fromkeys([k.UP, k.W, k.SPACE], InputType.UP)
            | dict.fromkeys([k.DOWN, k.S], InputType.DOWN)
            | dict.fromkeys([k.LEFT, k.A], InputType.LEFT)
            | dict.fromkeys([k.RIGHT, k.D], InputType.RIGHT)
        )
        self.physics_engine: PymunkPhysicsEngine | None = None

        self.camera: Camera | None = None

    def find_adjacent_blocks(self, block):
        """Returns a list of blocks adjacent to the given block"""
        adjacent_blocks = []
        for other_block in self.block_list:
            if block == other_block:
                continue

            if (
                block.right == other_block.left
                and block.center_y == other_block.center_y
                or block.left == other_block.right
                and block.center_y == other_block.center_y
                or block.top == other_block.bottom
                and block.center_x == other_block.center_x
                or block.bottom == other_block.top
                and block.center_x == other_block.center_x
            ):
                adjacent_blocks.append(other_block)
        return adjacent_blocks

    def load_tilemap(self, map_name):
        self.player_sprite = PlayerSprite(self)

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

        self.camera = Camera(self.width, self.height)

        arcade.set_background_color(arcade.color.AMAZON)

        self.load_tilemap("map.tmx")

        self.last_spread = self.global_time
        # Set the next spread time to be DARKMATTER_DECAY_RATE +/- DARKMATTER_DECAY_RATE_MARGIN
        self.next_spread = self.last_spread + DARKMATTER_DECAY_RATE * (
            1 + DARKMATTER_DECAY_RATE_MARGIN * (2 * random() - 1)
        )

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        if (type_ := self.control_map.get(key)) is None:
            return
        self.last_pressed[type_] = self.global_time
        self.pressed_inputs.add(type_)

    def on_key_release(self, key, modifiers):
        """Called whenever a key is released."""
        if (type_ := self.control_map.get(key)) is None:
            return
        self.pressed_inputs.discard(type_)

    def is_buffered(self, key):
        return self.last_pressed.get(key, -1) + INPUT_BUFFER_DURATION > self.global_time

    def consume_buffer(self, key):
        self.last_pressed[key] = -1

    def on_mouse_press(self, x, y, button, modifiers):
        """Called whenever the mouse button is clicked."""

        bullet = BulletSprite(20, 5, arcade.color.DARK_YELLOW)
        self.bullet_list.append(bullet)

        # Position the bullet at the player's current location
        start_x, start_y = bullet.position = self.player_sprite.position

        angle = math.atan2(y - start_y, x - start_x + self.camera.position[0])
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

        # Check if it's time to spread dark matter
        for block in sample([*self.block_list], len(self.block_list)):
            spreadable_blocks = ["darkmatter", "source"]
            if block.properties["type"] in spreadable_blocks:
                adjacent_blocks = self.find_adjacent_blocks(block)
                adjacent_solid_blocks = [
                    b for b in adjacent_blocks if b.properties["type"] == "solid"
                ]
                if len(adjacent_solid_blocks) > 0 and perf_counter() > self.next_spread:
                    new_block = choice(adjacent_solid_blocks)
                    new_block.properties["type"] = "darkmatter"
                    new_block.texture = DARKMATTER_TEXTURE
                    self.last_spread = perf_counter()
                    self.next_spread = self.last_spread + DARKMATTER_DECAY_RATE * (
                            1 + DARKMATTER_DECAY_RATE_MARGIN * (2 * random() - 1)
                    )

        # Move items in the physics engine
        self.physics_engine.step()

        camera_x_target = (self.player_sprite.center_x
                           - self.camera.viewport_width / 2)
        normalized_velocity = (8.7 - math.log2(401 - self.player_sprite.velocity[0])) / 6
        if normalized_velocity > CAMERA_LOOKAHEAD_THRESHOLD:
            camera_x_target += normalized_velocity * CAMERA_LOOKAHEAD
        self.camera.move_to(
            Vec2(max(camera_x_target, 0), 0),
            CAMERA_DAMPING,
        )

    def on_draw(self):
        """Draw everything"""
        self.clear()
        self.camera.use()
        self.block_list.draw()
        self.bullet_list.draw()
        self.player_sprite.draw()
        # self.player_sprite.draw_hit_boxes(color=arcade.color.RED, line_thickness=5)


def main():
    """Main function"""
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()
