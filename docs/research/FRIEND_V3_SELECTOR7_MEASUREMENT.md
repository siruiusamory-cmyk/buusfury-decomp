# Selector-7 overflow measurement

The coordinator asked whether the dialogue overflow could move to a spare container selector,
lifting the 15-bit decoded-start ceiling without an engine change. **Answer: NO**, on all
three parts, measured on `v3-mainline-text-dialogue-pass-wt.gba`.

Read-only probe: `build/fv3text001/selector7_probe.py` (ignored tree).

## a. The seventh slot exists but is not a container

The live table is at file `0x9A9CE8`, named by the literal at file `0x123CC`. Its first
twelve slots:

| slot | word | verdict |
| --- | --- | --- |
| 0 | `0x0894A020` | kind 0, declared 65348 |
| 1 | `0x08959F6C` | kind 0, declared 65474 |
| 2 | `0x08969F38` | kind 0, declared 65464 |
| 3 | `0x08979EF8` | kind 0, declared 65334 |
| 4 | `0x08989E38` | kind 0, declared 65322 |
| 5 | `0x08999D6C` | kind 0, declared 65394 |
| 6 | `0x087B5AA0` | kind 1, declared 436 |
| **7** | **`0x03004A68`** | **not a ROM pointer: IWRAM** |
| 8 | `0x03000FB0` | not a ROM pointer |
| 9 | `0x03003300` | not a ROM pointer |
| 10 | `0x03003898` | not a ROM pointer |
| 11 | `0x03004A8C` | not a ROM pointer |

So the table holds **seven** live containers, as `handles.py:99-103` records, and the slots
after them are not table entries at all: they are IWRAM addresses belonging to whatever data
follows the seven words. A record given selector 7 would load `0x03004A68` as its container
base, which is not a ROM container.

**Is selector 7 used by any handle in script data?** A scan for the record-word pattern finds
nine words whose low six bits are 7, and small counts for selectors 8 to 27. Those are not
dialogue records: a real handle must name a container the table resolves, and no selector
above 6 does. They are pattern coincidences in non-dialogue data, which is the same class the
inventory's own docstring warns about.

## b. The engine's table access is unbounded, but the table is not

The selector is isolated and scaled at `0x08012240`:

```
0x08012240  6868   ldr r0,[r5,#4]      ; the packed handle
0x08012242  4962   ldr r1,[pc,#0x188]  ; 0x080728AC, the table base
0x08012244  0680   lsls r0,r0,#0x1A    ; selector bits to the top
0x08012246  0E00   lsrs r0,r0,#0x18    ; selector * 4
0x08012248  5808   ldr r0,[r1,r0]      ; container base, NO BOUNDS CHECK
0x0801224C  F02B   bl 0xFB78F02B       ; veneer -> the child at 0x0801227E
```

The access is a plain scaled load with no comparison against a count, so the engine would
happily read slot 7. It would read an IWRAM address, and the child routine's container reads
would then come from IWRAM rather than the ROM. **Indexable but not usable**: there is no
spare ROM container slot behind the table to point at.

## c. What an overflow move would cost, if a slot existed

Handle sites per container, from the engine's own inventory: selector 0 has 723 sites over
526 records, 1 has 483/448, 2 has 516/466, 3 has 429/422, 4 has 498/486, 5 has 476/460, 6 has
6/6. No record in any container currently sits beyond start 65,534, because none can.

For the overflow to be reachable, every record whose start exceeded 65,534 would need its
selector changed in **every** handle word that carries it, and those words live in script
data the engine reads. The count is bounded by the sites in the affected container: up to 723
words for container 0. That is a data edit, and the existing tooling can address handle words
in place, but there is no free selector to move them to, so the edit has nothing to point at.

## Verdict

**NO.** The seventh slot is not a container, no slot above 6 is, and the only way to obtain a
container there is to point slot 6 or 7 at new space and then give records selector 6 or 7.
That is possible as a data edit, but selector 6 already names a live container with 51 handle
words referring to it, and creating an eighth container means the *container* is available
while the record's own **start field still cannot address past byte 65,534**. Moving records
into a fresh container resets their offsets only if the container they move to holds those
records within its first 65,534 bytes, and the duplication repair needs 128 KB in container 0
alone. The ceiling is a property of the handle word, not of the number of containers.

The 03:00 split therefore stands unchanged.
