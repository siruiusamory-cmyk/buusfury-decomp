# TOOLKIT-033 - One gameplay-effect native handler

Status: **CONFIRMED_ROM + LEVEL 4 runtime** (2026-09-10).

This is intentionally one narrow authoring bridge, not a native-handler census.
Discovery stopped when slot 178 satisfied the ticket.

## EXTERNAL / EXISTING BEHAVIOR TARGET

The existing project already established that Buu VM native slot 178 renders
verified UTF-16 text as centred OAM sprite text, and that canonical tournament
dialog 290 supplies text 1525 (`Match 2 Fight!`) at X=120, Y=65
([BUU_DIALOG_RUNTIME.md](BUU_DIALOG_RUNTIME.md):115-230). No new table search or
unrelated handler reconstruction was needed.

External corroboration was deliberately modest rather than load-bearing. The
[GameFAQs walkthrough](https://gamefaqs.gamespot.com/gba/920530-dragon-ball-z-buus-fury/faqs/37901)
describes the late-game tournament as a numbered run of ten fights ending with
Hercule. That establishes the player-recognisable context for canonical strings
`Match 2 Fight!` through `Match 9 Fight!`; the ROM and runtime remain the ground
truth for handler identity, argument order and rendering.

## WHY THIS HANDLER IS A GOOD FIRST TARGET

- It already had one measured canonical use and a complete static consumer
  chain; no speculative native name was needed.
- The call has three literal arguments with order proven from handler pops.
- It creates a short-lived visual overlay with no HP, inventory, save, warp or
  permanent-story mutation.
- A/B discrimination is direct: the banner is either present in the captured
  frame or absent.
- Reloading the map/state reverses the effect.

## Narrow semantic contract

`show_centered_sprite_text(text, x, y)` expands only for verified Buu profile
`buus_fury_usa_rev0_01c1707f` to:

```text
push_many 3 <text-index> <x> <y>
native_stack 178
```

The claim is no broader than: **native slot 178, given a verified Buu text-table
index followed by X and Y, creates centred sprite text at that coordinate.** It
is not called a general dialog API, and no lifetime or queue semantics are
claimed.

## STATIC

- Primary opcode `native_stack` is `0x02`, whose handler is raw pointer
  `0x08003CBF` / entry `0x08003CBE`; the secondary operand selects one of 283
  native slots ([BUU_SCRIPT_VM.md](BUU_SCRIPT_VM.md):34-75).
- Native slot 178 is table pointer `0x08003031` / entry `0x08003030`. It pops
  three values; the deepest becomes the text-table index and the other two are
  passed as coordinates ([BUU_DIALOG_RUNTIME.md](BUU_DIALOG_RUNTIME.md):115-178).
- Worker `0x0802BFBC` indexes text table `0x0806BCE8`, measures UTF-16 text,
  centres on X and emits OAM sprite text ([BUU_DIALOG_RUNTIME.md](BUU_DIALOG_RUNTIME.md):139-210).
- Canonical dialog 290 contains the unique exact invocation subsequence at ROM
  file `0x0078B5A7`:

  ```text
  1D 03 97 6A 81 70 81 02 02 B2
  push_many(3, 1525, 120, 65); native_stack(178)
  ```

- The authored project source is:

  ```text
  show_centered_sprite_text text:1525 120 105
  terminate
  ```

  Production bytes at `0x007EA428` / runtime `0x087EA428` are exactly:

  ```text
  1D 03 97 6A 81 70 81 52 02 B2 11
  ```

  That 11-byte body occurs **zero** times in canonical Buu and once in the
  authored output.

## Production allocation and build

The allocator measured the complete demand inside verified region
`[0x007EA400,0x007EA500)`:

| Body | Offset | Bytes |
|---|---:|---:|
| authored placement | `0x007EA400` | 32 |
| authored descriptor | `0x007EA420` | 8 |
| authored script | `0x007EA428` | 11 |
| expanded five-slot array | `0x007EA434` | 20 |
| **total payload demand** | | **71** |

The highest occupied byte ends at `0x007EA448`, leaving **184 bytes**. Alignment
adds one unoccupied byte between script and array. The descriptor bytes are
`1F 42 00 08 28 A4 7E 08`, so its handler is the verified script trampoline and
its payload is this authored script.

Two production builds were byte-identical. Authored output SHA-256 is
`bbd0bbbe1f01b4d715b89bb20a22f63276e36ec4fd2dc443e34ae3b99880ff35`;
**75 bytes** differ from canonical, limited to the four allocated bodies plus
the map entry's derived count/relocated-array fields. A production no-op build
is byte-identical to canonical.

## OBSERVED

### Canonical-invocation positive control

The control body used the exact canonical dialog-290 argument sequence
`[1525,120,65]` followed only by termination. At frame 1250:

```text
descriptor 0x087EA420 -> script 0x087EA428
handler pc 0x08003032
stack depth 3; arguments 1525, 120, 65
```

At frames 1255 and 1265 the captured screen visibly contained the centred
banner **MATCH 2 FIGHT!** at the higher canonical Y coordinate. This replays the
canonical invocation without importing dialog 290's many unrelated native
calls. The control ROM SHA-256 is
`c78cfaa077dd45b8c4c3df70d7c56d21dfff19574ace20becf7ec1edc7b6e448`.

### Authored build

At frame 3111 on active map 40, the corrected final replay captured the complete
chain. The native observer reads the engine's live operand cursor through `[r1]`
at `0x08003CC0`, and accepts the slot handler only when it immediately follows
that authored-frame dispatch:

```text
pc 0x08004220  descriptor 0x087EA420 -> payload 0x087EA428
pc 0x0800403A  authored cursor 0x087EA428
pc 0x08003CC0  live native_stack operand cursor 0x087EA431 -> slot 178
pc 0x08003032  slot-178 handler; depth 3; args 1525, 120, 105
```

At frame 3116 the captured game screen visibly contained **MATCH 2 FIGHT!**
centred at the intentionally changed Y=105 position. The image was inspected at
native 240x160 resolution; SHA-256 is
`637e154e16ad10f5fb4c8a7df052eefd4fca4328e38fd17cd2b7f217333ccc1b`.

**FIRSTHAND USER OBSERVATION:** the maintainer directly confirmed that he saw the text on
screen during this final corrected run. This is recorded separately from the
automated screenshot and breakpoint channels rather than substituted for them.

### Negative control

The negative retained the same authored entity and literal setup but replaced
the native invocation with three pops:

```text
1D 03 97 6A 81 70 81 52 14 14 14 11
```

At frame 1719 its authored descriptor and script cursor both executed. Slot 178
was never reached. Screenshots at frames 1720, 1724 and 1734 contained ordinary
gameplay and **no MATCH 2 FIGHT! banner**. The matched `+5` image SHA-256 is
`2042e1a60d7cbd66b3dcd6f21df05e0a2ab99005767ac5edde25e4914850000b`;
control ROM SHA-256 is
`12d5b99ed6ed0273bdc0fafbd9f28c32388d58d4a4f2de2bafeb792038003632`.

## INFERRED / not claimed

- The inherited placement trigger remains intermittent and gameplay-driven;
  its gameplay meaning and schedule are still **UNKNOWN**.
- Slot 178's broader ownership, queueing and lifetime behavior are not claimed.
- Reusing an existing text record is intentional; this ticket authors new
  behavior, not new text content.
- This proves one useful native invocation, not arbitrary gameplay scripting.

## Result and next blocker

> **GAMEPLAY-EFFECT NATIVE SEMANTIC: YES**
>
> **RUNTIME-PROVEN OBSERVABLE AUTHORED BEHAVIOR: YES**

The next measured blocker is control of **when** authored behavior runs. The
effect and invocation are intentional, but the attached canonical trigger is
still inherited and intermittent. The next authoring step is a deterministic,
SDK-authored trigger or schedule for the authored script; no work on that step
belongs to TOOLKIT-033.

The canonical ROM remained
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`
and the source savestate remained
`2d5740a8c54180d153024a11b0e4d1143306957af55a3ad0664c71cf7d9a1aab`
before and after every runtime channel.
