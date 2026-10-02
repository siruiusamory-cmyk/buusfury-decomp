# ROM-012 rectangle containment and callback capture

Capturing the containment-accepted path for an exact runtime object created by
factory `0x08007675`, including the query entity identity, the target rectangle,
the accepted-containment gate and the callbacks.

## Objective

Capture the containment-accepted path for an exact runtime object created by factory 0x08007675.

ROM-011 plus independent static analysis established:

- 0x080126D4..0x080127AC is a point-in-rectangle registry query.
- R0 = registry/manager.
- R1 = query entity.
- Query coordinates come from:
  entity+0x1A0 >> 8
  entity+0x1A4 >> 8
- Runtime rectangle fields are:
  +0x04 = signed x_min
  +0x06 = signed y_min
  +0x08 = signed x_max
  +0x0A = signed y_max
- Bounds are half-open:
  x_min <= X < x_max
  y_min <= Y < y_max
- 0x08012778 is the first instruction reached after all four containment tests pass.
- object+0x0C supplies the callback/receiver reference.
- containment success performs:
  vtable[2] filter
  then, if accepted,
  vtable[1] action.
- First matching object exits the loop.
- Return value is not meaningful to callers; behavior is side-effect driven.

ROM-011 runtime captured exact target X at PC 0x08012748.

That query failed immediately because:

X_query = 172
x_min = 592

Therefore the target was simply outside the query entity's position.

The objective now is:

PUT THE QUERY ENTITY INSIDE ONE FACTORY-0x08007675 RECTANGLE
→ CAPTURE PC 0x0801277A READING X+0x0C WITH THE NATIVE GATE
→ CAPTURE FILTER
→ CAPTURE ACTION
→ TRACE IMMEDIATE CONSEQUENCE
→ STOP

## Baseline

ROM-011 is committed as:

0d0c0e39c058b7cfba9abcdc30d95849c6310e10

Message:

feat: capture live spatial-object read

Portable suite:

250 passed

Working tree is clean.

ROM-012 begins from this baseline.

## Phase 1 - Identify the Best Target Rectangle

Load the user-created post-transition state directly. Preserve the original
unchanged and use an ignored copy under `build/rom012/`. Do not replay the
south transition or recapture the allocation/insertion chain.

After map population is complete, reconstruct the live registry identity chain:

live registry slot
→ runtime object
→ object+0x14 retained descriptor
→ descriptor+0 raw factory target

Select every object whose raw factory target is exactly `0x08007675`; preserve
the raw Thumb bit. Identify the current query entity and registry.

Capture:

- active MapEntry
- query entity pointer
- query integer X/Y
- registry
- current load epoch

Then inspect currently registered objects only far enough to identify objects belonging to factory family:

0x08007675

For each target-family object record:

- runtime object pointer
- descriptor
- rectangle:
  x_min
  y_min
  x_max
  y_max
- distance/direction from current query point

Do not build a general parser.

This is runtime target selection only.

Choose the nearest plausible target-family rectangle in the loaded map. Do not
require observing its original allocation event.

## Phase 2 - Verify Query Entity Identity

Before guiding the human, establish whether the query entity behaves like the player-controlled entity.

Use a tiny runtime experiment:

1. capture entity pointer and X/Y
2. user moves a short known direction
3. recapture X/Y

If coordinates move consistently with the player's movement:

STRONGLY SUPPORT that this query instance is using the player-controlled entity.

Do not require full entity-type reverse engineering.

If coordinates do not track the player:

stop and identify the actual query entity before attempting navigation.

## Phase 3 - Human Navigation

Once a target rectangle and player-correlated query entity are established, tell the user:

- current query coordinates
- target rectangle coordinates
- approximate direction required

Example:

Current:
(172, 190)

Target:
x = [592, 601)
y = [136, 241)

Direction:
move primarily east while remaining within target Y range.

Do NOT automate hundreds of movement frames.

The human controls gameplay.

the operator keeps instrumentation armed.

The user should navigate naturally toward the target rectangle.

One map transition maximum remains allowed.

## Phase 4 - Arm the Native Accepted-Containment Gate

Reuse the native probe with the exact gate:

- PC `0x0801277A`
- read overlapping `X+0x0C..X+0x10`

The predecessor at `0x08012778` is the first instruction after all four
rectangle bounds have passed. The native gate captures its concrete callback
reference load without leaving software breakpoints armed during gameplay.

Every hit must be validated.

Capture:

- matched object pointer
- object index
- query entity pointer
- query X/Y
- rectangle bounds
- descriptor
- factory identity

Reject the hit unless the matched object belongs to factory:

0x08007675

Do not use a containment hit from another object family as evidence.

## Phase 5 - Capture object+0x0C

For the exact accepted target object, capture:

- object+0x0C raw value
- pointed-to runtime structure
- its dispatch/vtable base
- concrete vtable[2] target
- concrete vtable[1] target
- raw code pointer
- normalized Thumb/ARM fetch address

Preserve raw pointer values separately from normalized executable addresses.

## Phase 6 - Filter Callback

Trace vtable[2] only far enough to establish:

- arguments
- object/receiver
- query entity if passed
- return value
- fields read
- immediate calls

If filter returns zero:

record that exact rejection and stop deeper action tracing.

If filter accepts:

continue to action callback.

## Phase 7 - Action Callback

Capture vtable[1]:

- raw target
- fetch address
- arguments
- receiver
- immediate calls
- immediate externally visible/game-state consequence

Trace only far enough to classify the direct role.

Possible evidence-supported classifications may include:

- map transition
- script/event activation
- interaction
- movement/collision effect
- state/flag update
- generic spatial action
- another demonstrated behavior

Do not force any of these labels.

## Phase 8 - Human Observation

When containment/action occurs, immediately ask the user what visibly happened.

Keep:

HUMAN OBSERVATION

separate from:

EXECUTABLE EVIDENCE

Example:

Human:
"Walking into the rectangle changed maps."

Executable:
callback target called map-loading function.

Only the combination may justify strong transition semantics.

## Runtime Instrumentation

Reuse the native playable mGBA probe infrastructure from ROM-011.

Do not return to expensive GDB read watchpoints.

Do not leave the eight discovery software breakpoints armed during gameplay.
Do not use software breakpoints or native instrumentation to recapture the
factory/allocation/insertion chain when post-load reconstruction succeeds.

Do not modify:

- ROM
- X
- query coordinates
- rectangle bounds
- callback state

The human must reach containment through actual gameplay.

## Important Exact-Target Rule

A native accepted-containment hit counts only when:

matched object
→ descriptor
→ factory

proves factory 0x08007675.

Other rectangle objects may also pass containment during gameplay.

Ignore them for semantic promotion.

## If Current Target Is Not Human-Reachable

Do not wander indefinitely.

If the nearest current-map target is clearly unreachable through bounded
natural gameplay, stop and report that precise result. Do not replay the south
transition.

stop with that precise result.

Do not progress story or explore additional maps.

## Static result preserved

Independent static analysis established:

Function:
0x080126D4..0x080127AC

Rectangle layout:
+0x04 x_min
+0x06 y_min
+0x08 x_max
+0x0A y_max

Signed 16-bit half-open containment.

Accepted path:
0x08012778

Native capture gate:
PC 0x0801277A reading X+0x0C

Callback reference:
object+0x0C

Two-stage dispatch:
vtable[2] filter
vtable[1] action

Do not re-prove this unnecessarily.

Runtime should now validate the concrete callback targets and consequences.

## Dialogue Hypothesis

Leave UNRESOLVED unless direct callback/scheduler evidence establishes a connection.

Dialogue is no longer the main research question.

## Parser Readiness

Do not implement a parser.

At completion reassess structural readiness.

Important:

Runtime object layout is NOT automatically source descriptor layout.

A YES requires sufficient source-side evidence for:

- descriptor boundary/extent
- factory field
- rectangle-producing source fields
- callback/reference-producing source field
- widths
- raw pointer handling
- lossless preservation

If source provenance is still insufficient:

NO.

State the smallest remaining structural blocker.

## Expected Outcomes

A - EXACT TARGET FILTER REJECTED

Containment succeeds for factory-0x08007675 object, but vtable[2] rejects it.

B - EXACT TARGET ACTION CAPTURED

Containment succeeds, filter accepts, and concrete vtable[1] action executes.

C - TARGET CONTAINMENT REACHED BUT CALLBACK ATTRIBUTION INCOMPLETE

D - NO BOUNDED HUMAN-REACHABLE TARGET FOUND

Do not invent another category unless necessary.

## Tests

Starting suite:

250 passed

Keep all previous regressions green.

Add synthetic tests only where new helper logic requires them.

Runtime evidence remains separate from portable pytest.

## Report fields

Report:

### Query Entity
- pointer
- coordinates
- evidence connecting or not connecting it to player movement

### Target Selection
- object
- descriptor
- factory
- rectangle
- initial query point
- navigation delta

### Accepted Containment
- PC
- query coordinates
- target bounds
- exact object identity

### Filter
- object+0x0C
- dispatch base
- concrete vtable[2]
- return/result
- immediate behavior

### Action
if executed:
- concrete vtable[1]
- immediate calls
- executable consequence

### Human Observation
separate from executable evidence

### Semantic Classification

### Evidence Level

### Parser Readiness



## Acceptance criteria

ROM-012 is complete when:

- query entity is characterized enough for navigation
- a practical factory-0x08007675 target rectangle is selected
- human-controlled movement is used
- exact target reaches the native PC `0x0801277A` / `X+0x0C` gate OR bounded reachability failure D is established
- object+0x0C concrete dispatch is captured on exact containment when reached
- filter is captured
- action is captured if filter accepts
- immediate consequence is traced
- no gameplay brute force occurs
- no parser is implemented
- tests pass
- independent review completes
- ROM/save/state remain unchanged
- ROM-012 remains uncommitted and unstaged

## Closing statement

Do not begin ROM-013.

Core question:

WHEN THE QUERY ENTITY IS ACTUALLY INSIDE A 0x08007675 RECTANGLE,
WHAT DO ITS FILTER AND ACTION CALLBACKS DO?
