"""Read-only ROM-gated evidence for LOGX-GFXSCAN-001.

Only findings independently established in
``docs/research/LOGX_GFXSCAN_PROVENANCE.md`` are asserted here, and every expected
number is a count, an address or a digest - never a decoded payload.  No
ROM-derived fixture is committed: nothing decoded from a container is stored, and
the suite skips cleanly when the private canonical image is not configured.

The suite's most important job is the one the portable suite cannot do: require
the **external** model - the reproduction of ``ImageScan/Gba/JCALG1.cs`` - to
reproduce the project decoder's bytes on real canonical containers.  During this
ticket two different plausible transcriptions of the external ``GetInteger`` each
decoded hand-built streams and failed on every canonical container; only this
check caught them.

Run with ``LOGX_CANONICAL_ROM`` pointing at the image, or place it at the default
``roms/Dragon Ball Z - Buu's Fury (U).gba``.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from tools.research import logx_gfxscan_probe as scan

# --- independently measured constants of the canonical image ------------------

#: The known-positive corpus, by resource class.  Every one of these is reachable
#: from an accepted graph; none was contributed by a sweep.
EXPECTED_CLASS_REFERENCES = {
    scan.CLASS_SPRITE_PIECES: 11005,
    scan.CLASS_MAP_CHUNKS: 3912,
    scan.CLASS_SELECTOR_STREAMS: 421,
    scan.CLASS_BANK_CONTAINERS: 187,
    scan.CLASS_ENGINE_DEFAULT: 1,
}
EXPECTED_CLASS_UNIQUE = {
    scan.CLASS_SPRITE_PIECES: 7390,
    scan.CLASS_MAP_CHUNKS: 3745,
    scan.CLASS_SELECTOR_STREAMS: 392,
    scan.CLASS_BANK_CONTAINERS: 187,
    scan.CLASS_ENGINE_DEFAULT: 1,
}
#: ``CLASS_ZERO_HEADER`` is a **subset** of ``CLASS_SELECTOR_STREAMS``, so the
#: class sizes sum to 11,717 while the corpus holds 11,715 containers.  Both
#: numbers are asserted, and the overlap is asserted by address, so a later
#: revision cannot quietly turn the subset into a sibling.
EXPECTED_SUBSET_CLASS_UNIQUE = {scan.CLASS_ZERO_HEADER: 2}
EXPECTED_CLASS_SIZE_SUM = 11717
EXPECTED_CLASS_OVERLAP = {
    0x082B5F1C: [scan.CLASS_SELECTOR_STREAMS, scan.CLASS_ZERO_HEADER],
    0x082B5F94: [scan.CLASS_SELECTOR_STREAMS, scan.CLASS_ZERO_HEADER],
}
EXPECTED_KNOWN_UNIQUE_CONTAINERS = 11715
EXPECTED_KNOWN_UNIQUE_DIGESTS = 11715
#: No two known containers share a payload digest, so the sharing the corpus does
#: have is by *reference*, not by duplicated bytes.
EXPECTED_KNOWN_SHARED_PAYLOAD_GROUPS = 0

#: The external model's scan loop, as explicit population counts.
EXPECTED_POSITIONS_TESTED = 8388093
EXPECTED_EXTERNAL_KIND_WORD_MATCHES = 29504
EXPECTED_EXTERNAL_KIND_WORD_MATCHES_ALIGNED = 27775
EXPECTED_EXTERNAL_SIZE_FILTER_PASSES = 13463
EXPECTED_EXTERNAL_SIZE_FILTER_REJECTS = 16041
EXPECTED_EXTERNAL_RAW_CANDIDATES = 12990
EXPECTED_EXTERNAL_DECODE_RAISED = 175
EXPECTED_EXTERNAL_EMPTY_OUTPUT = 298
EXPECTED_EXTERNAL_UNIQUE_DIGESTS = 12912
EXPECTED_EXTERNAL_CATEGORIES = {
    scan.CATEGORY_KNOWN_GRAPHICS: 7391,
    scan.CATEGORY_KNOWN_NON_GRAPHICS: 4123,
    scan.CATEGORY_UNRESOLVED_CONTAINER: 7,
    scan.CATEGORY_NEW_ENGINE_REFERENCED: 1453,
    scan.CATEGORY_NO_REFERENCE: 0,
    scan.CATEGORY_FALSE_POSITIVE: 16,
}
EXPECTED_EXTERNAL_FALSE_POSITIVES = {
    scan.FP_SHORT_VIA_END_MARKER: 14,
    scan.FP_INSIDE_ANOTHER_CANDIDATE: 2,
}

#: Recall per class.  Only the sprite class is a graphics denominator.
#: The bank row's agreeing digests moved 110 -> 187 with
#: WEBFOOT-LZ-LITERAL-BASE-001: every root-bank container now reproduces the
#: external JCALG1 model, which had the engine's literal-base rule all along.
EXPECTED_EXTERNAL_RECALL = {
    scan.CLASS_SPRITE_PIECES: (7390, 0, 7390),
    scan.CLASS_MAP_CHUNKS: (3745, 0, 3744),
    scan.CLASS_SELECTOR_STREAMS: (191, 201, 191),
    scan.CLASS_BANK_CONTAINERS: (187, 0, 187),
    scan.CLASS_ENGINE_DEFAULT: (0, 1, 0),
    scan.CLASS_ZERO_HEADER: (0, 2, 0),
}
#: Why the selector class is missed: the external size filter demands a declared
#: size that is a multiple of four, and these containers' declared sizes are
#: 2 mod 4.
EXPECTED_SELECTOR_MISS_REASONS = {"declared_size_not_a_multiple_of_four": 199,
                                  "form_0_stored_not_matched_by_the_model": 2}

#: The engine-informed model, word-aligned and exact.
EXPECTED_ENGINE_ALIGNED_POPULATION = 25074
EXPECTED_ENGINE_ALIGNED_CANDIDATES = 24283
EXPECTED_ENGINE_ALIGNED_RECALL_SPRITE = 7390
EXPECTED_ENGINE_ALIGNED_DECODE_ERRORS = 791
EXPECTED_ENGINE_ALIGNED_FALSE_POSITIVES = {
    scan.FP_INSIDE_KNOWN_CONTAINER: 4,
    scan.FP_INSIDE_ANOTHER_CANDIDATE: 7084,
}
EXPECTED_ENGINE_ALIGNED_NESTED = 12612
EXPECTED_ENGINE_UNCONSTRAINED_FALSE_POSITIVES = {
    scan.FP_INSIDE_KNOWN_CONTAINER: 267,
    scan.FP_INSIDE_ANOTHER_CANDIDATE: 15320,
    scan.FP_NOT_WORD_ALIGNED: 74,
}
EXPECTED_ENGINE_UNCONSTRAINED_NESTED = 21610

#: The one arm where the external grammar and the project decoder genuinely
#: differ: the external ``value == 0`` arm writes a literal zero, the project
#: writes its literal base.  Correcting that arm moves one known container's
#: payload, so the two grammars disagree on exactly that container.
#:
#: Re-baselined by WEBFOOT-LZ-LITERAL-BASE-001: the count used to be **78**,
#: because the project decoder also retained the 7-bit literal base across a
#: return to 8-bit literals and the external model clears it - 77 root-bank
#: containers plus this one.  With the engine's rule in place (proven against the
#: engine's own character memory in ``docs/research/BUU_MAP_GRAPHICS_DIAG.md``)
#: those 77 now agree with the external model, which is the independent
#: corroboration that the rule is right; only the literal-zero arm remains.
EXPECTED_EXTERNAL_VS_CANONICAL_DECODES = 11712
EXPECTED_EXTERNAL_VS_CANONICAL_DIFFERING = 1
#: The one container the literal-zero arm moves: a map chunk declaring 2,048
#: bytes.
EXPECTED_DIVERGENT_MAP_CHUNK = 0x0829B308

#: Representative containers, one per class, whose decode both models must
#: reproduce byte for byte.
REPRESENTATIVE_CONTAINERS = (
    (scan.CLASS_SPRITE_PIECES, 0x083C34D0, 1024),
    (scan.CLASS_MAP_CHUNKS, 0x08179A50, 2048),
    (scan.CLASS_SELECTOR_STREAMS, 0x0817A75C, 904),
    (scan.CLASS_BANK_CONTAINERS, 0x080945C0, 16384),
)


@pytest.fixture(scope="module")
def canonical_bytes() -> bytes:
    """The canonical image, read once for the whole module.

    Module scope is deliberate: the scanners walk the whole image and decode
    thousands of candidates, and the module's per-image tables are keyed on the
    image object.
    """
    path = Path(
        os.environ.get("LOGX_CANONICAL_ROM", "roms/Dragon Ball Z - Buu's Fury (U).gba")
    )
    if not path.is_file():
        pytest.skip("canonical Buu ROM not configured locally")
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest().upper() == scan.CANONICAL_SHA256
    return data


@pytest.fixture(scope="module")
def corpus(canonical_bytes: bytes) -> scan.KnownCorpus:
    return scan.build_known_corpus(canonical_bytes)


@pytest.fixture(scope="module")
def full(canonical_bytes: bytes) -> dict:
    """One full report per module: every model, classified, plus the residual.

    Module scope is required, not a convenience: a full report walks the whole
    image three times and decodes tens of thousands of candidates.
    """
    return scan.full_report(canonical_bytes)


@pytest.fixture(scope="module")
def external_run(canonical_bytes: bytes, corpus: scan.KnownCorpus) -> scan.ModelRun:
    run = scan.run_model(canonical_bytes, scan.MODEL_EXTERNAL)
    hits, _coverage = scan.reference_search(
        canonical_bytes,
        {
            candidate.address
            for candidate in run.candidates
            if corpus.resource(candidate.address) is None
            and not corpus.by_digest.get(candidate.decoded_sha256)
        },
    )
    scan.flag_nested_candidates(run.candidates)
    scan.classify_candidates(run.candidates, corpus, reference_index=hits)
    return run


# --- the known-positive corpus ------------------------------------------------


def test_known_class_reference_counts(corpus: scan.KnownCorpus) -> None:
    for name, expected in EXPECTED_CLASS_REFERENCES.items():
        resources = [corpus.resources[a] for a in corpus.classes[name]]
        assert sum(len(r.references) for r in resources) == expected, name


def test_known_class_unique_container_counts(corpus: scan.KnownCorpus) -> None:
    for name, expected in EXPECTED_CLASS_UNIQUE.items():
        assert len(corpus.classes[name]) == expected, name
    for name, expected in EXPECTED_SUBSET_CLASS_UNIQUE.items():
        assert len(corpus.classes[name]) == expected, name
    assert len(corpus.resources) == EXPECTED_KNOWN_UNIQUE_CONTAINERS
    assert len(corpus.by_digest) == EXPECTED_KNOWN_UNIQUE_DIGESTS
    assert (
        sum(1 for addresses in corpus.by_digest.values() if len(addresses) > 1)
        == EXPECTED_KNOWN_SHARED_PAYLOAD_GROUPS
    )


def test_known_classes_partition_the_corpus_except_the_named_subset(
    corpus: scan.KnownCorpus,
) -> None:
    """The per-class sizes over-count by exactly the zero-header subset.

    A revision that re-listed the form-0 selector members as a sibling class made
    the class sum 11,717 and the printed equation wrong.  The subset is asserted
    by address, and so is the size of the over-count.
    """
    overlap = corpus.class_overlap()
    assert overlap == EXPECTED_CLASS_OVERLAP
    assert corpus.class_size_sum() == EXPECTED_CLASS_SIZE_SUM
    assert corpus.class_size_sum() - len(corpus.resources) == len(overlap)
    for address, names in overlap.items():
        assert names == [scan.CLASS_SELECTOR_STREAMS, scan.CLASS_ZERO_HEADER]
        assert corpus.resources[address].kind == scan.wl.STORED
    # every address in the corpus is in at least one class
    assert set(corpus.resources) == set().union(*map(set, corpus.classes.values()))


def test_known_sprite_class_is_the_only_graphics_denominator() -> None:
    assert scan.GRAPHICS_CLASSES == {scan.CLASS_SPRITE_PIECES}
    assert scan.RECALL_CLASSES == (scan.CLASS_SPRITE_PIECES,)
    # the map chunk class is a *container* class whose payload is tile indices
    from tools.research import logx_codec_probe as codec

    assert scan.SLOT_SEMANTICS[scan.CLASS_MAP_CHUNKS].startswith("CONFIRMED")
    assert "NOT graphics" in scan.SLOT_SEMANTICS[scan.CLASS_MAP_CHUNKS]
    assert codec is not None


def test_every_known_container_decodes_and_its_extent_is_measured(
    corpus: scan.KnownCorpus,
) -> None:
    for address, resource in corpus.resources.items():
        assert not resource.decode_error, hex(address)
        assert resource.packed_end > address, hex(address)
        assert resource.decoded_length == resource.declared_size or resource.kind == 0


# --- the external model against real containers -------------------------------


@pytest.mark.parametrize("resource_class,address,declared", REPRESENTATIVE_CONTAINERS)
def test_external_model_reproduces_the_project_decoder(
    canonical_bytes: bytes, resource_class: str, address: int, declared: int
) -> None:
    """The external grammar and framing must reproduce the project's bytes.

    This is the check that distinguishes a faithful reproduction of
    ``ImageScan/Gba/JCALG1.cs`` from a plausible-looking one.
    """
    offset = address - scan.ROM_BASE
    canonical = scan.wl.unpack(canonical_bytes, offset)
    assert canonical.declared_size == declared
    assert canonical.data, resource_class
    payload, overrun, consumed, terminator = scan.external_decode(canonical_bytes, offset)
    assert payload == canonical.data
    assert overrun == 0
    assert terminator in ("declared_size", "end_marker")
    assert consumed % 4 == 0


def test_external_model_decodes_every_known_kind_one_container(
    canonical_bytes: bytes, corpus: scan.KnownCorpus
) -> None:
    """No canonical kind-1 container raises inside the external model.

    The divergence is asserted by *shape* rather than by count alone, so a future
    change that moves it to a different class cannot pass by keeping the total.
    Since WEBFOOT-LZ-LITERAL-BASE-001 the only one left is the literal-zero arm;
    the 77 root-bank containers that used to appear here were the project
    decoder's retained literal base, and they are the independent corroboration
    that the correction is the engine's rule.
    """
    same = 0
    differing: list[tuple[int, str, int]] = []
    for address, resource in sorted(corpus.resources.items()):
        if resource.kind != 1:
            continue
        payload, _overrun, _consumed, _terminator = scan.external_decode(
            canonical_bytes, address - scan.ROM_BASE
        )
        if scan._digest(payload) == resource.decoded_sha256:
            same += 1
        else:
            differing.append((address, resource.resource_class, resource.declared_size))
    assert same + len(differing) == EXPECTED_EXTERNAL_VS_CANONICAL_DECODES
    assert len(differing) == EXPECTED_EXTERNAL_VS_CANONICAL_DIFFERING
    banks = [row for row in differing if row[1] == scan.CLASS_BANK_CONTAINERS]
    assert banks == []
    others = [row for row in differing if row[1] != scan.CLASS_BANK_CONTAINERS]
    assert others == [(EXPECTED_DIVERGENT_MAP_CHUNK, scan.CLASS_MAP_CHUNKS, 2048)]


def test_sprite_containers_span_every_word_aligned_low_byte(
    corpus: scan.KnownCorpus,
) -> None:
    """The literal offset cannot be seeded from the declared-size word.

    If the external reader's ``literalOffset`` started at the low byte of the
    declared-size word, every literal it wrote would be shifted by that byte.  The
    7,390 known sprite containers sit at every word-aligned offset, so those shifts
    would differ from container to container and the external model could not
    reproduce the project decoder's bytes - which
    ``test_external_model_reproduces_the_project_decoder`` requires it to do.

    This test states the premise: the sprite corpus really does use many distinct
    low bytes, so the argument is not vacuous.
    """
    low_bytes = {address & 0xFF for address in corpus.classes[scan.CLASS_SPRITE_PIECES]}
    assert len(low_bytes) >= 32
    assert all(value % 4 == 0 for value in low_bytes)
    assert 0 in low_bytes
    assert max(low_bytes) >= 0xFC


# --- the scan population ------------------------------------------------------


def test_external_scan_population_is_deterministic(canonical_bytes: bytes) -> None:
    population = scan.scan_population(canonical_bytes)
    assert population.positions_tested == EXPECTED_POSITIONS_TESTED
    assert population.kind_word_matches == EXPECTED_EXTERNAL_KIND_WORD_MATCHES
    assert (
        population.kind_word_matches_aligned
        == EXPECTED_EXTERNAL_KIND_WORD_MATCHES_ALIGNED
    )
    assert population.size_filter_passes == EXPECTED_EXTERNAL_SIZE_FILTER_PASSES
    assert population.size_filter_rejects == EXPECTED_EXTERNAL_SIZE_FILTER_REJECTS
    assert len(population.submitted) == EXPECTED_EXTERNAL_SIZE_FILTER_PASSES
    # the size filter is a partition of the matched words
    assert (
        population.size_filter_passes + population.size_filter_rejects
        == population.kind_word_matches
    )


def test_external_scan_population_starts_at_the_external_constant() -> None:
    assert scan.EXTERNAL_SCAN_START == 0x200
    assert scan.EXTERNAL_REQUIRED_KIND == 1
    assert scan.EXTERNAL_PRIORITY_LENGTH == 256


# --- the external model's totals and recall -----------------------------------


def test_external_model_totals(external_run: scan.ModelRun) -> None:
    totals = scan._candidate_totals(external_run.candidates)
    assert external_run.stats["decode_raised"] == EXPECTED_EXTERNAL_DECODE_RAISED
    assert external_run.stats["empty_output"] == EXPECTED_EXTERNAL_EMPTY_OUTPUT
    assert totals["raw_candidates"] == EXPECTED_EXTERNAL_RAW_CANDIDATES
    assert totals["unique_decoded_digests"] == EXPECTED_EXTERNAL_UNIQUE_DIGESTS
    # every candidate is a candidate *reference*; the external loop tests each
    # byte offset exactly once, so there is no duplicate address
    assert totals["duplicate_reference_count"] == 0
    assert totals["raw_candidates"] == totals["unique_addresses"]
    assert totals["stored_arm_candidates"] == 0
    assert totals["unaligned_candidates"] == (
        totals["raw_candidates"] - totals["aligned_candidates"]
    )


def test_external_model_category_tally(external_run: scan.ModelRun) -> None:
    tally = scan._category_tally(external_run.candidates)
    assert tally == EXPECTED_EXTERNAL_CATEGORIES
    assert sum(tally.values()) == len(external_run.candidates)


def test_external_model_false_positive_classes(external_run: scan.ModelRun) -> None:
    assert scan._false_positive_classes(external_run.candidates) == (
        EXPECTED_EXTERNAL_FALSE_POSITIVES
    )


def test_engine_model_false_positive_classes(canonical_bytes: bytes) -> None:
    """The three false-positive mechanisms are counted apart, not merged.

    ``wrapper_start_inside_a_known_container`` and
    ``wrapper_start_inside_another_candidate`` are different defects: the first is
    a candidate whose "header" lies in a *known* container's compressed payload,
    the second starts inside another *candidate's* extent.  An earlier revision
    merged them and reported the merge under the first name.
    """
    aligned = scan.run_model(canonical_bytes, scan.MODEL_ENGINE_ALIGNED)
    aligned_hits, _ = scan.reference_search(canonical_bytes, set())
    corpus = scan.build_known_corpus(canonical_bytes)
    scan.flag_nested_candidates(aligned.candidates)
    scan.classify_candidates(aligned.candidates, corpus, reference_index=aligned_hits)
    assert scan._false_positive_classes(aligned.candidates) == (
        EXPECTED_ENGINE_ALIGNED_FALSE_POSITIVES
    )
    nested = [
        candidate
        for candidate in aligned.candidates
        if candidate.details.get("nested_inside_candidate")
    ]
    assert len(nested) == EXPECTED_ENGINE_ALIGNED_NESTED
    assert sum(1 for candidate in nested if candidate.kind != 0) == 6607
    assert sum(1 for candidate in nested if candidate.kind == 0) == 6005
    # the flag is geometric; the class is the reason for rejection.  A candidate
    # whose nesting owner is itself a known container is classified
    # ``inside_a_known_container``, never ``inside_another_candidate``.
    assert sum(
        1 for candidate in nested if corpus.container_containing(candidate.address)
    ) == 5526
    assert not [
        candidate
        for candidate in aligned.candidates
        if candidate.details.get("false_positive_class")
        == scan.FP_INSIDE_ANOTHER_CANDIDATE
        and corpus.container_containing(candidate.address)
    ]
    assert (
        sum(EXPECTED_ENGINE_ALIGNED_FALSE_POSITIVES.values())
        <= len(aligned.candidates)
    )


def test_engine_unconstrained_false_positive_classes_reach_alignment(
    canonical_bytes: bytes,
) -> None:
    """Only the unconstrained model produces the alignment class, and it is small.

    ``wrapper_start_not_word_aligned`` counts the candidates *classified* on that
    ground - 74 - which is not the same as the 7,221 unaligned candidates the
    engine-aligned model does not form at all.  Reporting the second number under
    the first name was a defect of an earlier revision.
    """
    unconstrained = scan.run_model(canonical_bytes, scan.MODEL_ENGINE_UNCONSTRAINED)
    corpus = scan.build_known_corpus(canonical_bytes)
    scan.flag_nested_candidates(unconstrained.candidates)
    scan.classify_candidates(unconstrained.candidates, corpus)
    assert scan._false_positive_classes(unconstrained.candidates) == (
        EXPECTED_ENGINE_UNCONSTRAINED_FALSE_POSITIVES
    )
    assert sum(
        1 for candidate in unconstrained.candidates if not candidate.aligned
    ) == 7221
    nested = sum(
        1
        for candidate in unconstrained.candidates
        if candidate.details.get("nested_inside_candidate")
    )
    assert nested == EXPECTED_ENGINE_UNCONSTRAINED_NESTED


def test_external_model_recall_per_class(
    corpus: scan.KnownCorpus, external_run: scan.ModelRun
) -> None:
    for name, (hits, misses, agreeing) in EXPECTED_EXTERNAL_RECALL.items():
        row = scan.recall_for(corpus, external_run.candidates, name)
        assert row.scanner_hits == hits, name
        assert row.scanner_misses == misses, name
        assert row.digests_agreeing == agreeing, name
        assert row.scanner_hits + row.scanner_misses == row.known_unique_resources, name


def test_external_model_sprite_recall_is_total(
    corpus: scan.KnownCorpus, external_run: scan.ModelRun
) -> None:
    """The strongest sprite-positive corpus is found in full, bytes included."""
    row = scan.recall_for(corpus, external_run.candidates, scan.CLASS_SPRITE_PIECES)
    assert row.known_unique_resources == 7390
    assert row.scanner_hits == 7390
    assert row.scanner_misses == 0
    assert row.digests_agreeing == 7390
    assert row.fail_reasons == {}
    assert row.hit_rate == 1.0


def test_external_model_selector_misses_have_one_named_cause(
    corpus: scan.KnownCorpus, external_run: scan.ModelRun
) -> None:
    row = scan.recall_for(corpus, external_run.candidates, scan.CLASS_SELECTOR_STREAMS)
    assert row.fail_reasons == EXPECTED_SELECTOR_MISS_REASONS


def test_external_model_misses_every_stored_form(corpus: scan.KnownCorpus,
                                                  external_run: scan.ModelRun) -> None:
    """Form 0 is invisible to the external model's ``kind == 1`` test."""
    found = {candidate.address for candidate in external_run.candidates}
    stored = [
        address
        for address, resource in corpus.resources.items()
        if resource.kind == 0
    ]
    assert stored
    assert not (set(stored) & found)


