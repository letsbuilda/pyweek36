from pathlib import Path

import arcade

ASSETS_DIR = Path(__file__).parent.parent / "assets"

SCREEN_TITLE = "PyMunk Platformer"

# How big are our image tiles?
SPRITE_IMAGE_SIZE = 64

# Scale sprites up or down
SPRITE_SCALING_PLAYER = 1
SPRITE_SCALING_TILES = 1

# Scaled sprite size for tiles
SPRITE_SIZE = int(SPRITE_IMAGE_SIZE * SPRITE_SCALING_PLAYER)

# Size of grid to show on screen, in number of tiles
SCREEN_GRID_WIDTH = 25
SCREEN_GRID_HEIGHT = 15

# Size of screen to show, in pixels
SCREEN_WIDTH = SPRITE_SIZE * SCREEN_GRID_WIDTH
SCREEN_HEIGHT = SPRITE_SIZE * SCREEN_GRID_HEIGHT

# --- Physics forces. Higher number, faster accelerating.

# Gravity
GRAVITY = 1500

# Damping - Amount of speed lost per second
DEFAULT_DAMPING = 1.0
PLAYER_DAMPING = 2

# Friction between objects
PLAYER_FRICTION = 2
WALL_FRICTION = 0.7
DYNAMIC_ITEM_FRICTION = 0.6

# Mass (defaults to 1)
PLAYER_MASS = 2.0

# Keep player from going too fast
PLAYER_MAX_HORIZONTAL_SPEED = 350
PLAYER_MAX_VERTICAL_SPEED = 700

# Force applied while on the ground
PLAYER_MOVE_FORCE_ON_GROUND = 6000

# Force applied when moving left/right in the air
PLAYER_MOVE_FORCE_IN_AIR = 2000

# Strength of a jump
PLAYER_JUMP_IMPULSE = 1200

# Close enough to not-moving to have the animation go to idle.
DEAD_ZONE = 0.1

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

# How many pixels to move before we change the texture in the walking animation
DISTANCE_TO_CHANGE_TEXTURE = 20

# How much force to put on the bullet
BULLET_MOVE_FORCE = 4500

# Mass of the bullet
BULLET_MASS = 0.1

# Make bullet less affected by gravity
BULLET_GRAVITY = 300

# How fast the dark matter spreads in seconds, give or take a margin percentage
DARKMATTER_DECAY_RATE = 1.0
DARKMATTER_DECAY_RATE_MARGIN = 0.2
DARKMATTER_TEXTURE = arcade.load_texture(
    ASSETS_DIR / "sprites" / "map" / "dark_matter.png"
)
