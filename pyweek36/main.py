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
        self.wall_list: Optional[arcade.SpriteList] = None
        self.bullet_list: Optional[arcade.SpriteList] = None
        self.item_list: Optional[arcade.SpriteList] = None
        self.moving_sprites_list: Optional[arcade.SpriteList] = None
        self.ladder_list: Optional[arcade.SpriteList] = None

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

        map_name = ":resources:/tiled_maps/pymunk_test_map.json"

        tile_map = arcade.load_tilemap(map_name, SPRITE_SCALING_TILES)

        # Pull the sprite layers out of the tile map
        self.wall_list = tile_map.sprite_lists["Platforms"]
        self.item_list = tile_map.sprite_lists["Dynamic Items"]
        self.ladder_list = tile_map.sprite_lists["Ladders"]
        self.moving_sprites_list = tile_map.sprite_lists["Moving Platforms"]

        self.player_sprite = PlayerSprite(
            self.ladder_list, hit_box_algorithm="Detailed"
        )

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

        def item_hit_handler(bullet_sprite, item_sprite, _arbiter, _space, _data):
            """Called for bullet/wall collision"""
            bullet_sprite.remove_from_sprite_lists()
            item_sprite.remove_from_sprite_lists()

        self.physics_engine.add_collision_handler(
            "bullet", "item", post_handler=item_hit_handler
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
            self.wall_list,
            friction=WALL_FRICTION,
            collision_type="wall",
            body_type=arcade.PymunkPhysicsEngine.STATIC,
        )

        # Create the items
        self.physics_engine.add_sprite_list(
            self.item_list, friction=DYNAMIC_ITEM_FRICTION, collision_type="item"
        )

        # Add kinematic sprites
        self.physics_engine.add_sprite_list(
            self.moving_sprites_list, body_type=arcade.PymunkPhysicsEngine.KINEMATIC
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
            if (
                self.physics_engine.is_on_ground(self.player_sprite)
                and not self.player_sprite.is_on_ladder
            ):
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
        # Update player forces based on keys pressed
        if self.left_pressed and not self.right_pressed:
            # Create a force to the left. Apply it.
            if is_on_ground or self.player_sprite.is_on_ladder:
                force = (-PLAYER_MOVE_FORCE_ON_GROUND, 0)
            else:
                force = (-PLAYER_MOVE_FORCE_IN_AIR, 0)
            self.physics_engine.apply_force(self.player_sprite, force)
            # Set friction to zero for the player while moving
            self.physics_engine.set_friction(self.player_sprite, 0)
        elif self.right_pressed and not self.left_pressed:
            # Create a force to the right. Apply it.
            if is_on_ground or self.player_sprite.is_on_ladder:
                force = (PLAYER_MOVE_FORCE_ON_GROUND, 0)
            else:
                force = (PLAYER_MOVE_FORCE_IN_AIR, 0)
            self.physics_engine.apply_force(self.player_sprite, force)
            # Set friction to zero for the player while moving
            self.physics_engine.set_friction(self.player_sprite, 0)
        elif self.up_pressed and not self.down_pressed:
            # Create a force to the right. Apply it.
            if self.player_sprite.is_on_ladder:
                force = (0, PLAYER_MOVE_FORCE_ON_GROUND)
                self.physics_engine.apply_force(self.player_sprite, force)
                # Set friction to zero for the player while moving
                self.physics_engine.set_friction(self.player_sprite, 0)
        elif self.down_pressed and not self.up_pressed:
            # Create a force to the right. Apply it.
            if self.player_sprite.is_on_ladder:
                force = (0, -PLAYER_MOVE_FORCE_ON_GROUND)
                self.physics_engine.apply_force(self.player_sprite, force)
                # Set friction to zero for the player while moving
                self.physics_engine.set_friction(self.player_sprite, 0)

        else:
            # Player's feet are not moving. Therefore up the friction so we stop.
            self.physics_engine.set_friction(self.player_sprite, 1.0)

        # Move items in the physics engine
        self.physics_engine.step()

        # For each moving sprite, see if we've reached a boundary and need to
        # reverse course.
        for moving_sprite in self.moving_sprites_list:
            if (
                moving_sprite.boundary_right
                and moving_sprite.change_x > 0
                and moving_sprite.right > moving_sprite.boundary_right
            ):
                moving_sprite.change_x *= -1
            elif (
                moving_sprite.boundary_left
                and moving_sprite.change_x < 0
                and moving_sprite.left > moving_sprite.boundary_left
            ):
                moving_sprite.change_x *= -1
            if (
                moving_sprite.boundary_top
                and moving_sprite.change_y > 0
                and moving_sprite.top > moving_sprite.boundary_top
            ):
                moving_sprite.change_y *= -1
            elif (
                moving_sprite.boundary_bottom
                and moving_sprite.change_y < 0
                and moving_sprite.bottom < moving_sprite.boundary_bottom
            ):
                moving_sprite.change_y *= -1

            # Figure out and set our moving platform velocity.
            # Pymunk uses velocity is in pixels per second. If we instead have
            # pixels per frame, we need to convert.
            velocity = (
                moving_sprite.change_x * 1 / delta_time,
                moving_sprite.change_y * 1 / delta_time,
            )
            self.physics_engine.set_velocity(moving_sprite, velocity)

    def on_draw(self):
        """Draw everything"""
        self.clear()
        self.wall_list.draw()
        self.ladder_list.draw()
        self.moving_sprites_list.draw()
        self.bullet_list.draw()
        self.item_list.draw()
        self.player_list.draw()


def main():
    """Main function"""
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()
