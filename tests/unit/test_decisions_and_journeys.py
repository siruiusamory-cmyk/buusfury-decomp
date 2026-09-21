"""The decision records and the golden journeys are contracts, not prose.

``docs/decisions/`` holds the engineering decisions a future contributor must
not have to re-derive, and ``docs/journeys/`` holds the shortest real user
journeys for capabilities that already ship. Both are easy to let rot, and both
are read as authority, so this module is their gate.

What it enforces mechanically:

* every ADR states its status, its evidence, and its decision, context and
  consequences, so an ADR cannot be filed as a ticket summary with a heading;
* the ADR index lists every ADR file and links nothing else;
* every journey declares well-formed front matter whose ``id`` matches its
  filename, and every journey in the directory is indexed;
* every capability a journey names is a **shipped** capability that exists in
  ``src/data/capabilities.json``, so a journey cannot invent a workflow for a
  capability the product does not ship, and cannot become a second capability
  list;
* every test a journey cites exists, so a reference cannot rot into fiction;
* every relative link in these two directories resolves, because a decision whose
  evidence link is dead is not authoritative evidence;
* a journey's declared proof level is one of ADR 0004's evidence levels, and the
  journey body carries the matching labelled "Proof level reached" statement, so
  a level cannot be a stray front-matter token.

What it does NOT do is read English. A journey whose steps do not match the
product, an ADR whose consequences are wrong, or a journey that picks the wrong
proof level are caught by review, not here. An earlier draft did try to check the
proof level against the capabilities' own ``proof`` field; measurement showed
that check was satisfied incidentally, so it was replaced rather than kept as
false comfort.
"""

from __future__ import annotations

import json
from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DECISIONS_DIRECTORY = PROJECT_ROOT / "docs/decisions"
JOURNEYS_DIRECTORY = PROJECT_ROOT / "docs/journeys"
DECISIONS_INDEX = DECISIONS_DIRECTORY / "README.md"
JOURNEYS_INDEX = JOURNEYS_DIRECTORY / "README.md"
REGISTRY_PATH = PROJECT_ROOT / "src/data/capabilities.json"

#: ``0001-some-decision.md``; the number orders the set and the slug names it.
ADR_FILENAME = re.compile(r"^(\d{4})-[a-z0-9-]+\.md$")

#: A stable capability or journey id: lowercase kebab-case.
STABLE_ID = re.compile(r"^[a-z][a-z0-9-]*$")

#: The evidence levels of ADR 0004, which a journey may declare.
JOURNEY_PROOFS = {"structural", "renderer", "runtime"}

#: Keys every journey's front matter must declare.
REQUIRED_JOURNEY_KEYS = ("id", "title", "capabilities", "proof", "tests")

#: Sections every ADR must carry, beyond its status and evidence lines.
REQUIRED_ADR_SECTIONS = ("## Decision", "## Context", "## Consequences")

_NUMBERED_STEP = re.compile(r"^\d+\.\s+\S", re.MULTILINE)
_MARKDOWN_LINK = re.compile(r"\]\(([^)]+)\)")


def adr_files() -> list[Path]:
    """Every ADR file, oldest number first."""
    return sorted(
        path
        for path in DECISIONS_DIRECTORY.glob("*.md")
        if ADR_FILENAME.match(path.name)
    )


def front_matter(path: Path) -> tuple[dict[str, object], str]:
    """Parse a journey's leading front matter into a mapping plus its body.

    A deliberately tiny reader for the one shape ``docs/journeys/README.md``
    documents: ``key: scalar`` lines and ``  - item`` list items, with no
    nesting, no quoting and no multi-line scalars. Anything else is a loud
    failure rather than a silent misread, and there is no second place a journey
    is declared.
    """
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path.name} does not open with front matter"
    parts = text.split("---\n", 2)
    assert len(parts) == 3, f"{path.name} front matter is never closed"

    _, block, body = parts
    data: dict[str, object] = {}
    key: str | None = None
    for number, line in enumerate(block.splitlines(), start=1):
        if not line.strip():
            continue
        where = f"{path.name} front-matter line {number}"
        if line.startswith("  - "):
            assert key is not None, f"{where} lists an item before any key"
            value = data[key]
            assert isinstance(value, list), f"{where} mixes a scalar and a list under {key!r}"
            value.append(line[4:].strip())
            continue
        assert not line.startswith(" "), f"{where} uses unsupported indentation: {line!r}"
        name, separator, scalar = line.partition(":")
        assert separator and name.strip(), f"{where} is not a key: {line!r}"
        key = name.strip()
        assert key not in data, f"{where} repeats the key {key!r}"
        scalar = scalar.strip()
        data[key] = scalar if scalar else []
    return data, body


