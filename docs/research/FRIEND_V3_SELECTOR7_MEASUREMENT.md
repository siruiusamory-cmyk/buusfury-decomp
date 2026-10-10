# Selector and table-extension measurement

The coordinator asked whether the dialogue overflow could move to another container selector,
lifting the 15-bit decoded-start ceiling without an engine change. The measurements are sound;
**the verdict is UNPROVEN**, and this document names the route they point to.

Read-only probe: `build/fv3text001/selector7_probe.py` (ignored tree).

## Verdict correction: the table already lives in space we own

The first version said NO and conflated two different addresses. Resolved:

| image | literal at file `0x123CC` | resolves to |
| --- | --- | --- |
| canonical retail | `0x087B5B64` | file `0x7B5B64`, inside 8 MiB |
| pre-BOOST foundation and the release | `0x089A9CE8` | file `0x9A9CE8`, **expansion space past 8 MiB** |

The table is **already relocated into space this project owns**, and `0x080728AC` in the
disassembly is a *different* constant: the literal the parse sequence loads for the table base
at runtime, not the file literal that names the table. The relocation came from the rename
splice (`git log -S 0x123CC` names commit `4814d8a`, "Make a rename pay for itself inside the
name it changes"), which rewrites the single word naming the table. That is also why a
post-splice image must be read through `0x123CC` and never through the retail literal.

## The route the measurements point to: split an oversized container

The engine's table access at `0x08012240` is a plain scaled load with **no bounds check**:

```
0x08012240  6868   ldr r0,[r5,#4]      ; the packed handle
0x08012242  4962   ldr r1,[pc,#0x188]  ; the table base literal
0x08012244  0680   lsls r0,r0,#0x1A    ; selector bits to the top
0x08012246  0E00   lsrs r0,r0,#0x18    ; selector * 4
0x08012248  5808   ldr r0,[r1,r0]      ; container base, no comparison against a count
```

The selector field is 6 bits, 64 values, and the table already sits in space we own and can
extend. So an oversized container can be **split into two or more containers**, each holding
its records under the 65,534-byte start ceiling, with the overflow records given their own
selector and a start inside their new container. The ceiling is a property of the handle word
per container, not in aggregate.

That is a **data edit**: extend or append to the table, repoint it through the one literal at
`0x123CC`, and rewrite the affected handle words, which the existing tooling already addresses
in place. It is not an engine change, so it belongs to the successor ticket's first step
rather than behind one.

## What remains UNPROVEN, named

1. **Other readers of the table or its literal.** The parse sequence is measured, but no census
   establishes that `0x08012248` is the only site that indexes the table or that `0x123CC` is
   the only word naming it. A second site would have to honour an extended table too.
2. **What owns the bytes after the seven entries.** Slots 8 onward hold IWRAM addresses, so
   those words are not free, and whether the table can grow in place rather than move is not
   established.
3. **The handle-word count for a split.** Sites per container are measured, but whether records
   whose spans are shared or duplicated need handle words beyond those counts is not.
4. **Which records move.** Split boundaries must respect the overlapping-record property that
   `plan_group` proved is contradictory for some pairs, so a split inherits that analysis.

Until 1 to 4 are answered the route is **UNPROVEN**, and the 03:00 split stands: the successor
ticket starts with this route, and takes the engine change only if it is disproven.

## The measurements themselves

### The seventh slot exists but is not a container

The live table is the one the literal at file `0x123CC` names. Its first twelve slots on the
release image:

| slot | word | verdict |
| --- | --- | --- |
| 0 | `0x0894A020` | kind 0, declared 65348 |
| 1 | `0x08959F6C` | kind 0, declared 65474 |
| 2 | `0x08969F38` | kind 0, declared 65464 |
| 3 | `0x08979EF8` | kind 0, declared 65334 |
| 4 | `0x08989E38` | kind 0, declared 65322 |
| 5 | `0x08999D6C` | kind 0, declared 65394 |
| 6 | `0x087B5AA0` | kind 1, declared 436 |
| 7 | `0x03004A68` | **IWRAM address, not a ROM pointer** |
| 8 | `0x03000FB0` | IWRAM address |
| 9 | `0x03003300` | IWRAM address |
| 10 | `0x03003898` | IWRAM address |
| 11 | `0x03004A8C` | IWRAM address |

So the table holds seven live containers, as `handles.py:99-103` records, and the slots after
them are not entries: they are IWRAM addresses belonging to whatever data follows. A record
given selector 7 today would load `0x03004A68` as its container base.

A scan for the record-word pattern finds nine words whose low six bits are 7, and small counts
for selectors 8 to 27. Those are not dialogue records: a real handle must name a container the
table resolves, and no selector above 6 resolves today. They are pattern coincidences in
non-dialogue data.

### Handle sites per container

From the engine's own inventory on the release image: selector 0 has 723 sites over 526
records, 1 has 483/448, 2 has 516/466, 3 has 429/422, 4 has 498/486, 5 has 476/460, 6 has 6/6.
No record sits beyond start 65,534, because none can.
