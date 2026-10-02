# Code review

The review gate for this repository. It applies to every nontrivial
code-bearing change, including SDK, build, format, relocation, VM, runtime
tooling, packaging, CI and deployment changes. Apply it by impact, not by
directory name.

A typo, a wording-only documentation change or a similarly trivial
non-behavioral edit may use a proportionate lighter review, and its closure
record must say why the full gate was not warranted.

## Independence

The implementation is frozen before it is reviewed: never review a moving
target.

The reviewer must not have implemented the change. They inspect the actual
diff, the relevant surrounding code, the tests, the architecture and the
underlying static or runtime evidence. The implementer's closure report is
orientation, not authoritative evidence.

Prefer a reviewer with fresh context, someone who did not implement the change
and is not carrying the implementer's assumptions, and where practical prefer a
reviewer whose strengths differ from the implementer's, so the review probes
what the implementation was least likely to check. This is not a seniority
ranking. Disagreement is resolved by evidence, never by authority.

## The four pre-review gates

A nontrivial code-bearing change must pass all four before review closes:

| Gate | Command | What it protects |
| --- | --- | --- |
| Source readability | `python -m tools.quality.readability --changed <rev>` | research narrative and dead scaffolding in shipped source |
| Architecture and repository purity | `python -m tools.quality.architecture` | where source, tests, evidence and configuration are allowed to live |
| Public surface | `python -m tools.quality.public_surface` | what the repository says about itself, and to whom |
| Built site | `python -m tools.quality.public_surface --built dist` and `python -m pytest tests/unit/test_site_consistency.py` | what a visitor actually receives, and whether the page still agrees with its own data |
| Independent review | this document | correctness and everything a test cannot see |

A gate may be run over the whole tree or over the changed set; both forms are
deterministic and both are documented by the tools themselves. A hard finding
is a failure. An advisory is a reading list, and a reviewer decides whether it
matters. The public-surface screens carry justified exceptions in
`config/public_surface_exceptions.json`; an exception is a written reason, and a
test asserts that every one is still load-bearing.

## What the review examines

The first pass produces findings and does not edit code. It actively looks for
defects rather than summarizing the implementation, and covers at least:

- **Correctness:** claimed behavior, edge cases, assumptions, bounds, alignment,
  ownership, pointers, lifetimes, state and safe failure paths.
- **Architecture and product alignment:** alignment with the shipping SDK, the
  concrete authoring blocker being addressed, reuse of existing abstractions,
  and no elevation of prototypes or research tooling into an authority they do
  not have.
- **ROM and data safety:** the canonical input stays immutable, writes are
  attributed and provenanced, relocation is complete, capacity is verified,
  bounds and alignment are correct, no candidate evidence is waived and no
  proprietary artifact reaches source control.
- **Determinism:** identical canonical input plus project state yields identical
  output; planning does not consume project edits; ordering, identifiers and
  serialization are stable.
- **Tests and evidence:** behavior-level proof, discriminating positive
  controls, tested failure paths, evidence-based assertion changes, and no test
  deleted or weakened merely to pass.
- **Compatibility:** intentional project-format, API and CLI effects, and
  documented failure or migration for old projects and authoring workflows.
- **Maintainability:** proven names, labelled speculation, no needless special
  case or duplicated codec or format logic, useful blocker errors, and comments
  and documentation that match measurement.
- **Public-release readiness:** secrets, proprietary data, dependency and
  licence posture, temporary probes and artifacts, and accurate user-facing
  capabilities and limits.

## Verdicts and findings

The verdict is exactly one of:

```text
APPROVE
APPROVE WITH NON-BLOCKING NOTES
BLOCK
```

A blocking finding gives its severity, file and location, the observed problem,
the impact, concrete evidence and the smallest recommended correction.

| Severity | Meaning |
| --- | --- |
| `CRITICAL` | corruption, a safety or provenance failure, secret exposure, or an invalid result |
| `HIGH` | incorrect behavior, architecture, determinism, relocation or allocation, evidence, or a serious regression |
| `MEDIUM` | a real correctness, compatibility or maintainability issue, due before public release |
| `LOW` | cleanup or clarity |

Style preference alone is not a blocker.

## Resolution

On `BLOCK`, the implementer fixes the accepted findings and runs the smallest
sufficient focused validation. The reviewer inspects the fix and explicitly
either changes the verdict or lists the remaining blockers. A narrow correction
does not automatically rerun the full suite; shared or uncertain corrections
follow the blast-radius policy in [`DEVELOPMENT.md`](DEVELOPMENT.md).

If a reviewer makes a small mechanical edit themselves, record it explicitly and
revalidate it rather than treating it as reviewed by default.

## Closure sequence

```text
implementation plus any public-progress change
-> focused validation
-> implementation frozen
-> readability, architecture and public-surface gates
-> independent review
-> review fixes if needed
-> reviewer sign-off
-> final integration gate when the blast radius warrants it
-> confirm what the change does to the public capability list
-> stage explicit paths
-> commit / merge request / push
-> verify the live site when the capability list changed
-> closure
```

For substantial production changes, prefer a feature branch and a merge request,
require its pipeline and the independent review, then merge. Do not force a
merge request for a trivial documentation-only change, do not change repository
visibility, and do not enable force-push.

## Repository relevance

Before a broadly announced public release, run a separate repository-wide
release-readiness review, independent of per-change review. It examines
architecture coherence, packaging and installability, dependencies and licences,
secret and proprietary leakage, dead and debug code, stale documentation,
public APIs, CI, portability, contributor onboarding, reproducibility, test
gaps and the release and licensing posture.

That review includes a **public repository relevance** pass over every tracked
artifact: would a Legacy of Goku modder, ROM hacker, contributor or SDK
maintainer reasonably benefit from this being public? If not, classify it for
exclusion rather than retaining it as a development by-product. Preserve
anything that materially supports reproducible reverse engineering, evidence,
ROM safety, testing, contributor workflows, known formats, usable emulator
instrumentation or engine research.

Report each candidate with `path`, `current purpose`, `community relevance`,
`KEEP / MOVE / TRIM / REMOVE / IGNORE`, `reason`, and `blocking before public
sharing? YES/NO`. Produce the inventory before making changes. Any possible
proprietary content, ROM-derived asset, save, state, secret or credential is a
high-priority release blocker.

## Record

Keep a concise review record with the change: the scope reviewed, the reviewer's
independence, the verdict, the findings and their resolution, the validation
performed, and the remaining uncertainty. Omit empty prose that adds nothing.
