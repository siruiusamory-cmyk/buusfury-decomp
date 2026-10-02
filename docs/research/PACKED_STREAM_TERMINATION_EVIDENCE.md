# Packed-stream termination evidence

The packed-stream termination rule, the measurements that resolved it, and the
encoder and write-path remediation built on that ruling.

## 1. The evidence question, resolved (Phase 1)

**CASE A: the retail decoder terminates a packed stream on an explicit escape and
on nothing else.** `CONFIRMED` by two independent disassemblies of the canonical
image plus a positive census finding no destination comparison, adjudicated in
[resolution](../research/PACKED_STREAM_TERMINATION.md) §2.1:

- entry ROM `0x087B79E4`, executed from IWRAM `0x03000040` through the Thumb to ARM
  veneer `0x08049120`;
- the decoder takes exactly `(source, destination)`; `container[+0x04]` is read on
  the kind-0 *stored* branch only;
- of the thirteen comparisons in its body, **none names the destination cursor**, so
  there is no destination bound and no output count;
- the escape is **twelve zero bits** at a token boundary: prefix `000`, seven-bit
  field `0000000`, two-bit selector `00`;
- consequently the decoder can read source words past the nominal packed payload
  until it meets that escape.

The audit's "two mutually exclusive rules" is real but is not an engine ambiguity:
one claim was about the engine, the other about the host tool, and the canonical
corpus satisfies both at once. The repository's wrong side of that contradiction is
corrected in §6 below. **`INFERRED`, never claimed as observed:** that a particular
authored stream caused visible or runtime memory corruption in a retail execution.
No runtime-consequence experiment was run, and none is required for closure.

## 2. The defect, measured before it was changed

`webfoot_lz.pack` wrote data tokens and then let `_WordBitWriter.finish` zero-pad
the final partial word only (`while self._count:`), and it never emitted the escape.
Measured over 32,202 synthetic payloads (Phase-1 probe `probe_flush.py`):

| Zero padding emitted by the pre-fix `finish()` | Share |
| --- | ---: |
| 0 - final token lands exactly on a word boundary | 0.1% |
| 1..11 - the escape would need bits from following bytes | 34.8% |
| >= 12 - the padding itself decodes as the escape | 65.1% |

The named pre-fix case, frozen as a test fixture, is `pack(b"A" * 64)`:
`0200000040000000fe53d020` (12 bytes, declared 64, **0 padding bits**). The ordinary
host decoder accepted it; the strict marker-required reader refused it. Roughly one
third of `pack` outputs were in that state, so a payload's validity depended on the
bytes that happened to follow it - allocation padding, expansion `0xFF` fill, or the
next object.

## 3. The fix: one production rule, in the codec layer

`tools/webfoot/formats/webfoot_lz.py`:

- `_WordBitWriter.write_end_marker()` writes the escape through the existing bit
  writer: `self.put(0, 12)`. It is a token, so it is emitted **at a token boundary**,
  not appended as zero bytes after finalization.
- `pack` emits it **after the final data token and before** `finish()` pads the
  word, so the emitted order is data tokens, escape, padding. Every output is
  self-terminating: it does not depend on the final token's alignment, on padding,
  or on anything after the payload.
- `validate_retail_termination(data, offset)` is the production owner of the
  postcondition, and the only implementation of it. Through
  `unpack(..., require_end_marker=True)` and `_unpack_stream(..., require_end_marker=True)`
  it requires, in one decode: exactly the declared output; a reachable explicit
  escape; that escape at exactly the declared boundary; and no malformed or
  truncated token before it. An early escape therefore fails (the length comparison),
  as does a stream that never reaches one.
- The escape scan is bounded by `_marker_scan_limit(expected) = expected + expected//4 + 4096`.
  A fixed 64 KiB ceiling was tried first and produced a **false refusal** on a valid
  incompressible payload whose packed form exceeds 64 KiB; the bound is derived from
  the declared size because this encoder's literal-only worst case is nine bits per
  byte. `test_a_payload_whose_packed_form_exceeds_64kib_still_validates` pins it.
- No production module gained a dependency on `tools.export`; the validator lives in
  the codec/formats layer.

Marker cost is bounded and measured, not assumed: **nothing or one packed word**.
`test_the_marker_costs_nothing_or_one_packed_word_and_never_more` asserts the delta
set is exactly `{0, 4}` over the generated corpus.

## 4. Both production write consumers guard the rule

**A. Compressed dialogue (the shipped write path)** -
`compressed_dialogue._prepare_replacement` now runs
source -> corrected `pack` -> `validate_retail_termination` -> size/fit decision ->
`ByteChange` / relocation plan (`:112`, `:119`, `:133`, `:142`, `:154`). An invalid
stream raises `CompressedDialogueError` naming the target, **before** any allocation
request or plan exists. There is no warn-and-continue, no expected-length-only
acceptance, and no assumption that expansion fill will terminate the stream.

