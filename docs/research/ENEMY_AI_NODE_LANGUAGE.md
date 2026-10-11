# The enemy AI node language

Read from the canonical image, byte by byte. Every address below is a GBA address; the file offset is that
address minus `0x08000000`. Canonical ROM sha256
`940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E`.

This document is the durable result of the AI research. Where an earlier note was wrong, the correction is
stated rather than quietly folded in, because a wrong model of this language produces a boss that stands
still.

## What the language is

The AI is a TREE PER ROW. A stat record's `+0x08` is a selector; the dispatcher computes
`row = 0x0870F514 + 8*selector` and reads two words. The table holds 828 rows, exactly two words in the image
name it (`0x0800AB50`, `0x080192AC`), and there is no bounds check.

A ROW is:

| offset | meaning |
| --- | --- |
| `+0x00` | PRIMARY node: the tree the state path runs |
| `+0x04` | SECONDARY node: the tree the node path evaluates |

All 828 rows carry both. Measured secondary handlers: AUX `0x08019284` in 418 rows, SEQ `0x08018F90` in 204,
the stub `0x0800A9B0` in 190, a LITERAL ZERO in 12 rows, SET in 2, `0x08039854` in 1, OR in 1.

A NODE is four words and a body:

| offset | meaning |
| --- | --- |
| `+0x00` | handler: an odd Thumb pointer, called `(node, actor) -> state` |
| `+0x04` | evaluator: a code pointer or 0 |
| `+0x08` | release |
| `+0x0C` | param: child COUNT for a composite, an operand for a leaf, or a CHILD NODE POINTER in the pointer form |

## Two evaluator paths

This is the part that was missing, and it explains why a node's `+0x04` is called code even though a leaf's
`+0x00` is what activates.

* **STATE path** `0x0800AB0C` (callers `0x0800FAF4`, `0x080391FA`): takes the controller's top state and runs
  the STATE's class slot `+0x04` over child STATES (count at `state+4`, children at `state+8+4i`).
* **NODE path** `0x0800AB2E` (only caller `0x0800FC82`, the per-frame AI update reached from
  `actor+0x238`): reads the row pointer, takes that row's **secondary** node at `+0x04`, and calls THAT NODE's
  `+0x04` over child NODE pointers. It never reads `+0x00`, so a secondary node whose handler word is zero is
  safe.
* **AUX's node evaluate** `0x08019298` is a third consumer: it takes the row it names and evaluates that row's
  secondary, while AUX's ACTIVATE pushes that row's **primary**.

## Two node forms, and this is an authoring trap

Conditional leaves come in two shapes. The form is a property of the HANDLER.

| form | node size | param | child node pointer |
| --- | --- | --- | --- |
| SCALAR | 20 bytes | scalar at `+0x0C` | at `+0x10` (e.g. RAND `0x080188A8`) |
| POINTER | 16 bytes | none: the slot holds the child | **in the param slot `+0x0C`** (e.g. SPAWN `0x08029FE6`) |

Write a scalar into a pointer-form node's `+0x0C` and it is dereferenced as a node pointer. Write a child
pointer at `+0x10` for that form and it is ignored. A census that follows only `+0x10` undercounts the
language: 199 handlers instead of **201**.

## Conditions are latched, not level

The shared condition evaluator is class slot `+0x04` = **`0x080342AE`**, reached by 35 handlers. It resolves
the state's class slot `+0x14` as the test and then:

* test TRUE and not yet latched: ACTIVATE the child once, set the latch, then evaluate the child every frame
  and return the child's value;
* test FALSE: release the child (class `+0x08`) and return 0.

The latch clears in the class's own `+0x00` (`0x080342A8`). Consequence for an author: a permanently true
condition does not re-spawn, but its child's EVALUATE runs every frame, and SET's evaluator calls the row
switcher (`0x0800AA4A`), so a condition wrapped around a SET spams row switching.

### The condition family is 34 distinct tests over 35 handlers

Grouping into twenty meanings is false. Only one test is shared by three handlers, and the two distance-in
handlers duplicate each other. Predicates measured, with the operand each reads:

