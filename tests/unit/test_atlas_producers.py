"""ROM-ATLAS-001 producer proofs. Synthetic ROM bytes only; no commercial image.

The producers themselves assert the canonical ROM's SHA-256, so these tests
exercise the properties that do not need 8 MiB of real image: that the package
carries no absolute path, that the traversal derives its records from bytes
alone, that the region producer never reads a prior `code_regions.jsonl`, and
that the pipeline's stage order leaves no producer depending on its own output.
"""

import ast
import inspect
from pathlib import Path

import pytest

from tools.webfoot.atlas_producers import (code_functions, graphics_extents,
                                           pipeline, regions, scan, seed)
from tools.webfoot.atlas_producers.traversal import BASE, Traversal, spans_from


PACKAGE = Path(regions.__file__).parent
MODULES = sorted(PACKAGE.glob("*.py"))


def _docstring_ids(tree: ast.AST) -> set[int]:
    """Ids of the string constants that are module/class/function docstrings.

    SC1 requires every module to name the scratchpad script it was ported from,
    and those provenance headers quote the originals verbatim — hardcoded
    `C:\\Dev` paths and the deleted `sys.argv` pass selector included. The
    prohibitions below are about executable code, so the prose is excluded
    rather than the rule weakened.
    """
    found = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if (isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                              ast.AsyncFunctionDef)) and body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)):
            found.add(id(body[0].value))
    return found


def _code_only(module: Path) -> str:
    """The module's source with every docstring blanked and comment stripped."""
    source = module.read_text(encoding="utf-8")
    tree = ast.parse(source)
    docstrings = _docstring_ids(tree)
    lines = source.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and id(node) in docstrings:
            for number in range(node.lineno - 1, node.end_lineno):
                lines[number] = ""
    return "\n".join(line.split("#")[0] for line in lines)


# --- the package is portable -------------------------------------------------


def test_no_absolute_path_literal_in_any_producer():
    """A hardcoded repository root is what made every original unusable."""
    offenders = []
    for module in MODULES:
        tree = ast.parse(module.read_text(encoding="utf-8"))
        docstrings = _docstring_ids(tree)
        for node in ast.walk(tree):
            if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                    and id(node) not in docstrings):
                text = node.value
                if "C:\\" in text or "C:/" in text or text.startswith("/home/"):
                    offenders.append((module.name, text[:60]))
    assert offenders == []


def test_every_producer_takes_its_paths_as_parameters():
    for build, wanted in ((seed.build, {"out_dir"}),
                          (graphics_extents.build, {"rom_path", "out_dir", "config_path"}),
                          (scan.build, {"rom_path", "out_dir"}),
                          (code_functions.build_wave2, {"rom_path", "out_dir"}),
                          (regions.build, {"out_dir"}),
                          (pipeline.run, {"rom_path", "out_dir"})):
        parameters = set(inspect.signature(build).parameters)
        assert wanted <= parameters, (build.__name__, parameters)


