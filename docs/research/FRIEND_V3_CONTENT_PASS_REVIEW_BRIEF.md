# Review brief: FRIEND-V3-CONTENT-PASS-001

Worktree: the ticket worktree. Candidate `f7e21ec8ef97d7a723ec165bf9abdd945be6d987`.
Baseline `origin/master` `0fa1aa70fe22aecb4aa58d6e3c19098f14f10b92`.

## What the ticket had to do

Apply owner-approved content to a private, locally supplied DBZ: Buu's Fury image
(the "friend v3" build), on top of an existing 451-record spoken-dialogue rename
pass, without disturbing the stable image:

1. original Bulma -> Tulma, with Tulma as Bulma's identical twin and no marriage
   line, preserving the separate Chi-Chi -> Bulma identity;
2. Great Saiyaman -> Great Soyman across all named references;
3. the four spoken records that still say `Bulma` where the closure says `Chi-Chi`;
4. correction of contradictory Z-Fighter scan biographies;
5. character-name consistency across cutscenes, dialogue, biographies, quests and
   menus;
6. enumeration of chapter titles and surprise-dialogue work needing owner-authored
   content;
7. preservation of the 451 renames, credits, graphics, level edits and crash fixes;
8. validation and a Kibito runtime regression.

Acceptance requires the existing token/splice system for offset-sensitive text, and
no unintended change to unrelated records.

## The diff to attack

`git diff 0fa1aa70..f7e21ec` covers two documents, one tool, one test file. The image
itself is NOT in the repository (it is a private, ignored artefact); its identity is
recorded in `docs/research/FRIEND_V3_CONTENT_PASS.md` as
`b3344a3fed42f13c34bdd28d74463e1f6a0d3e071f2a3cd159f73ef68e5885a7`.

## Claims to attack, in priority order

1. **The span rule.** `tools/research/apply_friend_v3_text_edits.py` claims a site's
   span is its own text plus its own terminator, that nothing beyond it is written,
   and that this cannot reach a neighbour. An earlier version measured the span as
   the distance to the next table-named string and silently erased 492 bytes of an
   orphaned retail biography. Try to construct a site where the current rule still
   over-reaches, or where the stray-byte check is blind.
2. **The guards.** Digest gate, slot-to-offset cross-check, expected-text check,
   over-length refusal, stray-byte refusal. Find a path that writes without passing
   one of them, or a check that can pass while the write is wrong.
3. **Report truthfulness.** The report is provenance. Can it name a slot the bytes
   did not come from, or omit a byte it changed?
4. **The blocked item.** The record claims the four spoken records cannot be closed
   because no tokenisation fits `Chi-Chi` into the 5 units `Bulma` occupies, and
   because the authoring registry does not carry the friend image's records. Verify
   or refute each half.
5. **Prose-versus-code.** Two false comments survived one revision in this file
   (a "zero-padded" write that no longer zero-pads, and a claim that the
   neighbouring string starts at the span's end). Hunt for any remaining comment
   that the code contradicts.

## Test policy

Do NOT run the project test suite. Only these are permitted:

- `python -m pytest tests/unit/test_friend_v3_text_edits.py -q`
- `python -m pytest tests/unit/test_dialogue_token_splice.py -q`

Do not read, modify or move anything under `roms/` or any other worktree. Do not
run mGBA. Report findings with evidence and a PASS or BLOCKED verdict.