| predicate | notes |
| --- | --- |
| `rand16() < param` | UNSIGNED compare |
| squared centre distance actor/player `<= param`, `> param` | param is a SQUARED radius (r100 = 10000), SIGNED compare |
| `[player] != 0` and `[player+0x1CC] != 0` | SPAWN: opens only when the player is doing something |
| `[0x03000F94] - [actor+0x210\|0x1E8\|0x1EC] > param` | SIGNED differences, so an "elapsed" reading inverts whenever the global sits below the actor field |
| `[actor+0x1E4] == param` | the gate counter |
| `u8(actor+0x10) == (u8(player+0x10) ^ 1)` | facing |
| own HP below `(((class+0x80(actor)) * param) >> 16) << 10` | signed; a param above 65535 never fires |
| sprite-def lookups by id | two handlers |

Six EWRAM globals have no static writer resolve: `0x03000F94`, `0x03001B50`, `0x03002FE4`, `0x03001C34`,
`0x030032E4`, `0x03001B30`.

### Return values

* OR state evaluate `0x08019192` returns 1 on the first truthy child, so **child order is priority**.
* OR node evaluate `0x08018FDA` returns the child's RAW value.
* The AND node evaluate `0x0801900A` ANDs byte-normalised but returns **2 as a sentinel** when any child
  returns exactly 2; SEQ's node evaluate is the same function, so 2 propagates.
* Class `0x0804B6D0` (handlers `0x080191C6`, `0x080191E8`) ORs on the STATE path and ANDs on the NODE path.
  The asymmetry is measured and NOT explained. Any tree built on those handlers must be proven in a run.

## Class resolution and SEQ

A class table is self-relative from the class word itself: `method = class + s32(class + slot)`, and the
resolved value keeps the Thumb bit. The common veneers are `0x08046AA4` = `bx r2` and `0x08046AA6` = `bx r3`.

SEQ's activate `0x08018F90` stores class **`0x0804AAF4`** (pool `0x0801906C`) and writes position `+4` = 0,
count `+8` = node param, child states at `+0xC+4i`. Class method `+0x00` (`0x08018EF6`) walks position against
count and indexes `+0xC`; method `+0x08` (`0x08018F74`) reads `{position, count}` from `+4`. The same rule
reproduces SET's class `0x0804BC98` from pool `0x0801894C`.

SET's param is a ROW INDEX. `SET` activate `0x0801890A` stores `{class, param}`; its evaluator `0x08018920`
takes `actor+0x00` (class `0x0804C484`), resolves slot `+0x68` to `0x0804ECB0`, adds `0x238` to reach the
controller, and calls the row switcher. AUX reads its param the same way. There is no other way to name a row
and no bounds check: a pointer value is silently multiplied by 8 and used as a row offset.

## Animation

`0x0800ECDA(actor, index)` stores `def+0x54+4*index` into `actor+0x50` with no null test and no count check.
`0x0800ECF0(actor, state_id)` maps through a 25-byte table at `0x08072670`.

Image-wide there are **162 BL sites** into `0x0800ECDA`; **exactly one computes its index** (`0x0802CB9A`,
reading `[actor+8]` through that table, whose only word reference in the image is pool `0x0802CBB0`). The rest
are immediates: **12** for the walk classes, **17 to 21** for the action classes. The approach helper
`0x08018C3A` requests the immediate **1**; its only caller is `0x080369E6`, inside class `0x0804AD38` slot
`+0x04`, instantiated by the approach node handler `0x080369FA`, which appears in rows 56, 57, 71 and 72 only.

`actor+0x1E4` is a GATE COUNTER, not an animation door. The pose leaf `0x0802968C` stores
`{class 0x0804BDD0, param}` and the param reaches the actor through class method `0x0804EA0E..0x0804EA12`
(`state+4` to `actor+0x1E4`). Nine sites touch the field: four writers, two increments (`0x08029EC4`,
`0x080501A2`) and one reader (`0x0804EE5C`, comparing it against `state+0xC`). None reaches `0x0800ECDA` or
the 25-byte table.

## Corrections this research made

* The language is **201 handlers behind 62 state classes**, not the ten a partial survey named, and not 199
  (the pointer form was missed). 3,213 nodes are reachable under a walk that follows every composite child.
* `0x08018CEE` is NOT a site in the Olibu/Hercule family. It sits inside the approach helper `0x08018C3A`;
  the WAIT handler `0x08018C08` ENDS at `0x08018C1C`. The earlier attribution was a scan that ran past a
  handler's exit, and Ghidra's own listing skips `0x08018C12..0x08018C38`, so the instrument has that hole.
