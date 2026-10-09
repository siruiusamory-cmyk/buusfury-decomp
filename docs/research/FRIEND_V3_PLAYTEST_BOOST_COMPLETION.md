# FRIEND-V3-PLAYTEST-BOOST-001 completion pass

This is the record of the second, bounded pass. The first pass is
`docs/research/FRIEND_V3_PLAYTEST_BOOST.md` and its image
`6d7a56c6f96e83cf6e5b86a1ab188d40ab88247c6ffa274f09531e03f609414e`, which stays identified
as the first verified consolidated baseline, not as the deliverable. Nothing here rewrites it.

**Status:** one corrected image now exists, `acd98c2ac90907ae0d83e78019c19b9b26001a49bc28e8bd436da7be9b4bb48c`.
The Bandana is still NOT delivered: its id and storage are now measured, and the new-game seeding site is the one missing piece, named in section 2. One defect was found by runtime observation and is fixed in this image.

## 0b. The corrected image

| | |
| --- | --- |
| image | `build/fv3boost001/out/v3-playtest-boost.gba` (ignored) |
| SHA-256 | `acd98c2ac90907ae0d83e78019c19b9b26001a49bc28e8bd436da7be9b4bb48c` |
| bytes | 10,140,972 |
| changed bytes | 25, all inside the character base-stat table |
| reproduced | twice, same digest, by `build/fv3boost001/build.ps1` |

**Why it is not `6d7a56c6`.** On a cold boot of that image, the owner read the in-game status
screen and the character showed HP -1 and EP -5 with energy attacks disabled. hp and ep are
u16 fields at record `+0x02` and `+0x04`; writing `0xFFFF` made the engine read them as
negative. The four u8 stats at `+0x06..+0x09` were correct at 255, and the level showed 200.
The owner's ruling, verbatim: "You don't even need to change the HP or EP tbh". Both fields are
now absent from the build's field table and hold the values the verified foundation already
carries, which is not always retail: record 1's hp and ep are `0x0064` in both the foundation
and this image, against `0x0055` in the canonical ROM, because the friend build had already
changed that record. The regression test
`test_hp_and_ep_keep_their_bytes_because_0xFFFF_reads_as_negative` pins the untouched bytes.

The screen that produced the ruling, captured afterwards on the same image family, reads:

```text
YAMCHA   LVL 200
HP: -1/-1    EP: -5/-1    XP: 50410227
NXT LVL: 0   ZENIE: 100   TIME: 0:06
STR: 255   POW: 255   END: 255   SPD: 255
```

## 0e. The roster identity, read correctly from the runtime screen

That same screen names the boosted character **YAMCHA**, and `BASE_STAT_NAMES`
(`tools/webfoot/formats/stat_tables.py:87`) is Goku, Gohan, Goten, Trunks, Vegeta, Gotenks,
Vegito, Gogeta, Hercule, with no Yamcha. Only records 0..4 are modified, so the record the
engine resolves for Yamcha sits inside 0..4. What follows, and what does not:

1. **Established:** the name-to-record mapping inferred from `BASE_STAT_NAMES` is contradicted
   by the game's own display for at least one record in 0..4. A record's label is not its
   identity.
2. **Not established:** that the order is wrong. This image is a character-swap build whose
   foundation already rewrites records 0, 1 and 4 against canonical, and whose story text says
   "Yamcha's son, Krillin" where retail says Gohan. A correctly ordered record carrying a
   renamed character fits the same evidence. The external RAM map's order
   (`0=Goku, 1=Gohan, 2=Goten, 3=Trunks, 4=Vegeta, ... 8=Videl`) is what this pass used, and it
   is an external source, not a measurement of this image.
3. **Unknown, and the consequence that matters:** which characters receive the boost. If the
   true order differs, some characters the ticket meant to boost may sit in records 5..8 and
   receive nothing.

The byte evidence is unaffected: whatever those records are, an emulator running `6d7a56c6`
showed level 200 and four stats at 255 in them, and the corrected image carries the same five
records with no hp or ep edit.

What would settle it: read the current-character index at `0x03001068` while the boosted
character is on screen, in a session that has that character selected. That gives the record
index the engine resolves, and the save blocks at a `0x68` stride then name it.


