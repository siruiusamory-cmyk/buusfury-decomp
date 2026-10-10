# FRIEND-V3-PLAYTEST-BOOST-001 inventory initialization pass

Continues the merged work at `a6e4aba245055dabe4fd46d2646cc0e1c32e5e82` (MR !170). The image
under test is unchanged at
`acd98c2ac90907ae0d83e78019c19b9b26001a49bc28e8bd436da7be9b4bb48c`. No new ROM was produced
in this pass, because the one remaining requirement is not yet located; that is stated as a gap
rather than filled with an invented patch.

## 1. What this pass established

The whole inventory module is now mapped, by disassembling it and by reading the live game.
All of the following is MEASURED on the delivered image.

| element | finding |
| --- | --- |
| count | u32 at `inventory + 0xE4`, which is `0x0300114C` |
| entry array | begins at `inventory + 0xE8`, which is `0x03001150` |
| entry | **one 4-byte word**. Low 28 bits are the gear id. The top nibble is zero when the item is held and unworn, and is the wearer's index plus one when worn |
| example, held | the operator's bandana sits at `0x030011A4` as `0x0000007E`: id 126, unworn |
| example, worn | after the operator equipped it the same word reads `0x1000007E`, and the item it displaced at `0x0300118C` went from `0x1000009E` to `0x0000009E` |
| capacity | `0xFA` (250). The add routine refuses silently at that count |

The module's routines, each disassembled here:

| address | role |
| --- | --- |
| `0x08004448` | **add.** `adds r0,#0xE4`; loads the count; refuses at 250; stores count+1; `lsls r2,r3,#2`; stores `id` masked to 28 bits at `+4+index*4` |
| `0x0800446C` | **remove.** Finds the first unworn entry for an id, decrements the count, shifts the remaining entries down |
| `0x080043C2`, `0x080043D8` | per-character block accessors: `ldrb r1,[r0]` then `muls r1, #0x68`, the stride confirmed elsewhere |
| `0x080043EE` | counts how many entries match an id, optionally filtered by wearer |
| `0x0800441E` | returns the index of an id, or a not-found value |
| `0x08004544`, `0x080045C8`, `0x08004656`, `0x080046F4` | further inventory and per-character operations |

The add routine has exactly five callers: `0x0800D758` (an item drop, matching the previously
recorded runtime id `0x74`), `0x0801F5E8` and `0x0802327C` (the script families), `0x08031CF4`
(a shop purchase), and one early-bank site. The seeding of the count itself is **not** in this
module and was not located.

## 2. What is still missing, exactly

The new-game initialization writes the count at `inventory + 0xE4` and then seeds whatever
entries a new game starts with. That write site has not been found. Two reasons it is not yet
found, stated so the next step is not a re-derivation:

1. The count is reached as a constant offset from the save-block base, so it carries no literal
   of its own: `0x0300114C` appears as no word in the image. A search for the address finds
   nothing.
2. The save-block base `0x03001068` appears as a word at 41 aligned offsets, and the only Thumb
   PC-relative literal load of that value is at `0x0804819A`, which reads a copy at file
   `0x481A4` in the early bank, not the pool word at `0x6B7080`. A pointer-chained seeding
   routine would not be visible to a literal scan at all.

## 3. The one next step, and it is cheap

A runtime watch on the first count transition of a genuine new game. Everything needed is
built: `tools/runtime/boost001_inventory_watch.lua` already logs the count every 30 frames and
dumps the whole inventory window whenever it changes, and the launcher
`tools/runtime/start_friendv3_coldboot_session.ps1` starts an emulator and gets out of the way.

The minimal human action, once such a session is armed: **start a new game and play until the
first menu appears.** Creating the save is the event; no playthrough is needed. The observer's
first snapshot after that shows the seeded count and the seeded entries, and the seeding writes
themselves are then found by watching what changed.

A note for that run: the observer's per-row `first`/`second` summary in `snapshot_*.txt` pairs
adjacent entries, because it was written under an earlier reading. **Read the raw line**, which
is the 1024 bytes from `0x03001068`, and take the count from `+0xE4` and the entries from
`+0xE8`, one 4-byte word each.

## 4. Unchanged and still true

- The image `acd98c2a` and its build pipeline are untouched. `build/fv3boost001/build.ps1`
  reproduces it.
- The canonical ROM re-hashes unchanged.
- No gate bypass was written. Nothing measured shows a gate that level 200 fails.
- The superseded `6d7a56c6` stays recorded as the first baseline.
- Full-campaign stability remains unverified and owner-driven.