# --- the engine-informed model ------------------------------------------------


def test_engine_aligned_model_totals(canonical_bytes: bytes) -> None:
    run = scan.run_model(canonical_bytes, scan.MODEL_ENGINE_ALIGNED)
    assert len(run.population.submitted) == EXPECTED_ENGINE_ALIGNED_POPULATION
    assert len(run.candidates) == EXPECTED_ENGINE_ALIGNED_CANDIDATES
    assert run.stats["rejected_decode_error"] == EXPECTED_ENGINE_ALIGNED_DECODE_ERRORS
    totals = scan._candidate_totals(run.candidates)
    assert totals["unaligned_candidates"] == 0
    assert totals["no_overrun_decodes"] == EXPECTED_ENGINE_ALIGNED_CANDIDATES
    assert totals["full_declared_length_decodes"] == EXPECTED_ENGINE_ALIGNED_CANDIDATES


def test_engine_aligned_model_finds_every_known_container_but_the_empty_default(
    canonical_bytes: bytes, corpus: scan.KnownCorpus
) -> None:
    """Requiring alignment costs the engine model nothing on the known corpus.

    One known container is not a candidate anywhere: the engine's own default
    container at ``0x08070808`` is a **form-0 container declaring zero bytes**, and
    every model here requires a declared size of at least one, so it is never even
    submitted.  It is named rather than quietly dropped, and the sprite class is
    still found in full.
    """
    run = scan.run_model(canonical_bytes, scan.MODEL_ENGINE_ALIGNED)
    found = {candidate.address for candidate in run.candidates}
    missing = set(corpus.resources) - found
    assert missing == {scan.codec.ENGINE_DEFAULT_CONTAINER}
    assert corpus.resources[scan.codec.ENGINE_DEFAULT_CONTAINER].kind == 0
    assert corpus.resources[scan.codec.ENGINE_DEFAULT_CONTAINER].declared_size == 0
    assert scan.codec.ENGINE_DEFAULT_CONTAINER not in {
        item.offset + scan.ROM_BASE for item in run.population.submitted
    }
    row = scan.recall_for(corpus, run.candidates, scan.CLASS_SPRITE_PIECES)
    assert row.scanner_hits == EXPECTED_ENGINE_ALIGNED_RECALL_SPRITE
    assert row.scanner_misses == 0
    assert row.digests_agreeing == row.scanner_hits


