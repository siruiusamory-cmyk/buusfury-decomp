# SPRITE-NEW-RECORD-RUN-001: is the controlled actor a member of a record run?

Runtime record. Baseline `origin/master` =
`7ce5b7bdfba64de2d264305e9df878709167abcc`. Ticket worktree
`C:\Dev\log1-remake-sprite-new-record-run-001`, branch
`ticket/sprite-new-record-run-001`. Canonical image read-only throughout
(`940ad5f0...36f059e`).

This ticket tests the hypothesis SPRITE-NEW-RUNTIME-001 left open: that the new
actor never moved because it was authored as a *lone* record instead of as a
member of the same contiguous record run the surrounding retail actors occupy.

## Verdict

The model is falsified, and the closing acceptance section below carries the
verdict line. Cui does **not** wander, and the reason is not the run. Map 102's
entire record run was relocated above EOF with its internal pointers rebased and
the new actor's record appended to it as a contiguous member, with its own
behaviour record immediately following, in a run the engine demonstrably walked
(all seven retail behaviour objects were rebuilt at their relocated addresses).
The new actor's behaviour was still not dispatched.

## 1. The retail run, reconstructed

Measured from the canonical image and confirmed at runtime by this ticket's
observer on a cold boot (`rr001b-retail`, `rr005-retail-table`).

| Quantity | Measured |
| --- | --- |
| map 102 `MapEntry` | rom `0x0808F930`, file `0x08F930` |
| `+0x04` object count | **10** |
| `+0x14` object array | `0x080784B4` |
| `+0x2C` second base | `0x0807830C`, which is `0x10` before the first record |
| next map's `+0x2C` base | `0x08078584`, so the slice is 632 bytes |

The ten records the array names are contiguous in the image, but the stride is
**not** a uniform `0x2C`:

| slot | record | stride to the next |
| --- | --- | --- |
| 0 to 5 | `0x0807831C` .. `0x080783F8` | `0x2C` |
| 5, 6 | `0x080783F8`, `0x0807841C` | `0x24` |
| 7, 8, 9 | `0x08078440`, `0x0807846C`, `0x08078498` | `0x2C`, `0x2C`, end |

The reason for the two short strides is the record's own shape, which the
records state themselves:

- a **`0x1C`-byte header**: `+0x00` factory `0x08017DA3`, `+0x04` flags,
  `+0x08` position (u16 x, u16 y), `+0x0C` data pointer, `+0x10` sprite id,
  `+0x14` constant 1, `+0x18` a pointer to the previous member's behaviour;
- immediately after it, a **behaviour record** whose size its own leading word
  defines: `0x10` bytes for factory `0x0800A7A1`, `0x08` for `0x0800A223`.

So a run member is a header plus its behaviour, and the stride is `0x1C` plus
that behaviour's size. Slot 9 is `0x1C` long because the object array follows
it, which is why its `+0x1C` word is `0x0807831C` and not a factory.

## 2. The constructor does NOT receive `record + 0x1C`

This is the correction that decides the ticket. The behaviour constructor
`0x0800A7A0` is reached with a pointer that is `record + 0x1C`, but **not from
the walker that names the record**:

| walker | caller address | argument | reached at runtime |
| --- | --- | --- | --- |
| map object array loop `0x08008C9E` | `0x08008CC5` | `r0 = P`, the record itself | 10 of 11 slots |
| behaviour dispatcher `0x0800A95A` | `0x0800A9AA` | `r0 = P + 0x1C` | 7 records |

The array loop is `ldr r0,[r6,#4] ; bl 0x08004784` as a guard, then
`r2 = *(P)` and `bl _call_via_r2` with `r0 = P`. It never touches `P + 0x1C`.

The dispatcher is a round-robin over a per-actor state block:

```text
0x0800A95A  ldr r0,[r4]        ; current node
            ldr r1,[r0]        ; the node's class pointer
            ldr r2,[r1,#8] ; adds ; bl _call_via_r4  ; a step method
0x0800A98E  ldr r0,[r4,#8]     ; the table
            ldr r2,[r0]        ; table[0] = count
0x0800A99A  ldrsb r1,[r4,#4]   ; index
0x0800A9A0  ldr r0,[r0,#4+4*i] ; the entry
0x0800A9A4  ldr r2,[r0]        ; *(entry), the behaviour's class word
0x0800A9A6  bl _call_via_r2    ; r0 = the entry
0x0800A9AA  str r0,[r4]        ; current = result
```

and it is called from `0x08011198`, which is `adds r0, obj, #0x1B0` then
`bl 0x0800A95A` with `r1 = obj`. So the block lives at `actor + 0x1B0` and the
table is `+0x08` inside it. `CONFIRMED` statically; the caller address
`0x0800A9AB` is `CONFIRMED` at runtime in every run.