## 0. Runtime evidence

Four runs, all in `build/fv3boost001/runtime/`, all on the **superseded** image
`6d7a56c6f96e83cf6e5b86a1ab188d40ab88247c6ffa274f09531e03f609414e`. Every run's own
`friendv3-boost.gba` copy hashes to that digest and each reported `game_code=BG3E` with
`rom_size=10140972`, so the emulator was running the consolidated friend image and not another
one.

**This matters for the corrected image.** `acd98c2a` is proven at the byte level and by the
build and test gates. No emulator run has been made on it, so every runtime statement below
belongs to `6d7a56c6`, whose only defect was the hp and ep edit that `acd98c2a` removes. The
one runtime action still owed is a status-screen read on `acd98c2a`.

**The instrument was proven before anything was believed.** The new read-only observer
`tools/runtime/friendv3_boost001_probe.lua` first reads the GBA cartridge header through four
paths and compares it with the values every cartridge carries: the logo word at `0x08000004`
read as `0x51AEFF24`, the mandatory `0x96` at `0x080000B2`, the title field at `0x080000A0`
reading `DBZBUUSFURY\0BG3E`, agreement between the per-byte, halfword, word and `readRange`
readers at one address, and a deliberately unmapped address behaving as unmapped. Verdict in
`romcheck.txt`: `status=WORKING`. That is the liveness channel, because the header is read on
the same bus path as the table below. The existing cold-boot observer had never tested this:
it trusted only EWRAM, so it could not have seen the table at all.

| requirement | result |
| --- | --- |
| cold boots | **YES.** `coldboot-01` ran 900 frames and its frame-900 screenshot is the Buu's Fury title screen with START and OPTIONS drawn. Its recorded mode is "cold boot, battery save, no savestate". `coldboot-02` went further from a stricter start: "cold boot, no savestate, no battery save, bounded input driver", 2100 frames |
| the boosted table is in the memory the emulator runs | **YES.** The 90 bytes of records 0..4 were read out of running memory at frame 30 of `coldboot-02`. Their SHA-256 is `f57d5a231061debbe3157c4bea0d3feca04fcf06065cfcf0ce1478ce7c899b84`, equal to that slice of `6d7a56c6` byte for byte, with the per-byte and `readRange` paths agreeing. Decoded: records 0..4 at level 200 and 65535/65535/255/255/255/255 |
| starts a New Game | **YES.** `coldboot-02` used the separate, bounded input driver `tools/runtime/boost001_input_driver.lua` (deliberately blind: A only) and reached Select Game, then GAME 1 New Game, then gameplay |
| presents the intended character statistics | **YES on `6d7a56c6`.** `human-01` was a cold boot with no savestate and no battery save, played by the owner for 34,800 frames; its `shot_033300.png` (sha256 `87b44bf4b6ff00fc3816f35ee7cc16855f6e2d75064aa42a184bbebeae33cb64`) is the Equip tab with STR, POW, END and SPD all 255. `human-02` resumed from that run's own savestate (`8752B3D78C45285D21EA269449A26C3B8195F173351D8AEA606397A37CB612D6`) and captured the Status tab at `shot_001320.png`, sha256 `e5851813865a8d411411990dad41528488ee6a508ae16fd8a22519456cd8d5d3`, enlarged at `zoom_status_4x.png` |
| that Status screen reads | `YAMCHA LVL 200`, `HP: -1/-1`, `EP: -5/-1`, `XP: 50410227`, `NXT LVL: 0`, `ZENIE: 100`, `TIME: 0:06`, `STR: 255 POW: 255 END: 255 SPD: 255`. The level and the four stats are the boost working; the hp and ep are the defect this pass removed |
| preserves representative story transitions | **YES, representative.** The frame-2100 screenshot of `coldboot-02` is an in-game map with a story dialogue box, so the opening cutscene, the map transition and the dialogue path all execute on this image. One transition out of a full campaign is not a campaign result |
| contains the standard Bandana | **NO.** The corrected image does not carry it, and section 2 says exactly what was established, what was not, and what remains before one can be granted |

Two notes so a later reader does not repeat my own first readings.

