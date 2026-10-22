# PLAY_CHECKLIST: the sitting on the read-logging runtime

Measured 2026-10-19 from `docs/research/RUNTIME_TARGETS.csv` (regenerated from
`docs/research/RESIDUAL_LEDGER.csv`), `docs/research/RECOMP_CITED.csv` and the ledger's six
end-of-ROM rows. One sitting, one range file, 155 rows / 166,285 B.

The instrument is MEASURED; the scene choices are INFERRED. A wrong step costs a restart, not the
data: every run watches the same file.

## Today's set (MEASURED)

| group | rows | bytes | question |
|---|---|---|---|
| `set_a` (map block, root `+0x10` data) | 36 | 50,760 | is the map block read while a map is live, and at what width |
| `set_b` (map block, child list) | 62 | 31,808 | is this child-list payload read, and at what offset from its start |
| `runtime_pending` | 51 | 980 | which instruction reads this row, and at what width |
| `endrom_stride` (R20/R23/R24/R28/R29) | 6 | 82,737 | what is the highest record index the game touches |
| **total** | **155** | **166,285** | |

### How this differs from the earlier numbers

- The roadmap's `runtime_pending` "89 rows / 30,280 B" measured 84 / 28,800 on master. The sprite
  cell-grid change emitted ten graphics rows; five rows that still carried `runtime-pending` sat
  inside those spans and left the class: `0x46D2EC` 104 B,
  `0x51C618` 640 B, `0x52781C` 608 B, `0x597DB0` 64 B, `0x5BFC44` 64 B, 1,480 B in all. No new
  `runtime-pending` row appeared.
- The earlier sheet's 152 rows / 84,324 B become 149 / 83,548. Two of those five rows (`0x51C618`
  and a 64-byte row) were already cited in `RECOMP_CITED.csv` and were not part of the 152; the
  three uncited rows are the 776 B difference.
- The six BF-401 rows with a reader-proven stride and no static count (K-252,
  `docs/research/ENDROM_BOUND_CENSUS.md`) add 6 rows / 82,737 B. A read log answers them with the
  highest record index the game touches.
- 42 target starts are already cited, so 149 of the regenerated table's 189 rows are watched here.

## The instrument

A read-logging GBA runtime recorded every read inside the range file, one CSV line per read
(`pc,lr,addr,width,frame,value`). The image it ran was the retail ROM's private copy, sha256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`, named explicitly on every run
so a stale config could not redirect it. The logger was armed by one environment variable for the
output CSV and one for the range file (hex FILE offsets as `start end`), and the front-end was
skipped so the game window opened first.

- Range file: `ranges.txt`, 157 lines (149 target rows, 6 end-of-ROM rows, 2 witness rows), 2,194
  bytes, 166,335 B of watched span. The six end-of-ROM spans come from the ledger (`leads-six.txt`).
- Witness rows: `6098 60c6` is read on the title screen (the instrument control, 438 lines per
  900 frames); `71734 71738` is read only once gameplay runs (pc `0x0800AFAA`; absent from the
  recorded attract log, one hit in each of the four recorded gameplay logs).

### Proof with no input (RUNTIME-PROVEN, 2026-10-19)

One windowed run, `--no-launcher --window --frames 900 --rom`, BelowNormal, affinity 0x3F, closed
by its own frame limit: exit 0, `ppu_frames=900`, 438 hit lines, log 21,055 B, **0 hits in the 149
target rows and the 6 end-of-ROM rows**, 438 hits in `6098 60c6`, 0 in `71734 71738`, ROM sha256
unchanged. Rate: 23.4 B per frame = 0.084 MB/min at 60 fps.

## Keys (defaults; a `keybinds.ini [player1]` beside the runtime overrides them)

The runtime's defaults map each key name to KEYINPUT bits as the table below shows.

| GBA | key |
|---|---|
| A (confirm) | `X` |
| B (cancel) | `Z` |
| Start | `Enter` |
| Select | `Right Shift` |
| D-pad | arrow keys |
| L / R | `C` / `V` |

`Alt+Enter` fullscreen, `Shift+P` pause, `F` FPS readout. Do not press `Tab`: it changes frame
pacing.

## Before you start

- The runtime's own DLL directory must be on `PATH`, or the process exits `0xC0000135` and writes
  nothing.
- Free 4 GB of disk: a gameplay run writes about 84 MB/min (30 minutes is about 2.5 GB). Close other
  emulators and games.
- One run block per run; do not reuse a log name between runs.
- Close each run with the window's X. Never kill the process: its 1 MiB log buffer is written at
  exit.
- No save exists, so run 1 starts from New Game; later runs may use Continue.

## The runs, in this order

Each run: arm the logger on the range file with a fresh log name, play until the scene is done, then
close the window with its own X. There is no time limit. A run is usable only if its liveness check
says `True`; `False` means it never reached gameplay and is redone.

**Run 1 - a live map** (`set_a`, `set_b`; 98 rows)

Log `run1-map.csv`. New Game from the title (`Enter`, then `X`); walk the first outdoor map a screen
or two; enter one interior and leave it; cross one screen transition.

**Run 2 - a battle** (`set_a`, `set_b` second chance; end-of-ROM `0x762270` INFERRED)

Same method, log `run2-battle.csv`. Continue if offered, else New Game; walk into an enemy, start a
fight, finish it, then walk one screen. The row's reader indexes an object's `[+0x10]` byte, so any
scene that constructs actors is a candidate.

**Run 3 - the status menu** (`runtime_pending` widths; `set_a` third chance)

Same method, log `run3-menu.csv`. Continue if offered, else New Game; open the status or pause
screen, page through every character's stat page, close it, then walk one screen and open one
shop or inventory list.

**Run 4 - a broad pass** (`endrom_stride` 6 rows INFERRED; `runtime_pending` leftovers)

Same method, log `run4-endrom.csv`. Play one map transition, one battle and one menu in a single
session, then stop. What each reader suggests, and how far that goes:

| row | reader | scene it suggests (INFERRED) |
|---|---|---|
| `0x762270` | `0x0801B2B4`, index `[obj+0x10]` | any actor-bearing scene: battle or overworld |
| `0x76E264` | `0x080383D4`, parallel direction pairs at `0x07268C` | movement or animation: overworld walking, battle |
| `0x72D6B8` | `0x080246B4`, beside a VRAM block copy from `0x72C3B8` | a map or scene graphics load |
| `0x7144D8` | `0x0800B55C`, `0x100`-byte blocks into VRAM `0x06010000` | any scene that shows that tileset |
| `0x76174C` | `0x08036FC0`, callers `0x0803A708` and `0x0803CDB2` pass index 2 | those callers' scene; not identified |
| `0x77B2A8` | `0x0803C2F8`, no static caller | unknown; only a broad pass can reach it |

