# ROM-009 exact-object callback trace

Whether a dialogue-free gameplay state reaches an AABB query and callback for the
exact current-load-epoch object created by a raw factory, and if not, which guard
rejects it first.

## Question

Determine whether the dialogue-free gameplay state reaches an AABB query and
callback for the exact current-load-epoch object created by raw factory
`0x08007675`. If it does not, identify the first rejecting guard with a bounded
fallback analysis.

## Why this investigation exists

ROM-008 reproduced the target factory, object, registry insertion, bounds, and
lifecycle but captured no AABB/callback for that exact object. The earlier state
may have been dialogue-gated. A new state now has normal control and no dialogue,
including after one south transition. This is a hypothesis to test, not a fact.

## Record-Specific Inputs

- Locate the new save/state locally rather than assuming its filename.
- Record its size and SHA-256 before use.
- Preserve every original input read-only.
- Use ignored byte-identical working copies.
- Use the canonical verified ROM profile from `docs/PROJECT_STATE.md`.
- Derive the active `MapEntry` from runtime. Do not infer it from a location or
  map name.

## Analyses required

Before the runtime experiment, two read-only analyses were required:

1. **Static callback analysis** for factory `0x08007675`, dispatch base
   `0x0804A09C`, object `+0x0C`, and the callback path around `0x08012784`,
   returning evidence and experiment-relevant findings only.
2. **Runtime experiment design** for the clean-state experiment, with exact object
   attribution, lifecycle checks and bounded rejection conditions, returning a procedure
   and failure classifications only.

A conditional scheduler review follows only if the clean-state experiment still
fails to produce the exact object's callback. Its read-only task is the
scheduler/guard decision tree around `0x080126D4`, `0x080127AE`, `0x08012846`,
and `0x08012784`.

## Experiment

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

## Result classifications

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
activation, or transition. Do not implement the parser in this record.

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

## Validation

- Reverify ROM and runtime-input hashes before and after the experiment.
- Keep all runtime artifacts under ignored paths.
- Run the full portable test suite.
- Add only synthetic portable tests for any new binary logic.
- Report private runtime checks separately from portable tests.
- Confirm no ROM, save, state, dump, or extracted proprietary artifact is
  tracked or staged.

## Stop

Stop after the first exact-object callback and its immediate consequence, the
first rejecting guard, or an explicit environment blocker. Do not implement a
parser and do not begin another record.
