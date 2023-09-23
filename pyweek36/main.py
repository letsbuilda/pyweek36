"""
Example of Pymunk Physics Engine Platformer
"""
import math
from random import random

import arcade
from arcade import PymunkPhysicsEngine, SpriteList

from .constants import *
from .sprites import BulletSprite, PlayerSprite


class GameWindow(arcade.Window):
    """Main Window"""

    textures = {
        "darkmatter": arcade.load_texture(DARKMATTER_TEXTURE_PATH),
        "wall": arcade.load_texture(WALL_TEXTURE_PATH),
        "death_animation": arcade.load_texture(PLAYER_IDLE_ANIM_PATH / "idle01.png"),
    }

    def __init__(self, width, height, title):
        """Create the variables"""

        super().__init__(width, height, title)

        self.player_sprite: PlayerSprite | None = None
        self.block_list: SpriteList = SpriteList()
        self.bullet_list: SpriteList = SpriteList()
        self.spread_queue = []  # heap to store when to spread each sprite

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
        self.dead: int = -1

    def spread_dark_matter(self, _time):
        spread_blocks = {
            block
            for block in self.block_list
            if block.properties["type"] in SPREADABLE_BLOCKS
        }
        target_locations = {
            (block.center_x + dx, block.center_y + dy)
            for block in spread_blocks
            for dx, dy in [
                (-SPRITE_SIZE, 0),
                (SPRITE_SIZE, 0),
                (0, -SPRITE_SIZE),
                (0, SPRITE_SIZE),
            ]
        }
        self.spread_queue.clear()
        for block in self.block_list:
            if block.properties["type"] not in SPREAD_TARGETS:
                continue
            elif block.position not in target_locations:
                continue
            decay_delay = SPREAD_MIN_DELAY + random() * (SPREAD_RATE - SPREAD_MIN_DELAY)
            self.spread_queue.append((self.global_time + decay_delay, block))
        self.spread_queue.sort(reverse=True)  # reverse since we pop from end later

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
        grid_x = 0
        grid_y = 2
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

        def wall_hit_handler(bullet_sprite, wall_sprite, _arbiter, _space, _data):
            """Called for bullet/wall collision"""
            bullet_sprite.remove_from_sprite_lists()

            if wall_sprite.properties["type"] == "darkmatter":
                wall_sprite.properties["type"] = "solid"
                wall_sprite.texture = self.textures["wall"]

        def player_wall_handler(_player_sprite, wall_sprite, _arbiter, _space, _data):
            return not wall_sprite.properties["type"] == "darkmatter"

        self.physics_engine.add_collision_handler(
            "bullet", "wall", post_handler=wall_hit_handler
        )

        self.physics_engine.add_collision_handler(
            "player", "wall", begin_handler=player_wall_handler
        )

        # Reschedule spreading to reset offset
        arcade.unschedule(self.spread_dark_matter)
        arcade.schedule(self.spread_dark_matter, SPREAD_RATE)

    def setup(self):
        """Set up everything with the game"""

        arcade.set_background_color(arcade.color.AMAZON)

        self.load_tilemap("map.tmx")

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
        bullet.properties["spawn_time"] = self.global_time
        self.bullet_list.append(bullet)

        # Position the bullet at the player's current location
        start_x, start_y = self.player_sprite.center_x, self.player_sprite.center_y
        bullet.center_x, bullet.center_y = start_x, start_y

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

        bullet.time = self.global_time

        # Add force to bullet
        self.physics_engine.set_velocity(
            bullet,
            (BULLET_MOVE_FORCE * math.cos(angle), BULLET_MOVE_FORCE * math.sin(angle)),
        )

    def update_tiles(self):
        """Spreads scheduled dark matter"""
        while self.spread_queue and self.spread_queue[-1][0] < self.global_time:
            block: arcade.Sprite
            _, block = self.spread_queue.pop()
            block.texture = self.textures["darkmatter"]
            block.properties["type"] = "darkmatter"

    def on_update(self, delta_time):
        """Movement and game logic"""

        self.global_time += delta_time

        self.player_sprite.on_update(delta_time)
        self.update_tiles()

        # Move items in the physics engine
        self.physics_engine.step()

        if self.player_sprite.position[1] < 0:
            self.load_tilemap("map.tmx")
            self.dead = self.global_time

        for bullet in self.bullet_list:
            if self.global_time - bullet.properties["spawn_time"] > BULLET_KILL_TIME:
                bullet.kill()

    def on_draw(self):
        """Draw everything"""
        self.clear()
        if self.global_time - self.dead > DEATH_ANIMATION_TIME:
            self.block_list.draw()
            self.bullet_list.draw()
            self.player_sprite.draw()
        else:
            self.textures["death_animation"].draw_scaled(
                self.width / 2,
                self.height / 2,
                DEATH_ANIMATION_SCALE
                * math.sin(
                    (math.pi / 4)
                    * (DEATH_ANIMATION_TIME - (self.global_time - self.dead))
                ),
            )


def main():
    """Main function"""
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()
