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

That same status screen names the boosted character **YAMCHA**, and `BASE_STAT_NAMES`
(`tools/webfoot/formats/stat_tables.py:87`) is Goku, Gohan, Goten, Trunks, Vegeta, Gotenks,
Vegito, Gogeta, Hercule, with no Yamcha. That is not a contradiction, and the reason is
measured: this friend build **renames the name table itself**. Index 116 "Goku" is "Yamcha"
here, 117 "SS Yamcha", 118 "SS3 Yamcha", and 123 "Gohan" is "Krillin". A YAMCHA status screen is
therefore what this build calls the record labelled Goku.

So the screen is consistent with the external record order, and the order stays labelled
external rather than becoming a measurement of this image. The consequence for a report is that
a character must be tracked by record index, since the on-screen name is this build's own
renaming.
## 1. What the pass measured

Every fact below states its source. Rows 1 and 8 come from an external RAM map and are labelled
EXTERNAL; the rest were measured here, and row 6's shape was settled by decompiling the game's
own add routine.

| # | finding | source |
| --- | --- | --- |
| 1 | The character roster is nine characters in this table's own order: `0=Goku, 1=Gohan, 2=Goten, 3=Trunks, 4=Vegeta, 5=Gotenks, 6=Vegito, 7=Gogeta, 8=Videl`, with a per-character block stride of `0x68`. This row is EXTERNAL: it comes from a third-party RAM map, not from a measurement of this image. | external Data Crystal RAM map, fetched through the Wayback mirror and read here |
| 2 | The ninth record is **Videl**, not Hercule. This corrects the earlier inference, and agrees with `tools/webfoot/formats/stat_tables.py:77`, which calls all nine records playable. | same |
| 3 | The gear and room names live in one shared name table at `0x06BCE8`, a flat table of 4-byte text pointers scaled by four in the renderer. Index 518 is "Bandana" and 519 is its description; 520 is already a room name ("Airship"), so the room run begins immediately after the pair. Index 428 is "Geromantium Bandana". | ROM read of the image under test |
| 4 | The 83-record item table at `0x3BD2F8` runs item ids 0..82 and names no bandana. Its names resolve through the same table at four entries per item: id 0 is text index 654 "Miso Soup", id 41 is "Ninja Key". | ROM read |
| 5 | The item-add routine at `0x08004448` takes an inventory pointer and an id, refuses silently once the count reaches `0xFA` (250), increments the count, and stores `id & 0x0FFFFFFF`. | Ghidra decompilation of `0x08004448` |
| 6 | An inventory entry is one 4-byte word: the top nibble is the wearer index plus one, the low 28 bits are the gear id. Section 2 has the routine that settles it, `0x08004448`. | decompilation of `0x08004448` and `0x08004468`, and live RAM |
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

**The storage.** Measured from the game's own add routine and from live emulated RAM. The two
agree, and the routine is what settles the shape.

| element | finding |
| --- | --- |
| count | a **u32** at inventory `+0xE4`, which is `0x0300114C`. The add routine at `0x08004448` does `adds r0,#0xE4`, loads and stores that word, so it is four bytes wide and the value read live was 28 |
| entry | **one 4-byte word per item**, not eight. The same routine shifts the index left twice (`lsls r2,r3,#2`), which is a stride of four, then stores at `inventory + 0xE4 + 4 + index*4` |
| entry contents | the **top nibble is the wearer's index plus one**, or zero when nobody wears it; the **low 28 bits are the gear id**. The companion search at `0x08004468` also steps by four and tests that same nibble |
| where the entries end | 28 entries from `0x03001150` end exactly at `0x030011BC`, which is 28 four-byte words |
| the observed transition | the operator equipped the bandana while an observer sampled every 30 frames. Read this one from the raw line of each snapshot: the observer's own per-row summary pairs adjacent entries, because it was written under the earlier 8-byte reading. | Between frame 1110 and frame 3210 exactly two bytes moved: the bandana's own word at `0x030011A4` went from `0x0000007E` to `0x1000007E`, and the word at `0x0300119C` went from `0x1000009E` to `0x0000009E`. The second is gear 158, "Diamond Amulet", which the equip removed. So an equip writes the new item's word and clears the previous wearer's word, and the count did not change |

The renderer `0x0801D988` reads the same table with a `lsls #3` before its `ldr [r0,#4]`, which
looks like two-column row indexing for display rather than a stride, so it is not evidence for
an eight-byte record and is not used as any here.

**Where this was measured.** The equip transition was read on the **canonical retail image**
(`940AD5F0…`) driven by the operator's completed save, not on this ticket's image, because the
run's own `inputs.json` records that digest. The id and the table arithmetic were read from
this ticket's image. Neither claim is transferred to the other.
**The remaining gap is the call site, not the id or the writer.** A grant must go through the
game's own routine at `0x08004448`, which takes the inventory pointer and an id, refuses
silently at 250 entries, increments the count and stores `id & 0x0FFFFFFF` with a zero wearer
nibble. A raw write following the shape above would work only if it also reproduced that
routine's other effects, so this record does not propose one. What is not located is the
new-game initialization path that seeds the inventory, so a call site cannot be chosen from
evidence. Two bounded routes to it:

1. Trace the writer that stores the count at inventory `+0xE4` on a new game. The save-block
   base pointer `0x03001068` sits as a literal at file `0x6B7080`, immediately before the
   experience threshold table at `0x6B7084`, and exactly one code site in the image loads that
   word as a Thumb literal: `0x0804819A`. That site is in the seeding path and is where the
   trace starts.
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
