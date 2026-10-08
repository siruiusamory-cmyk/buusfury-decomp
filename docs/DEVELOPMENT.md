# Development policy

The rules that apply to all work in this repository. Read
[`CONTRIBUTING.md`](../CONTRIBUTING.md) first if you are new here, and
[`README.md`](README.md) for the documentation index. This document is the
policy; [`ROM_SAFETY.md`](ROM_SAFETY.md) is the expanded safety contract and
[`REVIEW.md`](REVIEW.md) is the review gate.

## The product and its acceptance target

Build a modding SDK and toolchain for the three Webfoot Dragon Ball Z Game Boy
Advance games, capable of inspecting, extracting, decoding, editing, authoring,
serializing, relocating, validating, rebuilding and patching their content.

- The **shipping product** is the toolkit in `tools/webfoot/` plus its project
  and build formats. ROM and patch output are in scope, including executable
  patching.
- The **acceptance target** is authoring playable Legacy of Goku content inside
  the actual Webfoot LOGII/Buu's Fury engine. A subsystem is not valuable merely
  because it decodes: the playable ROM is what validates the SDK.
- The **supported games** are *The Legacy of Goku*, *The Legacy of Goku II* and
  *Buu's Fury*. Buu's Fury leads and is the measurement subject, because its
  binary and running memory are where measured constants come from, but no part
  of the architecture may assume a single game.
- The product goal is **not** a standalone remake. The former engine prototype
  in `remake/` was removed and must not be reintroduced or cited as evidence
  that the SDK has authored equivalent ROM content.
- A ROM-derived value enters shipped data only once it has been measured and
  confirmed. Anything still unmeasured is marked temporary and named as such.

This repository is an active reverse-engineering laboratory as well as a
product. Preserve existing conventions and verified regressions; do not
recreate or reinitialize a subsystem that already works.

## Public executable releases

A released randomizer executable is a first-class public surface, held to the
same standard as the progress site: it carries the project's own name, version
metadata and icon, ships only the executable and its README, and names no
machine, path or private process of its own. Those rules are enforced by
`python -m tools.quality.public_release`, which reads every release definition
through one shared product list in `tools/quality/public_release.py`. A new
randomizer product is added to that list and is then checked by the same rules,
never by a second copy of them.

## Repository independence

- This is a standalone repository. Do not add it as a submodule, subtree or
  linked worktree of another project, and do not link another checkout into it.
- Read from another checkout if that is useful. Write nothing into it.
- No tracked file may contain a machine-specific absolute path, including a
  path into another developer's checkout. The public-surface guard enforces
  this.

## ROM safety

The canonical commercial ROM is read-only. Every write goes through a working
copy, and every entry point verifies profile identity before it touches
anything. [`ROM_SAFETY.md`](ROM_SAFETY.md) states the full contract; the
short form is:

```text
verified base -> working copy/generated output -> patch/output ROM
```

Never commit a ROM, extracted ROM content, a save, a save state, a memory dump
or a checked-out upstream repository. Use synthetic fixtures for binary tests.

## Evidence discipline

Label every format claim with one of:

- `CONFIRMED`: directly established by adequate evidence.
- `INFERRED`: supported interpretation that is not independently proven.
- `UNKNOWN`: not established.

For executable and runtime research, these complementary levels are available
when they add precision:

- `LEVEL 0`: numeric shape only.
- `LEVEL 1`: static executable load or use.
- `LEVEL 2`: static downstream role.
- `LEVEL 3`: verified runtime observation.
- `LEVEL 4`: meaningful runtime subsystem or behavior confirmed.

Rules that keep the labels honest:

- Cite `file:line` for any mechanism claim. Absent evidence, say so and
  investigate; never substitute a plausible explanation.
- A passing test does not promote a claim. Neither does an upstream project's
  chosen field name, a value that resembles a pointer, an address that is
  aligned, or adjacent bytes that look plausible.
- Round-trip proves representation, not semantics.
- Executable behavior outranks upstream naming. Runtime behavior outranks
  numeric pattern guessing.
