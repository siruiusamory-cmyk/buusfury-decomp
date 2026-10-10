# Review brief: FRIEND-V3-TEXT-AND-DIALOGUE-PASS-001, second review

This is the review request for the change range `59203721..HEAD`. The first review of
`fb121791` returned BLOCKED with five findings; this round asks whether those five are
closed and whether the new material holds. Read this file from the bundle.

## What this ticket is

Under mission `FRIEND-V3-PLAYTEST-001`, one data-side ticket for the customized Buu's Fury
image: the approved text batch, a trailing-pad dialogue repair, and the tooling that
produces them. The owner has separately reserved all creative dialogue wording; none of it
is in this range.

## The five findings from the first review, and what was done

| # | finding | change |
| --- | --- | --- |
| B1 | a 20 KB slice of the image's real dialogue stream was committed as a test fixture, against `docs/ROM_SAFETY.md` | the fixture, its builder and the test that used it were removed. Confirm nothing in the range decodes as game dialogue |
| B2 | `dialogue_repack.main()` wrote handles from half values (`pack_handle(sel, start // 2, len // 2)`), corrupting every handle the default path rewrote | it re-authors the handle in bytes via `handle.replace(...)`, the same way its relocation branch did |
| B3 | `padtrim001_render_watch.lua:145` was not valid Lua | corrected; the file parses under `luaparser` |
| B4 | `inject_mgba_lua.ps1` appeared to be a whole-file line-ending conversion | the committed blob is LF and `git diff --ignore-all-space` against the parent is 12 insertions: the allowlist entry |
| B5 | neither writer refused to overwrite its own input, and neither staged its write | both call `ensure_not_source_alias` and stage, read back, then publish |

## What to judge

1. **Are B1 to B5 actually closed?** Re-derive each from the range; do not take the table
   above as evidence.
2. **The trailing-pad repair's safety claim.** `tools/research/trim_dialogue_padding.py`
   shortens a record's handle `decoded_length` by its trailing pad and asserts no other
   record's span can read differently, because the pad bytes stay in the container. Attack
   that: is there a way for another record to be affected?
3. **`tools/webfoot/dialogue_repack.py`.** `plan_group` refuses when overlapping records
   claim different characters for the same unit. Confirm the refusal is real, that no path
   writes after it, and that the module is not wired into any write path of the derivative.
4. **The build chain.** `tools/research/build_friend_v3_text_derivative.py` starts from the
   pre-BOOST foundation `a4c12a95818cab2781165658d25f2463bc6fe0f87040620a7c89f0034c5b49db`,
   refuses any other base, and checks that the BOOST image differs from that foundation only
   inside the base-stat table. Is that check sufficient to keep BOOST-only stats out of the
   derivative?
5. **Any claim the evidence does not support.** In particular: the tracker rows A13 to A18,
   and any docstring that says a behaviour is proven when only a static read supports it.

## Recorded gaps, so they are not mistaken for overclaims

- **No unit test for the trailing-pad repair.** Four synthetic fixtures failed; the failure
  and its likely cause are recorded in Adja `29e35270`. The repair's live coverage is
  `verify_trim.py` (four checks on a real image) and byte-identical reproduction of a
  candidate digest. Treat the missing test as an accepted, stated gap.
- **No runtime text capture.** Static verification only. The derivative is proven to boot
  and render a dialogue box by screenshot, and two instrument facts were measured on the
  packaged 0.11 build: `emu:setBreakpoint(callback, address)` is the accepted signature, and
  `emu:readRegister("pc")` does not return the program counter (one distinct value across
  240 samples while a breakpoint on a dispatch thunk fired 5,954 times).
- **The World Tournament rewrite is owner-authored and is NOT in this range.** Its records
  are located and preserved untouched.

## What this range does not contain

No ROM, image, savestate or capture. No capability or public-surface change. No change to
any tracked authority document. The derivative artifacts live under the ignored `build/`
tree and are not in git.
