# Proving the map-transition data model: integration notes

The condensed record of the transition-format pass: the supported family, what was
implemented, the acceptance measurements and the questions left open.

## Baseline drift, recorded rather than papered over

- **Requested baseline:** `ad03b895a419db3e8960b8297e92985011b3ba52`.
- **Actual record start:** `a commit since folded into its successor`.

`a commit since folded into its successor` **was and still is** current `origin/master` at record start, verified
two ways: local `master` and `origin/master` were both `a commit since folded into its successor` (0 ahead, 0
behind), and a live `git ls-remote origin refs/heads/master` returned
`a commit since folded into its successor`. The reflog shows `ad03b895a419db3e8960b8297e92985011b3ba52` sitting
four steps back as an older `origin/master`
(`refs/remotes/origin/master@{4}: fetch origin --prune: fast-forward`).

The **13 commits** between them are two separately closed records, not this
record's work, and history was not rewritten to make the requested baseline
appear current:

| Commits | Record |
| --- | --- |
| `2ae0d7d51016414a10e6048489d3a558e72d5e66`, `e0f2c997fe36f64849cff6160549df999f8e9660` | `MAP-GFX-DIAG-001`, diagnose the map graphics corruption, plus its documentation-note commit |
| `b3ddb94dd5c682f91b81ad0440bb21fc85011490`, `a commit since folded into its successor`, `93f04645878ea0cac6d4010493a553f5991655df`, `2d97fdc923da96043ebcbc73f7eba300c94f8723` | `WEBFOOT-LZ-LITERAL-BASE-001`, literal-base reset correction, merged and closed |
| `939e16cc7371f4bc57299bb6242150772949b67a`, `a commit since folded into its successor`, `5742353528484f473c5fdef8842eb8a48168c391`, `a commit since folded into its successor`, `bde93c6b4c6f14fee1535fa35f93ef632f287448`, `1551a275c01f7d953dc8f8f57b6dd4804a2ee33e`, `a commit since folded into its successor` | `TILESET-COMPOSITOR-001`, inferred authoring atlas, merged and closed |

`e0f2c997fe36f64849cff6160549df999f8e9660` is attributed to `MAP-GFX-DIAG-001` and not to
`WEBFOOT-LZ-LITERAL-BASE-001`: it touches only
`docs/research/BUU_MAP_GRAPHICS_DIAG.md`, and that record's own closure record
names `2ae0d7d51016414a10e6048489d3a558e72d5e66` plus its documentation-note commit `e0f2c997fe36f64849cff6160549df999f8e9660` as its baseline. The
two landed interleaved, which is why the commit order alone is misleading.

## Goal

Determine exactly how the supported Buu's Fury map transitions are represented,
and give the SDK one production authority for that family - without inventing any
field the evidence does not establish, and without claiming support the
measurements do not carry.

## Supported family

The 24-byte record a map's **selector-1 root** reaches through the root's `+0x40`
count / `+0x44` array of 4-byte record pointers, restricted to the two class
words the canonical corpus measured.

| Property | Result |
| --- | --- |
| Record size | 24 bytes, engine-accessed extent `+0x00..+0x17` |
| Source map identity | the `MapEntry` table index owning the selector-1 root |
| Destination map identity | the two independent bytes at `+0x11` (high) / `+0x12` (low) |
| Source position | `+0x08`/`+0x0A`/`+0x0C`/`+0x0E`, four `u16` forming two ordered intervals |
| Destination position | **not in the record**; not modelled |
| Type / flags | `+0x00` a called constructor word, semantics of both classes UNRESOLVED |
| Enumeration | explicit count, no terminator; array index is the identity |
| Record count | 735 records over 452 map identities; 348 maps carry at least one |
| Sharing | 0 shared records in this image; a second claim is refused, not assumed impossible |

## Implemented

| File | Role |
| --- | --- |
| `tools/webfoot/formats/map_transitions.py` | pure codec: layout, `TransitionRecord`, positional `TransitionRegion`, byte-exact round trip, two controlled edits, fail-closed `validate()` |
| `tools/webfoot/map_transitions.py` | SDK authority: enumeration, destination resolution, `TransitionIdentity = (source map, index)`, staged edits, `changes()`, `plan()` |
| `tests/unit/test_map_transitions.py` | 54 portable tests over a synthetic image built from the measured format |
| `tests/integration/test_map_transitions_rom.py` | 15 ROM-gated tests, read-only, `LOGX_CANONICAL_ROM` overridable |
| `MAP_WARP_FORMAT.md` | the evidence record |

