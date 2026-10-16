# FRIEND-V3-WT-SPLIT-CONTAINER-001, release 2: independent review record

Required by `docs/REVIEW.md`, which asks for the scope reviewed, the reviewer's independence,
the verdict, the findings and their resolution, the validation performed, and the remaining
uncertainty.

## Scope and independence

The whole branch, `917e6748d3428ed19304536b59490b40b3c07654`..`9c92fb3ef89ecb64c2f6ed4859931e0744a5766d`.
The reviewer is a separate lane that did not implement the change and reads it fresh. It read
`docs/REVIEW.md`, the diff, the route documents, the builder, both verifiers, the planner, the
observer and its allowlist entry, both unit tests, `handles.py`, `compressed_dialogue.py` and
`dialogue_repack.py`.

**Its one stated limit, kept rather than papered over:** that session had no shell, so it could
not run `git rev-parse`, hash an image, or compute a byte diff. Every number it used came from
tracked sources or the private artifacts under `build/`. The two measurements it named as
outstanding were run here and are recorded below.

## Verdict

**APPROVE WITH NON-BLOCKING NOTES.** No CRITICAL or HIGH finding.

## Findings and resolution

| # | sev | finding | resolution |
| --- | --- | --- | --- |
| 1 | MEDIUM | the release-2 run ended by closing the window, so the observer's shutdown summary and `marker.txt` were never written; the document quoted numbers not reconstructible from the run's own files | the runtime record now names the files it quotes (`route.csv` last row `24420,1033711,51,8,51,0x08090010,138`, and `sites.csv`) and states that no un-written file is used |
| 2 | MEDIUM | the runtime record said the log's text column was "the units the copier was about to take"; the observer reads them from the resolved container, not from the copier | corrected to "the units the record's own handle names, read back from the resolved container at container + 8 + start", and the table now says the log's semicolons are the log's substitution for commas |
| 3 | MEDIUM | the covering record `3:6232:3872` keeps its old handle and old text, and no check covered that | measured: it has exactly one handle site, at file `0x2FE434`, carrying a valid record word, and it is not repointed. Recorded as an **open item** for release 3 in the release record, with the mechanism as evidence and "nothing reads it" as inference |
| 4 | MEDIUM | the verifier's wording check was circular: it compared the decoded text against the manifest the same builder wrote | the verifier now imports the owner's row table from the builder and recomputes the expected text, prefix and passage substitution included; the manifest is no longer an input to that check |
| 5 | MEDIUM | the unit tests discriminated three of the eighteen wordings | the test now asserts all eighteen wordings and row 18's presence; PASS |
| 6 | MEDIUM | the release record named an artifact file that does not exist | corrected to `v3-wt-split-a.gba` |
| 7 | LOW | one sentence said slot 7 "carries none inside a payload and 9 elsewhere", which reads as a contradiction | reworded: "slot 7 carries no word inside a payload, and nine elsewhere" |
| 8 | LOW | the release table was headed "the fifteen rows" and listed eighteen | headed "the eighteen World Tournament rows", with a line saying three are no-change |
| 9 | LOW | a builder branch that could never fire | deleted |
| 10 | LOW | the verifier printed "the other 63 table slots are unchanged" while comparing slot words only | now says what it compares and that the unchanged table basis is what makes the comparison sufficient |
| 11 | LOW | the "one handle site per row" claim rested on one scanner | measured: each of the fifteen handles occurs in the base image exactly as many times as the inventory reports sites. 15 of 15, no second carrier |
| 12 | LOW | the runtime log normalises commas and the document did not say so | stated in the runtime record above its proof table |

## Validation performed

- The independent byte diff the reviewer could not run: 62 differing bytes in the shared range
  across 17 runs, 2,036 appended bytes, **0 stray bytes** outside the declared spans.
- The hardened verifier: VERIFY PASS with the expected text recomputed from the row table.
- `tests/unit/test_friend_v3_world_tournament_rows.py`: 4 passed.
- The two artifacts reproduce byte-identically: both `0b5ac8f4…`.
- The pre-review gates: `public_surface --all` 0 findings, `architecture` 0, `readability --all`
  0, `public_release` 0 findings.

## Remaining uncertainty, carried forward

1. Whether any scene reads the covering record `3:6232:3872` directly. Unresolved, and the most
   consequential unknown in this release. Release 3 item.
2. The nine record-shaped words elsewhere in the image that carry selector 7 now resolve to the
   appended container. Their spans were never checked against a 2,028-byte container, and no
   scene in the measured run resolved them.
3. The appended region reads because the emulator serves the whole file past the header's
   declared 8 MiB. An emulator behaviour, not a hardware claim, and no new kind of address
   relative to the six containers the base image already carries past 8 MiB.
4. Row 18's announcement is static-verified only; the driven run did not reach it.
5. The reviewer's own limit: no shell, so its byte-level numbers were derived from source and
   the manifest rather than measured. The measurements it named were taken here.