- Unknown means unknown. A hypothesis is recorded as a hypothesis.

## Runtime evidence

Any claim sourced from an emulator is governed by
[`docs/skills/mgba-runtime.md`](skills/mgba-runtime.md), and using it is
**mandatory**, not advisory:

- Read that file before the first mGBA action of a ticket. It is tracked
  precisely so that it exists in every worktree and can be reviewed; a runtime
  ticket that never cites it has not been done.
- Launch through a tracked launcher. A launcher may hand mGBA `--script` only
  when it keeps both gates that flag would otherwise bypass: every Lua file it
  passes must be accepted by `inject_mgba_lua.ps1 -CheckOnly`, and the launcher
  must itself fail closed on the emulator version and an exact ROM digest. A
  bare `mGBA.exe --script` outside a launcher is still forbidden, because it
  carries neither.
- An observer writes no emulated memory. Controller input is allowed but must be
  deliberate: gated by an environment variable the launcher sets, off by default,
  and bounded so the run ends by itself. Twenty-six allow-listed observers drive
  input this way; a new one states its gate rather than assuming it.
- Every observer carries a liveness channel, and the closure report says which
  of the three instrument states in section 8 of that file applies. A silent
  channel with a silent liveness channel is "no evidence", never a negative.
- `tests/unit/test_mgba_runtime_skill.py` enforces the mechanically checkable
  part of this. Loosening that test is loosening the policy.

## Semantic and binary rules

- Preserve `_raw` suffixes until semantics are justified.
- Never mask, align, normalize or reinterpret raw values silently.
- Apply the Thumb state bit only when interpreting an address as executable
  code.
- Preserve the original raw code pointer separately from its normalized fetch
  address.
- Do not infer structure size solely from pointer spacing, or a target type
  solely from count/pointer shape.
- Do not call data graphics because an upstream project did.
- Round-trip a format losslessly before editing it.
- Use the existing pointer and address helpers instead of ad hoc arithmetic.

## Reverse-engineering policy

Reverse engineering exists to unblock concrete authoring. It is not a goal in
itself, and adjacent unknowns are not roadmap justification.

**Name the blocker first.** Before starting an investigation, complete the
sentence "this blocks the SDK from authoring ______", naming the blocked
operation or playable feature, the exact unknown and the minimum evidence
needed. An investigation that cannot complete that sentence waits.

**Search existing evidence first.** The question may already be answered in
`docs/research/`, `docs/reverse-engineering.md` or the atlas. Do not re-derive a
value a documented table already supplies.

**Prefer external knowledge for player-visible behavior.** Whether the game does
something is usually already documented by guides, manuals, footage or firsthand
play. Escalate in this order: firsthand play knowledge, documentation and
guides, published research, direct static ROM reads, native recompilation,
emulator capture, and disassembly last. Reverse engineering earns its cost on
what external sources cannot answer: exact thresholds, tick-accurate durations,
executable anchors, field offsets, selection mechanisms and formulas.

**Prefer ROM-resident data to a runtime-construction hypothesis.** Assume the
durable identity, parameters, selectors and content records already exist in the
ROM rather than being synthesized at runtime. Atlas the likely persistent
records, watch them being consumed, explain the consumer statically, then author
the persistent data:

```text
atlas -> persistent ROM candidate -> live consumer capture
-> narrow static explanation -> evidence back into atlas
```

Switch to a runtime-construction hypothesis only when direct runtime evidence
shows the value is actually synthesized, transformed, allocated or written
dynamically. The default is a hypothesis, never a `CONFIRMED` claim.

**The loop for a new RE-backed capability:**

1. State the authoring capability being blocked.
2. Search existing project evidence first.
3. Use external and public knowledge where it can answer player-visible
   behavior.
4. Use binary and runtime research for the exact mechanism.
5. Label claims `CONFIRMED` / `INFERRED` / `UNKNOWN`.
6. Put measured values into shipped metadata only after adequate evidence.
7. Add discriminating tests, including a case that would distinguish the
   hypothesis from its plausible alternative.