**What the table contains is `UNKNOWN`.** A breakpoint on `0x0800A95A`, and one
on `0x0800A9A4`, each reported **zero hits** in sessions where five other
breakpoints on the same emulator all produced data, in every registration order
tried (first, last, and with only two breakpoints armed). By section 8 of
`docs/skills/mgba-runtime.md` that is the "silent, silent" row for the table and
is **not** a negative: the table's membership is stated here from the
disassembly and from which pointers were handed over, and nothing more.

## 3. Which neighbouring bytes each actor reads

For every retail slot, the pointer handed to `0x0800A7A0` is `P + 0x1C` and the
handler reads only forward from it:

```text
0x0800A7C2  ldr  r1,[r5,#4]     ; r5 = P+0x1C, so P+0x20
0x0800A7CC  ldrh r0,[r5,#8]     ; P+0x24   \
0x0800A7CE  ldrh r1,[r5,#0xa]   ; P+0x26    |  copied to the actor's
0x0800A7D0  ldrh r2,[r5,#0xc]   ; P+0x28    |  +0x48..+0x4F
0x0800A7D2  ldrh r3,[r5,#0xe]   ; P+0x2A   /
```

So an actor reads exactly its own `0x1C`-header's successor record, and the
four halfwords at `P+0x24..P+0x2A` that the retail records carry. It never reads
backwards into a neighbour and never reads past its own behaviour record. The
`+0x18` chain (`P_i + 0x18 = P_{i-1} + 0x1C`) is present in every member and is
rewritten consistently when the run moves, but no code path observed here reads
it.

**Is a lone cloned record with padding structurally invalid?** Not by itself.
SPRITE-NEW-RUNTIME-001's clone at `0x08801F38` is a byte-complete `0x2C` member -
header plus behaviour, `+0x1C = 0x0800A7A1` - differing from its donor only in
position and sprite id. Its structure is well formed. What it lacks is
membership of whatever the dispatcher walks.

## 4. The experiment

`tools/research/sprite_new_record_run.py` builds SPRITE-NEW-RUNTIME-001's image
(`build_experiment(target="new-actor")`, reproducing its recorded build digest
exactly) and then moves the run:

| step | value |
| --- | --- |
| run prefix copied byte for byte | image `0x0807830C .. 0x080784B4`, 424 bytes |
| internal names rebased | the ten `+0x18` words and slot 0's `+0x04` |
| the Cui pair appended | at run `+0x1A8`, header plus behaviour, 44 bytes |
| object array re-emitted | 11 words, first ten the relocated records |
| `MapEntry+0x04` | 10 to 11 |
| `MapEntry+0x14` | `0x080784B4` to `0x08802148` |
| `MapEntry+0x2C` | `0x0807830C` to `0x08801F74` |
| `+0x10`, `+0x68`, `+0x6C` | **untouched**: the slice tail stays canonical |
| new record | sprite id 307, position (209, 580), donor rect and handler |

The slice tail was deliberately not moved, so the change is bounded to the
object run and the array and the two MapEntry fields that name them.

Inbound references into `[0x0807830C, 0x08078584)` were censused at every byte
alignment: 31 4-byte-aligned words, of which two are MapEntry fields that moved
with the run, 20 are the run's own internal names, 5 are the tail's own internal
names, three are the MapEntry fields kept canonical, and one is a cross-slice
word at `0x08078590` that was left alone. Five unaligned hits are byte noise.

## 5. What happened at runtime

Both arms ran the same built-in control, which is what makes the result
attributable.

| | retail canonical | runtime build `29f9195a` | this build `54e4541b` |
| --- | --- | --- | --- |
| array count / base | 10 / `0x080784B4` | 11 / `0x08801F0C` | 11 / `0x08802148` |
| `+0x2C` | `0x0807830C` | `0x0807830C` | `0x08801F74` |
| object slots visited | 10 | 11 | 11 |
| factory calls | 9 | 10 | 10 |
| sprite resolutions | 9 | 10 | 10 |
| **behaviour objects built** | **7** | **7** | **7** |
| new record's sprite id resolved | - | 307 | 307 |
| new record's behaviour dispatched | - | **no** | **no** |

Retail, the seven behaviour objects built are `P+0x1C` for slots 0, 1, 2, 3, 4,
7 and 8, and all seven move.

Baseline: the clone at `0x08801F38` is visited by the array loop and its
identity resolves - sprite 307 to character structure `0x08801C68`, measured at
`0x08017DB0`, the instruction after the registry accessor returns inside the
sibling factory. This is the sibling-family identity evidence
SPRITE-NEW-RUNTIME-001 never captured. Its behaviour pointer `0x08801F54` is
never handed over, so no behaviour object exists for it and it cannot move.