The leftovers are 51 four-byte rows: only their read width is in question, so any scene that loads
the row answers it.

## Liveness check after each run

The log's byte count well above 29 (a header-only log) and a hit on `^0x0800afaa,` mean gameplay
with the logger armed. Read both by streaming the file; never read a multi-GB log into memory.

## After the sitting

`tools/research/recomp_cited.py --hits` over the four logs with `--exclude-cited` and the six-row
leads file reports the sitting; add `--write` only when a ticket records the citations into
`docs/research/RECOMP_CITED.csv`.

The summary's `target rows` column is 155 / 166,285 B: the four groups above plus `recomp_lead`,
which is the six end-of-ROM rows. `rows cited` against `target rows` is the sitting's result.

The six strided rows' highest index comes from the same logs: one streaming pass per log reads each
row's `addr`, takes its offset from `0x08000000`, and prints per stride the hit count and the highest
index. `max index` is the last record the game touched; `hits 0` means no run reached the row.

## Disk, time, failure

- Attract floor, measured (900 frames): 21,055 B of log = 23.4 B/frame. Gameplay rate from
  the runtime read survey's campaign log (6,000 frames, 212 ranges, 139,457,306 B): about 84 MB/min, so a
  30-minute run is about 2.5 GB.
- Time: INFERRED 25-35 minutes for the four runs including restarts.
- Launcher window appears instead of the game: `--no-launcher` was dropped; rerun the block.
- Window never appears and the process exits at once: the runtime's DLL directory is not on `PATH`
  (`0xC0000135`).
- Header-only log: the run never reached gameplay, or the ranges variable names the wrong file;
  redo it.
- `ROM resolution failed` or a file dialog appears: the `--rom` argument is missing or misspelled.

What would falsify this sheet: a log that shows pc `0x0800AFAA` while the player never left the
title, or a run the player calls gameplay whose log is header-only. In either case re-measure the
liveness channel before using the citations.

## Automated runs (2026-10-19)

The four runs can be driven with no keyboard. Each track is a frame-indexed KEYINPUT replay in the
runtime's own text format (a header line, then `frame,0xXXXX` active-low), one file per track:

| track | file | frames | scene it reaches |
|---|---|---|---|
| T1 | `t1-map.txt` | 20,000 | the opening map, walked; no interior or transition |
| T2 | `t2-battle.txt` | 18,000 | the map, walked to the characters standing there; no battle starts |
| T3 | `t3-menu.txt` | 9,600 | pause menu: the Inventory list and a Status skill page |
| T4 | `t4-broad.txt` | 20,000 | a menu pass, then the map walk |

Every track starts with the demo menu track's 0..8,400-frame prefix, the part that clears the title
and the opening dialogue. A replay of that prefix reproduced the demo track's frame-9,600 dump byte
for byte, so the replay path is the same input the demo driver sends.

A replay is one headless run per track: the replay file and the range file arm the run, the log gets
a fresh name, and `--dump-png` keeps the last frame. A per-frame dump directory is window-only, so a
headless run cannot produce the per-frame dumps the sheet used, and the tracks use `--dump-png`
instead.

### Where the old track stalls

The faster `campaign-safe` demo input variant opens the pause menu at frame 8,400 (Status, skill
list), sits on a skill description at 9,000, and is on the opening map by 9,600. It holds right into
the terrain and stops making progress there: the read log's last hit is frame 14,053 in a
14,600-frame run, and the 9,600 and 12,000 dumps show the same scene. The `campaign` variant
re-opens the pause menu every 144 frames because its masher keeps pressing Start, so it never stays
in a map.

### Result (RUNTIME-PROVEN)

| run | exit | frames | log bytes | liveness |
|---|---|---|---|---|
| `auto-t1-map.csv` | 0 | 20,000 | 3,962,478 | True |
| `auto-t2-battle.csv` | 0 | 18,000 | 3,817,138 | True |
| `auto-t3-menu.csv` | 0 | 9,600 | 2,697,242 | True |
| `auto-t4-broad.csv` | 0 | 20,000 | 4,059,202 | True |

| group | target rows | rows cited |
|---|---|---|
| `recomp_lead` (the six end-of-ROM rows) | 6 | 1 |
| `runtime_pending` | 51 | 0 |
| `set_a` | 36 | 0 |
| `set_b` | 62 | 0 |
| **total** | **155** | **1** |

Rows left unreached: 154. The citation is `0x7144D8`, a 1-byte read at `0x08715EF3` by pc
`0x08029178` on frame 4,940. The six-row max index: `0x7144D8` 299,136 hits, highest index 59 of
its 60 blocks; the other five rows are not touched. The opening area reads none of the map block, so
no `set_a` or `set_b` row is reached by walking 20,000 frames.

### Round 2: the talk route and what is still open (2026-10-19)

`t5-talk.txt` continues the round-1 prefix with B to close the pause menu, down 600 frames, A
taps, left 600 frames, A taps, up 420 frames and A taps, to frame 15,000. The A presses confirm
menu entries instead of opening a conversation: the run ends on Goku's stat page (`GOKU LVL 60`,
HP 135/135, STR 27, POW 27, END 28, SPD 50) and no scene changes. It cites none of the 154 rows.

So the opening is not left by walking to the two characters and pressing A on this route. The
remaining routes are shorter and were not tried: talk from directly beside each character, follow
the dialogue with A only (no movement), and walk north past the ridge after the dialogue.

### Round 3: the opening exits (2026-10-19)

Two public walkthroughs describe the opening the same way: Goku and King Kai start on Snake Way;
the road is crossed to the east, faster by dashing; at its end a giant snake head stands beside a
stairway; walking north from there enters Yenma's office, and the chapter continues through a
top-left door in that room.

The frame-9,600 point does not answer RIGHT. Holding RIGHT for 6,000 frames moves nothing: the road
runs diagonally there, and an eight-direction probe (300 frames each, camera scroll and sprite table
compared) moves the player for `LEFT`, `DOWN`, `RIGHT+DOWN`, `LEFT+DOWN` and `LEFT+UP`, and not for
`RIGHT`, `UP` or `RIGHT+UP`.

| route | input | result |
|---|---|---|
| R6 walker | dash walk east along the road, 20,553 frames | crosses the road, answers the line about walking being too slow, stops on the platform at the snake head (frame 30,152) |
| R6 tail | west 600, north 1,200 | Yenma's office interior (frame 31,952): tiled floor, desk, two clerks, room label |
| R7 dialogue | A at the desk, about two dozen presses | the desk conversation ends at frame 41,098; 6 presses end the clerk's at 45,322 |
| R8 door | talk to the clerk, then north | the clerk steps aside; north from the doorway leads behind the desk, no new map (frame 48,158) |

