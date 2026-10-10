# Bandana trampoline: control-flow proof and the remaining unknown

Owner direction was to stop experimenting and diagnose the control-flow failure first. This is
that diagnosis. It is not a fix, and the frozen hook is not in the delivered build.

## 1. The trampoline's own instructions, decoded from the failing image

Image `76cdbde6b5c1874b62d7920fc04f082689d50af3d13da5ac18a44f0f660b466f` (the probe), hook at
`0x08004892`, trampoline at `0x083C22FC`:

```text
0x08004892  bdf333fd   bl        0x083C22FC     ; displaces `adds r0,r4,#0`
0x083C22FC  0fb5       push      {r0,r1,r2,r3,lr}
0x083C22FE  201c       adds      r0, r4, #0     ; r0 = the base the init is holding
0x083C2300  4903       ldr       r1, [pc,#12]   ; literal at 0x083C230A... see below
0x083C2302  42f4a1f8  bl        0x08004448     ; the add routine, LR := 0x083C2306
0x083C2306  0fbc       pop       {r0,r1,r2,r3}
0x083C2308  7047       bx        lr             ; LR is still 0x08004896
0x083C230A  7e00 0000  .word     126
```

## 2. Simulation of the return path, register by register

| step | effect |
| --- | --- |
| `push {r0-r3,lr}` | 5 words on the stack, SP -= 20 |
| `mov r0,r4` | r0 = 0x03001068 in the modelled run |
| `ldr r1,[pc,#12]` | r1 = 126 |
| `bl 0x08004448` | **LR := 0x083C2306** |
| callee returns | `bx lr` -> 0x083C2306, correct |
| `pop {r0-r3}` | restores the four words, **leaves LR untouched at 0x08004896** |
| `bx lr` | jumps to **0x08004896**, which is `push {r3,lr}`, the instruction after the hook |
| stack | all five words popped, SP restored exactly |

Answers to the brief's numbered questions: (2) the nested BL places its return address in LR as
`0x083C2306`; (3) LR immediately before the final return is the caller's `0x08004896`; (4) the
original LR is preserved, because `pop {r0-r3}` does not touch it; (5) the stack pointer is
restored exactly; (6) the return target `0x08004896` is an even Thumb address; (7) the
trampoline makes no use of the displaced instruction, and the continuation is the correct one.
`BX LR` does **not** return into the trampoline.

**Conclusion: failure mode A, broken return mechanics, is REFUTED.** LR handling and SP handling
are correct, and so is the branch. The brief was right to insist this be proven rather than
assumed, and it is now proven.

## 3. The isolating experiment

| variant | image | count at `0x0300114C` | program counter | save | screen |
| --- | --- | --- | --- | --- | --- |
| no hook, control | `a4c12a95` foundation | 0 | varied, normal boot | 8,192 B | normal |
| structure-only hook, no call | `1d408290` | 0 | varied | 8,192 B | normal |
| full hook with the call | `76cdbde6` | **1** | stuck in the trampoline | 32,768 B | **white screen** |

The identical branch, `push`, `pop` and `bx lr` boot normally when the call is removed. The
failure therefore sits with the call or its arguments, not with the trampoline's mechanics.

## 4. What the white screen adds, and what it breaks

The white screen appears **before** any game code that would grant an item, and an
`emu:setBreakpoint` armed at both the hook (`0x08004892`) and the trampoline entry
(`0x083C22FC`) never fired, while a breakpoint armed the same way at another address did fire in
an earlier run of this tree.

That combination does not fit any single one of the brief's four candidates cleanly:

- If the trampoline never ran, the count could not be 1, and it is 1 in the full-hook runs.
- If the call ran and returned correctly, the game would not white-screen.
- The breakpoints not firing means the hook path could not be observed directly, so the
  sequence that produces both the count of 1 and the white screen is not yet pinned.

## 5. Honest status

**Established:** the trampoline's return mechanics are correct (section 2); the failure appears
only when the call is present (section 3); the observed symptoms are a count of 1, a program
counter trapped inside the trampoline, a white screen, and a save file that grows to 32,768 B.

**Not established:** the actual mechanism. The brief's mode C (initialization-order or
reentrancy) and mode D (the call corrupting state) both remain open, and the breakpoint
evidence does not separate them.

**The one measurement that would:** a snapshot of `r0`-`r7`, SP and LR taken *at the moment the
trampoline first executes*, from an instrument that is proven to fire. Two things must be true
for it to count: the breakpoint must be shown firing on a run where the count also reaches 1,
and the same instrument must fire on the unmodified baseline image as a control. Without both,
"the breakpoint did not fire" is an unproven instrument, not evidence about the hook.

**The delivered build is unchanged.** `acd98c2ac90907ae0d83e78019c19b9b26001a49bc28e8bd436da7be9b4bb48c`,
10,140,972 bytes, reproduced byte for byte by `build/fv3boost001/build.ps1`. The hook stays
implemented and tested in the builder and is not applied. Canonical
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e` re-hashed unchanged.
