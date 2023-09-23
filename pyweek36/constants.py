from enum import IntEnum
from pathlib import Path

from arcade import load_texture

SCREEN_TITLE = "PyMunk Platformer"

# How big are our image tiles?
SPRITE_IMAGE_SIZE = 64

SPRITE_SCALING_PLAYER = 1
SPRITE_SCALING_TILES = 1

# Scaled sprite size for tiles
SPRITE_SIZE = int(SPRITE_IMAGE_SIZE * SPRITE_SCALING_TILES)

SCREEN_GRID_WIDTH = 25
SCREEN_GRID_HEIGHT = 15

SCREEN_WIDTH = SPRITE_SIZE * SCREEN_GRID_WIDTH
SCREEN_HEIGHT = SPRITE_SIZE * SCREEN_GRID_HEIGHT

# Physics
GRAVITY = 2500
DEFAULT_DAMPING = 1.0
WALL_FRICTION = 0.0


# Controls
class InputType(IntEnum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


INPUT_BUFFER_DURATION = 0.15
COYOTE_DURATION = 0.15

# Player
PLAYER_MASS = 20
PLAYER_FRICTION = 0
PLAYER_DAMPING = 0.95

PLAYER_HORIZONTAL_SPEED = 400
PLAYER_ACCEL = 200
PLAYER_DECEL = 250
PLAYER_AIR_ACCEL_FACTOR = 0.4
PLAYER_JUMP_IMPULSE = 17000

# Player animation
DEAD_ZONE = 0.1
RIGHT_FACING = 0
LEFT_FACING = 1
DISTANCE_TO_CHANGE_TEXTURE = 20

# Bullet
BULLET_MOVE_FORCE = 1500
BULLET_MASS = 0.1
BULLET_GRAVITY = 0
BULLET_KILL_TIME = 1

# How fast the dark matter spreads in seconds, give or take a margin percentage
DARKMATTER_DECAY_RATE = 1.0
DARKMATTER_DECAY_RATE_MARGIN = 0.2

# Assets
ASSETS_DIR = Path(__file__).parent.parent / "assets"
DARKMATTER_TEXTURE_PATH = ASSETS_DIR / "sprites/map/dark_matter.png"
PLAYER_IDLE_ANIM_PATH = ASSETS_DIR / "player/idle"
PLAYER_JUMP_ANIM_PATH = ASSETS_DIR / "player/jump"
PLAYER_WALK_ANIM_PATH = ASSETS_DIR / "player/walk"

# Load texture now so it isn't loaded from disk every frame
DARKMATTER_TEXTURE = load_texture(DARKMATTER_TEXTURE_PATH)
