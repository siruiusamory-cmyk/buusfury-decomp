Buu's Fury Warp Randomizer v0.1.0
=================================

Shuffles where the doors in Dragon Ball Z: Buu's Fury lead, from a seed you
choose. Your own ROM is never modified - the tool reads it and writes a new file
beside it.

HOW TO USE
----------

1. Double-click Buu-Fury-Warp-Randomizer.exe.

   Windows may warn about an unknown publisher the first time. Choose
   "More info", then "Run anyway".

   The first launch takes a few seconds to show the window - the executable
   unpacks itself before it can start. Later launches are the same; this is
   normal for a single-file build.

2. In the Original ROM row, click Browse... and pick your clean US Buu's Fury
   ROM.

   The window tells you immediately whether the ROM is supported.

3. Leave the seed as Goku, or type your own, or click Random Seed.

4. Click Randomize. The Randomized ROM row names the file to create; it is filled
   in beside your ROM, and you can browse somewhere else if you prefer.

5. Load the generated ROM in your emulator or flashcart.

Two new files appear next to your ROM: the randomized .gba, and a
.manifest.json recording exactly what was changed and what was left alone.

SUPPORTED ROM
-------------

Only this exact image is accepted:

  Size      8,388,608 bytes
  SHA-256   940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E

Anything else is refused. There is no "continue anyway".

SEEDS
-----

- Same ROM + same seed = the same randomized ROM, on any machine. Default seed:
  Goku.
- The seed is used exactly as you type it. "Goku" and "goku" are different seeds.
- The manifest records your seed, so a run can be reproduced from the manifest
  alone.

GOOD TO KNOW
------------

- Randomized warps may make the game impossible to complete. Full-game
  progression is not guaranteed - that is the nature of a warp randomizer.
- 735 door transitions are considered. Doors are moved in reciprocal pairs, so
  the door you arrive on is the one that takes you back. Not every teleport in
  the game is randomized; the ones that cannot be read safely are left alone.
- A confirmed overwrite replaces the previous output and its manifest together,
  and it deletes them before writing the new ROM. If the write itself then fails
  - a full disk, a permission problem - the previous files are already gone. That
  is the cost of refusing to write over a file in place, and it is stated rather
  than hidden.
- The tool never writes to the ROM you selected. The output must be a separate
  file, and an output that is a copy of your clean ROM is refused even if you
  confirm the overwrite.
- Every run records the tool version and the warp algorithm version beside the
  seed, because a seed only identifies a result alongside the algorithm that
  consumed it.

No game data is included. You supply your own clean ROM.

Licence: MPL-2.0. Project home and third-party notices:
https://webfoot-sdk.siruiusamory.workers.dev/
