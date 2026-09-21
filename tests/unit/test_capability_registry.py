"""The DragonByte Z capability registry is the one current capability list.

``src/data/capabilities.json`` records what DragonByte Z can do today, and
``src/data/project.ts`` derives the public buildout list, its per-family tallies
and its percentage from it. This module is the consistency gate for that
contract: it reads the registry as data and checks it against the site source,
the rendered page and the repository's own provenance records.

Two ideas carry most of the weight. **Product capability and research knowledge
are separate lists**: only ``capabilities`` is counted, a counted capability
must name the editor surface a user reaches it through plus how it was proven,
and everything in ``researchOnly`` is proven-but-not-shipped and carries no
state of its own. **A figure has exactly one owner**: a count declared in
``measurements`` must be stated in its own capability's text and may not be
re-hardcoded in the page, and the hand-written blocker prose may not quote a
count that no capability owns.

What that enforces mechanically: divergent capability ids, a counted capability
without surface, proof or provenance, a research note dressed as a capability,
a missing limitation, and a published count that disagrees with the registry.
What it does NOT do is read English - a sentence describing the product wrongly
is caught only where it quotes a count, so the state contract, not prose
parsing, is what keeps the capability list and the page in agreement.

The site build repeats the structural half of this contract in
``src/data/project.ts``, so a malformed registry fails ``npm run build`` as well
as this suite. Both exist on purpose: CI runs this suite without Node, while a
site build must not publish a duplicated capability id any more than CI may
ignore one. The rendered-page assertions below therefore need a built site and
skip without one; everything else, including the roadmap's own derivation, is
asserted against the source so the automated gate is never inert.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import re

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = PROJECT_ROOT / "src/data/capabilities.json"
PROJECT_SOURCE = PROJECT_ROOT / "src/data/project.ts"
MAIN_COMPONENT = PROJECT_ROOT / "src/components/MainBand.astro"
BUILT_PAGE = PROJECT_ROOT / "dist/index.html"
TICKETS_DIRECTORY = PROJECT_ROOT / "docs/tickets"

#: A stable capability id: lowercase kebab-case, matching the site's row keys.
STABLE_ID = re.compile(r"^[a-z][a-z0-9-]*$")

#: A ticket id such as ``TOOLKIT-037`` or ``DRAGONBYTE-Z-MAP-BROWSER-001``.
TICKET_ID = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{3}$")

#: How a shipped capability's result was proven.
PROOF_LEVELS = {"runtime", "application"}

#: Fields that would let a research note masquerade as a product capability.
PRODUCT_ONLY_FIELDS = {"state", "surface", "proof", "measurements"}

#: The blocker prose is the site's statement of where the project currently
#: stands, and it is the field that goes stale first. A count written there must
#: be owned by a capability. The block is read from the project data, not from
#: the `ProjectStatus` interface that declares the same field names.
PROJECT_DATA_START = "export const project: ProjectStatus = {"
CURRENT_SUMMARY_START = "blockerShort:"
CURRENT_SUMMARY_END = "acceptanceTarget:"


@lru_cache(maxsize=1)
def registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def capabilities() -> list[dict]:
    return registry()["capabilities"]


def capability(capability_id: str) -> dict:
    return next(entry for entry in capabilities() if entry["id"] == capability_id)


def shipped() -> list[dict]:
    return [capability for capability in capabilities() if capability["state"] == "shipped"]


def family_ids() -> list[str]:
    return [family["id"] for family in registry()["families"]]


def family_tallies() -> dict[str, tuple[int, int]]:
    """Shipped and total per family, derived from the registry's own records."""
    tallies = {}
    for family in registry()["families"]:
        members = [c for c in capabilities() if c["family"] == family["id"]]
        tallies[family["id"]] = (
            len([c for c in members if c["state"] == "shipped"]),
            len(members),
        )
    return tallies


def owned_counts() -> set[str]:
    """Every count the registry declares, as written text."""
    return {
        str(value)
        for capability in capabilities()
        for value in capability.get("measurements", {}).values()
    }


def capability_text(capability: dict) -> str:
    return " ".join(
        [capability["title"], capability["detail"], capability.get("surface") or ""]
        + list(capability["limits"])
    )


def site_source() -> str:
    return PROJECT_SOURCE.read_text(encoding="utf-8")


def built_page() -> str:
    if not BUILT_PAGE.is_file():
        pytest.skip("site not built; run `npm run build`")
    return BUILT_PAGE.read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def ticket_text() -> str:
    """Ticket ids the repository actually records, filenames included.

    Evidence must be checkable from a checked-out tree and no deeper: CI clones
    shallowly, so nothing here may need repository history. A cited ticket has
    to exist somewhere under ``docs/tickets`` and a cited path has to exist on
    disk, which is what makes an invented provenance id fail rather than ship.
    """
    parts: list[str] = []
    for path in sorted(TICKETS_DIRECTORY.rglob("*.md")):
        parts.append(path.name)
        parts.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# The registry itself
