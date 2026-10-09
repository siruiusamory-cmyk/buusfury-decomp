# FRIEND-V3-PLAYTEST-BOOST-001 completion pass

This is the record of the second, bounded pass. The first pass is
`docs/research/FRIEND_V3_PLAYTEST_BOOST.md` and its image
`6d7a56c6f96e83cf6e5b86a1ab188d40ab88247c6ffa274f09531e03f609414e`, which stays identified
as the first verified consolidated baseline, not as the deliverable. Nothing here rewrites it.

**Status:** one corrected image now exists, `acd98c2ac90907ae0d83e78019c19b9b26001a49bc28e8bd436da7be9b4bb48c`.
The Bandana is still NOT delivered, with its mechanism named in section 2. Two defects were
found by runtime observation and one of them is fixed in this image.

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
now absent from the build's field table and keep their retail values, which is what the
regression test `test_hp_and_ep_keep_their_bytes_because_0xFFFF_reads_as_negative` pins.

The screen that produced the ruling, captured afterwards on the same image family, reads:

```text
YAMCHA   LVL 200
HP: -1/-1    EP: -5/-1    XP: 50410227
NXT LVL: 0   ZENIE: 100   TIME: 0:06
STR: 255   POW: 255   END: 255   SPD: 255
```

## 0e. A second defect, in the roster identity, found at runtime and NOT fixed

That same screen names the boosted character **YAMCHA**, and `BASE_STAT_NAMES`
(`tools/webfoot/formats/stat_tables.py:87`) is Goku, Gohan, Goten, Trunks, Vegeta, Gotenks,
Vegito, Gogeta, Hercule, with no Yamcha. Only records 0..4 are modified, so the record the
engine resolves for Yamcha sits inside 0..4. Two consequences, stated as they stand:

1. The inferred name order is wrong for at least that record, and the names this build prints
   in its change manifest are labels from an inference, not verified identities.
2. Which characters actually receive the boost is therefore **unknown**. Some that the ticket
   meant to boost may sit in records 5..8 and receive nothing.

The byte evidence is unaffected: whatever those records are, an emulator running the image has
level 200 and four stats at 255 in them, and no hp or ep edit.

The friend workstream already carries the matching warning: in the merged foundation the only
record labelled "Bulma" is retail Chi-Chi, and retail Bulma is labelled "Tulma". Labels in
this image are not identities, and this pass adds a second measured instance of that.


## 0. Runtime evidence, taken on the exact merged image

Two runs, both in `build/fv3boost001/runtime/`. The image under test hashed to
`6d7a56c6f96e83cf6e5b86a1ab188d40ab88247c6ffa274f09531e03f609414e` and each run reported
`game_code=BG3E` with `rom_size=10140972`, so the emulator was running the merged image and
not another one.

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
| the boosted table is in the memory the emulator runs | **YES.** The 90 bytes of records 0..4 were read out of running memory at frame 30 of `coldboot-02`. Their SHA-256 is `f57d5a231061debbe3157c4bea0d3feca04fcf06065cfcf0ce1478ce7c899b84`, which equals the same slice of the delivered file byte for byte and does **not** equal canonical's `89af830811fb78eeee1b525d02c4d7745ada3d7bc106b2cd8c0a4f58510b6efc`. The per-byte and `readRange` paths agree with each other. Decoded: all five records level 200, hp 65535, ep 65535, strength/power/endurance/speed 255 each. Raw reads: `boost_table_read8.bin`, `boost_table_range.bin`, `boost_table.csv` |
| starts a New Game | **YES.** `coldboot-02` added the separate, bounded input driver `tools/runtime/boost001_input_driver.lua` (deliberately blind: it presses A only) and reached the new game. The title screen is passed and the opening narrative plays: the frame-1900 and frame-2100 screenshots show story text boxes over gameplay scenes |
| presents the intended character statistics | **NOT OBSERVED in a menu.** No pause or status screen was reached. What is proven is that the running image holds those bytes |
| preserves representative story transitions | **YES, representative.** The frame-2100 screenshot is an in-game map with a story dialogue box, so the opening cutscene, the map transition and the dialogue path all execute on this image. One transition out of a full campaign is not a campaign result |
| contains the standard Bandana | **NO, and the reason is measured.** The run's own inventory was not inspected for a bandana because none can be granted: see section 2 |

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
4. **The Bandana.** Meaningful only after section 2 is resolved. With a bandana in the
   inventory, the entry can be read in a savestate or debugger: the RAM count at `0x0300114C`
   then the 8-byte slots from `0x03001150`, id in the low 28 bits of the second word. The id
   read there is the id the game uses, and that number is the one piece of information this
   pass could not obtain.