def journey_files() -> list[Path]:
    """Every journey document, by filename."""
    return sorted(
        path
        for path in JOURNEYS_DIRECTORY.glob("*.md")
        if path.name != "README.md"
    )


def journeys() -> list[tuple[Path, dict[str, object], str]]:
    return [(path, *front_matter(path)) for path in journey_files()]


def registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def capabilities_by_id() -> dict[str, dict]:
    return {entry["id"]: entry for entry in registry()["capabilities"]}


# ---------------------------------------------------------------------------
# The ADR set
# ---------------------------------------------------------------------------


def test_the_decision_set_exists():
    """An empty directory would make every check below vacuous."""
    assert adr_files(), "docs/decisions holds no ADR"


def test_adr_numbers_are_unique_and_ordered():
    numbers = [ADR_FILENAME.match(path.name).group(1) for path in adr_files()]
    assert len(set(numbers)) == len(numbers), f"duplicate ADR number: {numbers}"


def test_every_adr_states_status_evidence_decision_context_and_consequences():
    """The five parts are what make a record a decision rather than a summary.

    A ticket records what happened once; an ADR records what later work must
    obey. Dropping 'consequences' or 'evidence' is how the second becomes the
    first, so their absence is a failure rather than a style nit.
    """
    for path in adr_files():
        text = path.read_text(encoding="utf-8")
        assert "**Status:**" in text, f"{path.name} declares no status"
        assert "**Evidence:**" in text, f"{path.name} cites no evidence"
        for section in REQUIRED_ADR_SECTIONS:
            assert section in text, f"{path.name} has no {section!r} section"


def test_every_decision_file_is_named_like_an_adr():
    """A filename typo must not silently drop a decision out of the set.

    ``adr_files`` selects by filename and the index check only sees what that
    selection returned, so an ADR whose name does not match would be neither
    section-checked nor index-checked - a filename-shaped bypass of the
    "an unindexed decision is a decision nobody reads" invariant. Closed here
    rather than left implicit. Journeys need no equivalent: ``journey_files``
    takes every markdown file except the index, so a misfiled journey is still
    checked and still has to match its own id.
    """
    misplaced = sorted(
        path.name
        for path in DECISIONS_DIRECTORY.glob("*.md")
        if path.name != "README.md" and not ADR_FILENAME.match(path.name)
    )
    assert not misplaced, (
        "docs/decisions holds markdown that is not a numbered ADR: "
        + ", ".join(misplaced))


def test_the_adr_index_lists_every_adr_and_links_nothing_else():
    """An unindexed decision is a decision nobody reads."""
    index = DECISIONS_INDEX.read_text(encoding="utf-8")
    linked = {
        target
        for target in _MARKDOWN_LINK.findall(index)
        if "/" not in target and ADR_FILENAME.match(target)
    }
    recorded = {path.name for path in adr_files()}

    assert linked == recorded, (
        "the ADR index and the ADR files disagree: "
        f"missing from the index {sorted(recorded - linked)}, "
        f"linked but absent {sorted(linked - recorded)}")


# ---------------------------------------------------------------------------
# The golden journeys
# ---------------------------------------------------------------------------


def test_journey_front_matter_declares_the_documented_keys():
    for path, data, body in journeys():
        for key in REQUIRED_JOURNEY_KEYS:
            assert key in data, f"{path.name} declares no {key!r}"
        assert isinstance(data["capabilities"], list) and data["capabilities"], (
            f"{path.name} names no capability")
        assert isinstance(data["tests"], list) and data["tests"], (
            f"{path.name} cites no test")
        assert isinstance(data["proof"], str) and data["proof"], (
            f"{path.name} declares no proof level")
        # Type-strict on purpose: an empty scalar parses to an empty list, and
        # `str([])` is the non-empty string "[]", so a plain truthiness check
        # would accept a journey that declares no title at all.
        assert isinstance(data["title"], str) and data["title"].strip(), (
            f"{path.name} has no single-line title")
        assert body.strip(), f"{path.name} has no body"


def test_a_journey_id_matches_its_filename_and_is_unique():
    """The id is the join key, so it must not drift from the file that owns it."""
    seen: set[str] = set()
    for path, data, _ in journeys():
        assert isinstance(data["id"], str) and data["id"].strip(), (
            f"{path.name} declares no id")
        journey_id = data["id"]
        assert STABLE_ID.match(journey_id), f"{path.name} id {journey_id!r} is not kebab-case"
        assert journey_id == path.stem, (
            f"{path.name} declares id {journey_id!r}; the filename is the id")
        assert journey_id not in seen, f"duplicate journey id {journey_id!r}"
        seen.add(journey_id)


