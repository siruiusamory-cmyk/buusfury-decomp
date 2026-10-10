# FRIEND-V3-WT-SPLIT-CONTAINER-001: the runtime proof

This is the runtime half of `FRIEND_V3_WT_SPLIT_CONTAINER.md`. It is evidence taken under
`docs/skills/mgba-runtime.md` and `docs/runtime-capture.md`, on the emulator the repository
pins: `build/tools/mgba-dev/.../mGBA.exe`, `FileVersion 0.11.0.0`, verified from the binary
before every launch.

Images and state, sha256 re-verified after every run:

| input | bytes | sha256 |
| --- | --- | --- |
| `v3-mainline-text-dialogue-pass.gba` | 10,141,220 | `d2a25f9a56c9980e27ad4a6f4c23d653e87d15b71b908ee27bced48b88885543` |
| savestate `working-state.ss1` | 71,845 | `cab4580e23202f9ffe1200e90cfc3493eaf27fbbdc7ded3e6c519f6d82764378` |
| canonical ROM | 8,388,608 | `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e` |
| throwaway `v3-split7.gba` | 10,141,390 | `820a06e055dee97a82788844fd13a75b152815ad56bfe5df20d140a1ee3afd8b` |

## The instrument, and one bug that voided two runs

Observer `tools/runtime/fv3wt001_container_route_watch.lua`, allowlisted in
`tools/runtime/inject_mgba_lua.ps1` by an allowlist-only edit. Read-only: it reads registers
and memory and writes host files inside the run directory. It arms four breakpoints, all
`ok=true`:

| address | role |
| --- | --- |
| `0x08012248` | table-load site A (loader `0x08012230`) |
| `0x080122CE` | table-load site B (loader `0x080122B4`) |
| `0x0801227A` | the dialogue record copier |
| `0x08046AA4` | the dispatch thunk, chosen as the **liveness** channel |

**Liveness, and why the copier is not it.** The previous ticket measured the copier at zero
hits under a savestate and recorded that a state restores already-decoded dialogue, so the
copier is silent by construction there. The dispatch thunk fires tens of thousands of times
per run on this build and is the channel used: dispatch hits 102,995 and 108,169 in the two
runs reported below.

**Two runs are void and are named rather than quietly dropped.** The first observer derived
the handle's address as `site - 8`, which is the code word at `0x08012240`, and it returned
before incrementing its own hit counter, so a live site reported as silent. Both faults are
the instrument's, and the corrected runs are the ones reported. Any reading of
`fv3wt001-census-noinput` or `fv3wt001-census-input` as a negative is retracted here.

## Finding 1: the table is read by ONE site at runtime, and the selector is bits 0-5

Run `build/toolkit031/fv3wt001-census-input4`, 2,400 frames, unmodified image, the same
savestate, with `tools/runtime/npc_talk_driver.lua` pressing A every 180 frames:

```
dispatch_hits=102995  site_a_hits=9  site_b_hits=0  copier_hits=9
site_a_selector_low6_histogram:  A,3,9
site_a_max_selector_low6=3  site_a_over_6=0  site_b_max_selector_low6=-1
engine_index_vs_reading: site_a index_read=9 index_unreadable=0 agree_low6=9 agree_high6=0
```

Three results, each stronger than the static reading that predicted it:

1. **`0x08012248` is on the live dialogue path.** It fires 9 times, in step with the copier's
   9 calls, in a run where the dispatch thunk fires 102,995 times.
2. **`0x080122CE` never fires**, in any corrected run. The claim inherited from the previous
   ticket that two code sites read the table is **not supported at runtime**: the derivative
   reads it from one site. A split has one consumer to satisfy, not two.
3. **The engine's own index agrees with bits 0-5, nine times out of nine.** For the first hit
   the handle word is `0x02050017`; its low six bits are 3, the engine's index is 3, table
   slot 3 is `0x08979EF8`, and the decoded container at that pointer starts
   `0023 0054 0068 0061 0074 0020` = `#That we`. The alternative reading (bits 26-31) agrees
   in 0 of 9 rows. `tools/webfoot/handles.py`'s layout is confirmed at runtime.

**No selector above 6 on the retail route, and it is a real negative**: the dispatcher fired
102,995 times and the copier fired 9 times, so dialogue records were copied during the run,
and every resolved selector was 3.

## Finding 2: the split renders