A dialogue page changes only the background layer, so the sprite table stays frozen while the text
advances. "The player can move" is the only reliable end-of-dialogue test: press A, then push a
direction for 16 frames and compare the sprite table.

### Save states (verified)

Windowed build (the runtime's own states, not an emulator's):

- `Escape` opens the runtime settings menu. Its System page holds `State slot` 1-9 and the
  `Save state` / `Load state` actions; the main loop applies the queued action at a frame boundary.
- `Shift+F1`..`Shift+F9` save the same slots without the menu; `F1`..`F9` load them.
- The file lands beside the ROM the run loaded, `<rom path>.state<N>`; a run on `rom.gba` writes
  `rom.state1`..`rom.state9` there.
- A state is 553,424 bytes and holds the whole machine, so it needs the same ROM to load.

Headless:

- `--load-state <path>` restores it after the BIOS boot and prints `savestate_loaded ... frame=N`.
- The only headless way to *make* one is the runtime's debug server: `--tcp <port>`, then
  `{"cmd":"savestate_save","path":"..."}`. A `--tcp` run never enters the main loop, so a replay
  file does not apply there; the input is `{"cmd":"run_frames","n":N,"keyinput":0xKKK}`.

Proof: a state made at frame 9,599 (`saves\opening-field.state0`), loaded with `--frames 0` and
`--dump-png`, writes a frame byte-identical to the round-1 demo dump `safe-9600.png`
(sha256 `4b834fb16d4b2fca...`). The same state plus `tracks\r6-office.txt` replays routes R6 and R7:
exit 0, 25,900 frames, log 3,700,075 B, liveness `True`, dump `dumps\auto-r6-office.png` (the clerk's
line inside the office). `recomp_cited.py --hits` finds no new row, so `RECOMP_CITED.csv` is
unchanged and 154 rows stay unreached.

To settle the rest: pass the door in the windowed build (or reach a battle), press `Shift+F1`, and
hand over `rom.state1`. A headless run over it with `--load-state` and the logger armed then logs the
remaining rows.

### Round 5: the office door and the docking area (2026-10-19)

The round-4 "free" state was not free. `office-free.state0` (frame 32,632) sits in the middle of the
desk conversation: the speaker portrait is a sprite of its own, so a sprite-table change between two
segments read as "the player moved" while the game was still printing text. The desk conversation
ends at frame 36,532, 64 `A` presses at 60-frame spacing from that state (`probe5\dlg-24.state0` is
the halfway point, press 24).

Two input facts, both measured on the office states:

- A conversation's last box closes on `B`. `A` on a finished page re-shows the same page, so a train
  of `A` presses stalls there indefinitely; the dock's King Kai line did exactly that, and pressing
  `B` closed it.
- The player interacts with the tile he faces, not the tile he stands next to. Eight `A` presses
  beside the clerk did nothing until one 6-frame `RIGHT` turned Goku east; the next press opened his
  line, and ten presses at 60-frame spacing ended it at frame 37,528 (he then stands aside).

The door tile is one tile west of the doorway's right post. `UP` from the post is refused; `LEFT`
16 frames then `UP` crosses the map, and the crossing is visible in the BG0/BG1 scroll pair
(`0x04000018`): `360,72` inside the office, `8,352` in the area beyond it.

The area beyond the door is a walkway in the clouds, not a docking bay with planes. Its camera
offsets run x 0..272, y 296..352. The clamps are the ones a 512x512 background produces (272 = 512 -
240, 352 = 512 - 160), and the arrival tile sits on the x=8, y=352 corner. Walking it, the corridor
ends are dead ends; `A` anywhere shows one King Kai line about the journey, `B` closes it, and `A`
again shows the same line. The journal's Goals tab is empty on this map. The planes were not found,
so the Grand Kai's planet and the first battle were not reached. Routes tried and their stops: west
of the arrival, north from the arrival, both ends of the y=328 walkway, the y=337 walkway east to
x=63, the east walkway to the x=272 clamp, and the doorway back into the office (which works, and is
the transition the map run uses).

