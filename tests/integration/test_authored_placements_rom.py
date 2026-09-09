"""Private local-ROM TOOLKIT-022 proof. No emulator or proprietary fixtures."""
import hashlib
import json
from pathlib import Path

import pytest

from tools.webfoot.allocation import allocate, InsufficientSpaceError
from tools.webfoot.build import extract_project, build_project, validate_project, authored_capacity_plan
from tools.webfoot.layout import LayoutError
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.project import read_project
from tools.webfoot.project.placements import clone_placement


SHA = "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"


def maps_for(rom, catalog):
    """The same verified `Maps` the build loads, for reading published anchors."""
    from tools.webfoot.maps import load_maps
    return load_maps(rom, catalog)


def test_canonical_authoring_serializes_but_preserves_ownership_and_zero_capacity(tmp_path):
    candidates = sorted(Path("roms").glob("*Buu*.gba"))
    if not candidates:
        pytest.skip("canonical Buu ROM not configured locally")
    rom = candidates[0]
    before = rom.read_bytes()
    if hashlib.sha256(before).hexdigest() != SHA:
        pytest.skip("local ROM does not match exact canonical Buu identity")
    stamp = rom.stat().st_mtime_ns
    catalog = RomProfileCatalog.load("config/roms.yaml")
    try:
        roots = (tmp_path / "a", tmp_path / "b")
        for root in roots:
            extract_project(rom, root, catalog, graphics=False)
        contents = lambda root: {p.relative_to(root).as_posix(): p.read_bytes()
                                 for p in root.rglob("*") if p.is_file()}
        assert contents(roots[0]) == contents(roots[1])
        no_op = tmp_path / "noop.gba"
        result = build_project(roots[0], rom, no_op, catalog)
        assert not result.manifest.changes
        assert no_op.read_bytes() == before
        project = read_project(roots[0])
        assert all(not m.get("authored_placements") for m in project.maps.values())
        owner = next(i for i, m in sorted(project.maps.items()) if m.get("placements"))
        source = f"map:{owner:04d}/placement:{project.maps[owner]['placements'][0]['index']:04d}"
        clone = clone_placement(roots[0], map_index=owner, source=source, name="toolkit022",
                                position_low=123, position_high=456)
        assert validate_project(roots[0], rom, catalog).passed
        run, = authored_capacity_plan(roots[0], rom, catalog)
        assert owner == 10 and run.allocation_request.size == 108
        assert run.record(clone.identity).provenance == "AUTHORED_CLONE"
        assert len(run.records) == len(project.maps[owner]["placements"]) + 1
        assert run == authored_capacity_plan(roots[0], rom, catalog)[0]
        profile = next(p for p in catalog.profiles if p.id == project.meta.profile_id)
        assert profile.free_regions == ()
        # A capacity feasibility check, NOT a claim that build reached allocation.
        with pytest.raises(InsufficientSpaceError) as capacity:
            allocate(profile, [run.allocation_request])
        # TOOLKIT-025: the derived `MapEntry+0x04` count write now EXISTS, so the build
        # no longer stops on an unwritable count. It is derived from the validated
        # object array - never supplied by the project - and names the exact byte it
        # changes. Map 10's MapEntry sits at file 0x08E510, so the count byte is 0x08E514.
        change = run.derive_count_change(before)
        assert change.offset == 0x08E514
        assert (change.old, change.new) == (bytes((2,)), bytes((3,)))
        assert change.owner == "map:0010/object_array_count"
        assert "authored object-array expansion" in change.reason
        assert run.canonical_engine_count == 2 and run.target_slot_count == 3
        # The canonical array is carried whole, siblings included; map 10 happens to be
        # homogeneous, so its slot count equals its placement count.
        assert len(run.canonical_slots) == 2
        assert all(s.is_placement for s in run.canonical_slots)

        # TOOLKIT-026: the array anchor is relocatable in the production graph, so
        # the build passes that gate and stops one boundary later. Read the flag off
        # the same document the build uses, rather than restating it.
        from tools.webfoot.entities import PlacementTypes
        document = PlacementTypes(maps_for(rom, catalog)).reference_document()
        anchor = document.anchor(run.identity)
        assert anchor.kind == "placement_reference_array"
        assert anchor.relocatable is True
        assert anchor.range.start.value == 0x07293C and anchor.range.size == 8
        owner = [r for r in document.references if r.target == run.identity]
        assert len(owner) == 1 and owner[0].source.value == 0x08E524
        # Nothing else in the graph became movable.
        assert all(not a.relocatable for a in document.anchors
                   if a.kind != "placement_reference_array")

        errors = []
        for index in range(2):
            out, manifest = tmp_path / f"authored{index}.gba", tmp_path / f"authored{index}.json"
            # The blocker moved one gate downstream again: the array now relocates,
            # and what remains is the authored record body, which has no anchor and
            # no array-slot reference for the appended slot to point at.
            with pytest.raises(LayoutError, match="unmodelled authored record bodies") as blocked:
                build_project(roots[0], rom, out, catalog, manifest_path=manifest)
            errors.append(str(blocked.value))
            assert not out.exists() and not manifest.exists()
        assert errors[0] == errors[1]
        assert "derived count write is AVAILABLE and validated" in errors[0]
        assert "array anchor IS relocatable" in errors[0]
        assert "unwritable engine count" not in errors[0]
        assert "non-relocatable" not in errors[0]
        assert clone.identity in errors[0]
        evidence = {**run.to_json(), "capacity_feasibility_error": str(capacity.value),
                    "production_build_error": errors[0], "extraction_files": len(contents(roots[1])),
                    "noop_bytes": len(before), "base_sha256": SHA}
        print(json.dumps(evidence, indent=2))
    finally:
        assert hashlib.sha256(rom.read_bytes()).hexdigest() == SHA
        assert rom.stat().st_mtime_ns == stamp