Throwaway image `build/fv3wt001/runtime/v3-split7.gba`, built by
`build/fv3wt001/runtime/build_split_image.py` and described by
`build/fv3wt001/runtime/v3-split7.manifest.json`:

- a new container appended at file `10,141,220` (= runtime `0x089ABE24`), 4-byte aligned,
  `kind=0`, `declared_size=162`, payload 81 units of `ZZSPLITZZ` as UTF-16LE;
- table slot 7 at file `0x9A9D04`: `0x03004A68` -> `0x089ABE24`;
- the target record's packed handle replaced by `DialogueHandle(7, 0, 162).encode()` =
  `0x0A200007` at **all nine** of its handle sites, every before/after in the manifest;
- the script refuses to write on any disagreement: a slot that does not hold the expected
  word, a decode that does not match, a site that does not carry the expected handle, or zero
  sites repointed.

Run `build/toolkit031/fv3wt001-split7-run`, 2,400 frames, same state, same observer:

```
dispatch_hits=108169  site_a_hits=5  site_b_hits=0  copier_hits=5
A,1,0x0A200007,7,2,0,162,7,engine_index_matches_low6
site_a_selector_low6_histogram: A,7,5      site_a_over_6=5
last_handle_a=0x0A200007 low6=7 start=0 length=162
```

Both conditions the brief set hold:

- **(a) the engine resolved selector 7**: `r1` held the table base and the engine's own index
  was 7, five times, from the handle this image wrote.
- **(b) it renders**: `shot_000240.png` in that run shows the dialogue box filled with
  `ZZSPLITZZZZSPLITZZZZSPLITZ...` and the portrait. The same frame of the unmodified image
  (`fv3wt001-census-input4/shot_000240.png`) shows the retail line
  `Do you just want to see a Super Saiyan? Or should I take it up to the next level?`.

The copier count differs between the two runs (9 against 5) because every repointed record now
renders the same 81-unit marker, so fewer distinct strings are copied. That is the marker's
side effect, not a defect.

**Input was driven and is not the proof.** `tools/runtime/fv3wt001_input_driver.lua` (A only,
frames 300-1500) and `tools/runtime/npc_talk_driver.lua` (A every 180 frames) advanced the
scene; the causal chain claimed here is slot 7 -> engine index 7 -> the appended container's
bytes on screen, and the rendered marker is what closes it. The observer file contains no
input call; the driving code is a separate file, as the skill requires.

## Verdict

**SPLIT ROUTE PROVEN.** A dialogue container can live on a selector above 6, be resolved by
the retail engine, and render, with no engine change: one table word in dead copied data, one
appended container, and the handle words of the records that move.

## Limits, stated rather than implied

1. **The appended region is past the header's declared cart size.** The image's header word at
   file `0x7FFFFC` holds `0x21EE04B0` (declared 8 MiB), while the file is 10,141,220 bytes and
   `emu:romSize()` returns 10,141,220. The appended container at `0x089ABE24` therefore reads
   on the emulated bus **because mGBA serves the whole file**. Measured reachability:
   `build/toolkit031/fv3wt001-cartmap/map.txt` read `0x08800000` and `0x089ABE24`
   successfully. This is an **emulator behaviour, not proven hardware behaviour**, and it
   applies equally to the six containers this image already carries past 8 MiB - the route
   adds no new kind of address, but it does not settle the hardware question either.
2. **The marker filled the whole record.** D2 proves the routing for one 162-byte record. It
   does not exercise the planned 47,532-byte container, nor a record near the length ceiling.
3. **The copier's own source register was never resolved.** `copies.csv` stayed header-only in
   every run; condition (b) rests on the rendered marker, which is the stronger of the two
   proofs the brief allowed, not on the copier log.
4. **The census covers one scene, one save state, 2,400 frames, and one selector value.** "No
   selector above 6" is a real negative for this run. It is not a census of the whole game.
5. **The selector-13 case is untouched.** Three record-shaped words inside dialogue payloads
   carry selector 13 (see the route document). The split uses selector 7, where no such word
   exists inside a payload.

## Release 2: the World Tournament scene, on the real candidate

The release-2 candidate `v3-wt-split.gba` (`build/fv3wt001/release2/v3-wt-split-a.gba`, sha256
`0b5ac8f470277f3c674710e07ce9d744433acd6a331736a628e00d6f72a6ef22`, 10,143,256 bytes) was
loaded **cold**, with no savestate, on the battery save `v3.sav` (sha256
`29f89867cdfb1e6e9956f461727b2e01bff91929351bd47e23c2c2a5af44e66a`, the recorded map-133 ->
map-134 route save) and driven by hand from the tournament grounds.

