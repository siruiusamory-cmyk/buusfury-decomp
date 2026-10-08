# Cold-boot acceptance of the friend v3 image

Ticket: FRIEND-V3-COLD-BOOT-ACCEPTANCE-001. Verdict: **PASS** on the candidate, with the
delivery blockers listed in section 7. Baseline `origin/master`
`cc9265f1` (`b7f90a42` plus the merged DIALOGUE-TOKEN-PRODUCTIZATION-001), branch
`ticket/friend-v3-cold-boot-acceptance-001`.

Every claim below carries `CONFIRMED`, `INFERRED` or `UNKNOWN`, and the runtime ones a
`LEVEL 3` (verified runtime observation) or `LEVEL 4` (a runtime subsystem seen working
end to end), as `docs/DEVELOPMENT.md` requires. The private friend images and the rename
map are NOT in this repository, so a reader cannot reproduce the v3 numbers from a clone
alone; the images and the save are hashed here so a holder of them can.

## 1. What this answers, and why the earlier evidence was not enough

Every previous Kibito comparison loaded the operator's savestate, and that state's EWRAM
carried decoded dialogue captured on an older build (CONFIRMED by measurement, Adja
`1361b250`: the state holds `Yamcha` 0 hits, `Goku` 8). So each of those comparisons read
the image under test beside restored RAM, and the question "does this image's dialogue
survive the cutscene" was answered on a rig that partly bypassed the image.

This ticket boots from the battery save with NO savestate, and the game builds its own
dialogue cache. Prior work already established that a cold boot rebuilds that cache from
the ROM (CONFIRMED, Adja `3dceafd2`: fresh EWRAM shows `tien=10` on a renamed build and
`vegeta=10` on the base), and that `roms\v3-fixed-credits.sav` is the usable progress
save because `v3.sav` is blank and `1646 COMPLETE.sav` is post-story.

## 2. Identity, verified before and after every run

| what | sha256 | bytes |
| --- | --- | --- |
| candidate: final 451 renames + token engine | `d401d71c0ed3fbf93476aaa1825ea8c680e3caac7f7d7fbc05cbfe16344ab0f5` | 10132968 |
| candidate without the engine patch | `cffdb81e471567fab623d3ec3a0b920cc0b5ef3f0a11bc5f3c70e5bab1395446` | 10132968 |
| known-bad control | `ddfdf780591fd2fdbd37c6fe5118fe871088dc52ce3f6c7538bd5fc4d64c6286` | 9764900 |
| shipped reference, 236 renames | `328f5dcf12279f09d8820cbed26112d14beedc467ed68e6113a873fc474b9b7d` | 10132968 |
| the friend's own image | `a6f4442290c0fe88b83e6affd0250a7eff28b240e7320e04bba7767aa9f065a1` | 9732800 |
| the rename base | `b0de6ddffe53961bcade893107b7f9a8004d684b919552480ca688207e8f56d5` | 9740320 |
| battery save, all three runs | `f6d79dc8896c52943da38e012b3dee0bbc119cfd4ac7d54ef3bc0862140315b7` | 8192 |
| canonical image, untouched throughout | `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e` | 8388608 |

The launcher refuses any ROM whose digest or size is not the exact named pair, copies
the ROM and the save into an isolated run directory under ignored `build/`, verifies the
save copy's digest, refuses to race a running mGBA, and loads NO savestate. Each run's
copy of the candidate image was re-hashed afterwards and is unchanged (CONFIRMED, one
hash per run). The canonical image is byte-identical after all three runs.

## 3. The instrument

`tools/runtime/friendv3_coldboot_probe.lua`, injected with
`tools/runtime/start_friendv3_coldboot_session.ps1` through the tracked
`tools/runtime/mgba_session.ps1` mechanism (`--script` bootstrap, allowlist enforced by
`inject_mgba_lua.ps1`). Read-only: it reads registers and memory, arms ONE breakpoint,
writes host files inside the run directory, and never touches input. The operator drove
all three runs.

It writes a frame heartbeat with the program counter, a screenshot every 300 frames, and
the ENGINE'S OWN dialogue record copies with a text snippet read from the pointer
registers. The dialogue record copier at `0x0801227A` is the liveness channel, because a
silent instrument beside a silent liveness channel proves nothing (mgba-runtime.md s.8):
a run with no copier hits says the route never reached dialogue, not that the image is
clean. Identity is checked twice: the launcher by exact digest and size, the observer by
game code and by `romSize()`, which reports `10132968` and `9764900` for the two sizes
in play (CONFIRMED, the heartbeat column).

## 4. The three runs

Same save, same cold boot, same route driven by the operator to the World Tournament and
the Gohan-SSJ2/Kibito scene.

| image | frames reached | dialogue copies | outcome |
| --- | --- | --- | --- |
| `ddfdf780` known-bad control | **6900** | 35 | **FROZE** |
| `328f5dcf` shipped reference | **10440** | 36 | survived |
| `d401d71c` final image | **13440** | 46 | **survived** |

