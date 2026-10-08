"""WORKBENCH-001 live-QA fix: WriteError on a second build to the same output.

A second build raises `write.WriteError` ("refusing to overwrite"), which is NOT
a BuildError/ProjectError subclass and used to escape `_on_build` to the terminal.
The panel now catches it and, when the output file actually exists and is provably
not the source ROM, offers to overwrite (delete output + rebuild).

SC2 SAFETY: when the output path equals the source ROM the delete never happens.

WORKBENCH-OVERWRITE-ATOMICITY-001: a build publishes an artefact SET, and a
confirmed overwrite has to replace all of it.

`build_project` publishes the provenance manifest BESIDE its image, so on a second
build the writer refuses whichever of the two already exists - and a repair that
deletes only the image leaves the retry failing on the stale manifest, with the
user's previous output already gone. The two tests at the end of this file drive
the REAL publication path over the REAL manifest-name authority
(`build.manifest_path_for_build(MANIFEST_BESIDE_OUTPUT, ...)`) and the REAL
refusal gate (`write.emit_image`); only the project pipeline behind `build_project`
is replaced, so a stub can no longer hide the stale-manifest failure.

WORKBENCH-OVERWRITE-CANONICAL-GUARD-001: the overwrite branch also refuses a
destination that IS a copy of the canonical ROM, by content hash against
`session.profile.identity.sha256`, before the confirmation and before the first
unlink. The last test here drives that refusal over the same real publication path.
"""

import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest

# build_panel imports PySide6 at module scope; the SDK CI job installs only the
# base package. Skip before importing it so collection does not error there.
pytest.importorskip("PySide6")

from tools.webfoot import build as build_sdk  # noqa: E402
from tools.webfoot import write  # noqa: E402
from tools.webfoot.authored_image import staging_path  # noqa: E402
from tools.webfoot.workbench import build_panel as bp  # noqa: E402
from tools.webfoot.workbench.build_panel import BuildPanelTab, output_file_for  # noqa: E402
from tools.webfoot.workbench.session import Session  # noqa: E402
from tools.webfoot.write import WriteError  # noqa: E402
from PySide6.QtWidgets import QApplication, QMessageBox  # noqa: E402


#: The canonical bytes for this file's fake profile. The overwrite branch reads
#: the canonical identity as `session.profile.identity.sha256`, so the fixture has
#: to state one; it is derived from these bytes rather than written as a literal.
_CANONICAL_BYTES = b"synthetic canonical ROM fixture bytes"
_CANONICAL_SHA256 = hashlib.sha256(_CANONICAL_BYTES).hexdigest()


@pytest.fixture(scope="module")
def _app():
    return QApplication.instance() or QApplication([])


def _make_panel(tmp_path, _app):
    rom = tmp_path / "src" / "buus_fury.gba"
    rom.parent.mkdir()
    rom.write_bytes(b"\x00")
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    session = Session(
        rom_path=rom,
        profile=SimpleNamespace(
            id="buus_fury_usa_rev0",
            identity=SimpleNamespace(sha256=_CANONICAL_SHA256),
        ),
        project_dir=tmp_path / "proj",
        output_dir=out_dir,
    )
    session.record_validation(True)
    panel = BuildPanelTab(session, catalog=None)
    output_path = output_file_for(out_dir, session.profile.id)
    return panel, session, output_path


def test_overwrite_yes_deletes_output_and_rebuilds(tmp_path, monkeypatch, _app):
    panel, session, output_path = _make_panel(tmp_path, _app)
    output_path.write_bytes(b"OLD")  # simulate a prior build's output

    calls = {"n": 0, "finished": 0}

    def fake_build(project_dir, rom_path, out, catalog):
        calls["n"] += 1
        if Path(out).exists():
            raise WriteError("refusing to overwrite an existing output image")
        return SimpleNamespace(output_path=out)

    monkeypatch.setattr(bp.build_sdk, "build_project", fake_build)
    monkeypatch.setattr(QMessageBox, "question", staticmethod(lambda *a, **k: QMessageBox.Yes))
    panel.buildFinished.connect(lambda: calls.__setitem__("finished", calls["finished"] + 1))

    panel._on_build()  # must not raise

    assert not output_path.exists(), "prior output should have been unlinked"
    assert calls["n"] == 2, "build_project should be retried after unlink"
    assert calls["finished"] == 1, "buildFinished emitted on the retry"
    assert session.last_build is not None
    assert session.rom_path.exists(), "source ROM must never be touched"


