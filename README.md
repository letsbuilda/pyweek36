# pyweek36
PyWeek 36

# Mechanics

Side-scrolling 2D platform game over a double grid system, with a foreground and a background (like Terraria).

Each foreground grid cell contains one of three types of blocks:

1. Air; the player can walk/fall through.
2. Solid Block; the player collides with and thus can walk over, but not through.
3. Dark Matter Block; behaves as Air.

Similarly, the background will have the same above three block types, though none of them can be interacted with directly.

Dark Matter periodically spreads to adjacent Solid Blocks (through both foreground and background grids). This both opens and closes pathways as the time passes. It can also remove the floor from under the player's feet, and falling to the bottom of the map equals death. To win, the player has to reach the end of the map (either the top or the extreme right side, to be decided) without dying.

## Additional Mechanics

These mechanics are to be explored, with the following priority. Some might fall off or change slightly as we progress.

1. The player has a point and shoot device which turns Dark Matter blocks in a small blast radius into Solid-like blocks.
    1. Turns Dark Matter blocks into regular Solid Blocks.
    2. Turns Dark Matter blocks into Solidified Dark Matter, a new block type which behaves like Solid Blocks but:
        1. Are immune to spread for a time, then go back to Solid Blocks which are once again succeptable to spread.
        2. Goes back into being regular Dark Matter after a time, higher than the frequency of spread. Effectively works as ii.a initially, but then all of the blocks affected by a single shot would go back to Dark Matter at the same time, rather than allowing the spread to gradually take them over again.
    3. A fourth block type, Dark Matter Source, is added as a Dark Matter block immune to conversion.
        * Can facilitate the design of levels so that the player is not ever able to erradicate the Dark Matter (and thus completely stop spread, along with any loss condition).
    4. Can also turn Solid Blocks into Dark Matter (might [be incoherent](https://github.com/letsbuilda/pyweek36/pull/12/files#r1328208664), low priority).

# Roadmap

High-level overview of steps to be taken, in order of four phases. As the roadmap progresses, the potential for paralel contributions is expected to increase.

### Phase 1
- Project structuring, boilerplates and any initial setups.
- From [Basic mechanics](#mechanics).
    - Block types and Player entities.
    - Rendering (any sprites are acceptable, just so that we can see what we're working with).
    - Physics, Character Movement and Colision.
- Conceptual Art & Writing discussions.

### Phase 2
- From [Basic mechanics](#mechanics):
    - Camera Movement.
    - Dark Matter spread.
- [Additional Mechanics](#additional-mechanics).
- Paradigm or tool for level creation.
- Art & Writing:
    - Sprites and Tileset.
    - Home and Level Selection screen mockups (and/or any other required screens).

### Phase 3
- Handcrafting of levels (tilemaps).
- Screens implementation:
    - Home screen.
    - Level Selection screen.
    - Any others as per Phase 2's mockups.
- Art & Writing:
    - Music/Sounds.
    - Backstory & Dialog writeup.
    - Sprites enrichment.

### Phase 4
- Creating binaries, installation and compatibility checks.
- Bug hunting.
- Last improvements.
- Anything else that comes up during the other phases.
