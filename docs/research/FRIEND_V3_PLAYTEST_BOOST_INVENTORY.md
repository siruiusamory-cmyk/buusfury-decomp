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

## 3. What the genuine New Game actually wrote, MEASURED

The owner started a real New Game on an erased save with the observer armed, and played for
about six minutes. Result, and it changes the picture:

| observation | value |
| --- | --- |
| the count at `0x0300114C` | **0** for the whole run: 1,163 samples from frame 30 to frame 34,890, never anything else |
| the entry array from `0x03001150` | all zeros in every snapshot |
| the only non-zero bytes in the first `0x120` of the save block | `0x03001069` (`+0x01`) = 2, and `0x03001113` (`+0xAB`) = 8 |

So a New Game **does not seed the count-and-entry inventory at all.** The starting items appear
somewhere else: as plain per-item **quantity bytes** at fixed offsets from the save block base,
which is the mechanism the external RAM map already describes for consumables
(`0x03001069` is Miso Soup Quantity). A new game therefore opens with 2 Miso Soup and nothing
else, and the item count stays 0 until something calls the add routine.

Two consequences, both useful:

1. The grant does not belong in the count-and-entry array on a new game. It belongs wherever the
   game writes that quantity byte, or in whatever hands out the first item.
2. Neither `0x03001069` nor `0x0300106A` has a Thumb literal loader anywhere in the image: they
   are reached as an offset from the save base `0x03001068`, whose only literal loader is
   `0x0804819A` reading the copy at file `0x481A4`. The seeding write is therefore reached
   through the base pointer, not through its own address, which is exactly why three address
   searches found nothing.

## 4. The one next step

Find the instruction that writes `2` to save-block `+0x01`, by tracing the one loader of the
save base. That instruction's routine is the seeding path, and the same path either already
writes other starting bytes or can take one more with the Miso Soup write's own shape. Two ways:

1. Static: follow `0x0804819A`'s function and its callers for a store at base `+0x01`.
2. Runtime: buy or obtain any item that is stored as a quantity byte and watch which byte moves,
   which shows the write shape directly.



## 5. The Bandana grant: built, proven to fire, and WITHDRAWN because it hangs

An experiment that reached its stated goal and still could not ship. It is recorded so the next
attempt starts here instead of repeating it.

**What was built.** The save-block init at `0x08004838` zeroes the equipment count and rebuilds
the per-character blocks. A Thumb hook replaced one instruction of that function so the game's
own add routine, `0x08004448`, appends gear id 126 once per fresh save block. The trampoline
lives in a 4,348-byte zero run at `0x083C22FC`, saves the registers it clobbers, passes the
save-block base from `r4` and the id from a literal, and returns with `bx lr`.

**What it achieved.** MEASURED on `00d814d5…`: the equipment count at `0x0300114C` read **1**
for every one of 277 samples from frame 30 to frame 8,310. The hook fires, once.

**Why it was withdrawn.** The game hangs. In the same run the program counter never left
`0x083C2308` and `0x083C230A`, both inside the trampoline, and the save file grew from 8,192 to
32,768 bytes. In game that is a freeze.

**The isolating experiment.** A structure-only variant of the same hook, with the identical
branch, the identical `push`/`pop`/`bx lr` and only the call removed, boots normally.

| variant | image | count | program counter | save |
| --- | --- | --- | --- | --- |
| no hook, control | `a4c12a95` foundation | 0 | varied, normal boot | 8,192 B |
| structure-only, no call | `1d408290` | 0 | varied | 8,192 B |
| full hook with the call | `00d814d5` | 1 | stuck in the trampoline | 32,768 B |

So the branch, the stack handling and the return are sound, and the failure comes from calling
`0x08004448` at that site or from its effect.

**What is not established.** Why the call fails. Two candidates the evidence does not separate:
`r4` may not hold the save-block base on every path into the init, and the save path may enter
the init only as a scratch-pointer provider and then overwrite the block. The datum that
separates them is a runtime read of `r4` at the hook, or a call from a site proven to be the
player's new game.

**Consequence for the deliverable.** The builder does not apply the hook, and the delivered
image is the stat-only `acd98c2ac90907ae0d83e78019c19b9b26001a49bc28e8bd436da7be9b4bb48c`.
The patch code stays in the builder and stays covered by tests so it cannot drift while it
waits for the missing datum.

## 6. Unchanged and still true


- The image `acd98c2a` and its build pipeline are untouched. `build/fv3boost001/build.ps1`
  reproduces it.
- The canonical ROM re-hashes unchanged.
- No gate bypass was written. Nothing measured shows a gate that level 200 fails.
- The superseded `6d7a56c6` stays recorded as the first baseline.
- Full-campaign stability remains unverified and owner-driven.