# ---------------------------------------------------------------------------


def test_the_registry_declares_its_schema_and_track():
    data = registry()

    assert data["schemaVersion"] == 1
    assert data["track"]["title"].strip()
    assert data["track"]["label"].strip()
    assert data["track"]["blurb"].strip()
    assert isinstance(data["track"]["capabilityTotal"], int)
    assert data["families"] and data["capabilities"] and data["researchOnly"]


def test_stable_ids_are_unique_and_well_formed():
    """A duplicate id would let one capability shadow another in the count."""
    ids = [capability["id"] for capability in capabilities()]
    assert len(set(ids)) == len(ids), "duplicate capability id"
    for capability_id in ids:
        assert STABLE_ID.match(capability_id), capability_id

    family_names = family_ids()
    assert len(set(family_names)) == len(family_names), "duplicate capability family id"
    for family_id in family_names:
        assert STABLE_ID.match(family_id), family_id


def test_every_capability_belongs_to_exactly_one_declared_family():
    declared = family_ids()
    for family_id in declared:
        assert [c for c in capabilities() if c["family"] == family_id], (
            f"family {family_id!r} lists no capabilities")

    for capability in capabilities():
        assert capability["family"] in declared, (
            f"{capability['id']} names undeclared family {capability['family']!r}")

    assert len(declared) == len({c["family"] for c in capabilities()})


def test_the_declared_total_matches_the_registry_list():
    """The denominator is a deliberate declaration, not a side effect.

    This is the milestone-total guard: the family tallies, the denominator and
    the list itself must agree, so a capability cannot be added, dropped or
    moved between families without the public total moving with it.
    """
    total = registry()["track"]["capabilityTotal"]
    assert total == len(capabilities())

    per_family = sum(total_count for _, total_count in family_tallies().values())
    assert per_family == total

    done = len(shipped())
    assert 0 < done < total, "the buildout must report at least one shipped and one missing capability"
    assert all(0 <= count <= size for count, size in family_tallies().values())


# ---------------------------------------------------------------------------
# Product capability versus research knowledge
# ---------------------------------------------------------------------------


def test_a_counted_capability_declares_its_current_state_data():
    """A shipped capability has a surface and a proof, or it is not counted.

    This is the mechanism that stops a research result from becoming a product
    capability by being written into the list: a reverse-engineering fact has no
    editor surface and no proof level, and cannot supply them.
    """
    for capability in capabilities():
        if capability["state"] == "shipped":
            assert capability.get("surface", "").strip(), (
                f"{capability['id']} is counted as shipped without an editor surface")
            assert capability.get("proof") in PROOF_LEVELS, (
                f"{capability['id']} declares proof {capability.get('proof')!r}")
            assert capability["evidence"].strip(), (
                f"{capability['id']} is counted as shipped without provenance")
        else:
            assert capability["state"] == "missing"
            for field in ("surface", "proof"):
                assert field not in capability, (
                    f"{capability['id']} is not shipped but claims {field!r}")


def test_research_knowledge_cannot_masquerade_as_a_capability():
    """``researchOnly`` is proven knowledge that ships nothing, and never counts.

    The registry's example is the map-layout chunk-pointer structure: the
    structure is proven, and the product capability it supports is one bounded
    operation. Keeping the two lists apart, and forbidding the research list the
    fields that would make it countable, is what prevents the first from being
    reported as the second.
    """
    notes = registry()["researchOnly"]
    capability_names = {capability["id"] for capability in capabilities()}

    for note in notes:
        assert note["id"] not in capability_names, (
            f"research note {note['id']!r} collides with a product capability id")
        assert STABLE_ID.match(note["id"]), note["id"]
        assert note["statement"].strip()
        assert note["doesNotConfer"].strip(), (
            f"{note['id']} must state what proving it does not confer")
        assert note["contributesTo"], f"{note['id']} contributes to nothing"
        for target in note["contributesTo"]:
            assert target in capability_names, (
                f"{note['id']} contributes to unknown capability {target!r}")
        for field in PRODUCT_ONLY_FIELDS:
            assert field not in note, (
                f"research note {note['id']!r} carries the product field {field!r}")

    ids = [note["id"] for note in notes]
    assert len(set(ids)) == len(ids), "duplicate research note id"


# ---------------------------------------------------------------------------
# Limitations and figures
# ---------------------------------------------------------------------------