def test_engine_alignment_removes_an_alignment_artefact_population(
    canonical_bytes: bytes,
) -> None:
    aligned = scan.run_model(canonical_bytes, scan.MODEL_ENGINE_ALIGNED)
    unconstrained = scan.run_model(canonical_bytes, scan.MODEL_ENGINE_UNCONSTRAINED)
    aligned_addresses = {candidate.address for candidate in aligned.candidates}
    unconstrained_by_address = {
        candidate.address: candidate for candidate in unconstrained.candidates
    }
    # the aligned model's candidates are a subset: dropping the alignment rule can
    # only add candidates, never remove one
    assert aligned_addresses <= set(unconstrained_by_address)
    extra = set(unconstrained_by_address) - aligned_addresses
    assert extra
    # every candidate the alignment rule removes is at a non-word-aligned offset
    assert all(unconstrained_by_address[address].aligned is False for address in extra)
    assert all(
        candidate.aligned for candidate in aligned.candidates
    )


# --- reference search ---------------------------------------------------------


def test_reference_search_covers_every_word(canonical_bytes: bytes) -> None:
    targets = {0x083C34D0}
    hits, coverage = scan.reference_search(canonical_bytes, targets)
    assert coverage["word_positions_scanned"] == len(canonical_bytes) // 4
    assert coverage["word_aligned_only"] is True
    assert hits[0x083C34D0], "a known sprite container has no pointer into it"
    assert "computed" in coverage["coverage"]