def test_a_project_extracted_before_the_eligibility_rule_fails_closed(tmp_path):
    """TOOLKIT-026 compatibility: a stale reference graph is refused, not used.

    The extracted `events/placement_descriptors.json` mirrors the verified base's
    reference graph, `relocatable` column included, and `_check_maps` compares it
    against a freshly derived one. Publishing eligibility therefore changes that
    file, so a project extracted before this change no longer matches its base.

    That is the intended fail-closed behaviour rather than a silent acceptance:
    the catalog is a verified-base mirror, not editable content, and re-extracting
    the project resolves it. This test pins that a stale graph is REFUSED, and
    that the refusal names the catalog rather than failing somewhere later.
    """
    candidates = sorted(Path("roms").glob("*Buu*.gba"))
    if not candidates:
        pytest.skip("canonical Buu ROM not configured locally")
    rom = candidates[0]
    if hashlib.sha256(rom.read_bytes()).hexdigest() != SHA:
        pytest.skip("local ROM does not match exact canonical Buu identity")
    stamp = rom.stat().st_mtime_ns
    catalog = RomProfileCatalog.load("config/roms.yaml")
    try:
        root = tmp_path / "project"
        extract_project(rom, root, catalog, graphics=False)
        assert validate_project(root, rom, catalog).passed

        catalog_file = root / "events" / "placement_descriptors.json"
        document = json.loads(catalog_file.read_text())
        graph = document["reference_graph"]
        column = graph["anchor_columns"].index("relocatable")
        # A fresh extract publishes the eligible arrays.
        assert sum(1 for row in graph["anchors"] if row[column]) == 268
        # Rewind to the pre-TOOLKIT-026 shape: every anchor non-relocatable.
        for row in graph["anchors"]:
            row[column] = False
        catalog_file.write_text(
            json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8", newline="\n")

        result = validate_project(root, rom, catalog)
        assert not result.passed
        assert any("catalog differs from verified base" in p for p in result.problems)
    finally:
        assert hashlib.sha256(rom.read_bytes()).hexdigest() == SHA
        assert rom.stat().st_mtime_ns == stamp