def test_every_journey_names_shipped_capabilities_from_the_registry():
    """Journeys are for capabilities that already ship, and there is one list.

    This is also what stops the journeys becoming a second capability list: an
    id that the registry does not carry is a failure, and so is a journey
    written for a capability the product does not ship yet.
    """
    known = capabilities_by_id()

    for path, data, _ in journeys():
        named = [str(entry) for entry in data["capabilities"]]
        assert len(set(named)) == len(named), f"{path.name} repeats a capability id"
        for capability_id in named:
            assert capability_id in known, (
                f"{path.name} names unknown capability {capability_id!r}")
            assert known[capability_id]["state"] == "shipped", (
                f"{path.name} documents a journey for {capability_id!r}, "
                "which the registry does not record as shipped")


def test_every_journey_cites_existing_tests():
    """A reference that cannot be resolved is worse than no reference."""
    for path, data, _ in journeys():
        for reference in data["tests"]:
            relative = str(reference)
            assert relative.startswith("tests/"), (
                f"{path.name} cites {relative!r}, which is not a test path")
            assert ".." not in Path(relative).parts, (
                f"{path.name} cites {relative!r}, which escapes the test tree")
            target = PROJECT_ROOT / relative
            assert target.is_file(), f"{path.name} cites a missing test: {relative}"
            assert target.name.startswith("test_"), (
                f"{path.name} cites {relative!r}, which is not a test module")


def test_a_journey_proof_level_is_one_of_the_adr_levels():
    for path, data, _ in journeys():
        proof = str(data["proof"])
        assert proof in JOURNEY_PROOFS, (
            f"{path.name} declares proof {proof!r}; expected one of "
            f"{sorted(JOURNEY_PROOFS)}")


def test_a_journey_states_the_proof_level_it_reaches():
    """Every journey carries an explicit, labelled statement of its own level.

    This is the one part of the proof decision that can be checked mechanically,
    so it is checked exactly rather than by keyword. A loose search for "runtime
    proof" is satisfied by a sentence that *denies* runtime proof - which the map
    layout journey contains, because saying what a journey does not prove is half
    its value. The labelled form cannot be satisfied that way.

    Which level is *correct* remains a review question, and deliberately so: an
    earlier draft of this gate tried to cross-check the level against the
    capabilities' own ``proof`` field, and measurement showed it was satisfied
    incidentally by any single runtime-proven capability in the list - false
    comfort rather than a gate. A journey spans capabilities at different levels
    and states the level of its own last step; ADR 0004 is why those may differ.
    """
    for path, data, body in journeys():
        level = str(data["proof"])
        marker = f"**proof level reached: {level} proof"
        assert marker in body.lower(), (
            f"{path.name} declares proof {level!r} but carries no "
            f"'**Proof level reached: {level} proof.**' line")


def test_a_journey_describes_a_sequence_of_steps():
    """A journey is a sequence, not a capability summary."""
    for path, data, body in journeys():
        steps = _NUMBERED_STEP.findall(body)
        assert len(steps) >= 3, (
            f"{path.name} lists {len(steps)} numbered steps; a journey is the "
            "shortest sequence that reaches success")


def test_every_journey_and_adr_link_resolves():
    """A decision whose evidence link 404s is not authoritative evidence.

    Checked only over the files this directory owns. The repository has a known
    backlog of broken relative links under ``docs/research/archive/`` from
    archived ``PROJECT_<local-state-name>`` copies, and a repository-wide link check would fail
    on that pre-existing debt rather than on anything here.
    """
    for path in [DECISIONS_INDEX, JOURNEYS_INDEX, *adr_files(), *journey_files()]:
        text = path.read_text(encoding="utf-8")
        for target in _MARKDOWN_LINK.findall(text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            relative = target.split("#", 1)[0]
            if not relative:
                continue
            assert (path.parent / relative).exists(), (
                f"{path.name} links {target!r}, which does not resolve")


def test_the_journey_index_lists_every_journey_and_links_nothing_else():
    index = JOURNEYS_INDEX.read_text(encoding="utf-8")
    linked = {
        target
        for target in _MARKDOWN_LINK.findall(index)
        if "/" not in target and target.endswith(".md") and target != "README.md"
    }
    recorded = {path.name for path in journey_files()}

    assert linked == recorded, (
        "the journey index and the journey files disagree: "
        f"missing from the index {sorted(recorded - linked)}, "
        f"linked but absent {sorted(linked - recorded)}")
