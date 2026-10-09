# Anchors, allocation and relocation

TOOLKIT-003 is infrastructure. All demonstrated layouts below are constructed
synthetic data, not claims about a commercial game format.

## Portable proof

Run `.venv/Scripts/python.exe -m tools.webfoot relocation-proof` from the repo.
It prints deterministic JSON with anchors, classified references, allocations,
retired regions and write provenance; it performs no filesystem I/O for ROMs.
`tests/unit/test_relocation.py` independently constructs its fixture and checks
the exact bytes, graph, failure gates and file-emission behavior.

The fixture starts with an eight-byte region at file offset `0x100`, aligned
to eight bytes. A declared absolute-u32 reference at `0xC0` points to its start;
a confirmed signed-relative-i32 reference at `0xC4` points four bytes inside it.
The explicit synthetic free declaration is `[0x201, 0x300)`. A growing payload
allocates at `0x208`. Source `0xC0` becomes GBA address `0x08000208`; source
`0xC4` becomes signed displacement `0x20C - 0xC4 = 0x148`. The old eight bytes
remain intact. These are synthetic layout contracts, not newly confirmed game
reference semantics.

## API and trust boundaries

- `layout.py`: `AnchorId` is logical identity; `Anchor` binds it to a `RomRange`
  beginning at a typed `FileOffset`. Kind, owner, alignment, relocatability and
  profile/hash/evidence provenance travel with the anchor. `OwnedRegion`
  reserves occupied or retired bytes. None knows semantic record layouts.
- `profile.py`: optional `free_regions` declarations require explicit
  `file_offset`, positive `size`, `status: CONFIRMED`, and nonempty `evidence`.
  Unknown keys, candidate status, overlap and out-of-bounds declarations fail.
  Profile configuration is trusted; an evidence string is a citation supplied
  by verified research, not something the toolkit can independently prove.
- `RomDocument.from_bytes(image, profile, anchors=..., references=...)` verifies
  exact configured identity before layout access. Every anchor/reference
  provenance must match that profile and base hash. Source bytes must decode
  to the stated anchor plus interior delta. Free declarations must not cover
  initial anchors or reference fields. Metadata does not automatically discover
  content; supplying a layout contract is an explicit trusted backend operation.
- `document.inbound(anchor_id_or_range)` returns a stable reverse lookup view,
  including interior targets. Discovery and rewrite authority remain separate.
- `allocate(profile, requests, occupied=...)` sorts requests by anchor identity
  and free regions by position, then selects the lowest aligned fitting range.
  It is a pure policy primitive; production callers enter through verified
  `plan_relocation`. Empty free declarations cannot allocate. Earlier alignment
  gaps may be reused by later requests if they fit without overlap.
- `plan_relocation(document, requests)` takes logical anchor IDs and serialized
  payload bytes. It verifies the base again, allocates the whole batch, rewrites
  authoritative references, validates the proposed document and returns a
  `RelocationResult`. No partial plan escapes on failure. Semantic consumers
  supply payloads through codecs; they do not choose physical addresses.
- `emit_relocation(document, requests, base_path, output_path, manifest_path=...)`
  plans and validates first, then delegates to `write.emit_image`. The actual
  source file must still match the plan's base hash. Fixed-size stat edits and
  project builds do not call relocation.

## Reference policy

`DECLARED_REFERENCE` means a verified profile/layout contract;
`CONFIRMED_REFERENCE` means explicitly verified research;
`CANDIDATE_REFERENCE` means a numeric/heuristic observation only. Every record
retains its source, target anchor, interior delta, encoding, evidence class and
provenance. A raw numeric match never changes its evidence class.

Two wire encodings are implemented: absolute little-endian u32 GBA ROM address,
and little-endian signed i32 displacement measured from the reference source.
The latter is an extensibility proof, not a claim that any particular Webfoot
field has that encoding. Both validate widths and bounds; no Thumb bit masking,
alignment normalization or guessed encoding occurs.

Source fields entirely inside moved anchors move with them. Relative references
are re-encoded using their new source and target. Shrinks that remove source
fields or interior targets fail. Fields straddling anchor boundaries fail.
An unresolved candidate whose target or source would move blocks the batch and
reports its original source offset. Candidates on unaffected regions survive.
There is no force bypass or numeric-match promotion API.

The optional `scan_pointer_candidates` scans a caller-bounded range for absolute
u32 numeric matches into known anchors. Existing graph source fields are
excluded. It returns candidates; callers add them to the graph before planning.
This scanner does not establish completeness or safety, cannot find every
nonstandard reference, and never rewrites or infers semantics. The graph is
only as complete as its supplied verified contracts and recorded observations.

## Transaction and provenance

All requests in a batch target one original verified image. The output document
is for inspection and validation, not a new trusted base: submit related moves
together. Incremental reopening of modified images and graph persistence are
deferred. Old ranges are retained verbatim and reserved; no reclamation occurs.

