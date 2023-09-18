# pyweek36
PyWeek 36



# Mechanics

Side-scrolling 2D platform game over a grid system. Each grid cell contains one of three types of blocks:

1. Air; the player can walk/fall through
2. Solid Block; the player collides with and thus can walk over, but not through.
3. Dark Matter Block; usually behaves as Air.

To win, the player has to reach the end of the map, either the top or the extreme right side (without dying).

Each level is composed of a map built with the above 3 block types and a set of the following additional mechanics.

## Additional Mechanics

1. Dark Matter spreads to adjacent Solid Blocks, both opening and closing pathways as the time passes. It can also remove the floor from under the player's feet, and falling to the bottom of the map equals death.
2. The player has a device which allows him to interact with Dark Matter blocks as if they were Solid Blocks, effectively toggling the behavior of all Dark Matter blocks at the map when turned on.
    1. The device overheats after a fixed time being used, making it go into cooldown. The player has to control how much it uses it.
    2. The device flickers periodically, making it so that the player, given a short moment of warning, has to run to a safe Solid Block.
3. The player has a point and shoot device which turns Dark Matter blocks into Solid-like blocks.
    1. Turns blocks into Solid Blocks.
    2. Turns blocks into Solidified Dark Matter, which behaves like Solid Blocks but goes back into being regular Dark Matter after a time.