Variant: all ten relocated records are visited and **all seven retail behaviour
objects are rebuilt at their relocated addresses** (`0x088020F0`,
`0x088020C4`, `0x08802050`, `0x08802024`, `0x08801FF8`, `0x08801FCC`,
`0x08801FA0`). The run relocation is therefore sound and the engine is walking
the relocated run. The appended pair's behaviour pointer `0x08802138` is
**still not handed over**.

That is the falsification. Contiguity inside the same run is neither necessary
nor sufficient: the baseline already had a structurally complete `0x2C` member,
and the variant put it inside the run the engine walks, and the dispatch set did
not change in either.

## 6. The next smallest observed fact

The behaviour is reached only from the dispatcher at `0x0800A95A`, through the
count-prefixed pointer table at `[actor+0x1B0+0x08]`. Membership of that table
is decided independently of the object array: adding an array slot and adding a
contiguous run member both left the dispatched set at exactly the seven retail
records.

So the smallest next step is not another run layout. It is to find what enters a
pointer into that table - the routine that builds `[actor+0x1B0]` - and whether
an authored record can be entered into it. `0x0800FD74` is called from
`0x080110D8` with `(actor, structure, 0x03001B0C, P+0x14, P+0x08)` and is the
first place to read.

## 7. Instrument errors worth recording

1. **A breakpoint site that reports nothing while five others work.** Both
   `0x0800A95A` and `0x0800A9A4` produced zero hits across four sessions and
   every registration order, including with only two breakpoints armed. Their
   liveness control could not settle it in the saved-state run, because a
   construction-time breakpoint is silent by construction after a state load -
   the "silent, silent" row, which proves nothing. The dispatch table is
   therefore `UNKNOWN` and is reported as such rather than as a negative.
2. **A regex prune of the allowlist also matched the confinement roots.**
   `$allowedReadyRoot` and `$allowedMarkerRoot` are built with the same
   `Join-Path $workspaceRoot 'build'` shape as an allowlist entry. A prune
   removed them, leaving `$allowedReadyRoot =.TrimEnd('\') + '\'`. The file
   still parsed and the confinement check silently compared against an empty
   root. `tests/unit/test_mgba_runtime_skill.py` now pins both.
3. **`Set-Content -Encoding utf8` wrote a BOM** and broke line 1 of a `.lua`,
   and separately of a `.ps1`, in this session. Patch with `edit`; verify the
   first bytes after any whole-file write.

## 8. Enforcement added by this ticket

The mGBA runtime rules previously existed only as an untracked machine-local
file, absent from every ticket worktree, which is why they were missed here.

- `docs/skills/mgba-runtime.md` is now the tracked authority, named from
  `docs/DEVELOPMENT.md` under "Runtime evidence" as mandatory.
- `.claude/skills/mgba-runtime/SKILL.md` is now a pointer to it.
- A SessionStart hook (`~/.dsh/hooks/mgba-runtime-order.mjs`, registered in
  `~/.dsh/hooks/dsh-hooks.json`) injects the authority's text at the start of
  any session whose working directory is inside a repository carrying it, and
  emits nothing elsewhere.
- `tests/unit/test_mgba_runtime_skill.py` enforces the checkable part: the
  authority exists and is named by policy; every allowlisted observer exists and
  writes no emulated memory; the injector can act after the observer loads,
  which is what makes a savestate-after-injection possible; and any script that
  passes `--script` still keeps the version and ROM-digest gates.
- The allowlist carried **eight paths that no longer existed**. That is not
  inert: a file later created at one of those exact paths would be accepted
  without review. They are removed.

## 9. Acceptance

- **Does Cui wander?** No, in both the runtime build and this one.
- **Does the new sprite identity still render?** The engine resolved sprite 307
  to character structure `0x08801C68` at runtime in both derivative arms, so the
  identity resolves and the actor is constructed. No screenshot was taken in
  this ticket; rendering itself was photographed by SPRITE-NEW-RUNTIME-001 and
  is not re-claimed here.
- **Did any retail actor regress?** No. The same seven behaviour objects are
  built, with the same types, and in the variant they are built at their
  relocated addresses, which is also the control that proves the relocation.
- **ROM and runtime evidence**: canonical `940ad5f0...` unchanged and
  re-verified; runtime build `29f9195a2f7ed9ebb7cf72188dad2d52fec1b5cd1dc7d819432fa2954f946529`
  (byte-identical to SPRITE-NEW-RUNTIME-001's recorded build);
  this build `54e4541ba352ec57e7e2fd3d75d0b5fc9f1d8eb767e3dc06dc007df8152d0f30`.
  Seventeen canonical bytes change: the runtime ticket's fourteen plus
  `0x08F95C..0x08F95E`. Runs: `rr001b-retail`, `rr002-deriv-baseline`,
  `rr003-retail-table`, `rr005-retail-table`, `rr006-run-variant`,
  `rr007-run-table`, `rr009-state-table`.

**PLACEMENT RECORD-RUN MODEL: FALSIFIED.**
