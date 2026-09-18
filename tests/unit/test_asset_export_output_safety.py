"""Portable tests for ASSET-EXPORT-001 output safety, dedup reporting and CLI
guards. No ROM is required; the ROM-identity guard is exercised with synthetic
bytes.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.export import buu_resource_export as export
from tools.export import metadata as meta


# --- repository-ancestry guard ----------------------------------------------

def test_a_real_repository_root_is_detected(tmp_path: Path):
    repository = tmp_path / "repo"
    (repository / ".git").mkdir(parents=True)
    (repository / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    assert export.is_repository_root(repository)
    assert export.find_repository_root(repository / "deep" / "nested") == repository


def test_a_linked_worktree_gitfile_is_detected(tmp_path: Path):
    worktree = tmp_path / "wt"
    worktree.mkdir()
    (worktree / ".git").write_text("gitdir: /somewhere/.git/worktrees/wt\n", encoding="utf-8")
    assert export.is_repository_root(worktree)


def test_a_stray_empty_git_directory_is_not_a_repository(tmp_path: Path):
    """An interrupted clone or a bare `mkdir .git` must not refuse safe output."""
    stray = tmp_path / "stray"
    (stray / ".git").mkdir(parents=True)
    assert not export.is_repository_root(stray)
    assert export.find_repository_root(stray) is None


def test_output_inside_a_repository_is_refused(tmp_path: Path):
    repository = tmp_path / "repo"
    (repository / ".git").mkdir(parents=True)
    (repository / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    with pytest.raises(export.ExportError) as excinfo:
        export.ensure_outside_repository(repository / "Present", "resource output root")
    assert "outside version control" in str(excinfo.value)


def test_output_outside_any_repository_is_accepted(tmp_path: Path):
    export.ensure_outside_repository(tmp_path / "BuuFury_Resources", "resource output root")


def test_audit_root_is_a_sibling_with_the_suffix(tmp_path: Path):
    output = tmp_path / "BuuFury_Resources"
    assert export.audit_root_for(output) == tmp_path / "BuuFury_Resources_Audit"


# --- the exporter's own repository -------------------------------------------

def test_this_checkout_is_inside_a_repository():
    """The guard is meaningful here: the exporter itself lives in a work tree."""
    module_root = Path(export.__file__).resolve().parent
    assert export.find_repository_root(module_root) is not None


# --- ROM identity ------------------------------------------------------------

def test_a_non_canonical_rom_is_refused(tmp_path: Path):
    fake = tmp_path / "fake.gba"
    fake.write_bytes(b"\x00" * 1024)
    with pytest.raises(export.ExportError) as excinfo:
        export.read_canonical_rom(fake)
    assert "not the canonical Buu's Fury image" in str(excinfo.value)


def test_a_missing_rom_is_refused(tmp_path: Path):
    with pytest.raises(export.ExportError):
        export.read_canonical_rom(tmp_path / "absent.gba")


# --- CLI guards --------------------------------------------------------------

def _arguments(tmp_path: Path, *extra: str) -> list[str]:
    return [
        "--rom", str(tmp_path / "rom.gba"),
        "--output", str(tmp_path / "out"),
        *extra,
    ]


def test_cli_refuses_a_rom_that_is_not_canonical(tmp_path: Path):
    (tmp_path / "rom.gba").write_bytes(b"\x01" * 32)
    assert export.main(_arguments(tmp_path)) == 1


def test_cli_reports_a_refusal_as_a_message_not_a_traceback(tmp_path: Path, capsys):
    """A refusal must read as a refusal, with a status and no stack trace."""
    repository = tmp_path / "repo"
    (repository / ".git").mkdir(parents=True)
    (repository / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (tmp_path / "rom.gba").write_bytes(b"\x01" * 32)
    status = export.main(
        ["--rom", str(tmp_path / "rom.gba"), "--output", str(repository / "Present")]
    )
    captured = capsys.readouterr()
    assert status == 1
    assert captured.out == ""
    assert "Traceback" not in captured.err
    assert "outside version control" in captured.err
    assert captured.err.startswith(export.TOOL_NAME + ":")


def test_cli_reports_a_missing_rom_as_a_message(tmp_path: Path, capsys):
    status = export.main(_arguments(tmp_path))
    captured = capsys.readouterr()
    assert status == 1
    assert "Traceback" not in captured.err
    assert "does not exist" in captured.err


def test_cli_refuses_output_inside_a_repository(tmp_path: Path):
    repository = tmp_path / "repo"
    (repository / ".git").mkdir(parents=True)
    (repository / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (tmp_path / "rom.gba").write_bytes(b"\x01" * 32)
    with pytest.raises(export.ExportError) as excinfo:
        export._export(
            export.build_parser().parse_args(
                ["--rom", str(tmp_path / "rom.gba"),
                 "--output", str(repository / "Present")]
            )
        )
    assert "outside version control" in str(excinfo.value)


def test_cli_refuses_an_audit_root_equal_to_the_output_root(tmp_path: Path):
    (tmp_path / "rom.gba").write_bytes(b"\x01" * 32)
    with pytest.raises(export.ExportError):
        export._export(
            export.build_parser().parse_args(
                [
                    "--rom", str(tmp_path / "rom.gba"),
                    "--output", str(tmp_path / "out"),
                    "--audit", str(tmp_path / "out"),
                ]
            )
        )


def test_cli_refuses_a_nested_audit_root(tmp_path: Path):
    (tmp_path / "rom.gba").write_bytes(b"\x01" * 32)
    with pytest.raises(export.ExportError):
        export._export(
            export.build_parser().parse_args(
                [
                    "--rom", str(tmp_path / "rom.gba"),
                    "--output", str(tmp_path / "out"),
                    "--audit", str(tmp_path / "out" / "audit"),
                ]
            )
        )


def test_cli_refuses_a_non_empty_output_without_force(tmp_path: Path, monkeypatch):
    output = tmp_path / "out"
    output.mkdir()
    (output / "stale.png").write_bytes(b"x")
    monkeypatch.setattr(export, "read_canonical_rom", lambda path: b"\x00" * 16)
    with pytest.raises(export.ExportError) as excinfo:
        export._export(
            export.build_parser().parse_args(_arguments(tmp_path))
        )
    assert "--force" in str(excinfo.value)


def test_clear_generated_removes_only_the_exporters_own_directories(tmp_path: Path):
    root = tmp_path / "out"
    for name in export.GENERATED_DIRECTORIES:
        (root / name).mkdir(parents=True)
        (root / name / "artifact.png").write_bytes(b"x")
    (root / "USER_NOTES").mkdir()
    (root / "user_file.txt").write_text("mine", encoding="utf-8")
    foreign = export.clear_generated(root)
    for name in export.GENERATED_DIRECTORIES:
        assert not (root / name).exists()
    assert (root / "USER_NOTES").is_dir()
    assert (root / "user_file.txt").read_text(encoding="utf-8") == "mine"
    assert foreign == ("USER_NOTES", "user_file.txt")


def test_clear_generated_on_an_absent_root_is_a_no_op(tmp_path: Path):
    assert export.clear_generated(tmp_path / "absent") == ()


def test_generated_directories_are_exactly_the_documented_layout():
    assert export.GENERATED_DIRECTORIES == (
        "maps",
        "tiles",
        "sprites",
        "sprite_graphics",
        "palettes",
        "metadata",
    )


def test_default_selection_is_every_subsystem():
    parser = export.build_parser()
    args = parser.parse_args(["--rom", "r", "--output", "o"])
    every = args.all or not (args.maps or args.tiles or args.sprites)
    assert every


def test_subsystem_flags_are_independent():
    parser = export.build_parser()
    args = parser.parse_args(["--rom", "r", "--output", "o", "--sprites"])
    assert args.sprites and not args.maps and not args.tiles
    assert not (args.all or not (args.maps or args.tiles or args.sprites))


# --- audit documents ---------------------------------------------------------

def test_duplicate_document_groups_identical_content(tmp_path: Path):
    exporter = export.Exporter.__new__(export.Exporter)
    exporter.writer = export.Writer(tmp_path / "out", enabled=False)
    exporter.writer.write("a.png", b"same")
    exporter.writer.write("b.png", b"same")
    exporter.writer.write("c.png", b"other")
    document = export.Exporter.duplicate_document(exporter)
    assert document["artifact_count"] == 3
    assert document["distinct_content_count"] == 2
    assert document["duplicate_group_count"] == 1
    groups = document["duplicate_groups"]
    assert list(groups.values()) == [["a.png", "b.png"]]


def test_duplicate_document_is_sorted_for_determinism(tmp_path: Path):
    exporter = export.Exporter.__new__(export.Exporter)
    exporter.writer = export.Writer(tmp_path / "out", enabled=False)
    for name in ("z.png", "a.png", "m.png"):
        exporter.writer.write(name, b"same")
    document = export.Exporter.duplicate_document(exporter)
    assert list(document["duplicate_groups"].values()) == [["a.png", "m.png", "z.png"]]


def test_writer_digests_what_it_writes(tmp_path: Path):
    writer = export.Writer(tmp_path / "out", enabled=True)
    artifact = writer.write("metadata/x.json", b"hello")
    assert artifact.sha256 == export.sha256_bytes(b"hello")
    assert (tmp_path / "out" / "metadata" / "x.json").read_bytes() == b"hello"
    assert writer.total_bytes == 5


def test_writer_records_artifacts_when_disabled(tmp_path: Path):
    writer = export.Writer(tmp_path / "out", enabled=False)
    artifact = writer.write("a.png", b"data")
    assert artifact.size == 4
    assert not (tmp_path / "out").exists()


# --- comparison mode ---------------------------------------------------------

def test_compare_passes_on_an_identical_tree(tmp_path: Path):
    root = tmp_path / "tree"
    (root / "maps").mkdir(parents=True)
    (root / "maps" / "composite.png").write_bytes(b"pixels")
    hashes = tmp_path / "hashes.csv"
    hashes.write_text(
        "relative_path,bytes,sha256\n"
        f"maps/composite.png,6,{export.sha256_bytes(b'pixels')}\n",
        encoding="utf-8",
    )
    same, result = export.compare_with(root, hashes)
    assert same
    assert result["differing_count"] == 0


def test_compare_reports_a_difference(tmp_path: Path):
    root = tmp_path / "tree"
    (root / "a.png").mkdir(parents=True)
    (root / "a.png" / "b.png").write_bytes(b"changed")
    hashes = tmp_path / "hashes.csv"
    hashes.write_text(
        "relative_path,bytes,sha256\n"
        f"a.png/b.png,7,{export.sha256_bytes(b'original')}\n",
        encoding="utf-8",
    )
    same, result = export.compare_with(root, hashes)
    assert not same
    assert result["differing_count"] == 1


def test_compare_reports_missing_and_extra(tmp_path: Path):
    root = tmp_path / "tree"
    root.mkdir()
    (root / "extra.png").write_bytes(b"x")
    hashes = tmp_path / "hashes.csv"
    hashes.write_text("relative_path,bytes,sha256\ngone.png,1,aa\n", encoding="utf-8")
    same, result = export.compare_with(root, hashes)
    assert not same
    assert result["missing_count"] == 1
    assert result["extra_count"] == 1


def test_compare_without_a_hash_table_is_refused(tmp_path: Path):
    with pytest.raises(export.ExportError):
        export.compare_with(tmp_path, tmp_path / "absent.csv")


# --- the produced library carries no prose -----------------------------------

def test_a_produced_tree_with_no_prose_passes_the_scan(tmp_path: Path):
    (tmp_path / "metadata").mkdir()
    (tmp_path / "metadata" / "maps.json").write_text(
        json.dumps({"maps": [{"map_index": 0}]}), encoding="utf-8"
    )
    (tmp_path / "layer_0.png").write_bytes(b"\x89PNG")
    assert meta.scan_for_prose_files(tmp_path) == ()
    assert meta.scan_for_prose_keys(tmp_path) == ()


def test_a_produced_tree_with_a_readme_fails_the_scan(tmp_path: Path):
    (tmp_path / "README.md").write_text("how to use", encoding="utf-8")
    assert len(meta.scan_for_prose_files(tmp_path)) == 1


@pytest.mark.parametrize("name", ["NOTES.txt", "readme.markdown", "doc.rst"])
def test_every_document_suffix_is_caught(tmp_path: Path, name: str):
    (tmp_path / name).write_text("prose", encoding="utf-8")
    assert len(meta.scan_for_prose_files(tmp_path)) == 1


def test_unreadable_json_is_reported_by_the_scan(tmp_path: Path):
    (tmp_path / "broken.json").write_text("{not json", encoding="utf-8")
    found = meta.scan_for_prose_keys(tmp_path)
    assert len(found) == 1
    assert "unreadable" in found[0][1]
