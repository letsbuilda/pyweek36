from typing import TYPE_CHECKING

import arcade

from .constants import *

if TYPE_CHECKING:
    from .main import GameWindow


def load_texture_pairs(dir_path: str) -> list[list[arcade.Texture]]:
    dir_ = ASSETS_DIR / dir_path
    textures = []
    for file in sorted(dir_.iterdir()):
        textures.append(arcade.load_texture_pair(file))
    return textures


class PlayerSprite(arcade.Sprite):
    """Player Sprite"""

    def __init__(self, game: "GameWindow"):
        """Init"""
        # Let parent initialize
        super().__init__(
            scale=SPRITE_SCALING_PLAYER,
        )

        self.game = game
        self.facing_direction = RIGHT_FACING
        self.cur_texture = 0
        self.x_odometer = 0
        self.y_odometer = 0
        self.last_on_ground = -1

        # Load textures
        main_path = ASSETS_DIR / "sprites" / "player" / "player"
        self.idle_texture_pair = arcade.load_texture_pair(
            f"{main_path}_idle.png", "Detailed"
        )
        self.jump_texture_pair = arcade.load_texture_pair(f"{main_path}_jump.png")
        self.fall_texture_pair = arcade.load_texture_pair(f"{main_path}_fall.png")
        self.walk_textures = [
            arcade.load_texture_pair(f"{main_path}_walk{i}.png") for i in range(8)
        ]
        self.texture = self.idle_texture_pair[0]

        self.hit_box = self.texture.hit_box_points

    def on_update(self, delta_time: float = 1 / 60):
        engine = self.game.physics_engine
        on_ground = engine.is_on_ground(self)
        if on_ground:
            self.last_on_ground = self.game.global_time

        right_pressed = InputType.RIGHT in self.game.pressed_inputs
        left_pressed = InputType.LEFT in self.game.pressed_inputs
        target_vel = (right_pressed - left_pressed) * PLAYER_HORIZONTAL_SPEED
        accel = PLAYER_ACCEL if target_vel else PLAYER_DECEL
        if not on_ground:
            accel *= PLAYER_AIR_ACCEL_FACTOR
        vel_diff = target_vel - self.velocity[0]
        engine.apply_force(self, (vel_diff * accel, 0))

        if (
            self.game.is_buffered(InputType.UP)
            and self.last_on_ground + COYOTE_DURATION > self.game.global_time
        ):
            self.game.consume_buffer(InputType.UP)
            impulse_amount = PLAYER_JUMP_IMPULSE
            if not on_ground:
                impulse_amount -= self.velocity[1] * PLAYER_MASS
            engine.apply_impulse(self, (0, impulse_amount))
            self.last_on_ground = -1

    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        """Handle being moved by the pymunk engine"""

        self.x_odometer += dx
        self.y_odometer += dy
        self.velocity = [dx * 60, dy * 60]

        # Figure out if we need to face left or right
        if dx < -DEAD_ZONE and self.facing_direction == RIGHT_FACING:
            self.facing_direction = LEFT_FACING
        elif dx > DEAD_ZONE and self.facing_direction == LEFT_FACING:
            self.facing_direction = RIGHT_FACING

        # Jumping animation
        if not physics_engine.is_on_ground(self):
            if dy > DEAD_ZONE:
                self.texture = self.jump_texture_pair[self.facing_direction]
                return
            elif dy < -DEAD_ZONE:
                self.texture = self.fall_texture_pair[self.facing_direction]
                return

        # Idle animation
        if abs(dx) <= DEAD_ZONE:
            self.texture = self.idle_texture_pair[self.facing_direction]
            return

        # Have we moved far enough to change the texture?
        if abs(self.x_odometer) > DISTANCE_TO_CHANGE_TEXTURE:
            self.x_odometer = 0
            self.cur_texture = (self.cur_texture + 1) % 8
            self.texture = self.walk_textures[self.cur_texture][self.facing_direction]


class BulletSprite(arcade.SpriteSolidColor):
    """Bullet Sprite"""

    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        """Handle when the sprite is moved by the physics engine."""
        # If the bullet falls below the screen, remove it
        if self.center_y < -100:
            self.remove_from_sprite_lists()