def test_every_capability_carries_a_bounded_limitation():
    """A concise state may not erase the scope, so limits are mandatory."""
    for capability in capabilities():
        limits = capability["limits"]
        assert isinstance(limits, list) and limits, (
            f"{capability['id']} carries no bounded limitation")
        for limit in limits:
            assert isinstance(limit, str) and limit.strip(), (
                f"{capability['id']} carries an empty limitation")


def test_a_declared_measurement_is_stated_in_its_own_record():
    """A figure has one owner, and its own record has to agree with it."""
    for capability in capabilities():
        text = capability_text(capability)
        for name, value in capability.get("measurements", {}).items():
            assert isinstance(value, int) and value > 0, (capability["id"], name, value)
            assert str(value) in text, (
                f"{capability['id']} declares {name}={value} but never states it")


def test_a_measurement_name_means_one_thing_registry_wide():
    """Two capabilities may share a figure, but only if they agree on it.

    Without this, the same count could be recorded once per capability and drift
    apart, which is the duplication the registry exists to remove.
    """
    seen: dict[str, tuple[int, str]] = {}
    for capability in capabilities():
        for name, value in capability.get("measurements", {}).items():
            if name in seen:
                other_value, other_id = seen[name]
                assert value == other_value, (
                    f"{name} is {other_value} for {other_id} but {value} for {capability['id']}")
            else:
                seen[name] = (value, capability["id"])
    assert seen


def test_evidence_names_real_provenance():
    """Provenance must resolve in the checked-out tree, not read plausibly."""
    recorded = ticket_text()

    for entry in capabilities():
        tokens = [token.strip() for token in entry["evidence"].split(";")]
        assert all(tokens), f"{entry['id']} has an empty evidence token"
        for token in tokens:
            if "/" in token or token.endswith((".md", ".py", ".json")):
                assert (PROJECT_ROOT / token).is_file(), (
                    f"{entry['id']} cites a missing path: {token}")
            else:
                assert TICKET_ID.match(token), (
                    f"{entry['id']} cites a malformed provenance id: {token}")
                assert token in recorded, (
                    f"{entry['id']} cites an unrecorded ticket: {token}")


# ---------------------------------------------------------------------------
# The site derives from the registry
# ---------------------------------------------------------------------------


def test_the_site_source_holds_no_capability_records_of_its_own():
    """There must be no second list of capability states to keep in step."""
    source = site_source()

    assert 'from "./capabilities.json"' in source, (
        "src/data/project.ts no longer imports the capability registry")
    assert "registry.capabilities" in source, (
        "the buildout list is no longer derived from the registry")
    assert 'state: "shipped"' not in source, (
        "src/data/project.ts defines a capability state inline; the registry is the only source")
    assert 'state: "missing"' not in source, (
        "src/data/project.ts defines a capability state inline; the registry is the only source")


def test_the_roadmap_can_only_render_registry_capabilities():
    """The component may not introduce a row of its own.

    The rendered-page check needs a built site, and CI runs this suite without
    Node, so the derivation is asserted at source level as well: the rows come
    from ``roadmapRows``, they are keyed by the registry's stable id, and no
    component carries a capability id as a literal.
    """
    component = MAIN_COMPONENT.read_text(encoding="utf-8")

    assert "roadmapRows" in component, "MainBand no longer renders the derived roadmap"
    assert "data-capability={row.key}" in component, (
        "the roadmap rows are no longer keyed by the registry's stable id")
    assert "{row.title}" in component and "{row.detail}" in component, (
        "the roadmap rows no longer render the registry's own fields")

    for path in sorted((PROJECT_ROOT / "src").rglob("*.astro")):
        source = path.read_text(encoding="utf-8")
        assert 'data-capability="' not in source, (
            f"{path.name} hard-codes a capability id in the roadmap rows")
        for entry in capabilities():
            assert f'key: "{entry["id"]}"' not in source, (
                f"{path.name} defines the capability {entry['id']!r} inline")
            assert entry["detail"] not in source, (
                f"{path.name} repeats the {entry['id']!r} capability detail as its own copy")


def test_published_capability_figures_are_not_written_twice():
    """A count the registry owns is built from it wherever the page states it.

    The measured strip and the product-capture captions quote the same map
    figures as the roadmap, so `project.ts` reads them from `measurements`.
    Re-hardcoding one restores the duplication this ticket removed, and the
    rendered-page assertions below then verify the derivation end to end.
    """
    source = site_source()
    layout = capability("layout")["measurements"]
    warps = capability("warps")["measurements"]

    restated = [
        f'"{layout["mapsViewable"]} / {layout["mapsViewable"]}"',
        f'"{layout["editableMaps"]} / {layout["mapsViewable"]}"',
        f'"{layout["readOnlyMaps"]} / {layout["mapsViewable"]}"',
        f'"{layout["editableMaps"]} of {layout["mapsViewable"]} maps expose an editable layer"',
        f'"{layout["mapsViewable"]} maps viewable"',
        f'"{warps["transitionRecords"]} / 0"',
    ]
    for phrase in restated:
        assert phrase not in source, (
            f"{phrase} is a hand-written copy of a registry count; build it from measurements")

    for capability_id, name in (
        ("map-browser", "mapsViewable"),
        ("layout", "editableMaps"),
        ("layout", "readOnlyMaps"),
        ("warps", "transitionRecords"),
    ):
        assert f'capabilityCount("{capability_id}", "{name}")' in source, (
            f"the page no longer reads {name} from capability {capability_id!r}")


