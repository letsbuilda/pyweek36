import arcade

from .constants import *


class PlayerSprite(arcade.Sprite):
    """Player Sprite"""

    def __init__(self):
        """Init"""
        # Let parent initialize
        super().__init__(
            scale=SPRITE_SCALING_PLAYER,
        )

        self.facing_direction = RIGHT_FACING
        self.cur_texture = 0
        self.x_odometer = 0
        self.y_odometer = 0

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

    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        """Handle being moved by the pymunk engine"""

        self.x_odometer += dx
        self.y_odometer += dy

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
