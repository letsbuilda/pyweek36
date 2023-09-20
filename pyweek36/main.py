"""
Example of Pymunk Physics Engine Platformer
"""

import math
from typing import Optional

import arcade

from .constants import *
from .sprites import BulletSprite, PlayerSprite


class GameWindow(arcade.Window):
    """Main Window"""

    def __init__(self, width, height, title):
        """Create the variables"""

        super().__init__(width, height, title)

        self.player_sprite: Optional[PlayerSprite] = None

        self.player_list: Optional[arcade.SpriteList] = None
        self.block_list: Optional[arcade.SpriteList] = None
        self.bullet_list: Optional[arcade.SpriteList] = None

        # Track the current state of what key is pressed
        self.left_pressed: bool = False
        self.right_pressed: bool = False
        self.up_pressed: bool = False
        self.down_pressed: bool = False

        self.physics_engine: Optional[arcade.PymunkPhysicsEngine] = None

        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self):
        """Set up everything with the game"""

        self.player_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()

        map_path = ASSETS_DIR / "tiled" / "map.tmx"
        map_name = str(map_path.resolve())

        tile_map = arcade.tilemap.TileMap(
            map_name, SPRITE_SCALING_TILES, hit_box_algorithm="Detailed"
        )

        # Pull the sprite layers out of the tile map
        self.block_list = tile_map.sprite_lists["Map"]

        self.player_sprite = PlayerSprite(hit_box_algorithm="Detailed")

        # Set player location
        grid_x = 1
        grid_y = 1
        self.player_sprite.center_x = SPRITE_SIZE * grid_x + SPRITE_SIZE / 2
        self.player_sprite.center_y = SPRITE_SIZE * grid_y + SPRITE_SIZE / 2
        self.player_list.append(self.player_sprite)

        damping = DEFAULT_DAMPING

        gravity = (0, -GRAVITY)

        self.physics_engine = arcade.PymunkPhysicsEngine(
            damping=damping, gravity=gravity
        )

        def wall_hit_handler(bullet_sprite, _wall_sprite, _arbiter, _space, _data):
            """Called for bullet/wall collision"""
            bullet_sprite.remove_from_sprite_lists()

        self.physics_engine.add_collision_handler(
            "bullet", "wall", post_handler=wall_hit_handler
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

        self.physics_engine.add_sprite_list(
            self.block_list,
            friction=WALL_FRICTION,
            collision_type="wall",
            body_type=arcade.PymunkPhysicsEngine.STATIC,
        )

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
        start_x = self.player_sprite.center_x
        start_y = self.player_sprite.center_y
        bullet.position = self.player_sprite.position

        # Get from the mouse the destination location for the bullet
        # IMPORTANT! If you have a scrolling screen, you will also need
        # to add in self.view_bottom and self.view_left.
        dest_x = x
        dest_y = y

        # Do math to calculate how to get the bullet to the destination.
        # Calculation the angle in radians between the start points
        # and end points. This is the angle the bullet will travel.
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)

        # What is the 1/2 size of this sprite, so we can figure out how far
        # away to spawn the bullet
        size = max(self.player_sprite.width, self.player_sprite.height) / 2

        # Use angle to to spawn bullet away from player in proper direction
        bullet.center_x += size * math.cos(angle)
        bullet.center_y += size * math.sin(angle)

        # Set angle of bullet
        bullet.angle = math.degrees(angle)

        bullet_gravity = (0, -BULLET_GRAVITY)

        # Add the sprite. This needs to be done AFTER setting the fields above.
        self.physics_engine.add_sprite(
            bullet,
            mass=BULLET_MASS,
            damping=1.0,
            friction=0.6,
            collision_type="bullet",
            gravity=bullet_gravity,
            elasticity=0.9,
        )

        # Add force to bullet
        force = (BULLET_MOVE_FORCE, 0)
        self.physics_engine.apply_force(bullet, force)

    def on_update(self, delta_time):
        """Movement and game logic"""

        is_on_ground = self.physics_engine.is_on_ground(self.player_sprite)
        # Update player
        self.physics_engine.set_friction(self.player_sprite, PLAYER_FRICTION)
        x_movement = self.right_pressed - self.left_pressed
        if x_movement:
            if is_on_ground:
                x_force = PLAYER_MOVE_FORCE_ON_GROUND
            else:
                x_force = PLAYER_MOVE_FORCE_IN_AIR
            x_force *= x_movement
            self.physics_engine.apply_force(self.player_sprite, (x_force, 0))
            self.physics_engine.set_friction(self.player_sprite, 0)

        # Move items in the physics engine
        self.physics_engine.step()

    def on_draw(self):
        """Draw everything"""
        self.clear()
        self.block_list.draw()
        self.bullet_list.draw()
        self.player_list.draw()


def main():
    """Main function"""
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()