Run directory `build/friendv3-coldboot/fv3wt001-wt-route`. The candidate digest was re-verified
before the run and again after; the battery save is a copy and its source was not written.

**Which files this section quotes.** The session was ended by closing the window, so the
observer's own shutdown path never ran: there is no `marker.txt` and no summary block. The
numbers below come from `route.csv` (last row `24420,1033711,51,8,51,0x08090010,138`) and from
`sites.csv`, both of which are frozen in the run directory. The same numbers also appear in the
live `histogram.txt` heartbeat tail. Nothing in this section depends on a file that was not
written.

**Instrument proven.** All four breakpoints `ok=true` before the session started. Liveness
dispatch `0x08046AA4` fired 1,033,711 times in 24,420 frames; `site_a` 51; `site_b` **8**;
copier 51.

**The census first: the second loader is not dead after all.** The earlier census saw
`site_b = 0` and the route document recorded the table as having one runtime consumer. That
statement was scoped to the scene it measured, and this run falsifies the general form: with a
level-up and a stat screen in the run, `0x080122CE` fires. Its eight hits resolve selectors 5,
3 and 0 and read the same containers site A does. **The split therefore has two consumers to
satisfy, and both load the same literal**, so the single table word this release writes is seen
by both. Nothing about the route changes; the earlier sentence does.

**The proof: fourteen of the fifteen rows were resolved by the engine out of the appended
container, with their approved wording.** Every line below is a `sites.csv` row: the engine's
index 7, the resolved container `0x089ABE24`, and the units the record's own handle names, read
back from the resolved container at `container + 8 + start` (the observer reads them from that
address; it is not the copier's own register). The log substitutes a semicolon for every comma
inside text, so the punctuation style in this table is the log's, not the ROM's.

| record | resolved start | text read from the appended container |
| --- | --- | --- |
| `3:7406:136` | 0 | `#Hey sis, if you win the tournament, what do you think you'll get with the prize Zeni?` |
| `3:7542:42` | 172 | `#Uh, tons of okonomiyaki, I guess!` |
| `3:7584:80` | 240 | `#Sheesh, Videl! How are you not fat?` |
| `3:7664:60` | 312 | `#EXCUSE ME?! What are you going to get then?` |
| `3:7724:72` | 400 | `#Candy. Lots and lots of candy.` |
| `3:7796:204` | 462 | `#And you call me fat. Hey, isn't that kind of meta?` |
| `3:8000:214` | 564 | `#Hey, half pint! We don't take too kindly to your folk around here.` |
| `3:8214:118` | 698 | `#Huh? Do you mean brown people?` |
| `3:8332:218` | 760 | `#What?! No! My mom may be racist, but I'm not! Geez, I meant adopted kids!` |
| `3:9112:62` | 908 | `You really made me look bad earlier.` |
| `3:9174:114` | 980 | `#Bruh. You were still totally a dick.` |
| `3:9288:282` | 1054 | `#That's my baby Idasa down there! Oooooo! Idasa! I wish they would match Idasa up with a whiter kid! This is a disgrace!` |
| `3:9662:116` | 1294 | `#Get him, Uub! You make that boy sorry his mom is racist!` |
| `3:9778:114` | 1408 | `Noooo! My baby! That was unfair! That thing cheated!` |

**And on screen.** `shot_021900.png` (and the identical `shot_022200.png`) shows the junior
division arena with the dialogue box reading `That's my baby Idasa down there! Oooooo! Idasa! I
wish they would match Idasa up with a whiter kid! This is a` and Idasa's mother's portrait,
which is record `3:9288:282`, row 14 of the owner's table, resolved from the appended
container. The operator drove the scene and confirmed the lines played.

**One row was not observed.** `3:9892:486` (row 18, the announcer's championship passage) has
no row in `sites.csv`: the run did not reach that announcement, or its record was resolved
after the operator stopped. It is verified statically (it resolves through slot 7 and reads
the approved passage back, checked by the release verifier) and is **not** claimed as seen at
runtime.

## Release 2 verdict

**RUNTIME-VERIFIED on the release candidate**: fourteen of the fifteen rows resolved out of the
appended container with their approved wording, one of them photographed on screen in the
junior division scene, and the operator drove the scene and confirmed it played. Row 18 is
static-verified only, and that limit is stated rather than folded into the claim.

