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

2. Click Browse... and pick your clean US Buu's Fury ROM.

   The window tells you immediately whether the ROM is supported.

3. Leave the seed as Goku, or type your own, or click Random Seed.

4. Click Randomize.

5. Load the generated ROM in your emulator or flashcart.

Two new files appear next to your ROM: the randomized .gba, and a
.manifest.json recording exactly what was changed and what was left alone.


SUPPORTED ROM
-------------

Only this exact image is accepted:

  Size      8,388,608 bytes
  SHA-256   940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E

Anything else is refused. There is no "continue anyway".


GOOD TO KNOW
------------

- Randomized warps may make the game impossible to complete. Full-game
  progression is not guaranteed - that is the nature of a warp randomizer.
- Same ROM + same seed = the same result, on any machine. Default seed: Goku.
- Randomizer policy: reciprocal-door-pairs/3, over 735 door transition records.
- Not every teleport in the game is randomized; unsupported ones are left alone.
  The tool never writes to the ROM you selected.
- Doors are moved in reciprocal pairs, so the door you arrive on is the one that
  takes you back.

No game data is included. You supply your own clean ROM.

Licence: MPL-2.0. Built with Python and Qt; see THIRD-PARTY-NOTICES.txt in the
project repository.