def test_reference_absence_names_its_coverage(canonical_bytes: bytes) -> None:
    """An absence claim carries its coverage, and a small offset is not a hit.

    ``0x08004604`` is inside the code area, which no accepted graph reaches as a
    container, so the word-aligned sweep must find nothing naming it in full
    GBA-address form.  (The bare file-offset form ``0x4604`` does occur as a small
    integer elsewhere, which is exactly why the two forms are reported apart.)
    """
    target = 0x08004604
    hits, coverage = scan.reference_search(canonical_bytes, {target})
    assert coverage["targets_with_a_gba_address_hit"] == 0
    assert coverage["targets_with_a_hit"] <= coverage["targets"]
    assert coverage["word_positions_scanned"] == len(canonical_bytes) // 4
    assert hits.get(target) or coverage["targets_with_a_hit"] == 0


# --- the residual set ---------------------------------------------------------


def test_residual_report_invariants(full: dict) -> None:
    residual = full["residual"]
    rows = residual["rows"]
    universe = full["models"][scan.MODEL_ENGINE_ALIGNED]["totals"]["raw_candidates"]
    assert residual["candidate_universe"] == universe
    assert residual["residual_candidates"] == len(rows)
    assert set(residual["residual_by_category"]) <= set(
        residual["candidate_universe_by_category"]
    )
    assert sum(residual["residual_by_category"].values()) == len(rows)
    assert (
        residual["residual_with_a_known_payload"]
        + residual["residual_with_a_novel_payload"]
        == len(rows)
    )
    assert (
        residual["residual_engine_referenced"]
        + residual["residual_no_reference_found"]
        == residual["residual_with_a_novel_payload"]
    )
    for row in rows:
        assert row["category"] in scan.RESIDUAL_CATEGORIES
        assert row["address"].startswith("08")
        assert row["decoded_sha256"]
        assert row["engine_reference_status"] in (
            "ENGINE-REFERENCED",
            "NO REFERENCE FOUND WITHIN THE DOCUMENTED COVERAGE",
        )
        # a residual candidate is never called graphics, and its evidence is
        # about the missing rendering consumer rather than about pointers
        assert "no rendering consumer established" in row["graphics_evidence"]
        assert "no engine reference established" not in row["graphics_evidence"]
        assert row["confidence"] in (
            "INFERRED: a word in the image names this address",
            "UNKNOWN: structurally valid container, no consumer found",
            "UNKNOWN: container semantics unresolved",
        )


