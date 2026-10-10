# Bandana trampoline: the crash dialog found the bug, and the exact repair

Owner direction was to read the emulator's error dialog rather than theorise. That was the right
call: mGBA reported **"Jumped to invalid address: E129F004"**, and 0xE129F004 is not an address
the game ever builds, so the branch left through a register or a stack word that had already been
overwritten.

`acd98c2ac90907ae0d83e78019c19b9b26001a49bc28e8bd436da7be9b4bb48c` remains the delivered image
and the builder in this revision does not apply the hook. What follows is the defect list, each
one measured, and the repair specified exactly enough to implement without further guessing.

## 1. The defects, in the order they were found

| # | defect | how it was found |
| --- | --- | --- |
| 1 | **Five registers pushed, four popped.** SP ended four bytes low and the caller's LR was left on the stack. | owner inspection of the listed instructions |
| 2 | **The continuation was wrong.** BL is four bytes on two-byte instructions, so the hook swallowed `adds r0,r4,#0` *and* the first half of `b #0x800484e`. Returning to the byte after the hook lands inside the remains of that branch. | owner inspection |
| 3 | **A literal was unreachable.** Thumb's PC-relative base is `((here + 4) & ~3)`, so a literal is only reachable at a four-byte multiple from that base. `ldr r1,[pc,#12]` at `0x083C2300` reads `0x083C2310`, and the value written at `0x083C230A` was never read. | owner inspection, then confirmed by computing the address the instruction encodes |
| 4 | **The branch target was carried in a register the pop restores.** One version loaded the epilogue address into `r2` and then executed `pop {r0-r4,pc}`, which overwrote `r2` with the caller's old value. The branch left through a stale register. | the mGBA crash dialog |
| 5 | **A push/pop list mismatch.** `push {r0-r6,lr}` paired with `pop {r0-r6,pc}` is one register short on the pop side: the `pc` form's register-list bit 8 is the pc itself, so the list must be written to match. | disassembly of the emitted halfwords |

Defect 4 is the one that produced the invalid jump. Defects 1, 2 and 5 all corrupt SP or the
return path; defect 3 only misreads a constant.

## 2. The verified contract, which none of the defects concerned

`0x08004448` takes the save-block base in `r0` and the gear id in `r1`, refuses only at 250
entries, and stores `id & 0x0FFFFFFF` as one four-byte entry. Measured on the delivered image and
on live RAM: the count is a u32 at `0x0300114C`, entries are four bytes each from `0x03001150`,
the low 28 bits are the id and the top nibble is the wearer index plus one, zero when unworn.

The grant itself works: the hooked build wrote count 1 and entry `0x0000007E` (id 126, unworn)
before it crashed. That part is not in doubt.

## 3. The repair, specified

Trampoline, all offsets from its base:

```asm
    push {r0-r4, lr}          @ six words, the same depth init itself pushed
    mov  r0, r4               @ replays the displaced `adds r0,r4,#0`
    ldr  r1, [pc, #ID]        @ the gear id, from a literal at a reachable address
    ldr  r5, [pc, #RET]       @ the epilogue address
    push {r5}                 @ the sixth frame word, so the pop delivers it to pc
    bl   0x08004448           @ the game's own add routine
    pop  {r0-r4, pc}          @ six words popped, control to the epilogue
ID:  .word 126
RET: .word 0x0800484e
```

Rules the emitter must follow, each of which one attempt got wrong:

1. `pop {r0-r4, pc}` and `push {r0-r4, lr}` cover the same six words, so SP ends where the
   epilogue expects its own frame.
2. The branch target is pushed, never carried in a register that a pop restores.
3. Each literal is placed at `code_length` rounded up to four bytes, then `+4`, and the LDR's
   immediate is `(literal - ((here + 4) & ~3)) / 4`, which must be a whole number in 0..255.
   The emitter must compute this and refuse otherwise, which is what the corrected builder now
   does: `_ldr_literal` raises rather than emit a load that reads the wrong word.
4. The hook is a four-byte BL at `0x08004892`, so the displaced bytes are the two-byte
   `adds` **and** the two-byte `b`. Replaying only the `adds` is not enough, and the
   continuation is `0x0800484e`, the branch's destination, not `0x08004896`.

## 4. Honest status

The grant is implemented, the inventory contract is measured, the count and the entry were
observed correct on the hooked build, and the crash's immediate cause is known and repaired in
specification. What is **not** delivered is a hooked image that boots: the last hooked image
still crashed, because the register-carry defect (4) was present in it.

The delivered image stays `acd98c2a…`. The builder does not apply the hook, its tests pass
(9 passed), and the image reproduces byte for byte.
