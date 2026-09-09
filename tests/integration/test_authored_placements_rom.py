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


def test_canonical_authoring_materializes_into_a_built_rom(tmp_path):
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
        # TOOLKIT-028: the profile now declares ONE verified 256-byte window. It is a
        # narrow carve of the tail TOOLKIT-011 refused whole, not that tail.
        region, = profile.free_regions
        assert (region.range.start.value, region.range.size) == (0x7EA400, 256)
        assert "TOOLKIT-028" in region.evidence
        # `allocation_request` is the OLD single-block packing PROPOSAL: 108 bytes,
        # 3 pointer slots plus all 3 whole bodies. The transaction the build actually
        # issues is smaller and split in two - a 32-byte body and a 12-byte array,
        # 44 bytes - because the two canonical bodies are not rewritten, only
        # re-pointed. This pins BOTH numbers so the stale proposal cannot quietly
        # become the sizing rule for a future declaration.
        assert run.allocation_request.size == 108
        assert allocate(profile, [run.allocation_request])[0].range.size == 108
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

        # TOOLKIT-028: the chain runs against the PRODUCTION profile, not a synthetic
        # one. The authored body is anchored by its stable project identity, allocated
        # by the production allocator out of the declared window, and its address is
        # what the relocated array's third slot actually holds.
        from tools.webfoot.authored_placements import plan_authored_materialization
        plan = plan_authored_materialization(document, run)
        placed = {a.request.anchor.value: a.range for a in plan.allocations}
        # The EXACT canonical demand, measured from the plan rather than assumed:
        # two requests, 32 + 12 = 44 bytes, both alignment 4.
        assert sorted((a.request.size, a.request.alignment) for a in plan.allocations) == [
            (12, 4), (32, 4)]
        assert sum(a.range.size for a in plan.allocations) == 44
        body_span = placed[clone.identity]
        assert placed[run.identity.value].size == 4 * 3
        assert body_span.size == len(run.authored_records[0].payload)
        # The two canonical map 10 slots are preserved byte-for-byte.
        moved = plan.relocation.document.anchor(run.identity)
        canonical_slots = before[0x07293C:0x07293C + 8]
        start = moved.range.start.value
        assert plan.relocation.document.image[start:start + 8] == canonical_slots
        # The third slot points at the authored body, not at 0x00000000.
        third = plan.slot_pointer(2)
        assert third != 0x00000000
        assert third == 0x08000000 + body_span.start.value
        assert plan.to_json() == plan_authored_materialization(document, run).to_json()
        # Both allocations land inside the ONE declared window, and stay disjoint.
        assert body_span.start.value >= 0x7EA400 and body_span.end <= 0x7EA500
        array_span = placed[run.identity.value]
        assert array_span.start.value >= 0x7EA400 and array_span.end <= 0x7EA500
        assert not body_span.overlaps(array_span)
        # The allocator used the PRODUCTION declaration, not an injected one.
        assert all("TOOLKIT-028" in a.free_region_evidence for a in plan.allocations)

        # TOOLKIT-028: the build now EMITS the expansion instead of refusing it.
        built = []
        for index in range(2):
            out, manifest = tmp_path / f"authored{index}.gba", tmp_path / f"authored{index}.json"
            result = build_project(roots[0], rom, out, catalog, manifest_path=manifest)
            assert out.exists() and manifest.exists()
            built.append((out.read_bytes(), json.loads(manifest.read_text())))
        # Repeated builds are byte-identical, ROM and manifest alike.
        assert built[0][0] == built[1][0]
        assert built[0][1] == built[1][1]
        image = built[0][0]
        assert len(image) == len(before)

        # EXACTLY the intended bytes changed - nothing else in the 8 MiB image.
        differing = [i for i in range(len(before)) if before[i] != image[i]]
        assert len(differing) == 48
        assert min(differing) == 0x08E514 and max(differing) == 0x7EA42B
        # The derived count, written as part of its own MapEntry record.
        assert image[0x08E514] == 3 and before[0x08E514] == 2
        # The owner pointer now addresses the relocated array.
        assert int.from_bytes(image[0x08E524:0x08E528], "little") == 0x08000000 + start
        # The two canonical slots survive the move byte-for-byte, and the third
        # slot in the BUILT image points at the authored body.
        assert image[start:start + 8] == canonical_slots
        assert int.from_bytes(image[start + 8:start + 12], "little") == third
        # The authored body's bytes are the production codec's, in the ROM.
        assert image[body_span.start.value:body_span.end] == run.authored_records[0].payload
        # Everything outside the declared window and that one MapEntry is untouched.
        assert image[:0x08E510] == before[:0x08E510]
        assert image[0x08E548:0x7EA400] == before[0x08E548:0x7EA400]
        assert image[0x7EA500:] == before[0x7EA500:]

        evidence = {**run.to_json(), "extraction_files": len(contents(roots[1])),
                    "noop_bytes": len(before), "base_sha256": SHA,
                    "authored_materialization": plan.to_json(),
                    "third_slot_pointer": f"0x{third:08X}",
                    "relocated_array_file_offset": start,
                    "built_sha256": hashlib.sha256(image).hexdigest(),
                    "changed_byte_count": len(differing),
                    "manifest": built[0][1]}
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