def test_overwrite_no_keeps_output_no_crash(tmp_path, monkeypatch, _app):
    panel, session, output_path = _make_panel(tmp_path, _app)
    output_path.write_bytes(b"OLD")

    def fake_build(project_dir, rom_path, out, catalog):
        if Path(out).exists():
            raise WriteError("refusing to overwrite an existing output image")
        return SimpleNamespace(output_path=out)

    monkeypatch.setattr(bp.build_sdk, "build_project", fake_build)
    monkeypatch.setattr(QMessageBox, "question", staticmethod(lambda *a, **k: QMessageBox.No))

    panel._on_build()  # must not raise

    assert output_path.exists(), "output must be kept when the user declines"
    assert output_path.read_bytes() == b"OLD"
    assert session.last_build is None


def test_output_equals_rom_never_deletes(tmp_path, monkeypatch, _app):
    """SC2 SAFETY: if output_path resolves to the source ROM, no unlink, no build.

    The pre-build guard fires the refuse dialog; build_project is never called and
    the source ROM survives. Proven by making output_file_for return rom_path.
    """
    panel, session, _ = _make_panel(tmp_path, _app)
    rom = session.rom_path
    rom_before = rom.read_bytes()

    monkeypatch.setattr(bp, "output_file_for", lambda out_dir, pid: rom)
    build_called = {"n": 0}
    monkeypatch.setattr(
        bp.build_sdk, "build_project",
        lambda *a, **k: build_called.__setitem__("n", build_called["n"] + 1))
    monkeypatch.setattr(QMessageBox, "critical", staticmethod(lambda *a, **k: None))
    # If code ever reached the delete branch this would flag it:
    monkeypatch.setattr(QMessageBox, "question", staticmethod(lambda *a, **k: QMessageBox.Yes))

    panel._on_build()

    assert build_called["n"] == 0, "build must not run when guard fails"
    assert rom.exists() and rom.read_bytes() == rom_before, "source ROM untouched"


def test_stale_validation_never_authorizes_build(tmp_path, monkeypatch, _app):
    panel, session, _ = _make_panel(tmp_path, _app)
    session.project_mutated()
    build_called = {"n": 0}
    monkeypatch.setattr(
        bp.build_sdk, "build_project",
        lambda *a, **k: build_called.__setitem__("n", build_called["n"] + 1),
    )
    monkeypatch.setattr(QMessageBox, "information", staticmethod(lambda *a, **k: None))

    panel._on_build()

    assert build_called["n"] == 0
    assert not panel._build_button.isEnabled()


# --- WORKBENCH-OVERWRITE-ATOMICITY-001 ---------------------------------------


def _writer_backed_build(counter):
    """A `build_project` stand-in that performs the REAL two-artefact publish.

    The project pipeline is the one thing a unit test cannot run, so only that is
    replaced. The manifest name comes from `build.manifest_path_for_build` (the
    same authority `build_project` uses), the refusal and the publication come from
    `write.emit_image`, and the result is a real `BuildResult`. Each build writes a
    different first byte, so "these artefacts are not the previous build's" is
    decidable from the files themselves.
    """

    def fake_build(project_dir, rom_path, out, catalog):
        counter["n"] += 1
        source = Path(rom_path)
        out = Path(out)
        base = source.read_bytes()
        manifest_path = build_sdk.manifest_path_for_build(
            build_sdk.MANIFEST_BESIDE_OUTPUT, out)
        plan = write.plan_changes(
            base,
            (write.ByteChange(
                offset=0,
                old=base[0:1],
                new=bytes([counter["n"]]),
                owner="workbench-overwrite-test",
                reason="distinguish two builds in this test",
            ),),
            profile_id="synthetic-overwrite-test",
            base_sha256=hashlib.sha256(base).hexdigest(),
        )
        manifest = write.emit_image(source, out, plan, manifest_path=manifest_path)
        return build_sdk.BuildResult(
            manifest=manifest,
            output_path=out,
            manifest_path=manifest_path,
            project_name="overwrite-test",
        )

    return fake_build


