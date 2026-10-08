"""The product version, the build identity, and the N-26 provenance fix.

Two things are proved here. First, that the product version has exactly one
authority, because a second literal is how a release comes to be named one version
and report another. Second, that a *packaged* build can still name the commit it
was cut from - the packaged randomizer wrote a null build commit, which is the
ledger's N-26 - without ever asking the filesystem it is running on.

The frozen half is simulated rather than built: a real frozen executable is an
owner-run release gate, and the behaviour that matters here is which source the
answer comes from, which is testable without one.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import types

import pytest

import tools.webfoot as webfoot_package
from tools.webfoot import release_identity
from tools.webfoot.randomizer import service as randomizer_service
from tools.webfoot.release_identity import (
    PRODUCT_NAME,
    PRODUCT_VERSION,
    VERSION_TUPLE,
    BuildIdentity,
    build_identity,
    identity_document,
    release_identity as read_release_identity,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
RECORD_MODULE = "tools.webfoot._build_identity"
SENTINEL_COMMIT = "c0ffee1234567890abcdef1234567890abcdef12"


@pytest.fixture(autouse=True)
def _fresh_identity_cache(monkeypatch):
    """Every test starts with nothing remembered, since the identity is cached."""
    monkeypatch.setattr(release_identity, "_BUILD_CACHE", None)


def _install_record(monkeypatch, commit=SENTINEL_COMMIT, dirty=False,
                    built_at="2026-10-08T00:00:00Z"):
    """Make `from . import _build_identity` resolve to a generated record."""
    module = types.ModuleType(RECORD_MODULE)
    module.COMMIT = commit
    module.DIRTY = dirty
    module.BUILT_AT = built_at
    monkeypatch.setitem(sys.modules, RECORD_MODULE, module)
    monkeypatch.setattr(webfoot_package, "_build_identity", module, raising=False)
    return module


def _remove_record(monkeypatch):
    monkeypatch.delitem(sys.modules, RECORD_MODULE, raising=False)
    monkeypatch.delattr(webfoot_package, "_build_identity", raising=False)


def _no_process_may_start(monkeypatch):
    """Fail loudly if anything reaches for git while it must not."""

    def refuse(*arguments, **keywords):
        raise AssertionError(f"a packaged build must not start a process: {arguments}")

    monkeypatch.setattr(release_identity.subprocess, "run", refuse)


# --- one version authority --------------------------------------------------


def test_the_product_version_has_exactly_one_authority():
    """The literal is written once. A second copy is the drift this prevents."""
    carriers = [
        path
        for path in sorted((REPOSITORY_ROOT / "tools" / "webfoot").rglob("*.py"))
        if PRODUCT_VERSION in path.read_text(encoding="utf-8")
    ]
    assert carriers == [REPOSITORY_ROOT / "tools" / "webfoot" / "release_identity.py"]


def test_the_version_tuple_agrees_with_the_version_string():
    numbers = PRODUCT_VERSION.split(".")[:3]
    assert tuple(int(number) for number in numbers) == VERSION_TUPLE[:3]
    assert VERSION_TUPLE[3] == 0


def test_the_identity_is_the_pre_release_identity():
    identity = read_release_identity()
    assert identity.product_name == PRODUCT_NAME
    assert identity.version == PRODUCT_VERSION
    assert identity.display == f"{PRODUCT_NAME} {PRODUCT_VERSION}"


def test_the_identity_document_is_json_serialisable_and_versioned():
    document = identity_document()
    assert document["schema_version"] == 1
    assert document["product"]["name"] == PRODUCT_NAME
    assert document["product"]["version_tuple"] == list(VERSION_TUPLE)
    assert json.loads(json.dumps(document, sort_keys=True)) == document


# --- where the build identity comes from ------------------------------------


def test_a_checkout_reports_its_own_commit_and_tree_state():
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    identity = build_identity()
    assert identity.source == "checkout"
    assert identity.commit == head
    assert identity.dirty == bool(status)
    assert identity.built_at is None


def test_a_packaged_build_reports_the_baked_record_without_asking_git(monkeypatch):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    _install_record(monkeypatch, dirty=True)
    _no_process_may_start(monkeypatch)

    identity = build_identity()
    assert identity == BuildIdentity(
        SENTINEL_COMMIT, True, "2026-10-08T00:00:00Z", "record"
    )
    assert identity.display == f"build {SENTINEL_COMMIT[:12]} (modified tree)"


def test_a_packaged_build_with_no_record_reports_unknown_and_starts_nothing(
    monkeypatch,
):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    _remove_record(monkeypatch)
    _no_process_may_start(monkeypatch)

    identity = build_identity()
    assert identity == BuildIdentity(None, None, None, "unknown")
    assert identity.display == "build unknown"


def test_a_checkout_prefers_its_live_answer_over_a_leftover_record(monkeypatch):
    """A stale record must not be able to misname the tree a developer runs."""
    _install_record(monkeypatch, commit="1" * 40, dirty=False)
    identity = build_identity()
    assert identity.source == "checkout"
    assert identity.commit != "1" * 40


def test_a_malformed_record_is_treated_as_absent(monkeypatch):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    _install_record(monkeypatch, commit=12345)
    _no_process_may_start(monkeypatch)
    assert build_identity().source == "unknown"


@pytest.mark.parametrize(
    "commit",
    ["abc", "A" * 40, "a" * 39, "a" * 41, "a" * 40 + "!", "g" * 40, " " * 40],
    ids=["short", "uppercase", "39", "41", "trailing", "non-hex", "blank"],
)
def test_a_recorded_commit_must_be_a_commit(monkeypatch, commit):
    """Anything that is not forty hexadecimal characters is not an identity."""
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    _install_record(monkeypatch, commit=commit)
    _no_process_may_start(monkeypatch)
    assert build_identity().source == "unknown"


def test_a_checkout_without_a_usable_git_reports_the_record(monkeypatch):
    """The fallback direction, stated: no live answer, so the baked one is used."""
    _install_record(monkeypatch, commit=SENTINEL_COMMIT)
    monkeypatch.setattr(release_identity, "_git", lambda *arguments: None)

    identity = build_identity()
    assert identity.source == "record"
    assert identity.commit == SENTINEL_COMMIT


# --- baking the record into a package ---------------------------------------


def test_the_written_record_is_python_carrying_this_checkout(monkeypatch, tmp_path):
    record = release_identity.write_build_record(tmp_path / "record.py")
    namespace: dict = {}
    exec(compile(record.read_text(encoding="utf-8"), str(record), "exec"), namespace)

    assert namespace["COMMIT"] is not None
    assert len(namespace["COMMIT"]) == 40
    assert isinstance(namespace["DIRTY"], bool)
    assert namespace["BUILT_AT"].endswith("Z")


def test_the_generated_record_is_ignored_by_git():
    """A record names one machine's commit, so it can never be committed."""
    result = subprocess.run(
        ["git", "check-ignore", f"tools/webfoot/{release_identity.BUILD_RECORD_NAME}"],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert release_identity.BUILD_RECORD_NAME in result.stdout


def test_the_entry_point_reports_both_identities(monkeypatch, capsys):
    assert release_identity.main(["--json"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["product"]["version"] == PRODUCT_VERSION
    assert printed["build"]["source"] in ("checkout", "record", "unknown")

    assert release_identity.main([]) == 0
    lines = capsys.readouterr().out.strip().splitlines()
    assert lines[0] == f"{PRODUCT_NAME} {PRODUCT_VERSION}"


def test_the_entry_point_can_bake_the_record(monkeypatch, tmp_path, capsys):
    destination = tmp_path / "baked.py"
    monkeypatch.setattr(release_identity, "build_record_path", lambda: destination)
    assert release_identity.main(["--write-record"]) == 0
    assert capsys.readouterr().out.strip() == str(destination)
    assert destination.is_file()


# --- N-26: the packaged randomizer names its commit --------------------------


def test_a_packaged_randomizer_reports_the_baked_commit(monkeypatch):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    _install_record(monkeypatch, dirty=False)
    _no_process_may_start(monkeypatch)

    assert randomizer_service.repository_commit() == SENTINEL_COMMIT
    assert randomizer_service.repository_is_dirty() is False


def test_a_packaged_randomizer_without_a_record_still_reports_null(monkeypatch):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    _remove_record(monkeypatch)
    _no_process_may_start(monkeypatch)

    assert randomizer_service.repository_commit() is None
    assert randomizer_service.repository_is_dirty() is None


def test_the_manifest_records_the_identity_the_service_reports(monkeypatch):
    """The value reaches the document a release reads, in the shape it expects."""
    from tools.webfoot.randomizer.manifest import build_manifest

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    _install_record(monkeypatch, dirty=True)
    _no_process_may_start(monkeypatch)

    document = build_manifest(
        tool_name="Enemy Randomizer",
        tool_version="0.1.0",
        modules=(),
        enabled=frozenset(),
        plans=(),
        module_seeds={},
        profile_id="synthetic",
        source_sha256="0" * 64,
        source_size=1,
        master_seed="Saiyan-0001",
        output_filename="synthetic.gba",
        output_size=1,
        output_sha256="1" * 64,
        changed_byte_count=0,
        tool_commit=randomizer_service.repository_commit(),
        tool_dirty=randomizer_service.repository_is_dirty(),
    )
    assert document["build"] == {"commit": SENTINEL_COMMIT, "dirty": True}