**The control's freeze is confirmed from outside the emulator** (CONFIRMED): its frame
log stopped at 6900 while mGBA stayed open, and 15 seconds later it had gained zero rows.
That is the recorded fault signature for this defect - no mGBA popup, the frame counter
simply stops, and the program counter sits at the normal BIOS idle address
`0x000001C4` - which is why the detector is the frame log and not the program counter.

**All three images reached the same dialogue line.** Copy index 35 is
`What enormous energy! He's far s` on all three. The control's log ends there. The other
two play past it, and the final image goes on to 46 copies and frame 13440, with combat
on screen afterwards at frame 10200 (LEVEL 4, continued gameplay).

### 4.1 The same line, three encodings, and the outcome

The three images copy the SAME line at copy index 33, and each carries a different
encoding of the same intent (CONFIRMED, the engine's own copies):

| image | what the engine copied at index 33 |
| --- | --- |
| known-bad `ddfdf780` | `It can't be! Krillin's the Great` - plain text, the name as literal letters |
| shipped `328f5dcf` | `It can't be! Gohan's the Great` - retail name, this rename withheld |
| final `d401d71c` | `It can't be! .ill.'s the Great` - dots are token units |

In the final image the stored text is `[KR]ILL[IN]`: five units where retail holds the
seven of `KRILLIN`, with the two tokens composing back to the same glyphs. That is the
whole method in one line, and it is why this image renames a record the shipped build
leaves alone and still survives the scene where the plain-text rename freezes.

### 4.2 The renamed name on screen

Frame 12900, `shot_012900.png`, sha256
`8ce6fc2e5c80d2941d5eae91cdaf0cafaf0df652614153d4dc02dd5aef4035bd` (LEVEL 4): the
Supreme Kai portrait with

> All of you stay where you are! Kibito will take care of Krillin now. He has no need
> of your assistance.

`Krillin` is the renamed name - retail reads `Gohan` - rendered with correct letter
forms, wrapped by the line fitter across four lines with no overflow and no gap. The
surrounding scene renders as it does on the shipped build: the same cutscene line
`What? There's a level beyond Super Saiyan?` at frame 8100 is byte-identical to the
screenshot the previous ticket captured from a savestate run (both
`88d7227e8318bde90a146c450c5814a850562359abf7e380c6fd0606bd7582b3`), so the cold boot
reproduces the earlier rendering exactly (CONFIRMED, matching digests).

## 5. What this closes

The caveat the previous ticket left open is closed: the Kibito route was re-run with no
savestate, the game built its own cache, and the image survived while its own text was
what the engine copied. The tokenised renames therefore work on a clean rig, not only
beside restored RAM.

It also resolves the shape of the earlier freeze: the plain-text grown rename of that
line freezes the scene, and the same rename carried in tokens, at the retail unit count,
does not.

## 6. Reproduce

```text
powershell -NoProfile -ExecutionPolicy Bypass -File tools/runtime/start_friendv3_coldboot_session.ps1 `
  -RomPath <candidate.gba> -RomSha256 d401d71c0ed3fbf93476aaa1825ea8c680e3caac7f7d7fbc05cbfe16344ab0f5 `
  -SavePath <v3-fixed-credits.sav> -Label final-451-engine -MGBPath <mGBA 0.11> -ExpectedRomSize 10132968
```

Then drive to the Kibito scene and close the window. Evidence lands in
`build/friendv3-coldboot/<label>/`: `coldboot.csv`, `shot_*.png`, `inputs.json`,
`marker.txt`. A freeze is detected by the frame column of `coldboot.csv` ceasing to grow
while the window is open; the program counter is not a detector.

## 7. Delivery blockers and limits

* **The private inputs are not in the repository.** The candidate, the control, the
  reference and the save live on this machine only, so the v3 numbers in section 4 are
  UNVERIFIABLE FROM A CLONE. They are reproducible by anyone holding the files, whose
  digests are in section 2.
* **One operator, one route, one save.** The route was driven by hand to the cutscene
  and past it. A different save or a different route is a different experiment, and the
  candidate's 13,440 frames are not a statement about the whole game.
* **The freeze detector is the frame log.** It cannot distinguish a frozen game from a
  window that was closed, which is why the control was held open and re-read 15 seconds
  later before being closed.
* **`romSize()` is an identity check, not a size gate.** It reports the file size here,
  but the launcher's exact digest and size pair remains the authority.
* **Not covered by this ticket:** the `F0674DD8` crash and the unsafe tail allocation,
  both left alone as the earlier ticket required; and the narrower questions the
  previous record lists (constant cave address, the two opt-in encoder seams, and the
  space payment that shows as a wider gap).

## 8. Changes in this ticket

Two new runtime-evidence tools and one allowlist entry, plus this record. No product code
and no part of the merged token implementation was modified:

* `tools/runtime/friendv3_coldboot_probe.lua` (new): the read-only cold-boot observer.
* `tools/runtime/start_friendv3_coldboot_session.ps1` (new): the state-less launcher.
* `tools/runtime/inject_mgba_lua.ps1`: the observer added to `$allowedLua`, 11 added
  lines in the file's existing bare-LF region, with no line ending changed.