def test_a_confirmed_overwrite_replaces_the_image_and_its_manifest(
    tmp_path, monkeypatch, _app
):
    """A confirmed overwrite replaces the whole artefact set, or nothing at all."""
    panel, session, output_path = _make_panel(tmp_path, _app)
    session.rom_path.write_bytes(b"\x00" * 64)
    source_before = session.rom_path.read_bytes()
    manifest_path = build_sdk.manifest_path_for_build(
        build_sdk.MANIFEST_BESIDE_OUTPUT, output_path)
    decoy = output_path.parent / "unrelated.txt"
    decoy.write_text("not this build's artefact", encoding="utf-8")

    counter = {"n": 0}
    criticals = []
    monkeypatch.setattr(bp.build_sdk, "build_project", _writer_backed_build(counter))
    monkeypatch.setattr(
        QMessageBox, "question", staticmethod(lambda *a, **k: QMessageBox.Yes))
    monkeypatch.setattr(
        QMessageBox, "critical", staticmethod(lambda *a, **k: criticals.append(a)))

    # 1-3: the first build publishes the image AND its beside-output manifest.
    panel._on_build()
    assert not criticals, criticals
    assert counter["n"] == 1
    assert output_path.is_file()
    assert manifest_path.is_file()
    first_image = output_path.read_bytes()
    first_manifest = manifest_path.read_text(encoding="utf-8")

    # 4-9: the second build meets the existing set, the user confirms, the stale
    # set is replaced and the rebuild succeeds.
    panel._on_build()
    assert not criticals, criticals
    assert counter["n"] == 3, "the rebuild must run once the old set is removed"
    assert output_path.is_file(), "the new image must exist"
    assert manifest_path.is_file(), "the new manifest must exist"

    # 10: neither artefact is the previous build's.
    assert output_path.read_bytes() != first_image
    assert manifest_path.read_text(encoding="utf-8") != first_manifest

    # 11: the source ROM is byte-identical, and no sibling was touched.
    assert session.rom_path.read_bytes() == source_before
    assert decoy.read_text(encoding="utf-8") == "not this build's artefact"


def test_an_unsafe_artefact_is_refused_rather_than_unlinked(
    tmp_path, monkeypatch, _app
):
    """SAFETY: every path in the set is re-checked before the one destructive act.

    The pre-build guard judges the image, which is safe here. The manifest is made
    to fail the same policy, so the overwrite must refuse with nothing removed and
    no rebuild attempted.
    """
    panel, session, output_path = _make_panel(tmp_path, _app)
    session.rom_path.write_bytes(b"\x00" * 64)
    manifest_path = build_sdk.manifest_path_for_build(
        build_sdk.MANIFEST_BESIDE_OUTPUT, output_path)

    counter = {"n": 0}
    criticals = []
    monkeypatch.setattr(bp.build_sdk, "build_project", _writer_backed_build(counter))
    monkeypatch.setattr(
        QMessageBox, "critical", staticmethod(lambda *a, **k: criticals.append(a)))

    panel._on_build()  # both artefacts now exist
    assert output_path.is_file() and manifest_path.is_file()
    image_before = output_path.read_bytes()
    manifest_before = manifest_path.read_text(encoding="utf-8")
    attempts = counter["n"]

    real_guard = bp.is_safe_output_path
    monkeypatch.setattr(
        bp,
        "is_safe_output_path",
        lambda path, rom: Path(path) != manifest_path and real_guard(path, rom),
    )
    monkeypatch.setattr(
        QMessageBox, "question", staticmethod(lambda *a, **k: QMessageBox.Yes))

    panel._on_build()

    assert criticals, "an unsafe artefact must be reported"
    assert counter["n"] == attempts + 1, "no rebuild may run after the refusal"
    assert output_path.read_bytes() == image_before, "the image must survive"
    assert manifest_path.read_text(encoding="utf-8") == manifest_before


# --- WORKBENCH-OVERWRITE-CANONICAL-GUARD-001 ---------------------------------