def test_the_site_current_phase_names_the_registry_track():
    """The current summary states the track by name, so the two must agree."""
    phase = re.search(r'currentPhase:\s*"([^"]+)"', site_source())
    assert phase, "the site declares no current phase"

    assert phase.group(1) == registry()["track"]["title"], (
        "the site's current phase and the registry's track are different names "
        "for the same active track")


def test_the_public_current_summary_quotes_only_registered_counts():
    """The current-state prose may not introduce a count the registry does not own.

    The blocker prose is written by hand and is the public statement of what is
    still missing, so it is where a stale count survives longest. Every count of
    three digits or more written there must be a figure some capability owns,
    which makes a new or outdated number a deliberate registry change.
    """
    source = site_source()
    data = source[source.index(PROJECT_DATA_START):]
    summary = data[data.index(CURRENT_SUMMARY_START):data.index(CURRENT_SUMMARY_END)]

    found = set(re.findall(r"\b\d{3,}\b", summary))
    assert found, "the current-summary block could not be read; the test would be vacuous"
    assert found <= owned_counts(), (
        "the public current summary quotes counts no capability owns: "
        f"{sorted(found - owned_counts())}")


def test_the_built_page_renders_the_registry_list():
    """The published page is the end of the derivation chain, so check it there.

    The rendered rows are compared against the registry by stable id, in order,
    with the chip and the tallies and the derived percentage; a page that
    disagrees with the registry is the drift this ticket exists to stop.
    """
    html = built_page()

    rows = re.findall(
        r'<li(?P<tag>[^>]*\bdata-capability="(?P<id>[^"]+)"[^>]*)>(?P<body>.*?)</li>',
        html,
        re.S,
    )
    assert rows, "the built page carries no roadmap rows identified by capability id"

    expected = [(c["id"], c["state"]) for c in capabilities()]
    assert [row_id for _, row_id, _ in rows] == [row_id for row_id, _ in expected], (
        "the rendered capability list diverges from the registry")

    for (tag, row_id, body), (_, state) in zip(rows, expected):
        wanted = "is-done" if state == "shipped" else "is-todo"
        chip = "DONE" if state == "shipped" else "PLANNED"
        assert wanted in tag, f"{row_id} renders with the wrong state class"
        assert re.search(rf'class="chip">\s*{chip}\s*<', body), (
            f"{row_id} renders the wrong state chip")

    done, total = len(shipped()), len(capabilities())
    percent = round(done / total * 100)

    assert f"{done} / {total} SHIPPED" in html
    assert f"{done} of {total} capabilities complete" in html
    assert f'class="progress-pct">{percent}%<' in html
    assert f'aria-valuenow="{percent}"' in html

    rendered = re.findall(
        r'<li class="is-(?:complete|partial)" title="[^"]*">\s*'
        r"<span>([A-Z]+)</span>\s*<b>(\d+)/(\d+)</b>",
        html,
        re.S,
    )
    assert rendered, "the built page carries no per-family capability tallies"

    tallies = family_tallies()
    expected_tallies = [
        (family["label"],) + tallies[family["id"]] for family in registry()["families"]
    ]
    assert [(label, int(one), int(two)) for label, one, two in rendered] == [
        (label, one, two) for label, one, two in expected_tallies
    ], "the rendered family tallies diverge from the registry"

    # The figures the page states outside the roadmap, which are derived from
    # the registry's measurements rather than written again.
    layout = capability("layout")["measurements"]
    warps = capability("warps")["measurements"]
    viewable = capability("map-browser")["measurements"]["mapsViewable"]
    for phrase in (
        f'{viewable} / {viewable}',
        f'{layout["editableMaps"]} / {viewable}',
        f'{layout["readOnlyMaps"]} / {viewable}',
        f'{layout["editableMaps"]} of {viewable} maps expose an editable layer',
        f'Every one of the {viewable} maps opens here without a running emulator.',
        f'{warps["transitionRecords"]} / 0',
    ):
        assert phrase in html, f"the built page does not state {phrase!r}"
