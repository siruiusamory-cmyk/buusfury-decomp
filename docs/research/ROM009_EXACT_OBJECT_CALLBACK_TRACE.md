# ROM-009 - Clean Gameplay Exact-Object Callback Trace

## Objective

Determine whether the dialogue-free gameplay state reaches an AABB query and
callback for the exact current-load-epoch object created by raw factory
`0x08007675`. If it does not, identify the first rejecting guard with a bounded
fallback analysis.

## Why This Ticket Exists

ROM-008 reproduced the target factory, object, registry insertion, bounds, and
lifecycle but captured no AABB/callback for that exact object. The earlier state
may have been dialogue-gated. A new state now has normal control and no dialogue,
including after one south transition. This is a hypothesis to test, not a fact.

## Ticket-Specific Inputs

- Locate the new save/state locally rather than assuming its filename.
- Record its size and SHA-256 before use.
- Preserve every original input read-only.
- Use ignored byte-identical working copies.
- Use the canonical verified ROM profile from `docs/PROJECT_<local-state-name>`.
- Derive the active `MapEntry` from runtime. Do not infer it from a location or
  map name.

## Required Delegation

Before the runtime experiment, obtain these read-only analyses and wait for both:

1. **Static callback review - the model an independent reviewer**
   - Perform static callback analysis for factory `0x08007675`, dispatch base
     `0x0804A09C`, object `+0x0C`, and the callback path around `0x08012784`.
   - Return evidence and experiment-relevant findings only.
2. **Runtime experiment design - an independent reviewer**
   - Design the clean-state runtime experiment with exact object attribution,
     lifecycle checks, and bounded stopping point.
   - Return a procedure and failure classifications only.

The primary agent owns all edits, integration, runtime execution, and final
conclusions.

Request a **conditional scheduler review - the model an independent reviewer** only if the
clean-state experiment still fails to produce the exact object's callback. Its
read-only task is a
scheduler/guard decision tree around `0x080126D4`, `0x080127AE`, `0x08012846`,
and `0x08012784`. Do not request it prematurely.

A an independent reviewer independent final review is required by `docs/DEVELOPMENT.md`.

## Required Experiment

1. Verify the canonical ROM identity without modifying it.
2. Locate and hash the new state/save.
3. Preserve originals and load an ignored working copy.
4. Derive the active `MapEntry` from runtime.
5. Capture the first suitable descriptor whose raw factory is `0x08007675`.
6. Dynamically capture its returned object X.
7. Verify registry insertion, load epoch, descriptor, factory, slot, and object
   lifecycle.
8. Observe ordinary gameplay for an AABB query and callback attributed to X.
9. Use only bounded deterministic movement.
10. Optionally transition south exactly once.
11. If the new map creates target X2, track X2 as a separate identity and epoch.
12. If the exact callback is reached, capture it and trace only its immediate
    consequence.
13. Stop after the first exact callback or precise rejecting guard.

Object identity must include the verified runtime chain, not merely an EWRAM
pointer. Reject callbacks from unrelated objects.

## Conditional Fallback

Only if the clean dialogue-free experiment fails to produce an exact-object
callback, including when the AABB is reached but the callback is filtered:

- examine query entries `0x080126D4`, `0x080127AE`, and `0x08012846`;
- inspect the callback path around `0x08012784`;
- verify entry callers and current-load-epoch identity;
- identify the first rejecting guard;
- stop there rather than expanding gameplay or general archaeology.

## Required Result Classifications

Dialogue hypothesis result must be exactly one of:

- `SUPPORTED`
- `NOT SUPPORTED`
- `UNRESOLVED`

Primary runtime result must be exactly one of:

- `A. EXACT CALLBACK CAPTURED`
- `B. EXACT AABB REACHED, CALLBACK FILTERED`
- `C. FIRST REJECTING GUARD IDENTIFIED`
- `D. ENVIRONMENT BLOCKED`

## Structural Parser Readiness

Answer `YES` or `NO` for whether the `0x08007675` descriptor family has enough
structural evidence for a future minimal read-only parser. This judgment is
independent of perfect gameplay semantics.

`YES` requires sufficient evidence for:

- family discrimination;
- source descriptor extent or boundary sufficient for minimal parsing;
- exact modeled field offsets and widths;
- raw pointer handling;
- rectangle-producing fields;
- callback/source field where established;
- lossless raw preservation.

It does not require deciding whether the region is collision, trigger,
activation, or transition. Do not implement the parser in this ticket.

## Scope Boundaries

- Do not write to the ROM.
- Do not alter original saves or states.
- Do not implement any parser.
- Do not perform general descriptor parsing.
- Do not brute-force gameplay.
- Use at most one current map plus one south transition.
- Do not progress the story.
- Do not accept another object's callback as evidence.
- Do not continue guard archaeology after the first precise rejection.

## Ticket-Specific Validation

- Reverify ROM and runtime-input hashes before and after the experiment.
- Keep all runtime artifacts under ignored paths.
- Run the full portable test suite.
- Add only synthetic portable tests for any new binary logic.
- Report private runtime checks separately from portable tests.
- Confirm no ROM, save, state, dump, or extracted proprietary artifact is
  tracked or staged.

## Completion Criteria

- Required A/B read-only reviews completed before runtime work.
- Clean state tested first with exact object attribution.
- One primary runtime classification recorded.
- Dialogue hypothesis classified.
- Conditional C used only if its condition was met.
- Structural parser readiness answered `YES` or `NO` without implementing it.
- Research documents updated with evidence and unresolved limits.
- `docs/PROJECT_<local-state-name>` updated only with newly verified facts.
- Portable tests and `git diff --check` pass.
- Independent final review completed and legitimate findings resolved.

## Required Final Report Additions

In addition to `docs/DEVELOPMENT.md`, report:

- located runtime input identities without embedding proprietary bytes;
- exact runtime identity chain for X and, if applicable, X2;
- primary runtime classification;
- dialogue hypothesis classification;
- immediate callback consequence or first rejecting guard;
- structural parser readiness `YES` or `NO` with the smallest remaining blocker;
- whether the conditional scheduler review was used and why.

## Stop

Stop after the first exact-object callback and its immediate consequence, the
first rejecting guard, or an explicit environment blocker. Do not implement a
parser and do not begin another ticket.