def test_a_canonical_copy_at_the_output_is_never_replaced(tmp_path, monkeypatch, _app):
    """SAFETY: a clean copy of the canonical ROM is a ROM, not an overwritable output.

    `is_safe_output_path` compares the destination to the source ROM by FILE
    IDENTITY, so a byte-identical copy of the canonical ROM sitting under the
    generated-output name passes it. Nothing else on the overwrite path asked
    whether the destination merely *is* the canonical image, so a confirmed
    overwrite would unlink a ROM. The whole occupied set must survive a refusal,
    and no rebuild may run.
    """
    panel, session, output_path = _make_panel(tmp_path, _app)
    # The source ROM is the canonical image, and the destination is a second
    # clean copy of it under the generated name.
    session.rom_path.write_bytes(_CANONICAL_BYTES)
    source_before = session.rom_path.read_bytes()
    assert hashlib.sha256(source_before).hexdigest() == _CANONICAL_SHA256
    manifest_path = build_sdk.manifest_path_for_build(
        build_sdk.MANIFEST_BESIDE_OUTPUT, output_path)
    output_path.write_bytes(_CANONICAL_BYTES)
    manifest_path.write_text('{"stale": "manifest"}', encoding="utf-8")
    image_before = output_path.read_bytes()
    manifest_before = manifest_path.read_text(encoding="utf-8")
    published_before = sorted(path.name for path in output_path.parent.iterdir())

    counter = {"n": 0}
    criticals = []
    monkeypatch.setattr(bp.build_sdk, "build_project", _writer_backed_build(counter))
    monkeypatch.setattr(
        QMessageBox, "question", staticmethod(lambda *a, **k: QMessageBox.Yes))
    monkeypatch.setattr(
        QMessageBox, "critical", staticmethod(lambda *a, **k: criticals.append(a)))

    panel._on_build()

    assert criticals, "a canonical copy at the destination must refuse the overwrite"
    assert "canonical" in criticals[0][2], criticals
    assert counter["n"] == 1, "no rebuild may run after the refusal"
    assert output_path.exists(), "the canonical copy must not be unlinked"
    assert output_path.read_bytes() == image_before
    assert manifest_path.exists(), "no companion artefact may be unlinked"
    assert manifest_path.read_text(encoding="utf-8") == manifest_before
    assert session.rom_path.read_bytes() == source_before
    assert sorted(path.name for path in output_path.parent.iterdir()) == published_before
    assert session.last_build is None


# --- CQA-11: a failed rebuild must not destroy the known-good output ---------


def test_a_failed_rebuild_keeps_the_previous_output(tmp_path, monkeypatch, _app):
    """RELEASE BLOCKER CQA-11: a confirmed overwrite must not delete before it builds.

    The overwrite branch unlinked every occupied artefact and only then called
    `_run_build`, so a rebuild that failed after the delete left the user with
    neither the previous output nor a new one. The previous set is now renamed
    aside and restored when the rebuild fails.
    """
    panel, session, output_path = _make_panel(tmp_path, _app)
    session.rom_path.write_bytes(b"\x00" * 64)
    manifest_path = build_sdk.manifest_path_for_build(
        build_sdk.MANIFEST_BESIDE_OUTPUT, output_path)

    counter = {"n": 0}
    monkeypatch.setattr(bp.build_sdk, "build_project", _writer_backed_build(counter))
    monkeypatch.setattr(
        QMessageBox, "question", staticmethod(lambda *a, **k: QMessageBox.Yes))
    panel._on_build()  # a real image and its real manifest now exist

    assert output_path.is_file() and manifest_path.is_file()
    first_image = output_path.read_bytes()
    first_manifest = manifest_path.read_text(encoding="utf-8")
    published_before = sorted(path.name for path in output_path.parent.iterdir())
    first_build = session.last_build

    def failing_build(project_dir, rom_path, out, catalog):
        if Path(out).exists():
            raise WriteError("refusing to overwrite an existing output image")
        raise failure

    for failure in (
        build_sdk.BuildError("the replacement could not be built"),
        # A bare OSError is the writer's own staging failure (a full disk, a
        # read-only output directory). It is not a BuildError and not a WriteError,
        # so the slot has to name it explicitly or the click produces no dialog.
        OSError("the output directory is not writable"),
    ):
        criticals = []
        monkeypatch.setattr(bp.build_sdk, "build_project", failing_build)
        monkeypatch.setattr(
            QMessageBox, "critical", staticmethod(lambda *a, **k: criticals.append(a)))

        panel._on_build()  # must not raise

        assert criticals, f"a failed rebuild must be reported: {failure!r}"
        assert output_path.is_file(), "the known-good image must survive a failed rebuild"
        assert output_path.read_bytes() == first_image
        assert manifest_path.is_file()
        assert manifest_path.read_text(encoding="utf-8") == first_manifest
        assert sorted(path.name for path in output_path.parent.iterdir()) == published_before, (
            "no staging artefact may be left behind")
        assert session.last_build is first_build
        assert session.rom_path.read_bytes() == b"\x00" * 64