Milestone states (all 553,424 B, in the session's `saves` directory): `office-north-36892.state0`
(at the doorway), `clerk-done-37528.state0` (clerk aside, door open), `dock-37921.state0` (first new
map), `maprun-office.state0` (back through the door), `broad-end.state0`.

| run | state | frames | exit | log bytes | liveness |
|---|---|---|---|---|---|
| `auto-r11-maprun.csv` | `office-north-36892` | 1,800 | 0 | 298,581 | True (11 hits) |
| `auto-r12-broad.csv` | `dock-37921` | 2,600 | 0 | 1,018,553 | True (3 hits) |

The map run (`tracks\r11-maprun.txt`) talks the clerk, crosses into the new map at frame 37,753,
walks it, and comes back through the door at frame 38,077. The broad run (`tracks\r12-broad.txt`)
walks both maps and opens the pause menu. Dumps: `dumps\auto-r11-maprun.png`,
`dumps\auto-r12-broad.png` (both the office interior after the return crossing).

Citations: `recomp_cited.py` over every `auto-*.csv` in `play002` with `--exclude-cited` reports

| group | target rows | target bytes | rows cited | citations |
|---|---|---|---|---|
| `runtime_pending` | 51 | 980 | 0 | 0 |
| `set_a` | 36 | 50,760 | 0 | 0 |
| `set_b` | 62 | 31,808 | 0 | 0 |
| **total** | **149** | **83,548** | **0** | **0** |

so the new map reads none of the 154 unreached rows and `RECOMP_CITED.csv` is unchanged. The
six-row end-of-ROM table over the two new logs (256-byte blocks) shows the same concentration as
round 1: `0x7144D8` 25,472 hits, highest block 29 of 60, 2 readers, first hit frame 36,902; the
other five rows touch nothing.

One instrument caveat, measured once and not reproduced: pressing `A` at 28-frame spacing through
the desk conversation aborted the run with
`SELF-HEAL bridge for 0x080125E8 exceeded 200000000 instructions without returning to
stop_pc=0x080127A0`; the same presses at 60-frame spacing ran to the end. Every later script uses
the slower cadence.

### Round 6: the plane, the Grand Kai's planet and the first cited map rows (2026-10-19)

Two walkthroughs were the route source this round, one of them illustrated, and they agree: the door at the top
left of Yenma's office leads to a docking area with two planes, and the plane to the Grand Kai's
planet is the RIGHT-hand one.

- GameFAQs/Gamerstemple, chapter 1: talk the blue clerk aside, pass the door, board the right plane.
- dbz.advanced.free.fr, chapter 1 (illustrated): after the talk with Yenma, talk to the man on the
  left, pass the door, then turn right and take the second plane.

The docking area is not a bay with two parked jets beside the door. It is a fenced cloud platform
whose two gangways leave north to two separate dock maps, one per plane: the west gangway reaches a
plane whose attendant says the Higher Plane is on the other dock, and the east gangway reaches the
plane King Kai boards. The route that works, all of it scripted through the debug port:

1. From `saves\dock-37921.state0`, `B` closes the open King Kai line, then `UP` walks the west
   corridor north to the platform's north edge.
2. `RIGHT` crosses the platform east; the camera clamp at x=272 is not a wall (P-749).
3. On the east side the gangway appears at world x ~292-332 on the clamped dumps (INFERRED from its
   screen x plus the x=272 clamp), so the player steps west about 25 px to line up with it, then
   `UP` crosses into the dock map (by frame 56,615, camera `221,221`).
4. King Kai's line on that dock names the plane and the Grand Kai's planet; `A` advances it, `B`
   closes it, and the flight ends on the Grand Kai's planet (frame 58,963, camera `288,168`).

Milestone states (the session's `probe6` directory, same 553,424 B format): `j3.state0` (plane dock,
King Kai's line open), `k2.state0` (first frame of the Grand Kai's planet), `l4.state0` (Olibu's
greeting), `m4.state0` (the training forest), `o4.state0` (Olibu points at the Battlefield Royale),
`p4.state0` (the royale's fighter clearing). `probe6\e3.state0` is the wrong-dock plane.

The Battlefield Royale clearing is where this round stops: its camera sits at `504,56` and no `A`
press, direction or 3,600-frame mash changes the scene, so the first battle was not started and the
battle run below stayed quiet.

| run | state | track | frames | exit | log bytes | liveness |
|---|---|---|---|---|---|---|
| `auto-r13-maprun.csv` | `o4.state0` | `r13-maprun.txt` | 3,000 | 0 | 1,016,415 | True |
| `auto-r14-battle.csv` | `p4.state0` | `r14-battle.txt` | 3,600 | 0 | 787,270 | False |
| `auto-r15-broad.csv` | `k2.state0` | `r15-broad.txt` | 5,000 | 0 | 2,224,625 | True |
| `auto-r16-battle.csv` | `m4.state0` | `r14-battle.txt` | 3,600 | 0 | 780,663 | False |

`r13` walks the forest into the royale clearing, `r15` walks from the arrival south to Olibu and
east into the forest, and both are gameplay (the witness row fires). `r14` and `r16` are quiet on
the witness row: `r16` never reached the track's first key (its track is frame-stamped for `p4`),
and `r14` replayed the mash in the stalled royale clearing.

Citations, `recomp_cited.py --hits` over every `auto-*.csv` with `--exclude-cited`:

| group | target rows | target bytes | rows cited | citations |
|---|---|---|---|---|
| `recomp_lead` | 5 | 67,360 | 0 | 0 |
| `runtime_pending` | 51 | 980 | 0 | 0 |
| `set_a` | 36 | 50,760 | 1 | 1 |
| `set_b` | 62 | 31,808 | 6 | 6 |
| **total** | **154** | **150,908** | **7** | **7** |

All seven are map-block rows read as 4-byte words by pc `0x08009D04` (row extent `0x9B80`-`0x9D6C`),
first on the Grand Kai's planet at frame 58,963: `set_a` `0x17AFA4`-`0x17B1B0` and `set_b`
`0x17A9AC`-`0x17AFA4`. `RECOMP_CITED.csv` gains those seven rows and 147 target rows stay unreached.

The six-row end-of-ROM table over the three gameplay logs: `0x7144D8` 30,336 hits, highest 256-byte
block 29 of 60, 2 readers, first hit frame 59,056; the other five rows touch nothing.


### Round 7: the controls and the field fight (2026-10-19)

The game fights on the field map, not on a separate battle screen: `A` attacks, `B` uses the
selected technique, and `R` blocks. Keys are the runtime's own: `A` = `X`, `B` = `Z`, `R` = `V`,
`L` = `C`, `Start` = `Enter`, `Select` = `Right Shift`.

| GBA | action | runtime key | source |
|---|---|---|---|
| A | attack: walk up to an enemy and hit it | `X` | gamerstemple tips 6 |
| B | special technique, with `L` to cycle which one | `Z`, `C` | gamerstemple tips 7 |
| R | block | `V` | gamerstemple tips 8 |
| Start | status, inventory and equipment screens | `Enter` | gamerstemple tips 3-5 |
| Select | scouter and map overlay | `Right Shift` | gamerstemple tips 1-2 |

Round 6's "the royale clearing ignores input" is wrong and this round corrects it. The clearing is
free: from `probe6\p4.state0` a sustained `LEFT` moves the camera `504,56` to `504,264`, `DOWN` and
`UP` move it, and `START` opens the status screen (GOKU LVL 60, HP 135/135, EP 87/90, XP 2,200,
next 675, ZENIE 100). What failed in round 6 was the cadence, not the scene: 8-frame direction taps
against a map edge, and A-only mashes that move nothing by design. A full HP bar also says nothing
had hit Goku, so there was never a fight there to finish.

States saved this round: `probe7\a8.state0` (training ground, dialogue done), `probe7\b3.state0`
and `probe7\f5.state0` (east of the fighters), `probe7\q3.state0` (map south edge, free),
`probe7\r4.state0` (the clearing). Dumps: `probe7\k2-start.png` (the status screen),
`probe7\z-r.png` (the clearing at 2x), `probe7\z-bar2.png` (the wide light bar under the HUD,
unchanged across 40 attack presses).

No enemy was killed and no battle was started: the figures in the clearing are NPCs and the wide
light bar under the HUD does not shrink under 40 attack presses.

### Round 8: Olibu's challenge and the royale maps (2026-10-20)

Sources read step by step: the illustrated chapter 1 page on dbz.advanced.free.fr, the Gamerstemple
chapter-1 walkthrough, and the Meristation chapter-1 guide. All three put the Battlefield Royale
after Olibu's challenge: two Kais in the first area, three on the top-right path, four fighters on
the bottom-right path, then Olibu.

F1 started from `probe6\o4.state0`, the state nearest Olibu (`l4.state0` is only King Kai's
greeting). The challenge conversation was advanced one press at a time, with a screenshot and a
state per press (`probe8\r8-o4-a1..a5.state0`, `probe8\r8-pre6..pre17.state0`). It ends with
Olibu's good-luck line and returns to free movement. No Yes/No box appeared in twelve single
presses, so the guide's "Yes" is scripted acceptance in this image, not a choice box. State at
acceptance: `probe8\r8-accepted.state0` (frame 69,626, camera `503,190`).

The map pointer at IWRAM `0x03001980` is `0x0808EB68` in every Grand Kai state, i.e. MapEntry 39.
Map 39's eleven placement slots are actor families only: zero `0x0800FD55` enemy records. The
royale sequence is maps 40-43: 2, 3, 4 and 1 enemy records, stat selectors 86/86/86/85 (85 is
Olibu per K-004). First enemies: map 40, selector 86, at `(176,208)` and `(192,224)`, sprites 209
and 211.

Routes from an accepted state, and where each stopped:

| route | track | stop |
|---|---|---|
| south into the forest | `r8-a7.txt` | camera clamps `503,264`; no enemy |
| north then east to the clearing | `r8-a8.txt` | camera clamps `504,56`; three actor NPCs, A on one starts nothing |
| east at Olibu's row | `r8-a20.txt` | camera stays `503,190`; no transition |
| east along the southern road | `r8-a28.txt`, `r8-a29.txt` | camera `503,242` then `503,264`; no transition |
| top-right clearing, crossing `(592,136)` | `r8-a30.txt`, `r8-a31.txt`, `r8-a33.txt` | MapEntry stays 39 |

Two headless replays logged the map-transition ranges (`ranges-r8.txt`: `2948d8-2949a0`,
`753d0-75400`, `8e2e0-8e318`, `8ee90-8eec8`): `auto-r17-east.csv` (1,661,270 B, replay
`r8-a28.txt` from `r8-accepted.state0`, frames 69,626-140,226) and `auto-r18-clearing.csv`
(76,904 B, replay `r8-a8.txt` from `r8-pre13.state0`, frames 69,566-72,866). Neither reads
`0x08294930` or `0x08294948`: the transition records are never consulted on these routes. The
map-block rows `0x082948D8`-`0x08294924` are read every frame.

Citations: `recomp_cited.py --hits` over every `auto-*.csv` with `--exclude-cited` gives 0 new
rows; the remaining table is 142 rows / 81,496 B with 0 cited. The six-row end-of-ROM table has
hits only in `0x7144D8` (426,880 hits, max block 59 of 60, 3 readers, first frame 4,892); the
other five rows are 0.

F5 wanted: a save state from a few frames before the first Battlefield Royale fight (the
two Kais east of Olibu), plus which input started it. Scene detail learned in
F1: the challenge auto-accepts and no Yes/No box appears; map 39 has no enemy placements, while
maps 40-43 hold the guide's 2/3/4/1 enemies.

## Round 9 - the royale exit as data, map 40 reached, the first two royale fights (2026-10-20)

The exit is a record, not a walk target. `MapEntry+0x2C` names the entry's section-root array; the
accessor at `0x080089CC` returns slot `variant-1` (the byte at `MapEntry+0x02`). The root record is
`0x50` bytes: `+0x40` is a count and `+0x44` a pointer to that many `0x18`-byte transition records.
Each record is: function word `+0x00`, second word `+0x04`, trigger rectangle at `+0x08..+0x0F` as
four `u16` corners, destination key high/low at `+0x11`/`+0x12`, arrival `x,y` at `+0x14..+0x17`.
The key is matched against a `MapEntry`'s own `+0x00`/`+0x01` bytes by `0x08008A06` over the table
at `0x0808E2E0`, stride `0x38`.

Map 39 carries two records: `0x08294930` -> map 38 (rectangle `96,0`-`257,17`) and `0x08294948` ->
map 40 (rectangle `592,136`-`601,241`, arrival `0,139`). Map 40 carries two: `0x0829343C` -> map 39
(`0,112`-`9,169`, arrival `599,196`) and `0x08293454` -> map 41 (`232,0`-`273,17`, arrival
`80,260`). Maps 41 and 42 each carry a return and a forward record; map 43 carries a return to 42
and a record to map 44.

The rectangle is in the engine's own coordinates, which run 128 to the left of the player
coordinate that the state probe prints as `cam + screen`. Walking into `592..601`,
`136..241` as printed does nothing (crossed both ways and pressed A: no transition). Walking to
`720..729` of the printed coordinate does transition: at frame 69,927 `state` reads `"map":40`,
`"y":139`, and `r9-map40.state0` holds it. The same offset holds on map 40: the printed `232..273`
does nothing, while `360..401` at the top edge arrives on map 41 at frame 71,832
(`r9-map41.state0`).

On map 40 the two enemy records of the round-8 static read are live: the arrival dialogue is one
line, then both Kais attack. Goku's HP falls 135 -> 110 -> 105 -> 100 -> 95 across the states
below, the first damage seen in this session. Attacking with A, adjacent and facing, prints red
damage numbers (51 seen) and empties a slot: XP 2,200 -> 2,425 after the first kill, then 2,650
after the second, with ZENIE +10 on the second. `r9-kill1.state0` (frame 70,842) is one kill in;
`r9-kill2.state0` (frame 71,442) is the cleared map.

Live units are `0x74`-byte EWRAM records whose `+0x00` word is the unit definition (`0x0804C9F0`
for Goku, `0x0804C484` for the Kais), `+0x04` the sprite/frame id and `+0x6C`/`+0x70` the signed
screen anchor. Three were found on map 40 (Goku and both Kais); `state` reports them as
`"kind":"unit"` rows with world x/y. Enemy HP was not found: diffing the unit record across a
death only shows the slot zeroed, and no field of it falls by the damage amount.

Run table (headless, `ranges.txt`, `--no-window`):

| run | state | track | frames | log bytes | liveness |
|---|---|---|---|---|---|
| `auto-r19-fight.csv` | `r9-kill1.state0` (70,842) | `r9-fight.txt` | 70,842-71,242 | 185,538 | 0 |
| `auto-r19-broad.csv` | `r9-kill2.state0` (71,442) | `r9-broad40.txt` | 71,442-71,942 | 152,652 | 0 |
| `auto-r19-warp.csv` | `r9-kill2.state0` (71,442) | `r9-warp41.txt` | 71,442-72,042 | 242,085 | 2 |

The liveness line `0x0800afaa,...,0x08071734,4,...` fires only in the run that walks through a
transition, which is the map-row reader; the two runs that stay on one map carry zero.

Citations: `recomp_cited.py --hits` over the three logs with `--exclude-cited` cites one new target
row, `set_a` `0x19c744..0x19c870`, read at `0x0819c788` by pc `0x08009d04` at frame 70,851. One row
appended to `RECOMP_CITED.csv` (1 insertion, 0 deletions).

Map 41's arrival leaves the player immobile in this state: at `(96,215)` every direction is
blocked and A advances nothing, so no broad run through map 41 is in this round.

## Round 10 - the map-41 arrival dialogue, the three and four royale fights, Olibu's defeat blocked (2026-10-20)

Map 41's arrival is not a freeze and not a coordinate fault: a dialogue box with a portrait is on
screen while `mode` (`IWRAM 0x03001BA8`) still reads `field`. The same box opens on arrival on maps
42 and 43. It is dismissed by A: on map 41 one press starts the reveal, a second fills the line and
a third clears the box. Movement is suppressed while the box is up and works when it is gone,
measured from one unchanged position: holding UP for 60 frames at `(96,215)` moves nothing; after
three A presses and a 40-frame settle, the same UP hold moves the player to `(96,154)`. The first A
press is also what spawns map 41's three fighters. No stable "dialogue up" flag was found to add to
`state`: a full IWRAM+EWRAM diff across two independent boxes (map 41 and map 39) leaves only
script ids, stack locals and render queues, and no byte is nonzero-open and zero-closed in both.

The three maps run in the guide's order. Map 41's three records are at `(56,112)`, `(240,200)`,
`(128,96)`; map 42's four at `(168,120)`, `(104,136)`, `(208,144)`, `(144,176)`; map 43's single
record at `(136,120)` (sprite 206, selector 85). Each kill is worth 225 XP. Goku's map-41 fight runs
XP 2,650 -> 2,875 -> 3,100 -> 3,325 and ZENIE 110 -> 130, HP 95 -> 70 then 147 after a level-up
(max HP 135 -> 147). The map-42 fight runs XP 3,325 -> 4,225 over four kills and HP 147 -> 123 then
157 after a level-up (max HP 147 -> 157). Exits: map 41's forward rectangle is printed
`392,248`-`457,265` (arrival on 42 at `40,4`), map 42's is `432,192`-`441,249` (arrival on 43 at
`0,116`), map 43's return is `128,88`-`137,145` and its forward record goes to map 44.

Milestone states in the session's `checkpoints` directory: `r10-free41` (71,994, the box cleared, before contact),
`r10-clear41` (72,664, three down), `r10-map42` (77,904, arrival), `r10-free42` (78,270, box cleared,
four live), `r10-clear42` (79,214, four down), `r10-map43` (79,554, arrival), `r10-free43` (79,800,
box cleared), `r10-pre-olibu` (79,840, Olibu engaged).

Olibu's defeat does not complete in this build. Two attempts that brought his health bar to a small
fraction ended with the runtime's own guard: `runtime_arm: SELF-HEAL bridge for 0x0800F668 exceeded
200000000 instructions without returning to stop_pc=0x08011A5E (current pc=0x000001B4). Aborting
rather than spinning silently.` and, on the second attempt, the same line with `0x0800424E` and
`stop_pc=0x0800F686`, `current pc=0x03000838`. Standing still for 300 frames does not abort (Olibu
attacks, HP 138 -> 102); the abort follows the player's attacks as his bar empties. The static
coverage proposal names the nearby region (`0x0800F60C` is a covered entry, `0x0800F668` is not),
so the death path calls code the runtime's dispatch table does not carry.

Enemy HP is still NOT FOUND. Searches this round: one-hit full-RAM diffs (IWRAM 32 KB + EWRAM
256 KB) around single A hits on a live enemy changed 1,559 and 5,903 bytes of animation, HUD and
render staging, with no field falling by a damage amount; the unit record's `0x74` bytes change only
in sprite/frame id, the `+0x12`/`+0x14` animation words and the `+0x30`/`+0x50` scratch pointers.

Run table (headless, `ranges.txt`, `--no-window`, BelowNormal/0x3F):

| run | state | track | frames | log bytes | liveness `^0x0800afaa,` |
|---|---|---|---|---|---|
| `auto-r20-broad.csv` | `r10-free41.state0` (71,994) | `r10-broad2.txt` | 71,994-73,494 | 776,482 | 2 |
| `auto-r20-fight.csv` | `r10-free42.state0` (78,270) | `r10-fight42b.txt` | 78,270-79,070 | 728,401 | 3 |

The broad run walks map 41's forest to the south exit, crosses to map 42, clears its arrival box and
reaches `(156,140)` among the four fighters. The fight run reproduces three kills (XP 3,325 ->
4,000). Liveness is the map-row reader `0x0800afaa`: it fires in both runs, and on the fight run
because the fight's map load reads the row, not because of the walk.

Citations: `recomp_cited.py --hits` over both logs with `--exclude-cited` cites 13 new target rows
in `runtime_pending` (27 citations, 11 distinct readers, frames 71,999-72,063), 128 rows / 80,216 B
left. Twenty-seven rows appended to `RECOMP_CITED.csv` (27 insertions, 0 deletions).

G5 wanted: a save state of the Olibu fight at any point after his bar first drops, plus anything
known about the covered code around `0x0800F668`; the fight itself replays deterministically
from `r10-pre-olibu` up to the abort.

## Round 11 - Olibu defeated, the abort diagnosed and fixed in game.toml, the level-65 gate (2026-10-21)

Olibu's defeat now completes. His bar emptying used to abort the runtime; the abort is
reproduced from a parked-overlay control and removed by two config entries.

Cause, measured. With the two self-heal overlays for `0x0800F668` and `0x0800424E` moved out of the
cache and everything else left warm, the same 1400-frame replay of the Olibu fight from
`r10-pre-olibu` (frame 79,840) exits 3 with:

```
runtime_arm: SELF-HEAL bridge for 0x0800F668 exceeded 200000000 instructions without returning to stop_pc=0x08011A5E (current pc=0x00000158). Aborting rather than spinning silently.
```

The instruction-trace ring, armed on a dispatch miss at `0x0800F668`, names the call path: the
teardown loop dispatches the method through the `bx r1` veneer at `0x08046AA2` (return address
`0x08011A5E`), the method's loop block at `0x0800F656` runs five times, and its taken
`beq 0x0800F668` (`0x0800F65E`, encoding `D003`) dispatches to `0x0800F668`, which has no dispatch
entry. Three trace lines carry those three pcs in order (frames 6,868,201, 6,868,206 and 6,868,207),
and the miss handler reports the block it heals as `0x0800F668`..`0x0800F67E` over `E28AEF5C`.

So it is not a mode switch and not a missing function entry in the ordinary sense: the finder emits
the block that branches to `0x0800F668` but never registers that block as an entry, the miss handler
heals it (the overlay compiles, as the handler reports) yet the dispatch that triggered the miss
is bridged, and the bridge never observes `stop_pc`. `0x0800424E` is the other half: a
six-instruction Thumb function (`push {r3,lr}; ldr r0,[r0,#4]; movs r1,#0; bl 0x08012588;
pop {r3,pc}`) that 86 odd words in the image name, which the finder never rooted; on the second
round-10 attempt its bridge ran away too.

Fix (two entries in the runtime's translation config; generated code untouched): each address was
declared a Thumb entry, `0x0800F668` as a taken branch target inside the region of the block at
`0x0800F60C`, and `0x0800424E` as an address-taken six-instruction function reached through the `bx`
veneer at `0x08046AA2`.

A regeneration discovers 8,406 functions (32 shards) and the build exits 0 (`[35/36] Linking CXX
executable`). The two addresses are now dispatch entries.

After the fix, the same state and the same track: exit 0, `ppu_frames=81240`, no `exceeded` line,
one unrelated miss (`0x0801CD42`, healed). The fight finishes: XP 4,225 -> 4,625, HP 138/157,
ZENIE 140 at frame 80,782 (`r11-clear43`). Enemy HP is still NOT FOUND (third search: a single A hit
on a live map-42 fighter moves only the `0x74`-byte record's sprite/frame word, its `+0x11`/`+0x12`/
`+0x14` animation words, the `+0x30`/`0x50`/`0x54` scratch pointers and the screen anchor).

The next story beat is the character gate. East of the fight the path ends at a wooden door marked
`65` (captured `r11-gate-block.png`); the player stops at `x=199` on `y=104` and a 700-frame RIGHT
hold moves nothing, while A does nothing and `mode` stays `field`. The guide (Gamerstemple chapter
1) says Olibu walks through a character gate marked 65 and that the gate opens only after Goku
reaches level 65 in the earlier areas: four routes were spent on this beat - walk into the gate
(blocked at `x=199`), A at the gate (no change), and the map-43 return record (`rect_player`
`128,88`-`137,145`) crossed leftwards at `y=104` and at `y=143`. Neither crossing transitions, so
the earlier areas are not reachable from this state by that record.

Run table (headless, `ranges.txt`, `--no-window`, BelowNormal/0x3F):

| run | state | track | frames | exit | log bytes | liveness `^0x0800afaa,` |
|---|---|---|---|---|---|---|
| `auto-r21-olibu.csv` | `r10-pre-olibu.state0` (79,840) | `r11-olibu.txt` | 79,840-81,240 | 0 | 1,196,715 | 4 |
| `auto-r21-broad.csv` | `r10-free41.state0` (71,994) | `r10-broad2.txt` | 71,994-73,494 | 0 | 776,686 | 2 |

The liveness PC `0x0800afaa` reads `0x08071734` in both: 4 lines at frames 80,358-80,425 during the
Olibu death path, 2 on the map-41-to-42 walk. `auto-r21-broad.csv` also reproduces round 10's end
state (map 42, `(158,140)` at frame 73,402 against `(156,140)` at 73,400).

Citations: `recomp_cited.py --hits` over both logs with `--exclude-cited` cites 14 new target rows
in `runtime_pending` (41 citations, 24 distinct readers), 114 rows / 80,216 B left. Forty-one rows
appended to `RECOMP_CITED.csv` (41 insertions, 0 deletions).

Regression on the rebuilt binary: `r9-kill1` (map 40) loads at frame 70,842 `(168,208)` HP 100 XP
2,425 and its fight clears to XP 2,650; `r10-clear41` loads at 72,664 `(120,185)` HP 147 XP 3,325;
`r10-clear42` loads at 79,214 `(195,135)` HP 147/157 XP 4,225 and `r10-fight42b.txt` still ends at
frame 79,088 with XP 4,000. Seven self-check tests pass.

## Round 12 - level 65, the character gate and the cave of the ancients

**Level is not a stored field.** A diff across one level-up (XP 3,325 -> 3,775, maximum HP 147 ->
157, three points at `0x0300158C`) contains no counter that rises by one, and a three-state
intersect for 60/61/62 over IWRAM and EWRAM returns 0 hits. The stat page's LVL is the game's own
threshold table read against the XP word at `0x03001584`: 151 ascending u32 at file `0x6B7084`,
entry i being the threshold for level 50 + i; the table base word `0x086B7084` is named by two words
in the code band (file `0x013610`, `0x013908`). Measured agreements: XP 2,200 shows LVL 60 and
NXT LVL 675 (table 2,875); XP 4,625 shows LVL 62 and NXT LVL 75 (table 4,700); XP 4,675 shows
NXT LVL 25 (table 4,700). Level 65 is 7,325 XP. `bfplay state` now reports the derived `lvl` and
the `nxt` remainder.

**Fighters respawn on re-entry, measured.** Map 41 entered through the map-42 top ledge holds three
live `0x0804C484` records after that map had been cleared in the same save's history, and map 42
holds four again after its own clear. `bfplay grind <target>` uses it: fight, leave through a
transition record, come back, repeat, checkpointing each level, and stop at the target level, on low
HP or at a frame cap. Run: map 42, XP 4,225 -> 7,375, level 62 -> 65, 4,758 frames, 3 round trips
(the first level alone took 1,244 frames; 4 kills pay 900 XP).

Two mechanisms cost this round and are handled in the tool now. A level-up box ("Goku has reached
level 63!") and Olibu's post-fight line hold movement while `mode` stays `field`, so
`ensure_control` probes a step and presses A until the player actually moves. And a transition
rectangle's player coordinates are per record: map 41's record fires at its printed `rect_player`
centre, while map 42's fires inside its raw `rect` x range (crossing at x 57-71, y 4; the same press
at x 166 does not fire).

**Stat points.** The status page's allocation screen stages the edits and commits them on A; RIGHT
adds a point to the highlighted stat, UP/DOWN move the highlight. Fifteen points from levels 61-65
spent: STR 27 -> 31, POW 27 -> 32, END 27 -> 32, point word `0x0300158C` 15 -> 0.

**The gate.** Re-entering map 43 replays Olibu, who falls again for +400 XP (7,825 -> 8,225); the
hint box at the door says to walk up to the gate and press A. At level 65 that A press destroys the
wooden door marked 65. Walking north enters map 44 (CAVE OF THE ANCIENTS); L selects the
Kamehameha, a 90-frame B hold and release blasts the stone door open (EP 113 -> 85), and walking
north reaches map 45, the Katchin wall room (`r12-katchin45`). The Instant Transmission target was
not landed on the chest, so the chest and the tournament are unplayed and this is the round's stop.

Run table (headless, `ranges.txt`, `--no-window`, BelowNormal/0x3F):

| run | state | track | frames | log bytes | liveness `^0x0800afaa,` |
|---|---|---|---|---|---|
| `r12-fight42.csv` | `grind-lvl65.state0` (105,870) | `r12-fight42.txt` | 105,870-106,490 | 508,957 | 3 |
| `r12-broad44.csv` | `r12-cave44.state0` (112,892) | `r12-broad44.txt` | 112,892-113,370 | 101,084 | 0 |

The liveness PC `0x0800afaa` reads `0x08071734` three times during the map-42 fight; the
cave-to-Katchin-room walk is silent. The instrument is proven live by the fight run in the same
build, so the silence is a measured property of those two scenes, not a dead channel.

Citations: `recomp_cited.py --hits` over both logs with `--exclude-cited` cites 0 new target rows
(`runtime_pending` 0 of 24, `set_a` 0 of 34, `set_b` 0 of 56), 114 rows left, 80,792 B. The byte
total corrects round 11's 80,216: that figure was `set_a` + `set_b` only and left out the 576 bytes
of `runtime_pending`.

Enemy HP: fourth search, still not found. One A press next to a live map-42 fighter with a
whole-IWRAM before/after diff (770 bytes changed, 179 u16 down, 533 up) names no field that falls by
a damage amount; round 11's per-record diffs stand.

## Round 13 - the live sitting: the arena beat, 45 open ranges read

Played live at the keyboard in one windowed pass starting from the
`r13-chest-ready` checkpoint at frame 114,046 and ending at frame 249,826. Two read logs came out of
it: `20261020-204914.csv` (15,115,371 B, frames 118,637-249,826, 288,940 data rows) and
`20261020-212835.csv` (73,532 B, one hit at frame 228,340, resumed from the last saved state). The
read alarm fired on the first read of each still-open range and wrote a state beside the log, so
every row below has a state at its frame.

**What the sitting covered, in plain words.** It began in the chest room the previous round stopped
in, went back out through the cave, crossed the outdoor cluster of rooms (twice through part of it),
revisited the cave, and finished at the two-map arena beat at maps 138/139, where it stopped with
the play clock at frame 249,826. Nothing past the arena was read, so the next sitting starts where
this one ended.

**Result: 45 of the 114 open ranges read, 13,600 of 80,792 B.**

| group | open rows | read rows | read bytes | rows left | bytes left |
|---|---|---|---|---|---|
| `runtime_pending` | 24 | 24 | 576 | 0 | 0 |
| `set_a` | 34 | 6 | 6,012 | 28 | 43,924 |
| `set_b` | 56 | 15 | 7,012 | 41 | 23,268 |
| **total** | **114** | **45** | **13,600** | **69** | **67,192** |

The citation tool over the two logs yields 121 citation rows (one per row-and-reader pair, 37
distinct readers); all 121 were new, so they were appended to `RECOMP_CITED.csv` with 0 deletions
(378 -> 499 citation rows, 123 distinct row starts). Every range the live alarm reported is also a
row the tool cites from the same log, so the ledger and the tool agree row for row. The three ranges
the live alarm first saw through the IWRAM JCALG1 decoder at `0x03000040` cite from the ROM reader
pc on a later pass over the same row: `0x28ec28` at frames 118,637 then 118,641, `0x21e878` at
217,859 then 217,864, `0x260ea8` at 205,294 then 205,365.

Run table (windowed, reading `uncited_ranges.txt`, 4-byte watch):

| run | start | frames | log bytes | liveness `^0x08009d04,` |
|---|---|---|---|---|
| `20261020-204914.csv` | `r13-chest-ready` (114,046) | 118,637-249,826 | 15,115,371 | 10,974 |
| `20261020-212835.csv` | last hit state (228,337) | 228,338-249,826 | 73,532 | 61 |

The liveness pc is `0x08009d04`, the per-frame map-record walk that feeds the block copy; it fires
in every scene, so its count proves the read channel was open in each run. The old liveness pc
`0x0800afaa` is the map-row reader and stays at 0 in both logs, which is P-764's point: silence
there means a single-map burst, not a dead channel. Several ranges were first read in the same
frame, and the runtime writes one state per frame, so 12 rows share a state with a frame mate
(listed in the hit ledger); no row is without a state at its frame.

The open list was refreshed from the new citation set: `uncited_ranges.txt` now carries 69 ranges /
67,192 B (114 / 80,792 before), and the previous list is kept beside it as
`uncited_ranges.prev.txt`, so the next sitting alarms only on what is still open.

## Round 14 - the warp sweep: 68 of 69 cited from the logs, the last row closed by its decoder call site

Headless, not at the keyboard: 102 maps, one logged run each. Each run loaded a copy of one save
state, changed the destination key in a RAM copy of an exit record, and let the engine's own key
resolver and map loader load the requested map; only IWRAM/EWRAM bytes were written, never the image.
**These maps were reached by redirecting an exit, not by play**, and every read below is the game's
own map-load code reading the ROM. The mechanism itself is in the warp report, outside this tree.

| what | number |
|---|---|
| maps swept, one run each | 102 |
| logs used (a 29-byte probe log with no rows excluded) | 102 |
| read-log rows | 220,179 |
| maps that read at least one open row | 75 |
| maps that read nothing | 27 |
| open rows read, union over runs | 69 of 69 |
| bytes read, union | 67,192 of 67,192 |

Per-map sums are larger (140,932 B) because a shared child list is read by every map that names it.

The citation tool yields 262 citation rows (205 `set_a`, 57 `set_b`), all new against the tracked
file, and they were appended with 0 deletions (499 -> 761 citation rows). That cites 68 of the 69
rows. One row stays open:

- `0x1d2711-0x1d2754` (67 B, `set_b`). Maps 338, 342 and 352 read it - 16 reads each, at
  `0x081d2714` through `0x081d2750`, one frame per run - but every such line carries an IWRAM pc
  (`0x03000068` and three siblings inside the IWRAM JCALG1 decoder at `0x03000040`, which is 166
  ARM instructions long), with the ROM call site only in `lr`
  (`0x08009b31`, inside transcribed row `0x08009ada`+114). Longer runs of the same three maps
  (3,600 frames each, the one-range watch) show the same shape and no ROM pc: 160, 160 and 96 reads,
  all IWRAM (the map-352 run aborted at exit 3 in a self-heal bridge after 96 of them). The read is
  therefore made by the IWRAM JCALG1 decoder called from that ROM site, and the row was cited with
  that caller as its reader (`0x08009b31`, reader row `0x08009ada`+114) under the rule that an
  IWRAM-only read is cited to the ROM call site of the decoder, so
  the tracked citation set now closes the last 67 B. **The open list is empty: 0 ranges, 0 B.**

Liveness: the per-frame walk pc `0x08009d04` fires 0-220 times per log, non-zero in 73 of the 102.
The 29 zero logs are 27 that read nothing at all plus two that read only a 12-byte map-entry row
before the walk begins (`warp-002.csv`, 5 rows; `warp-423.csv`, 89 rows), so a zero here means a tiny
entry read, not a dead channel.

Open list after this round: 0 ranges, 0 B.