Editable fields are exactly two: the destination `MapEntry` key and the record's
two ordered interval pairs. The class word, the invariant `+0x04` word and the
UNRESOLVED `+0x10`/`+0x13`/`+0x14`/`+0x16`/`+0x17` bytes are carried
byte-for-byte and never authored.

Refused before any plan exists: an unmeasured class word; an unordered or
degenerate region; an unresolvable destination key; two maps sharing one lookup
key; a null, unaligned or out-of-image selector-1 source, root, array element or
record address; a count and array pointer that are not null together; a record
reached by two maps; two records whose 24-byte extents overlap.

## Acceptance, as measured

| Criterion | Result |
| --- | --- |
| Canonical enumeration | **MET** - 735 records, 452 identities, 348 non-empty maps, max 14, deterministic order |
| Unchanged round trip | **MET** - 735/735 byte-identical; a no-op pass emits 0 differing bytes |
| Known source/destination decode | **MET** - map 38 -> 39, map 39 -> {38, 40}, map 33 -> 34; 735/735 destinations resolve |
| Controlled destination edit | **MET** - exactly `+0x11`/`+0x12` change, both key bytes, decoded destination correct |
| Controlled region edit | **MET** - exactly `+0x08..+0x0F` change, decoded region correct |
| Unrelated records unchanged | **MET** - every other record and every byte outside the record is identical |
| Non-square / asymmetric coordinates | **MET** - `map:0039/transition:0001` intervals `(592, 601)` and `(136, 241)`, all four endpoints distinct, lengths 9 and 105 |
| Fail-closed invalid map / coordinates / type | **MET** - asserted portably and against the canonical image |
| Canonical ROM unchanged | **MET** - SHA-256 `940ad5f0…f059e` before and after; the input is refused as a write target |
| Mutations M1-M4 | **MET** - each breaks the named regression; see the evidence record section 7 |

## Independent verification

One pass, independent context, an independent local review headless in a clean detached worktree at
the frozen candidate. Job `the review job`, local session
`2a8c3964-c141-4522-b3c0-e32e935e27cc`, exit 0, 308 s, $2.52, verdict read from
`local_headless`.

**Verdict: `APPROVE` - zero blocking findings, zero non-blocking notes.** The
verification pass ran the two named test files itself against the canonical image through
`LOGX_CANONICAL_ROM` (69 passed) and re-checked the image hash either side.

The three probes it was invited to attack hardest, and its conclusions:

1. **The selector-1 route's second hop.** `_resolve_root` taking `word[0]` and
   requiring it to be a non-null aligned in-ROM address is *equivalent* to the
   accepted route's `run[0] if run else 0` and **strictly stronger** than
   `formats.map_graphics.read_map_entries`' unchecked `reader.u32(source)`. Not
   inspecting `word[1]` is correct, because the route is `word[0]`, not "verify a
   run". **Sufficient.**
2. **A directly constructed record with an unordered region can serialize.**
   Confirmed by probe, and judged **not a defect**: no authoring path reaches it -
   the loader validates every record in its second pass and both edit methods call
   `validate()` - so the bypass requires a caller to hand-instantiate a frozen
   dataclass, which is not the authoring model.
3. **Zero-area refusal, the one-family framing and the `_KEY_FIELD_NAMES`
   tripwire** all read as corpus-invariant or tripwire language rather than
   engine law, and the guard passes against the current `map_entry` layout.

**Cloud review: NOT RUN - readable verdict unavailable.** `cloud_attach` is
UNAVAILABLE on this account, so a cloud session would have produced no locally
readable verdict; the launch was refused as unreadable rather than paid for, and
`require_readable_verdict` was enforced on the local launch.

## Boundaries observed

No Workbench UI. No project authoring, project format or builder change. No
runtime capture, emulator launch, save or state write. No capability-registry or
site change. No CLI surface. No GUI serializer. No raw-offset authoring API. No
renaming of positional fields to X/Y. The canonical image was read-only
throughout.

## Still UNRESOLVED

- the meaning of the two constructor/class words;
- which of the two region intervals is horizontal;
- the region endpoints' unit;
- the meaning of the invariant word at `+0x04`;
- the semantics of `+0x10`, `+0x13`, `+0x14`, `+0x16`, `+0x17`;
- where the destination position comes from;
- the origin of the LOGExtractor `+8` viewer adjustment.