def test_a_first_build_that_fails_with_a_bare_oserror_is_reported(
    tmp_path, monkeypatch, _app
):
    """The FIRST attempt's handler names OSError too, not only the retry's.

    `emit_image` raises a bare OSError from its own staging (a full disk, a
    read-only output directory). It is neither a BuildError nor a WriteError, so a
    handler that omits it turns the click into a traceback with no dialog.
    """
    panel, session, output_path = _make_panel(tmp_path, _app)
    session.rom_path.write_bytes(b"\x00" * 64)
    criticals = []

    def failing_build(project_dir, rom_path, out, catalog):
        raise OSError("the output directory is not writable")

    monkeypatch.setattr(bp.build_sdk, "build_project", failing_build)
    monkeypatch.setattr(
        QMessageBox, "critical", staticmethod(lambda *a, **k: criticals.append(a)))

    panel._on_build()  # must not raise

    assert criticals, "a first-build OSError must reach the user as a dialog"
    assert "not writable" in criticals[0][2]


def test_a_stale_manifest_with_no_image_can_still_be_replaced(
    tmp_path, monkeypatch, _app
):
    """The gate judges the artefact set, so a lone manifest is not a dead end."""
    panel, session, output_path = _make_panel(tmp_path, _app)
    session.rom_path.write_bytes(b"\x00" * 64)
    manifest_path = build_sdk.manifest_path_for_build(
        build_sdk.MANIFEST_BESIDE_OUTPUT, output_path)
    manifest_path.write_text('{"stale": "manifest"}', encoding="utf-8")

    counter = {"n": 0}
    criticals = []
    monkeypatch.setattr(bp.build_sdk, "build_project", _writer_backed_build(counter))
    monkeypatch.setattr(
        QMessageBox, "question", staticmethod(lambda *a, **k: QMessageBox.Yes))
    monkeypatch.setattr(
        QMessageBox, "critical", staticmethod(lambda *a, **k: criticals.append(a)))

    panel._on_build()

    assert not criticals, criticals
    assert output_path.is_file(), "the build must be allowed to replace a lone manifest"
    assert counter["n"] == 2, "the first attempt is refused, the retry writes"


def test_a_canonical_copy_at_a_staging_name_is_never_overwritten(
    tmp_path, monkeypatch, _app
):
    """SAFETY: the move-aside destination is judged too.

    The rename that moves an old artefact aside would overwrite whatever sits at
    the staging name. A clean copy of the canonical ROM there is a ROM, not a spare
    slot, so the whole overwrite must refuse with nothing moved.
    """
    panel, session, output_path = _make_panel(tmp_path, _app)
    session.rom_path.write_bytes(_CANONICAL_BYTES)
    manifest_path = build_sdk.manifest_path_for_build(
        build_sdk.MANIFEST_BESIDE_OUTPUT, output_path)
    output_path.write_bytes(b"OLD")
    manifest_path.write_text('{"stale": "manifest"}', encoding="utf-8")
    staging = staging_path(output_path)
    staging.write_bytes(_CANONICAL_BYTES)
    staged_before = staging.read_bytes()
    published_before = sorted(path.name for path in output_path.parent.iterdir())

    counter = {"n": 0}
    criticals = []
    monkeypatch.setattr(bp.build_sdk, "build_project", _writer_backed_build(counter))
    monkeypatch.setattr(
        QMessageBox, "question", staticmethod(lambda *a, **k: QMessageBox.Yes))
    monkeypatch.setattr(
        QMessageBox, "critical", staticmethod(lambda *a, **k: criticals.append(a)))

    panel._on_build()

    assert criticals, "a canonical copy at the staging name must refuse the overwrite"
    assert "canonical" in criticals[0][2], criticals
    assert counter["n"] == 1, "no rebuild may run after the refusal"
    assert staging.read_bytes() == staged_before, "the canonical copy must survive"
    assert output_path.read_bytes() == b"OLD", "nothing may be moved"
    assert manifest_path.read_text(encoding="utf-8") == '{"stale": "manifest"}'
    assert sorted(path.name for path in output_path.parent.iterdir()) == published_before
