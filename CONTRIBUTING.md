# Contributing

Thanks for your interest in the Webfoot SDK and DragonByte Z. This page is the
practical entry point. The rules behind it live in
[`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) (policy),
[`docs/ROM_SAFETY.md`](docs/ROM_SAFETY.md) (the safety contract) and
[`docs/REVIEW.md`](docs/REVIEW.md) (the review gate).

## Ground rules

- **No ROM, no game data.** This repository distributes neither. Do not attach
  a ROM, an extracted asset, a save, a save state or a memory dump to an issue,
  a merge request or a commit.
- **The canonical ROM is read-only.** Everything the toolkit writes goes to a
  new file. See [`docs/ROM_SAFETY.md`](docs/ROM_SAFETY.md).
- **Evidence before certainty.** Format claims are labelled `CONFIRMED`,
  `INFERRED` or `UNKNOWN`, and a mechanism claim cites `file:line`. A passing
  test does not promote a claim.
- **Tests are the proof.** Add a discriminating test with a behavior change, and
  do not weaken one to reach green.
- **Keep public documentation public.** Notes about how the work was organised
  privately do not belong in the repository.

## Ways to contribute

- **Measure something the SDK needs.** A field offset, a threshold, a format
  rule or an engine anchor that unblocks a specific authoring capability.
- **Improve the SDK.** `tools/webfoot/` is the shipping product: parsing,
  authoring, relocation, build and validation.
- **Improve DragonByte Z.** The desktop editor in `tools/webfoot/workbench/`.
- **Improve the runtime toolbox.** `tools/runtime/` holds the emulator
  instrumentation and GDB client used to produce runtime evidence.
- **Document a format.** `docs/project-format.md`, `docs/architecture.md` and
  the notes under `docs/research/` describe what has been measured.
- **Report a defect.** Include the exact command, the input profile, and what
  happened instead. Never include proprietary data.

## Setting up

Requirements: Windows PowerShell, Git, [`uv`](https://docs.astral.sh/uv/) on
`PATH` (setup installs Python 3.12 if it is missing), and mGBA for the Run
action and optional runtime research.

```powershell
git clone <repository-url>
cd log1-remake
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup.ps1
.\.venv\Scripts\Activate.ps1
```

Keep a legally obtained ROM outside version control (the ignored `roms\`
directory is the usual place) and identify it before doing anything else:

```powershell
webfoot identify ".\roms\Dragon Ball Z - Buu's Fury (U).gba"
```

## Picking work

Start from the public capability list,
[`src/data/capabilities.json`](src/data/capabilities.json), and the route to
1.0 in [`docs/ROADMAP_TO_1_0.md`](docs/ROADMAP_TO_1_0.md). A capability is
valuable when it lets an author do something in a real game, so the most useful
work names the blocked authoring operation it unblocks.

Before starting a reverse-engineering task, read the policy in
[`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md): name the blocker, search the
existing evidence first, use public knowledge for player-visible behavior, and
reach for the binary for the exact mechanism.

## Making a change

1. Branch from `master`.
2. Make the smallest change that completes the capability or fixes the defect.
3. Add or update the tests that prove it, including a case that would fail if
   the behavior regressed.
4. Run the focused gates that cover your change; [`docs/testing.md`](docs/testing.md)
   names them. Do not start the full suite for a narrow fix.
5. Run the readability, architecture and public-surface gates
   ([`docs/REVIEW.md`](docs/REVIEW.md)).
6. If your change alters a capability, blocker, milestone or public roadmap,
   update [`src/data/capabilities.json`](src/data/capabilities.json) and
   [`src/data/project.ts`](src/data/project.ts) in the same change, then run
   `npm run check`, `npm run build` and the site consistency tests. The site is
   a public product surface: a stale status page is a release defect, not a
   cosmetic one.
7. Open a merge request describing the behavior change, the evidence behind it
   and how it was validated.

## Evidence standard

- State what was measured, on which profile, and how it was verified.
- Label the claim `CONFIRMED`, `INFERRED` or `UNKNOWN`.
- Put the proof in an evidence document under `docs/research/` or
  `docs/reverse-engineering.md`, not in production source or in a pull request
  comment.
- Production source carries semantic comments only: what the code does, why an
  invariant holds, and what a reader must know that the code cannot say.

## Source style

- Prefer a name that is supported by evidence. Where a name is a guess, say so
  in a comment or leave the `_raw` suffix in place.
- Do not duplicate codec, format or address logic that already exists as a
  helper.
- Fail closed. A refusal with a stated reason is better than a silent guess.
- Match the surrounding file's conventions.

## Legal

The Webfoot SDK and the other original code in this repository are licensed
under the [Mozilla Public License 2.0](LICENSE). By contributing you agree that
your contribution is licensed under the same terms. Third-party material keeps
its own licence and is recorded in
[`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md).
