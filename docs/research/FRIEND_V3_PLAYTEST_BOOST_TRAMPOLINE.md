# Bandana trampoline: the return path is fixed, and a visible menu defect remains

## 1. The delivered candidate

`6439085fa6c3f88ecf582b851290c0c43c487dd3ed49d30712ea06094f4a6563`, 10,140,972 bytes,
reproduced twice with identical hashes. It contains the stat boost and the Bandana hook.

The fallback `acd98c2ac90907ae0d83e78019c19b9b26001a49bc28e8bd436da7be9b4bb48c` is the stat-only
image. The canonical ROM is unchanged: `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`.

## 2. The trampoline, disassembled from the emitted bytes

```text
0x083c22fc  0449        ldr  r1, [pc, #0x10]   -> 0x083c2310 = 126
0x083c22fe  054d        ldr  r5, [pc, #0x14]   -> 0x083c2314 = 0x0800484E
0x083c2300  20b4        push {r5}              S-4 = the epilogue
0x083c2302  10b4        push {r4}              S-8 = the caller's r4
0x083c2304  201c        adds r0, r4, #0        r0 = the save-block base, for the call
0x083c2306  42f49ff8    bl   0x08004448
0x083c230a  201c        adds r0, r4, #0        replays the displaced instruction after the call
0x083c230c  10bd        pop  {r4, pc}
0x08004892  bdf333fd    bl   0x083C22FC
```

The frame mapping at the pop, which is the part that decides whether this works:

| slot | pushed by | holds | popped into |
| --- | --- | --- | --- |
| S-4 | `push {r5}` | 0x0800484E | r4? no: this is the FIRST register the pop reads, and that is r4 |
| S-8 | `push {r4}` | the caller's r4 | r4? no: this is the second word, and that is pc |

A pop reads its register list from the lowest address upward with the lowest register at the
lowest address, so the two single pushes are ordered to give r4 the caller's r4 and pc the
epilogue. Two earlier versions failed here: one pushed r4 then r5, which reversed the frame and
sent the caller's r4 to pc; the other returned through lr, which points at 0x08004896 inside a
different routine, because the displaced `b #0x800484e` went to 0x0800484E instead.

`adds r0, r4, #0` is replayed both before and after the call because r0 is live at the
continuation as this function's return value to its own caller.

## 3. Runtime result

| measurement | hooked image | unmodified foundation |
| --- | --- | --- |
| cold boot | reaches the title screen, 60 fps | reaches the title screen |
| equipment count at 0x0300114C | 1 | 0 |
| entry at 0x03001150 | 0x0000007E | 0x00000000 |
| save file size | 8192 | 8192 |
| main menu | **selection arrow glitched** | normal |

The control run is the important half: the same harness, the same fresh 8192-byte save, the
same foundation image with no hook, count 0. So the count of 1 and the entry 0x0000007E are
produced by this patch, and the menu defect appears with it.

## 4. The remaining defect

The observer samples the equipment count at frame 30 and reads 1, so the hook deposits its entry
during early boot, while the game is still initialising. The main menu selection arrow is then
visibly wrong. That is a real, externally visible defect and the candidate is not shippable with
it.

What is NOT the cause: the return path. The trampoline reaches the epilogue, SP is exact, r4 is
restored, and the game boots and draws its menu. What IS still open: the moment the entry is
deposited, and whether a deposit at that moment is what the menu is reacting to. The next
measurement is a breakpoint at 0x08004892 that records the frame and r0 at each call, which is
already written as `tools/runtime/boost001_hook_site_watch.lua`, plus a control that hooks the
same site and calls nothing, to separate "the hook fires here" from "the entry is written here".

## 5. Honest status

The control-flow error the review proved is fixed, and it is fixed by the review's own repair
direction: order the frame so the epilogue reaches pc. The game now cold-boots to its title
screen at full speed with the correct inventory entry in the save.

Not delivered: a shippable image. The menu defect is visible and unresolved.