## 1. What the pass measured

All facts below are MEASURED on the merged friend image or on its own support data. Nothing
here is inferred from a name, an offset or a stored note.

| # | finding | source |
| --- | --- | --- |
| 1 | The character roster is nine characters in this table's own order: `0=Goku, 1=Gohan, 2=Goten, 3=Trunks, 4=Vegeta, 5=Gotenks, 6=Vegito, 7=Gogeta, 8=Videl`, with a per-character block stride of `0x68`. | external Data Crystal RAM map, fetched through the Wayback mirror and read here |
| 2 | The ninth record is **Videl**, not Hercule. This corrects the earlier inference, and agrees with `tools/webfoot/formats/stat_tables.py:77`, which calls all nine records playable. | same |
| 3 | The gear and room names live in one shared table of 8-byte records at `0x06BCE8`: a name pointer, then a description pointer. Index 428 is "Geromantium Bandana", index 518 is "Bandana" with the description "Only a really vicious criminal would wear something like this." Index 519 onward are room names ("Airship", "Atrium"). | ROM read of the image under test |
| 4 | The 83-record item table at `0x3BD2F8` runs item ids 0..82 and names no bandana. Its names resolve through the same table at four entries per item: id 0 is text index 654 "Miso Soup", id 41 is "Ninja Key". | ROM read |
| 5 | The item-add routine at `0x08004448` takes an inventory pointer and an id, refuses silently once the count reaches `0xFA` (250), increments the count, and stores `id & 0x0FFFFFFF`. | Ghidra decompilation of `0x08004448` |
| 6 | The inventory slot is an 8-byte record: a count word and an id word whose top nibble is a flag. One renderer reads ids as `id & 0xFFFFFFF`, multiplies by `0x2C` to find the item record, then indexes the name table by `record[0]`. | save-block read, and Ghidra decompilation of `0x0801D988` |
| 7 | The battery save is one 4096-byte save block followed by 4096 bytes of `0xFF`. Its inventory block begins at offset `0x100` with a first entry of count 5 and id `0x74` (116). The RAM map names `0x0300114C` as the item count and `0x03001068` as the current character. | direct read of `v3-fixed-credits.sav`, and the RAM map |
| 8 | The external RAM map records no item-id field for gear; the nearest entries are the derived "Currently Equipped STR/POW/END/SPD" totals at `0x03002B70`.., which are computed values, not ids. | RAM map |

## 2. The unresolved mechanism, stated exactly

The blocker is one piece of arithmetic, and it is the only thing standing between the evidence
above and a safe Bandana insertion.

**What is established.** An inventory id is a small integer. The renderer multiplies it by
`0x2C` to reach an item record and then indexes the name table at `0x06BCE8` by a halfword
inside that record. The 83-record table supplies that mapping for ids 0..82 only, and none of
its records names a bandana.

**What is not established.** Which record table and which id the game uses for the Bandana.
Two readings of the renderer are both arithmetically consistent with the bytes:

- reading A: the bandana id is the name-table index, 518, and its `0x2C` record lives in a
  second table whose base is not `0x3BD2F8`; or
- reading B: the bandana id is a small index into a second `0x2C`-stride table whose record's
  first halfword points at name index 518.

The two readings produce different patched bytes. Choosing one, or choosing an insertion point
at the new-game entry without knowing it, would be invention. The project's rule is that an
unsupported input fails closed with its reason, and this is that case.

**Why the available routes did not close it.** The public reconstruction repository is a
repackaging harness: 98.568 percent of its image is verbatim INCBIN, and the four addresses
this question needs appear zero times in its entire history (its `docs/REFERENCE_AUDIT.md:49`
to `:68`). The decompilation pass returned UNSUPPORTED on the inventory initializer, on the
level consumer and on every level gate, for the same reason. Ghidra does hold the code, and
`0x08004448` and `0x0801D988` decompiled cleanly from it, but the name-resolution routine that
would settle reading A against reading B was not reached before that lane's budget ended.

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

- The merged baseline `42106cacaed0b3f7878181dbec2d0b1ae4b23763` and its image
  `6d7a56c6...` are untouched, and the reproducible pipeline in `build/fv3boost001/build.ps1`
  still reproduces that digest.
- No level-gate bypass was written. Nothing measured in this pass shows a gate that level 200
  fails, and adding bypass code without that evidence would be exactly the speculative change
  the ticket forbids.
- No new ROM variant was produced, because no remaining modification could be implemented
  without invention. The single-ROM rule is therefore satisfied by there still being one image.