**B. Sprite graphics payload planner** - `plan_graphic_payload` invokes the same
production rule (`sprite_graphics.py:673`) and fails closed with `SpriteFormatError`
before the capacity comparison. It holds no independent marker parser. The sprite
packed-payload path still has no GUI or CLI caller, and **no new capability is
claimed** for it; the capability count is unchanged.

## 5. Final encoded size owns fit and allocation

Both consumers compare `len(payload)` - the final encoded length, terminator and
final padding included. No pre-marker bookkeeping survives anywhere in the tree.
Tested: an exact fit stays in place; relocation uses the corrected size; a
payload that passes the rule but cannot be allocated still fails cleanly with
`InsufficientSpaceError`; and a payload refused by the rule never reaches the
allocator. For the shipped dialogue target the corrected encoded payload is
unchanged at 17,932 bytes against a 16,856-byte retail allocation, so it relocates
to generated expansion exactly as before.

One deliberate asymmetry is documented rather than hidden: the sprite planner
bounds a replacement by the **original** container's declared-size-terminated
extent, which does not credit that container with an escape word that may belong to
its neighbour. A corrected payload whose own escape begins a fresh word is one word
larger than that bound and is refused. Refusal is the honest answer; the alternative
is a write into a neighbouring asset.

## 6. Engine, host and validation semantics are stated distinctly

- **RETAIL ENGINE:** terminates a packed stream on the explicit escape marker, and
  has no declared-size termination and no destination bound.
- **HOST SHIPPING DECODER:** may use the declared expected output length as a
  safe host-side bound; it was not rewritten to mimic the engine's unbounded reads.
- **STRICT / RETAIL VALIDATION:** proves an explicit escape exists at the correct
  output boundary.