* The pose leaf does not write `actor+0x1E4` directly, and `+0x1E4` is not an animation door.
* A row's words are NODE data addresses, normally EVEN. A tool that requires the Thumb bit on them finds no
  rows at all. Two predicates are needed: a code pointer (odd) for handler/evaluator/release, and a node
  pointer (any in-image address) for row words and child slots.
* The null-handler SEQ child is INERT, not a crash: node `0x0870F33C` is row 819's SECONDARY, its child[1]
  `0x0870F328` has handler 0, and that child is evaluated every frame but can never be ACTIVATED because
  activation calls `+0x00`. Row 819's secondary is only ever evaluated, never pushed.
* The approach node `0x080369FA` does not consume its param as an arrival row: the param flows as `r1` into
  `0x08018C3A` and no row arithmetic is formed on that path.

## Authoring minimum, and what a two-animation character can reuse

Smallest correct tree, from measured primitives only:

```
row 0 (idle)     = OR 2
    child 0 = DIST-in  {param: squared radius, e.g. 2500 for r50, child -> row 1 node}
    child 1 = APPROACH {handler 0x080369FA, param -> walk helper}
row 1 (attack)   = SEQ 2
    child 0 = an action leaf, or SPAWN whose param points at a SET node
    child 1 = SET 0
row 2 (recover)  = SEQ 2  {WAIT 18 ; SET 0}
```

Failure modes, each measured:

| mistake | what happens |
| --- | --- |
| null child | `0x08046AA4` is `bx r2` with `r2 = child->[0x00]`, so a null word jumps to 0. No null test exists |
| wrong child count | the loader reads past the node into the next node's header and `bx`es it. No length word, no terminator |
| gate that never opens | silent: RAND's param is a 16-bit UNSIGNED threshold, DIST params are SQUARED radii, SPAWN needs the player acting |
| chain deeper than five | the controller push guard (`cmp r0,#5`) drops the sixth row. Count the SET and AUX hops |
| leaf param naming a row that does not exist | SET and AUX multiply it by 8 with no clamp. All 642 retail params are in range, so retail never trips it |
| animation index with no definition slot | `0x0800ECDA` stores it with no null test: the actor gets no animation and nothing logs |

**A two-animation character can reuse**: the row skeleton unchanged (OR, SEQ, WAIT, SET, AUX, DIST, RAND and
their params) and the approach primitive, which requests index 1.
**It cannot reuse**: any node requesting index 12 or 17 to 21, and the variant probe `0x0802A288`, which reads
the definition's slots 4, 5 and 6 (`def+0x64/+0x68/+0x6C`) for non-null and returns 0 to 3. With two slots it
returns 0, so the branch degrades rather than fails. Fix by filling or cycling those definition slots, or by
rewriting the tree to request only indices 0 and 1.

## Row reachability

151 rows are named by a stat record's `+0x08` (the true entry points). 642 distinct rows are named by SET or
AUX params (internal jumps). Union 763, so 65 rows are dead by this census, and 121 entry rows are never
jumped to. An author starts a tree only from a stat record.

## The tool

`tools/research/ai_node_census.py` is read-only and takes an image path:

```
python -m tools.research.ai_node_census --image <image>                 # the census
python -m tools.research.ai_node_census --image <image> --row 204       # one row's tree
python -m tools.research.ai_node_census --image <image> --secondaries   # the secondary handler census
```

Every function in it takes bytes, so `tests/unit/test_ai_node_census.py` drives the decoder with a synthetic
image and needs **no ROM**. Run over the canonical image it reports the same **201 distinct handlers** the
research lane measured. Its node total is policy-dependent: it follows every composite child, so it reports
more nodes than a single-child walk, and `null_handler_nodes` counts the slots that walk reaches which are not
nodes. Read those two numbers as the walk's own bookkeeping, not as a claim about the language.

## Not established

1. The final predicate of ten partially decoded tests, which needs the callees `0x0800FE78`, `0x08011C70`,
   `0x08011CCA`, `0x08009324` and `0x08000158` decoded.
2. Which subsystem owns the six EWRAM globals above. A watchpoint on each settles it.
3. The third argument reaching every node evaluate, from `0x0800AB46`.
4. Whether the OR-on-state / AND-on-node asymmetry is intentional.
5. Nothing here is runtime-verified. Every claim is a static byte measurement, from bounded scans run twice.
