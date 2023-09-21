from pathlib import Path

ASSETS_DIR = Path(__file__).parent.parent / "assets"

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

# Player
PLAYER_MASS = 20
PLAYER_FRICTION = 0
PLAYER_DAMPING = 0.9

PLAYER_HORIZONTAL_SPEED = 400
PLAYER_ACCEL = 200
PLAYER_DECEL = 250
PLAYER_AIR_ACCEL_FACTOR = 0.6
PLAYER_JUMP_IMPULSE = 15000

# Player animation
DEAD_ZONE = 0.1
RIGHT_FACING = 0
LEFT_FACING = 1
DISTANCE_TO_CHANGE_TEXTURE = 20

# Bullet
BULLET_MOVE_FORCE = 4500
BULLET_MASS = 0.1
BULLET_GRAVITY = 300