The normal write manifest gains a `relocations` block only for relocation. It
records anchor, owner, old/new ranges, payload size/alignment, free-region
evidence and rewritten reference records, including old/new source/target
offsets and classifications. Existing byte changes and base/output hashes are
retained. No paths, timestamps or random identifiers enter the manifest. A
reference between two moving anchors can appear in both anchors' provenance;
the actual byte write occurs once.

Emission rejects input/output/manifest aliases and existing outputs before
writing. It stages complete files, flushes them, and publishes using exclusive
links, with image publication last. Caught staging/publication failures remove
only this invocation's links and temporary files. No partial image is published.
This is not a multi-file crash journal: an OS crash between publications can
leave a complete manifest without its image. An unsupported hard-link filesystem
fails closed; there is no overwrite fallback. Existing images/manifests survive.

## Canonical scope and remaining unknowns

The checked-in game profiles have no verified free-space declarations. Relevant
MapEntry census code explicitly calls its fields candidates; numeric validity
is not relocation authority. No new research was authorized to establish free
space or complete canonical inbound references. Canonical relocation is therefore
omitted. Local-ROM TOOLKIT-001/002 stat/build regressions validate preservation
separately; no mGBA capture, Ghidra analysis or new game-format evidence occurs.

Whole-ROM anchoring, game content adapters, relative game-format contracts,
complete reference discovery, source backends, expansion and reclamation remain
outside this ticket. Unknown game semantics remain UNKNOWN.

## Later registrations

This document describes the infrastructure TOOLKIT-003 built. Since then the
authority for what MAY be relocated has stayed exactly one constant,
`layout.RELOCATION_ELIGIBLE_KINDS`, and the authority for where it may go has
stayed exactly one allocator, `allocation.allocate`. Later tickets added kinds
deliberately, each on a stated argument, and each per-anchor decision is still
made by `layout.relocation_eligible` rather than by membership alone:

- `placement_reference_array` (TOOLKIT-024, TOOLKIT-026);
- `text-string` (TOOLKIT-036, proven per entry by measured inbound count);
- `graphics_container` (GRAPHICS-IMPORT-BOUNDARY-001). A container is a graph
  leaf: the reference walk publishes no reference sourced inside one, so its
  whole inbound surface is the set of `CONFIRMED` piece words that name it.
  Membership is **not** a claim that the published set is every word in the
  image that equals the payload's address; that completeness is `UNKNOWN`,
  which is why the graphics relocation path leaves the original payload bytes
  intact rather than retiring them.
  `docs/research/GRAPHICS_PIXEL_OVERRIDE.md` records the runtime proof that the
  retail engine follows a rewritten graphics reference into allocator-chosen
  expanded storage.

`Addressability` moved with them. `PACKED_STREAM` is `EXPANDED_PERMITTED`;
`LAYER_RECORD`, `TRANSITION_RECORD` and `TRANSITION_POINTER_ARRAY` are
`EXPANDED_ONLY` because their aggregate demand is unbounded and the canonical
image declares one small verified-free region; `GRAPHICS_CONTAINER` is
`EXPANDED_PERMITTED`, because a re-encoded container that genuinely fits trusted
verified-free bytes is a strictly weaker addressability claim than an expanded
one, and first fit therefore takes the conservative option when one exists.

## Growth

`plan_relocation` accepts a payload of any size, including one larger than the
anchor it replaces. That is the whole growth path, and it is one path: the
allocator, the reference re-encoding, the relocation provenance and the
generated-allocation provenance all come from the same call. A second domain that
needs to grow a container supplies a payload and a reason for the move; it does
not supply an allocator, an encoder, a plan or a manifest.

Size alone decides nothing about where the payload goes. `AllocationRequest.kind`
names the semantic class of what is being placed and the kind's
`Addressability` says whether an above-EOF span may be offered to it at all;
`RelocationRequest.addressability` may override that for one request when the
caller has an argument the kind's default does not carry.

An above-EOF placement is authorized, never inferred.
`RelocationRequest.generated` names the destination's `(domain, resource,
pointer_offset)`, and that is what turns an expanded allocation into a
`GeneratedAllocationProvenance` the write layer accepts. A request the allocator
places above canonical EOF without one is refused, because no plan record could
then say at what address those bytes were written. The bound each dislodged
reference is encoded against is the image its own placement was authorized
against, which for an expanded anchor is the generated image rather than the
canonical one.

`RelocationResult.document` carries the image the plan would publish. For a grown
batch that is the generated image with the changes applied, which is longer than
the canonical input, so the proposed document states that size; it is an
inspection artefact and not a new trusted base. The original payload region is
still left byte-intact, because the consumer set a domain publishes is not
claimed to be every word in the image that happens to equal the payload's
address.
