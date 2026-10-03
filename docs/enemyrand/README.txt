Enemy Randomizer v0.1.0
=======================

Randomizes the ordinary enemies in Dragon Ball Z: Buu's Fury, from a seed you
choose. Your own ROM is never modified - the tool reads it and writes a new file
beside it.

WHAT IT DOES
------------

- Shuffles enemy placements. Eligible ordinary enemies are moved among
  placements the map already had, within the same map. No new spawn is created
  and no coordinate is invented.
- Randomizes enemy stats. Supported stats - HP, experience, level, strength,
  power and endurance - are scaled around each enemy's own original values, so a
  weak enemy stays weak and an endgame enemy stays endgame.

Both are on by default. That combination is the STREAM SAFE preset, and the
button in the window restores it.

WHAT IT DOES NOT DO
-------------------

- It does NOT change enemy species or types. An enemy is never replaced by a
  different kind of enemy, and enemy identity/type swapping is not supported in
  this version. This is not a hidden limitation: every manifest the tool writes
  records it.
- It does not randomize bosses, NPCs, quest-critical actors or scripted actors.
  Anything the tool cannot positively classify as an ordinary enemy is left
  alone, and there is deliberately no "randomize everything" switch.
- It does not randomize items, map warps or map layouts. The Map Warp Randomizer
  is a separate tool.

HOW TO USE
----------

1. Double-click Enemy-Randomizer.exe.

   Windows may warn about an unknown publisher the first time. Choose
   "More info", then "Run anyway".

   The first launch takes a few seconds to show the window - the executable
   unpacks itself before it can start. Later launches are the same; this is
   normal for a single-file build.

2. Click Browse... and pick your clean US Buu's Fury ROM.

   The window tells you immediately whether the ROM is supported.

3. Leave the seed as StreamBlind-0001, or type your own, or click Random Seed.

4. Tick or untick "Shuffle enemy placements" and "Randomize enemy stats".

5. Click Randomize.

6. Load the generated ROM in your emulator or flashcart.

Three files appear next to your ROM: the randomized .gba, a .manifest.json
recording exactly what was changed and what was left alone, and (unless you
untick it) a .spoiler.json. The spoiler is never opened for you, so a blind run
stays blind.

SUPPORTED ROM
-------------

Only this exact image is accepted:

  Size      8,388,608 bytes
  SHA-256   940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E

Anything else is refused. There is no "continue anyway".

SEEDS
-----

- Same ROM + same seed + same options = the same ROM, on any machine.
- The seed is used exactly as you type it. "StreamBlind-0001" and
  "streamblind-0001" are different seeds.
- Each module derives its own seed from yours, so turning one off never changes
  what the other produces.
- The manifest records your seed and every derived module seed, so a run can be
  reproduced from the manifest alone.

GOOD TO KNOW
------------

- Randomized placements and stats change the game's difficulty. Progression
  stays bounded - nothing is drawn from a global range - but full-game balance
  is not guaranteed.
- A confirmed overwrite deletes the previous output only once the new one is
  certain to be produced.
- The tool never writes to the ROM you selected. The output must be a separate
  file, and an output that is a copy of your clean ROM is refused even if you
  confirm the overwrite.
- Every run records the tool version and each module's algorithm version beside
  the seed, because a seed only identifies a result alongside the algorithms that
  consumed it.

No game data is included. You supply your own clean ROM.

Licence: MPL-2.0. Project home and third-party notices:
https://webfoot-sdk.siruiusamory.workers.dev/
