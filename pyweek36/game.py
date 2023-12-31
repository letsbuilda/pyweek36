"""
Example of Pymunk Physics Engine Platformer
"""
import math
from random import random

import arcade
from arcade import PymunkPhysicsEngine, SpriteList, Camera
from pyglet.math import Vec2

from .constants import *
from .sprites import BulletSprite, PlayerSprite


class GameWindow(arcade.Window):
    """Main Window"""

    textures = {
        "darkmatter": arcade.load_texture(DARKMATTER_TEXTURE_PATH),
        "wall": arcade.load_texture(WALL_TEXTURE_PATH),
        "death_animation": arcade.load_texture(PLAYER_IDLE_ANIM_PATH / "idle01.png"),
    }

    def __init__(self, level_name: str, previous_window):
        """Create the variables"""

        self.previous_window = previous_window

        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=False)

        self.player_sprite: PlayerSprite | None = None
        self.block_list: SpriteList = SpriteList()
        self.background_sprite_list: SpriteList = SpriteList()
        self.bullet_list: SpriteList = SpriteList()
        self.spread_queue = []  # heap to store when to spread each sprite
        self.spread_rate = SPREAD_RATE
        self.minimum_spread_delay = SPREAD_MIN_DELAY

        self.map_name = level_name

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

        self.camera: Camera | None = None

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
            decay_delay = self.minimum_spread_delay + random() * (
                self.spread_rate - self.minimum_spread_delay
            )
            self.spread_queue.append((self.global_time + decay_delay, block))
        self.spread_queue.sort(reverse=True)  # reverse since we pop from end later

    def load_tilemap(self, map_name):
        self.player_sprite = PlayerSprite(self)

        tile_map = arcade.tilemap.TileMap(
            ASSETS_DIR / "tiled" / "levels" / f"level{map_name}.tmx",
            SPRITE_SCALING_TILES,
            hit_box_algorithm="Detailed",
        )

        # Get spread rate from map
        if (spread_rate := tile_map.properties.get("Spread Rate")) != "":
            self.spread_rate = float(spread_rate)
        if (spread_min_delay := tile_map.properties.get("Minimum Spread Delay")) != "":
            self.minimum_spread_delay = float(spread_min_delay)

        self.physics_engine = PymunkPhysicsEngine(
            damping=DEFAULT_DAMPING,
            gravity=(0, -GRAVITY),
        )

        # Load player position from Player layer of map
        player_layer = tile_map.sprite_lists["Player"]
        self.player_sprite.position = Vec2(*player_layer[0].position)

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

        # Background
        self.background_sprite_list = tile_map.sprite_lists["Background"]

        # Bullets
        self.bullet_list.clear()

        def wall_hit_handler(bullet_sprite, wall_sprite, _arbiter, _space, _data):
            """Called for bullet/wall collision"""
            bullet_sprite.remove_from_sprite_lists()

            if wall_sprite.properties["type"] == "darkmatter":
                wall_sprite.properties["type"] = "solid"
                wall_sprite.properties["health"] = 1
                wall_sprite.texture = self.textures["wall"]

        def player_wall_handler(_player_sprite, wall_sprite, _arbiter, _space, _data):
            return not wall_sprite.properties["type"] in {"darkmatter", "source"}

        self.physics_engine.add_collision_handler(
            "bullet", "wall", post_handler=wall_hit_handler
        )

        self.physics_engine.add_collision_handler(
            "player", "wall", begin_handler=player_wall_handler
        )

        # Reschedule spreading to reset offset
        self.spread_queue.clear()
        arcade.unschedule(self.spread_dark_matter)
        arcade.schedule(self.spread_dark_matter, self.spread_rate)

    def setup(self):
        """Set up everything with the game"""

        self.camera = Camera(self.width, self.height)

        arcade.set_background_color(arcade.color.AMAZON)

        self.load_tilemap(self.map_name)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        if key in {arcade.key.ESCAPE, arcade.key.Q}:
            # Open previous window
            self.close()
            window = self.previous_window()
            window.setup()
            window.open_level_selector()
            arcade.run()

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
        start_x, start_y = bullet.position = self.player_sprite.position

        angle = math.atan2(y - start_y, x - start_x + self.camera.position[0])
        bullet.angle = math.degrees(angle)

        # Move the bullet forwards a bit to prevent it from colliding with the player
        bullet.position += Vec2.from_polar(30, angle)

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
        self.physics_engine.set_velocity(
            bullet,
            (BULLET_VELOCITY * math.cos(angle), BULLET_VELOCITY * math.sin(angle)),
        )

        sound = arcade.Sound(SOUNDS_DIR / "bullet.wav")
        sound.play(volume=0.5)

    def update_tiles(self):
        """Spreads scheduled dark matter"""
        while self.spread_queue and self.spread_queue[-1][0] < self.global_time:
            block: arcade.Sprite
            _, block = self.spread_queue.pop()
            if block.properties.get("health", 0) > 0:
                block.properties["health"] -= 1
                continue
            block.texture = self.textures["darkmatter"]
            block.properties["type"] = "darkmatter"
            block.remove_from_sprite_lists()
            self.block_list.append(block)
            self.physics_engine.add_sprite(
                block,
                friction=WALL_FRICTION,
                collision_type="wall",
                body_type=arcade.PymunkPhysicsEngine.STATIC,
            )

    def on_update(self, delta_time):
        """Movement and game logic"""

        # If player is to right of screen, win
        if self.player_sprite.position[0] > self.width:
            sound = arcade.Sound(SOUNDS_DIR / "level_complete.wav")
            sound.play(volume=2)
            self.player_sprite.stop_movement_sound()
            self.close()
            window = self.previous_window()
            window.setup()
            window.open_level_selector()
            arcade.run()

        self.global_time += delta_time

        self.player_sprite.on_update(delta_time)
        self.update_tiles()

        # Move items in the physics engine
        self.physics_engine.step()

        # camera_x_target = self.player_sprite.center_x - self.camera.viewport_width / 2
        # x_vel = self.player_sprite.velocity[0]
        # abs_normalized_vel = math.log2(
        #     PLAYER_WALK_SPEED - min(abs(x_vel), PLAYER_WALK_SPEED - 1)
        # ) / math.log2(PLAYER_WALK_SPEED)
        # if abs_normalized_vel > CAMERA_LOOKAHEAD_THRESHOLD:
        #     camera_x_target += (
        #         math.copysign(abs_normalized_vel, x_vel) * CAMERA_LOOKAHEAD
        #     )
        # self.camera.move_to(
        #     Vec2(max(camera_x_target, 0), 0),
        #     CAMERA_DAMPING,
        # )

        if self.player_sprite.position[1] < 0:
            self.load_tilemap(self.map_name)
            self.dead = self.global_time

            self.player_sprite.stop_movement_sound()

            sound = arcade.Sound(SOUNDS_DIR / "fall.wav")
            sound.play(volume=0.5)

        for bullet in self.bullet_list:
            if self.global_time - bullet.properties["spawn_time"] > BULLET_KILL_TIME:
                bullet.kill()

    def on_draw(self):
        """Draw everything"""
        self.clear()
        if self.global_time - self.dead > DEATH_ANIMATION_TIME:
            self.camera.use()
            self.background_sprite_list.draw()
            self.block_list.draw()
            self.bullet_list.draw()
            self.player_sprite.draw()
        else:
            try:
                self.textures["death_animation"].draw_scaled(
                    self.width / 2 + self.camera.position.x,
                    self.height / 2 + self.camera.position.y,
                    DEATH_ANIMATION_SCALE
                    * math.sin(
                        (math.pi / 4)
                        * (DEATH_ANIMATION_TIME - (self.global_time - self.dead))
                    ),
                )
            except:
                pass