8. Keep source comments semantic: say what the code does.
9. Put the proof in an evidence document, never in production source.
10. Complete independent review before closure.

When external evidence and runtime evidence disagree, say so explicitly and
prefer the runtime observation: the binary is ground truth for this project.
Firsthand gameplay is legitimate evidence and is labelled as such, distinct from
runtime capture.

## Determinism, profiles and addressing

- The same verified base ROM, project state and SDK version must produce a
  byte-identical image. Identical input plus project state yields identical
  output, and planning must not consume project edits.
- Verify the exact configured profile before any profile-specific access, and
  fail closed on an identity or provenance mismatch.
- Keep ROM addresses and file offsets explicit and distinct. Never copy an
  offset between profiles or revisions without independent validation.
- Ordering, identifiers and serialization are stable: a project written twice
  is the same project.
- Relocation must move every reference to a structure, or prove that none
  exists. A partially relocated structure is a corruption, not an incomplete
  feature.

## Testing and validation

Tests are the proof of correctness. Preserve every established regression.

- Use synthetic tests for binary logic. Portable tests must not require a
  private save, a save state or a ROM.
- Local-ROM integration tests must be gated so they skip cleanly without one,
  and must not commit anything derived from a ROM.
- Report private runtime validation separately from portable results. A runtime
  claim that could not be reproduced is reported as not reproduced.
- Run the relevant portable tests before and after a change, and name the
  focused gate rather than reconstructing a path list. [`testing.md`](testing.md)
  defines the gates.
- Run `git diff --check` before completion.
- Never weaken, delete or skip a test merely to reach a green result.

### Focused validation and the full suite

**Work at the fastest speed that still meets the quality bar.** For every
change, prefer the smallest scope that proves the claim: focused named tests,
targeted measurement before broad automation, existing tooling over new. Product
quality is never traded for speed.

The full suite is an **expensive integration gate**, never an iterative
debugging loop and never a reflex after every fix.

- **Run it** at meaningful integration boundaries: a substantively complete
  implementation; a broad or shared production change (parsers, codecs, VM
  assembler/decoder, build/extract, profile/layout/reference internals, semantic
  IDs, transaction logic, dependencies); a fix affecting unrelated systems; a
  radius that focused tests cannot bound; or a prior failure signalling broader
  risk. Never skip a warranted gate because it is slow.
- **Do not rerun it** after a correction that is narrow, understood, local and
  covered by a focused test. Run the smallest scope that validates the
  correction. A change since the previous run is not itself a reason.
- **Blast radius sets the scope.** Narrow: the failing test, its module, its
  directly relevant regressions. Shared or uncertain: the broader affected
  suites, or the full suite. Focused validation never substitutes for real
  integration validation of a shared change, and never rerun merely for a
  cleaner aggregate number: evidence comes from knowing what ran, not from a
  fresh total.
- **Report measured and derived separately**: observed totals, then post-suite
  fixes with their focused reruns, then remaining known failures. An expected
  aggregate is labelled `DERIVED / NOT DIRECTLY OBSERVED`, never called
  measured.
- **A failure caused by the change stops closure**: classify it, fix it, scope
  by blast radius, and never commit with one unresolved. A reproduced
  environment-blocked failure is reported rather than weakened to reach zero.

## Code review

Every nontrivial code-bearing change requires independent review of the frozen
implementation before it closes. [`REVIEW.md`](REVIEW.md) states the gate, the
dimensions it examines, the verdicts and the closure sequence.

## Public progress accuracy

The public capability list is
[`src/data/capabilities.json`](../src/data/capabilities.json), rendered by the
progress site from [`src/data/project.ts`](../src/data/project.ts). It is a
statement of what the SDK can demonstrably do, and it must not overstate.

The deployed site at <https://webfoot-sdk.siruiusamory.workers.dev/> is a
**public product surface**, not an internal dashboard. A visitor who finds the
project through the site rather than through the repository must be able to tell
what the product is, what works today, what remains, and where the evidence
lives. It is held to the same standard as the repository: no development-process
material, no hosted-service vocabulary, no ticket mechanics, no session history,
and no machine-specific path.

