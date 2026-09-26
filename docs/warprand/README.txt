Buu's Fury Warp Randomizer
==========================

A small Windows utility that shuffles where the doors in Dragon Ball Z: Buu's
Fury lead.

Version 0.1.0


WHAT IT DOES
------------

It randomizes the destinations of supported Buu's Fury map-door transitions.

You supply your own clean ROM, choose a seed, and the tool writes a NEW
randomized ROM next to it. Your original ROM is never modified.

Doors are moved as **reciprocal pairs**: if a door now takes you somewhere, the
door you arrive on is the one that brings you back. That is how the retail game
behaves, and it is what keeps a randomized door usable rather than a dead end.

The tool also refuses to connect two dead-end maps to each other, because that
would close a two-room loop with no way on.


HOW TO USE
----------

1. Launch the app.
2. Choose your clean US Buu's Fury ROM.
3. Enter a seed, or keep the default: Goku.
4. Click Randomize.
5. Load the generated ROM in your emulator or flashcart.

The app tells you whether the ROM you picked is the supported one as soon as you
select it, so you find out before you press anything.

A "Random Seed" button generates a short, shareable seed such as "Saiyan-4821".

Two files are created next to your ROM:

  Buu's Fury - Warp Randomized - <seed>.gba
      the randomized ROM

  Buu's Fury - Warp Randomized - <seed>.manifest.json
      a record of exactly what was changed, and what was deliberately left
      alone, and why


SUPPORTED ROM
-------------

This version supports exactly one image: the United States release of Buu's
Fury (game code BG3E).

  Size:      8,388,608 bytes
  SHA-256:   940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E

Any other file is refused. There is no "continue anyway" option: randomizing an
image this tool was not verified against would produce a broken ROM.

To check a file on Windows:

  certutil -hashfile "your rom.gba" SHA256


CURRENT RANDOMIZER POLICY
-------------------------

  reciprocal-door-pairs/3

It covers the 735 transition records this tool has been verified against. On the
supported image, for the default seed Goku, it randomizes 496 of them, moves 492
destinations, and leaves 239 records untouched with a recorded reason.


LIMITATIONS
-----------

- Not every teleport mechanism in the engine is randomized. Scripted moves,
  cutscene transitions and other families are outside this tool.
- Unsupported records may remain completely unchanged. In particular, one whole
  class of record stores its arrival as a scene-relative offset rather than a
  position, so its destination cannot be moved safely and it is skipped.
- Full-game progression is NOT guaranteed. Randomized warps may make the game
  impossible to complete.
- The tool never modifies the ROM you selected. It only ever writes a new file.
- There is no logic or reachability checking. A seed that is unwinnable is a
  possible outcome, not a bug.


SEEDS
-----

Same ROM + same tool version + same seed produces the same randomized ROM,
byte for byte, on any machine.

The default launch seed is: Goku

You can use any non-empty text as a seed. Punctuation and spaces are fine; the
seed is recorded exactly as you typed it in the manifest, and only the output
file name is cleaned up so it is a legal file name.

If the algorithm ever changes in a way that changes what a seed produces, the
version and the policy id both change with it, so a seed can always be traced
back to the build that produced it.


TROUBLESHOOTING
---------------

"This version currently supports the verified US Buu's Fury ROM only."

  The file you chose is not the supported image. Check the size and SHA-256
  above. Common causes: a different region, a different revision, a patched or
  already-randomized ROM, or a bad dump.

"The output file is the input ROM."

  Choose a different output name. This tool will not write to your ROM.

"<name> already exists."

  A file with that name is already there. Choose another name, or confirm that
  you want to replace it. The tool never overwrites silently.


REQUIREMENTS
------------

Windows x64. Nothing else: no Python, no install, no terminal.

The application carries no game data of any kind. It does not include a ROM, and
it cannot - you supply your own clean copy.


LICENSE
-------

Mozilla Public License 2.0. See LICENSE.

This application is built with, and ships, other people's software, including
Python and Qt. THIRD-PARTY-NOTICES.txt lists what is bundled and under which
licences. Read the "Known gap" section at the end of that file: the full LGPL
licence texts for Qt are not bundled yet, which matters if this build is ever
distributed publicly.