def test_the_rom_is_only_ever_opened_read_only():
    """No producer may open the image for writing, truncating or appending."""
    for module in MODULES:
        code = _code_only(module)
        for mode in ('"wb"', "'wb'", '"r+b"', "'r+b'", '"ab"', "'ab'"):
            assert mode not in code, (module.name, mode)
        tree = ast.parse(module.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            # `Path.write_bytes` on anything is the other way to damage a ROM.
            if isinstance(node, ast.Attribute) and node.attr == "write_bytes":
                pytest.fail(f"{module.name} calls write_bytes")


# --- the broken chain is actually broken --------------------------------------


def test_regions_never_reads_a_prior_code_regions_file():
    """SC2: `code_regions.jsonl` must not depend on a previous copy of itself."""
    source = Path(regions.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    reads = [node for node in ast.walk(tree)
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
             and node.func.id == "read_jsonl"]
    assert reads == [], "regions.py must derive from traversal records, not artifacts"
    assert "read_jsonl" not in {n.name for node in ast.walk(tree)
                                if isinstance(node, ast.ImportFrom)
                                for n in node.names}


def test_regions_build_signature_takes_traversals_not_artifact_rows():
    parameters = inspect.signature(regions.build).parameters
    assert "wave2" in parameters and "wave4" in parameters
    assert not any("region" in name for name in parameters)


def test_no_producer_reads_the_artifact_it_writes():
    """Each module's own output file must never appear in a read path."""
    writes = {
        "seed.py": ("seed_knowledge.jsonl",),
        "graphics_extents.py": ("graphics_extents.jsonl",),
        "regions.py": ("code_regions.jsonl",),
        "code_functions.py": ("code_functions.jsonl", "code_functions_wave4.jsonl"),
    }
    for name, artifacts in writes.items():
        source = (PACKAGE / name).read_text(encoding="utf-8")
        tree = ast.parse(source)
        read_targets = set()
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "read_jsonl"):
                for constant in ast.walk(node):
                    if isinstance(constant, ast.Constant) and isinstance(constant.value, str):
                        read_targets.add(constant.value)
        for artifact in artifacts:
            assert artifact not in read_targets, f"{name} reads its own {artifact}"


# --- all six scan passes are unconditional ------------------------------------


def test_scan_has_no_pass_selector():
    """The historical `ONLY` argv gate produced three partial runs; it is gone."""
    code = _code_only(Path(scan.__file__))
    assert "sys.argv" not in code
    assert "ONLY" not in code


def test_scan_build_writes_all_six_artifacts(monkeypatch, tmp_path):
    """Every pass must emit, in one invocation, with no selector to skip any."""
    written = []
    for name in ("_text_rows", "_pointer_rows", "_pointer_table_rows",
                 "_entropy_rows", "_compression_rows", "_code_shape_rows"):
        assert hasattr(scan, name), name

    monkeypatch.setattr(scan, "_text_rows", lambda *a, **k: [])
    monkeypatch.setattr(scan, "_pointer_rows", lambda *a, **k: [])
    monkeypatch.setattr(scan, "_pointer_table_rows", lambda *a, **k: [])
    monkeypatch.setattr(scan, "_entropy_rows", lambda *a, **k: [])
    monkeypatch.setattr(scan, "_compression_rows", lambda *a, **k: ([], 0))
    monkeypatch.setattr(scan, "_code_shape_rows", lambda *a, **k: ([], 0))

    rom = tmp_path / "synthetic.gba"
    rom.write_bytes(bytes(scan.IMAGE_SIZE))
    out = tmp_path / "out"
    out.mkdir()
    (out / "seed_knowledge.jsonl").write_text("", encoding="utf-8")

    summary = scan.build(rom, out)
    for name in ("scan_text", "scan_pointers", "scan_pointer_tables",
                 "scan_entropy", "scan_compression", "scan_code_shape"):
        assert (out / f"{name}.jsonl").is_file(), name
        assert name in summary
    written.append(summary)


# --- traversal derives from bytes ---------------------------------------------


def _thumb_rom(size=0x1000):
    """A tiny synthetic image: push {lr} ... pop {pc} at offset 0."""
    data = bytearray(b"\x00" * size)
    data[0:2] = (0xB500).to_bytes(2, "little")  # push {lr}
    data[2:4] = (0xBD00).to_bytes(2, "little")  # pop {pc}
    return bytes(data)


def test_traversal_walks_a_synthetic_function_and_records_its_end():
    walker = Traversal(_thumb_rom())
    end, reason, calls, ptrs, pools, _span = walker.walk(BASE)
    assert end == BASE + 4
    assert reason == "pop_with_pc"
    assert calls == set() and ptrs == [] and pools == set()
    assert {0, 1, 2, 3} <= walker.reached_bytes


def test_traversal_prologue_text_names_the_pushed_registers():
    walker = Traversal(_thumb_rom())
    assert walker.prologue_text(BASE) == "push {lr}"


def test_jump_tables_are_derived_from_rom_bytes_only():
    """Eight consecutive aligned odd in-ROM words make a table; seven do not."""
    for entries, expected in ((8, 1), (7, 0)):
        data = bytearray(b"\x00" * 0x200)
        for index in range(entries):
            data[index * 4:index * 4 + 4] = (BASE + 0x101).to_bytes(4, "little")
        walker = Traversal(bytes(data))
        tables = walker.jump_tables(0, len(data))
        assert len(tables) == expected, entries
        if expected:
            assert tables[0]["entries"] == entries
            assert tables[0]["size"] == entries * 4


def test_spans_from_merges_only_contiguous_offsets():
    assert spans_from({1, 2, 3, 7, 8}) == [(1, 4), (7, 9)]
    assert spans_from(set()) == []


# --- the pipeline order is the documented one ---------------------------------


def test_pipeline_runs_producers_in_the_dependency_order():
    code = _code_only(Path(pipeline.__file__))
    order = []
    for marker in ("seed.build", "graphics_extents.build", "scan.build",
                   "build_wave2", "build_wave4", "regions.build"):
        assert marker in code, marker
        order.append(code.index(marker))
    assert order == sorted(order), "stages must appear in dependency order"


def test_pipeline_refuses_a_rom_that_changed_under_it(tmp_path, monkeypatch):
    """SC/V6: the canonical image is read-only and the run proves it stayed so."""
    rom = tmp_path / "synthetic.gba"
    rom.write_bytes(b"\x00" * 16)
    out = tmp_path / "out"

    calls = {"n": 0}

    def mutating_seed(out_dir):
        calls["n"] += 1
        rom.write_bytes(b"\x01" * 16)  # simulate damage mid-run
        path = Path(out_dir) / "seed_knowledge.jsonl"
        path.write_text("", encoding="utf-8")
        return path

    monkeypatch.setattr(pipeline.seed, "build", mutating_seed)
    monkeypatch.setattr(pipeline.graphics_extents, "build",
                        lambda *a, **k: Path(a[1]) / "graphics_extents.jsonl")
    monkeypatch.setattr(pipeline.scan, "build", lambda *a, **k: {})
    monkeypatch.setattr(pipeline.code_functions, "build_wave2",
                        lambda *a, **k: (Path(a[1]) / "code_functions.jsonl", _Stub()))
    monkeypatch.setattr(pipeline.code_functions, "build_wave4",
                        lambda *a, **k: (Path(a[1]) / "code_functions_wave4.jsonl", _Stub()))
    monkeypatch.setattr(pipeline.regions, "build",
                        lambda *a, **k: Path(a[0]) / "code_regions.jsonl")
    monkeypatch.setattr(pipeline.code_functions, "write_coverage",
                        lambda *a, **k: Path(a[0]) / "code_coverage_wave4.json")

    with pytest.raises(RuntimeError, match="changed during the run"):
        pipeline.run(rom, out, assemble=False)
    assert calls["n"] == 1


class _Stub:
    functions: dict = {}


def test_a_clean_output_directory_is_enough_for_the_first_stage(tmp_path):
    """No producer may require a pre-existing artifact: seed reads nothing."""
    out = tmp_path / "empty"
    path = seed.build(out)
    assert path.is_file()
    #: The row count moves whenever a ticket records new structural evidence,
    #: so it is asserted as a floor rather than an equality: this test exists to
    #: prove the producer needs no pre-existing artifact, not to freeze the
    #: corpus. The previous `== 51` was frozen at 0e05cac and left stale by two
    #: later tickets, so it failed for a reason unrelated to what it checks.
    assert path.read_text(encoding="utf-8").count("\n") >= 51


def test_seed_output_is_byte_identical_across_two_runs(tmp_path):
    """Determinism at the one stage that needs no ROM."""
    first = seed.build(tmp_path / "a").read_bytes()
    second = seed.build(tmp_path / "b").read_bytes()
    assert first == second