- A capability is shipped only when the behavior is proven, and each entry
  records how its own result was proven. Knowing what a structure is and being
  able to author with it are tracked separately.
- Every visible status statement must be one of: a confirmed current fact, a
  historical milestone, an explicitly directional estimate, or a future target.
  A reader must be able to tell which one it is.
- Never leave a superseded blocker or an outdated figure on the site. A visitor
  reading a blocker the project already passed is being told something false.
- A milestone marked complete must not describe its own work as unfinished. If a
  completed milestone genuinely has to name something left open, it declares that
  item in its `openItems` field, so a reader sees a stated limit rather than
  finished work presented as finished. The site consistency tests enforce both
  halves of that rule.
- Change the site in the same closure as the capability it describes, and
  confirm the deployed site serves the change rather than assuming a deploy
  landed.
- The site is built from `src/data/project.ts` and published to
  <https://webfoot-sdk.siruiusamory.workers.dev/> by `.gitlab-ci.yml` when the
  default branch moves. Run `npm run check` and `npm run build` before pushing.
  After the pipeline finishes, fetch the live page and confirm the new strings
  are present. Leaving the live site ahead of the default branch means the site
  can no longer be reproduced from the repository.
- The status data is also served as JSON at `/project.json`, generated in the
  same build as the page. The consistency tests read that document, so the page
  and the data it renders cannot drift apart unnoticed.
- Screen the built output, not only the sources:
  `python -m tools.quality.public_surface --built dist` scans what a visitor
  actually receives.
- The approximate overall percentage is directional and changes only after a
  deliberate product or roadmap review. No hand-written percentage may be
  reintroduced where a derived count exists.

## Git safety

Never use a destructive command against someone's work:

```text
git reset --hard
git clean -fd
```

Before any commit:

1. inspect `git status`;
2. inspect the full diff;
3. run the relevant tests;
4. verify no proprietary file is staged;
5. verify ROM safety, including that the canonical image is unchanged.

Stage explicit paths. Never `git add -A` in a checkout that may hold unrelated
work, and verify the staged file list against an expected list before
committing.

A commit subject describes the change, not the process behind it. Never add
model, tool or vendor attribution to a commit message, a trailer, a merge
request description or release notes.

## Third-party, proprietary and licensing boundaries

- Do not commit commercial ROM content, extracted proprietary binaries, saves,
  save states, memory dumps, generated commercial assets or upstream
  repositories. `extern/` is ignored for exactly this reason.
- Respect the licence of every upstream. A repository with no licence is
  all-rights-reserved: it may be read, but its source and assets must not be
  copied into this repository.
- Commercial toolchains are never committed. Install them locally and point an
  environment variable at them.
- Third-party material keeps its own licence, which the root licence does not
  override. Record new third-party material in
  [`THIRD-PARTY-NOTICES.md`](../THIRD-PARTY-NOTICES.md).
- Dependencies must be free of any requirement for a hosted service or a
  proprietary credential to build, test or use the SDK.

## Documentation and source discipline

Three kinds of file answer three different questions. Keep them separate.

- **Production source answers "what does the SDK do?"** It carries the
  implementation, concise semantic comments, safety invariants and the
  explanation of anything architecture-sensitive. It does not carry research
  narrative.
- **Tests answer "what proves this behavior?"** They carry discriminating cases,
  failure paths, round-trip checks, mutation and regression cases, and
  deterministic-output assertions.
- **Evidence documents answer "how was this established?"** They carry ROM
  addresses, runtime observations, disassembly evidence, historical hypotheses,
  validation counts and the research narrative.

A future reverse-engineering change must not put its proof transcript into
production source. Put it in the evidence document and leave a semantic comment
behind.

Write documentation for a contributor who has none of the research history.
A reader should be able to understand the project from the repository alone,
without reconstructing it from a conversation record.

## Text files and line endings

Never change a line's ending unless you also change the line, and write added
lines bare-LF. Several tracked files mix CRLF with bare LF.
[`line-endings.md`](line-endings.md) has the byte-safe recipe.