1. A flat program counter at `0x000001C4` across a whole run is the game's idle loop, and the
   frame-900 screenshot is the title screen, so that is a live run parked at the title and not
   a wedge.
2. The frame-1900 screenshot reads "Yamcha's son, Krillin was able to tap into his deepest
   powers and finally destroy the monstrous Cell". That is the friend build's own text
   appearing after the title, drawn by the game's dialogue path, which is why it is evidence
   about this image rather than about a restored save.

### What remains for a human, stated as exact actions

1. **Statistics.** Boot the image, press START, choose New Game, and open the first pause-menu
   or status screen. Expected: every party member reads level 200, hp and ep at the boosted
   maximum, and the four combat stats at 255.
2. **Boost persistence.** Switch the lead character twice and reopen that screen. The values
   should be unchanged, because the table is read when a character's block is initialized.
   This is also the step that distinguishes a new game from an old save, since a save can
   persist absolute stats written by an older build.
3. **A representative level gate.** Play to any progression door or story gate this build was
   suspected of gating on level. Expected: it opens on the same trigger as retail, because no
   level gate was found that level 200 fails, and no bypass was written for one. A refusal
   here is the evidence a bypass would need.
4. **The Bandana.** Its id and storage are measured; the grant is not written. With a bandana in the
   inventory, the entry can be read in a savestate or debugger: the RAM count at `0x0300114C`
   then the 8-byte slots from `0x03001150`, id in the low 28 bits of the second word. The id
   read there is the id the game uses, and that number is the one piece of information this
   pass could not obtain.



## 1. What the pass measured

All facts below are MEASURED on the merged friend image or on its own support data. Nothing
here is inferred from a name, an offset or a stored note.

| # | finding | source |
| --- | --- | --- |
| 1 | The character roster is nine characters in this table's own order: `0=Goku, 1=Gohan, 2=Goten, 3=Trunks, 4=Vegeta, 5=Gotenks, 6=Vegito, 7=Gogeta, 8=Videl`, with a per-character block stride of `0x68`. This row is EXTERNAL: it comes from a third-party RAM map, not from a measurement of this image. | external Data Crystal RAM map, fetched through the Wayback mirror and read here |
| 2 | The ninth record is **Videl**, not Hercule. This corrects the earlier inference, and agrees with `tools/webfoot/formats/stat_tables.py:77`, which calls all nine records playable. | same |
| 3 | The gear and room names live in one shared name table at `0x06BCE8`, a flat table of 4-byte text pointers scaled by four in the renderer. Index 518 is "Bandana" and 519 is its description; 520 is already a room name ("Airship"), so the room run begins immediately after the pair. Index 428 is "Geromantium Bandana". | ROM read of the image under test |
| 4 | The 83-record item table at `0x3BD2F8` runs item ids 0..82 and names no bandana. Its names resolve through the same table at four entries per item: id 0 is text index 654 "Miso Soup", id 41 is "Ninja Key". | ROM read |
| 5 | The item-add routine at `0x08004448` takes an inventory pointer and an id, refuses silently once the count reaches `0xFA` (250), increments the count, and stores `id & 0x0FFFFFFF`. | Ghidra decompilation of `0x08004448` |
| 6 | The inventory slot is an 8-byte record of two words. The renderer reads the id as `id & 0xFFFFFFF`, multiplies by `0x2C` to reach the gear record, and indexes the name table by that record's `+0x00` halfword. The remaining nibble decides whether an " E" marker is also drawn (name index 69), tested at `0x0801DBC2`. | save-block read, and Ghidra decompilation of `0x0801D988` |
| 7 | The battery save is one 4096-byte save block followed by 4096 bytes of `0xFF`. At offset `0x100` it holds `00000005 00000074`, which reads as count 5 and id 116 ("White Belt") only if each four-byte pair is read big-endian, so this row does not by itself corroborate an id ordering. The renderer's own code path does, and is what section 2 rests on. | direct read of the save, and the RAM map |
| 8 | The external RAM map records no item-id field for gear; the nearest entries are the derived "Currently Equipped STR/POW/END/SPD" totals at `0x03002B70`.., which are computed values, not ids. This row is EXTERNAL, like row 1. | RAM map |