The stale statements that attributed declared-size termination to the engine were
corrected **with their evidence rather than deleted**:
`tools/export/webfoot_strict.py` (`decode_packed`'s docstring, which contradicted
that module's own docstring, and the "why the check is opt-in" paragraph),
`tests/unit/test_asset_export_strict_lz.py`,
`tools/research/webfoot_codec_reference.py`'s `stop_on` documentation, and the
"seventeen bits" marker length plus the moot precedence question in
`docs/research/LOGX_CODEC_PROVENANCE.md` §8.4, §9 and §23.

## 7. Phase-1 measurement correction, recorded rather than rewritten

The Phase-1 record gives `pack(b"A" * 64)` a packed length of **292 bytes** in the
resolution's §2.3 and in the separate investigator memo. Re-measured against the untouched
pre-fix module at the START SHA, the value is **12 bytes**
(`0200000040000000fe53d020`), with `fill = 0` and 0 padding bits - every other
property §2.3 states about that case holds. The 292 figure belongs to the 256-byte
random payload in the first row of the investigator's own probe output
(`<temporary directory>\cqa02\flush.txt`, section B), whose `fill = 0` it shares; the figure was
carried across rows. A 64-byte payload cannot reach 292 bytes under this encoder,
whose literal token is nine bits.

Resolution **§7** records this explicitly. The Phase-1 numbers were **not** silently
edited to hide the error, and no Phase-1 conclusion changed. Before commit the
three Phase-1 documents also received one repository-required Markdown change: the
em dash (U+2014), which this repository's commit hook rejects, was replaced by
ordinary punctuation in 94 places. Wording is unchanged - the pre-normalisation
SHA-256 of both investigator memos equals the hashes the record recorded for Phase 1
(`A80179A4...`, `86940F2F...`), and every line's word sequence is identical apart
from one table cell whose lone dash became `-`.

## 8. Evidence levels preserved

`CONFIRMED`: the retail decoder's termination rule; the explicit marker grammar; no
declared-size termination on the packed path; no destination-bound comparison in
that path; that the pre-fix `pack` could emit streams lacking an in-stream marker;
that the corrected `pack` self-terminates; and the canonical-corpus property in §10.

`INFERRED`: that a specific affected authored payload would cause visible or runtime
memory corruption in a retail execution. **No mGBA corruption demonstration was
performed and none is claimed.**

## 9. Tests and mutation evidence

Added or inverted, all portable and synthetic:

- **The pinned discriminator.** `test_the_a64_flush_payload_is_the_pinned_cqa_02_discriminator`
  holds both frozen fixtures (`...fe53d020` and `...fe53d02000000000`). The pre-fix
  bytes decode under the host rule and are refused by the validator; the corrected
  bytes pass both and decode to `b"A" * 64`.
- **Marker grammar at the bit level.**
  `test_the_end_marker_is_twelve_zero_bits_written_at_the_token_boundary` asserts the
  writer consumes exactly twelve more bits, that they are zero, and that the token
  bits before them are untouched.
- **Universal postcondition.** `test_every_packed_payload_is_self_terminating` runs a
  deterministic corpus covering empty, one to three bytes, flush/31/32/33-style
  alignments, powers of two, repeats, alternating patterns, ramps and incompressible
  data up to 4 KiB, asserting per input: source equality, validator acceptance, escape
  at the declared boundary, and self-contained termination. No earlier escape can
  terminate early, because the validator consumes tokens in order and stops at the
  first escape, and an early one fails the length comparison.
- **Independent oracle.** `tests/unit/test_logx_codec_reference.py` drives the
  separately written research reader with `stop_on="end_marker"` and requires the
  first escape at exactly the declared size, over its own corpus.
- **Both guards wired.** `tests/unit/test_compressed_dialogue_write_guard.py` drives
  the real shipping entry point `materialize_dialogues` over a synthetic image that
  reproduces the target's measured container-table layout, and includes the positive
  control that its pre-fix payload really lacks an escape. `tests/unit/test_sprite_graphics.py`
  adds the sprite-side refusal, the capacity charge and the self-termination check.
- **The export oracle agrees.** The strict export reader now accepts every `pack`
  output, which is the inversion the old test was pinning.
- **Round-trip unchanged.** `unpack(pack(source)) == source` for every supported
  payload; the escape never becomes decoded output; malformed-input validation was
  not loosened.

Mutation sensitivity (each mutation applied to the frozen tree and reverted, with
file hashes and `git status` confirming the revert; the verification pass repeated M and N
independently):

| Mutation | Change | Result |
| --- | --- | --- |
| **M1** marker removed | `writer.write_end_marker()` removed from `pack` | 12 focused tests fail (13 in the verification pass's run, which included the >64 KiB case) |
| **M2** dialogue guard bypassed | `raise CompressedDialogueError` replaced by `pass` | 2 tests fail: the refusal and the guard-runs-before-allocation tests |
| **M3** marker corrupted | one of the twelve marker bits set | 9 tests fail; permanently pinned for **all twelve** bit positions by `test_altering_any_bit_of_the_marker_defeats_retail_validation` |

## 10. Canonical corpus record

Measured with the **Phase-1 scan thresholds unchanged** (halfword stride, kind in
{1,2}, declared in range, accepted only when the shipping decoder then produces
exactly that many bytes):

| Scan | Structurally valid | Validator-accepted | Refused |
| --- | ---: | ---: | ---: |
| declared `<= 0x4000` | 13,168 | 13,162 | 6 |
| declared `<= 0x10000` | 13,189 | 13,183 | 6 |

The six refusals are the same structurally-plausible-but-longer headers Phase 1
identified (declared 1-2, refused with `literal at output N overruns the declared N`),
and they are refused **identically** by the production validator and the strict
export reader. Validator disagreement: **0**. No canonical stream contradicts the
confirmed rule, and no scanner threshold was widened or narrowed to obtain these
counts. The wide-cap population contains the 65,474-byte dialogue container that the
narrow cap excludes.

## 11. Canonical ROM safety

Canonical image `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`,
8,388,608 bytes, identical before and after every run; its boundary bytes, hole
regions and mtime are unchanged. The ROM-gated tests read a derivative copy placed
in the working copy, which was removed afterwards. No ROM, save, state, dump or
extracted payload was committed; every committed fixture is synthetic.

## 12. Focused validation

- Portable suite: **2,097 passed, 23 skipped, 0 failed** with no ROM present;
  **2,099 passed** with a local derivative copy in place (the two extra passes are
  ROM-gated).
- ROM-gated: `test_graphics_rom.py` **32 passed**;
  `test_webfoot_lz_strict_rom + test_rom_expand_001 + test_decoded_text_rom +
  test_logx_codec_rom + test_graphics_override_build_rom` **40 passed**.
- `compileall` clean; `git diff --check` clean; the independent verification pass ran
  `tests/unit` and `tests/integration` once from its own worktree: 2,125 passed,
  996 skipped, 0 failed.
- The full suite was **not** run manually, per standing policy.

## 13. Finding closure

### CQA-02: resolved

The engine's packed-stream termination rule is stated once, with evidence, in
[resolution](../research/PACKED_STREAM_TERMINATION.md); `pack` emits the
escape by construction; the production validator proves the rule; both production
write consumers invoke it and fail closed; final encoded size drives fit and
allocation; the stale claims are corrected in place; and the mutation checks detect
the critical bypasses. The remediation is integrated to `origin/master` on this
record's merge request.

### CQA-10: **PARTIAL / IMPROVED** (unchanged)

This record touched one write boundary (the packed-payload planner) but did not
close any of CQA-10's recorded debt: the overwrite-policy divergence, the
repository-output policy, atlas atomic publication, or the remaining unguarded
writers. CQA-10 is **not** closed or reduced by this record.

## 14. Scope boundaries observed

No product capability changed and no capability claim was added for sprite
authoring. No other audit finding was touched: CQA-03, CQA-04, CQA-05, CQA-06,
CQA-07, CQA-08, CQA-09, CQA-10, CQA-12 and CQA-15 remain open exactly as the audit
recorded them. `ROM-CAPACITY-AND-ALLOCATION-001` was not started and remains
**BLOCKED** on that set. `WORKBENCH-006` was never read as a baseline, staged,
reset, cleaned, fast-forwarded or branched.
