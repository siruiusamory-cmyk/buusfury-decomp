# Playtest guide: consolidated friend ROM

Everything a human needs to start playing and to report what breaks. This guide describes the
frozen image only. It does not claim the campaign was tested; nobody has walked a chapter yet.

## 1. The ROM

| field | value |
| --- | --- |
| path | `build/fv3boost001/out/v3-playtest-boost.gba` |
| SHA-256 | `acd98c2ac90907ae0d83e78019c19b9b26001a49bc28e8bd436da7be9b4bb48c` |
| size | 10,140,972 bytes |
| canonical retail ROM | unchanged, `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e` |

Verify before playing:

```powershell
(Get-FileHash build\fv3boost001\out\v3-playtest-boost.gba -Algorithm SHA256).Hash.ToLower()
```

It must print the hash above. If it does not, the build was modified and the playtest is invalid.

**Getting the file.** The ROM itself is never committed, so it is handed over out of band. To
rebuild it instead, run `build/fv3boost001/build.ps1` from the repository root. That script reads
an unpacked foundation image from the ignored `build/fv3boost001/staging/` directory, so it needs
that directory present; it refuses rather than guessing if it is missing. Either route must end at
the hash above.

## 2. How to launch

Load that file in any GBA emulator. mGBA is what the evidence was produced on; any current
build of it works.

Nothing else is required. There is no patcher to run and no per-session setup.

**If the game refuses to run, check the save type.** This title needs EEPROM (or Flash 128K).
A misconfigured emulator shows `The game will not run on this hardware`, and it appears early,
at the Grand Kai, so a save started before the fix has to be restarted. The smoke test on this
image wrote an 8,192-byte save, which is consistent with EEPROM. Sources:
[Almar's Guides][almar], [Gamer's Temple walkthrough][gamerstemple].

[almar]: https://almarsguides.com/retro/walkthroughs/GBA/games/DragonBallZBuusFury/
[gamerstemple]: https://gamerstemple.com/guides/game-boy-advance/1580/1/dragon-ball-z-buus-fury-walkthrough

## 3. Start from a fresh save

**Start a New Game from an empty save.** The image ships to a save slot with no play data; do not
load an old save from this or any other build.

Why it matters: this build is a static edit of the character base-stat table. A save written by a
different image can carry old stat values, and a mid-campaign load that shows retail stats is a
save-state artifact rather than a build defect. To start genuinely clean, delete or move the
`.sav` beside the ROM, then begin a new game.

## 4. What is different from retail

| change | what to expect |
| --- | --- |
| five party slots at level 200 | the first five party records start at the level ceiling |
| STR, POW, END and SPD at 255 | maximum for those four attributes |
| HP and EP left at retail values | deliberately not raised: `0xFFFF` reads as negative and broke energy attacks, so HP/EP were excluded |
| character names, menu text, credits | the completed text pass, which renames identities: Goku reads as **Yamcha**, and Chi-Chi as **Tulma**. Krillin, Gohan, Goten, Trunks, Vegeta and Tien keep their names |
| Tulma | replaced actor sprite, portrait slot 17, and two rewritten dialogue records |

**Read the roster before reporting a stat defect.** The boosted slots wear the build's renamed
identities, so a level 200 character may be one you did not expect under that name. If a stat looks
wrong, note which character you selected and what the status screen showed.

Everything else is retail: items, shops, enemies, progression and controls. Nothing was remapped
or removed, and no item is added to your inventory at the start.

## 5. Known limitations

1. **No chapter was walked.** Progression past the smoke-test window is unverified.
2. **Tulma's encounter is unconfirmed.** The graphics and dialogue are in the image, but no
   scripted in-game encounter has been observed.
3. **The level cap of 200 is a code constant, not a table.** Nothing was done about raising it.
4. **Late-game stability is not claimed.** Two hazard records remain open as latent:
   zero composition-buffer slack (297 of 297 slots) and a latent tail-write hazard,
   both in `docs/research/FRIEND_V3_STABILITY_PASS.md`.
5. **This is a 10,140,972-byte image, not the 8 MiB canonical ROM.** Any digest check must name
   this file.
6. **A crash is possible in principle.** If the game stops advancing, note the screen, the
   chapter and what you were doing, and follow section 8.

## 6. Chapter-by-chapter checklist

These are the walkthrough's chapter names for this game, in order. The source has twelve
walkthrough sections, and the twelfth is the short closing chapter. This guide previously listed
invented saga names. Source:
[Gamer's Temple walkthrough][chapters].

Tick what you actually played. Leave the rest blank; a blank is honest and useful.

| # | chapter | started | finished | notes |
| --- | --- | --- | --- | --- |
| 1 | The Other World | [ ] | [ ] | |
| 2 | Great Saiyaman | [ ] | [ ] | |
| 3 | World Tournament | [ ] | [ ] | |
| 4 | Babidi | [ ] | [ ] | |
| 5 | Majin Vegeta | [ ] | [ ] | |
| 6 | Dragon Ball | [ ] | [ ] | |
| 7 | Majin Buu | [ ] | [ ] | |
| 8 | Janemba | [ ] | [ ] | |
| 9 | Super Buu | [ ] | [ ] | |
| 10 | Fusion | [ ] | [ ] | |
| 11 | Kid Buu | [ ] | [ ] | |
| 12 | A New Beginning | [ ] | [ ] | |

[chapters]: https://gamerstemple.com/guides/game-boy-advance/1580/1/dragon-ball-z-buus-fury-walkthrough

Also worth watching for, because they are what this build touches:

| # | check | result |
| --- | --- | --- |
| a | stat screen shows level 200 and 255 in STR/POW/END/SPD | [ ] |
| b | HP and EP read as normal positive values, not odd or huge | [ ] |
| c | an energy-consuming ability works | [ ] |
| d | movement and basic attacks work | [ ] |
| e | a Tulma appearance matches the intended art and dialogue | [ ] |
| f | save, quit, reload preserves progress and inventory | [ ] |
| g | the Grand Kai does not show `The game will not run on this hardware` | [ ] |

## 7. Reporting a bug

Include all of the following, or the report cannot be acted on:

1. The ROM SHA-256 as printed in section 1.
2. Whether the save was genuinely fresh.
3. The chapter and, if visible, the room or fight.
4. What you did immediately before it happened.
5. What the screen showed.
6. Whether the game kept running, froze, or closed.
7. The contents of the `.sav` file beside the ROM, if the game wrote one, and its exact size.
8. A screenshot if the defect is visual.

A reproducible defect beats a description. If it happens twice from a fresh save, say so: that is
the difference between a build defect and a one-off.

## 8. What this build is for

Getting the campaign played. If normal progression works, the next step is a full human
playthrough, and that playthrough is the evidence that closes the remaining progression claims.