def test_residual_size_characterisation_is_measured(full: dict) -> None:
    """The residual set is not a homogeneous block of large tile banks.

    The packed residual population is dominated by 256-byte and 4 KiB candidates;
    only a minority are 8 KiB or larger.  The documents must not describe it as
    "all large", and this test states the distribution so a later revision cannot.
    """
    rows = [row for row in full["residual"]["rows"] if row["wrapper_kind"] == 1]
    assert len(rows) == 387
    sizes = sorted(row["declared_size"] for row in rows)
    assert sizes[0] == 128
    assert sizes[-1] == 65474
    assert sum(1 for size in sizes if size >= 8192) == 26
    assert sum(1 for row in rows if row["decoded_length"] % 32 == 0) == 381
    referenced = [row for row in rows if row["engine_references"]]
    assert len(referenced) == 387
    assert (
        sum(
            1
            for row in referenced
            if row["decoded_length"] % 32 == 0 and row["declared_size"] >= 8192
        )
        == 21
    )
    external_confirmed = [row for row in rows if row["external_model_agrees"]]
    # Re-baselined by WEBFOOT-LZ-LITERAL-BASE-001: 384, not 381. The three
    # additions are 0x086B9A9C, 0x086BC6A0 and 0x086D8C78 - engine-referenced
    # 4,096-byte containers whose engine-aligned decode now reproduces the
    # external model. Nothing moved out: the external sweep never submits a
    # declared size that is not a multiple of four, so the large containers whose
    # size is 2 mod 4 stay outside its population on both sides of the change.
    assert len(external_confirmed) == 384
    assert sum(1 for row in external_confirmed if row["decoded_length"] % 32 == 0) == 381
    assert sum(1 for row in external_confirmed if row["declared_size"] >= 8192) == 23


def test_residual_is_deterministic(full: dict) -> None:
    """Determinism is asserted on the report's own ordering, not a second scan."""
    rows = full["residual"]["rows"]
    addresses = [row["address"] for row in rows]
    assert addresses == sorted(addresses)
    assert len(set(addresses)) == len(addresses)


# --- canonical-ROM integrity --------------------------------------------------


def test_scanning_does_not_mutate_the_image(canonical_bytes: bytes) -> None:
    """The probes take ``bytes``; this asserts the object they were given."""
    before = hashlib.sha256(canonical_bytes).hexdigest().upper()
    scan.scan_population(canonical_bytes, start=0, end=4096)
    run = scan.run_model(canonical_bytes, scan.MODEL_EXTERNAL, max_candidates=8)
    assert run.candidates
    after = hashlib.sha256(canonical_bytes).hexdigest().upper()
    assert before == after == scan.CANONICAL_SHA256