## 2. The Bandana: storage MEASURED, grant not written

An earlier version of this record called the id arithmetic an unresolved blocker. That was
wrong, and an independent review contradicted it. All of the following is measured on the
delivered image and on live emulated RAM.

**The id.** The name table at `0x06BCE8` is a flat table of 4-byte text pointers scaled by
four in the renderer. The renderer `0x0801D988`'s literal pool holds the name table at
`0x0801DC68` and a **gear table** at `0x0801DC74`, file offset `0x6F82EC`: 162 records of
`0x2C` bytes, the name index at `+0x00`, the description index at `+0x02`. Gear record **126**
names index 518, "Bandana". The renderer reads an inventory id, keeps its low 28 bits,
multiplies by `0x2C` and adds that base, so ids index this gear table directly.

**The storage.** Measured twice, and the two agree: once by reading the completed battery save
directly, and once by reading live emulated RAM with the operator's equipped bandana in place.

| element | finding |
| --- | --- |
| count | u16 at `0x0300114C`; read live as 28 on the completed save |
| slot | 8 bytes: **word 0 is the item's own gear id**, **word 1 is a status word** |
| a held but unequipped item | status word `0x00000000`; the pair is (`id`, `0`) |
| an equipped item | the top nibble of the status word is set to the wearer's index plus one |
| the observed transition | the operator equipped the bandana. At frame 1110 the pair at `0x030011A4` was `0x0000007E 0x0000007E`; at frame 3210 it was `0x1000007E 0x0000007E`. Only that nibble moved, and the count stayed 28 |

Reading the same structure out of the completed save independently corroborates it: it holds
`00000005 00000044` at `0x140` and `0000009C 0000007E` at `0x150`, which is the bandana with
status `0x7E` marking it held and available.

**The remaining gap is the site, not the shape.** A grant has to write id 126 into the next
free slot with status 0 and increment the count at `0x0300114C`. The routine that does that
already exists and is known: `0x08004448` takes the inventory pointer and an id, refuses
silently at 250 entries, increments the count and stores `id & 0x0FFFFFFF`. What is not yet
located is the new-game initialization path that seeds the inventory, so a call site cannot be
chosen from evidence. Two bounded routes to it:

1. Trace the writer that stores the count at inventory `+0xE4` on a new game, from the
   save-block base pointer the ROM holds as a literal at file `0x6B7080`.
2. Have the operator start a brand-new game on a session with the inventory watch armed, and
   read the first count transition. That shows the seeding writes directly.

Either yields a call site inside the game's own path, which is what a grant should use rather
than a raw byte patch of the live save block.



## 3. The specific next action that resolves it

One of these two, both bounded:

1. **Ghidra, one routine.** Follow `0x0801D988`'s two name lookups (`DAT_0801dc68` indexed by
   a halfword at item record `+0x00`, and by `+0x02`) back to the routine that maps an id to a
   name, and quote its addressing arithmetic. That yields the bandana id directly, because the
   name index is already known to be 518.
2. **Runtime, one observation.** In a human-driven session on the merged image, obtain or hold
   any bandana and read the inventory block: the RAM count at `0x0300114C` then the entry
   slots from `0x03001150`, each 8 bytes, id in the low 28 bits of the second word. The id
   seen there is the id the game uses.

With either answer, the insertion itself is small and already scoped: add the id once at
new-game initialization, or extend the existing grant site, with the `0xFA` cap and the flag
nibble preserved. The add routine's contract is measured, so the patch writes one known value
through a known function rather than raw bytes.

## 4. What is unchanged

- The merged baseline `42106cacaed0b3f7878181dbec2d0b1ae4b23763` is untouched, and
  `build/fv3boost001/build.ps1` now reproduces `acd98c2a...`. The earlier `6d7a56c6...` is
  retired, not deleted, and its four runtime runs stay on record.
- No level-gate bypass was written. Nothing measured in this pass shows a gate that level 200
  fails, and adding bypass code without that evidence would be exactly the speculative change
  the ticket forbids.
- The corrected image replaces the first one rather than joining it, so there is still one current image. No competing variant exists
  without invention. The single-ROM rule is therefore satisfied by there still being one image.
