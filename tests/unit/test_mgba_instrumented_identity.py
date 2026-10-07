"""Instrumented-build provenance and measured runtime identity (ROM-011/ROM-012).

Outcomes 4 and 5 of RUNTIME-FOUNDATION-CONSOLIDATION-001.

Outcome 4. `build/rom011/mgba-probe-sdl/log1-probe-build.json` records
`patch_sha256` `8863b2e235add144c7af6d817bf30375a44326ccd13dc1acb89ccf6cd3be9e9a`,
which does not match the tracked `tools/mgba_probe/mgba-0.10.5-log1-read-probe.patch`
(`8ee9d92d...`), so rom011 refuses its own instrumented build. The mismatch is
real provenance, not a corrupt manifest:

* `8863b2e2...` is the sha256 of the patch blob at
  `git rev-parse 61f062e7b355fc410c3f7229d8adac1702fedf4d:tools/mgba_probe/mgba-0.10.5-log1-read-probe.patch`
  (blob `29efbe22f7ef`, also at `0d0c0e39`), an earlier revision that predates
  the `matchKind` / `MATCH_ACCEPTED_X0C` protocol the tracked client speaks;
* `tools/mgba_probe/build.ps1:153` writes the field with `Get-FileHash` of the
  patch on disk, so the writer is automatic and the manifest is honest;
* the rom011 executable itself carries the older protocol only: it contains
  `E634` and `E635` and does NOT contain `E636`, the rejection code the newer
  revision added, while the rom012 executable contains all three.

So the BUILD is superseded, not the manifest, and the refusal is correct. These
tests pin that determination and require the refusal to be named rather than
generic, without editing any digest.

Outcome 5. `tools/runtime/rom011_live_watch.py` wrote the literal
`"mgba_version": "0.10.5.0"` into its fallback armed record, a version claim
nothing on that path measured. The armed record now reports the identity of the
manifest that `verify_instrumented_mgba` actually verified, and no literal may
be bound to that field anywhere in the instrumented verification path.

Every refusal below is proven to happen before any emulator process exists: the
machine's own process list is counted before and after, and `subprocess.Popen`
is replaced by a recorder that raises, so a launch path that had lost its gate
would be caught rather than started.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import uuid

import pytest

from tools.mgba_probe import runtime
from tools.runtime import rom011_live_watch, rom012_live_containment

ROOT = Path(__file__).resolve().parents[2]

#: The main checkout, where both instrumented build trees live. A ticket
#: worktree has no `build/tools` tree, so the on-disk evidence is named
#: relatively and every test that needs it skips when it is absent. The location
#: is derived from this checkout's parent rather than written as a machine path,
#: and `LOG1_MAIN_CHECKOUT` overrides it for an unusual layout.
MAIN_CHECKOUT = Path(
    os.environ.get(
        "LOG1_MAIN_CHECKOUT",
        str(Path(__file__).resolve().parents[2].parent / "log1-remake"),
    )
)
ROM011_MANIFEST = MAIN_CHECKOUT / "build/rom011/mgba-probe-sdl/log1-probe-build.json"
ROM012_BUILD = MAIN_CHECKOUT / "build/rom012/mgba-probe-sdl"

#: The shared install, measured 0.11.0.0 sha256 C91FF99B..., which the
#: instrumented family must refuse. The Windows program-files location is read
#: from the environment so the source names no machine's layout.
DEV_MGBA = Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "mGBA" / "mGBA.exe"

#: The instrumented verification path: the policy and the two drivers it gates.
INSTRUMENTED_PATH = (
    "tools/mgba_probe/runtime.py",
    "tools/runtime/rom011_live_watch.py",
    "tools/runtime/rom012_live_containment.py",
)


def _emulator_processes() -> int:
    """How many mGBA processes this machine has, read from the OS itself.

    A missing process lister is not a failure and must not be read as "none":
    ``ps`` is absent from some CI images, so Linux falls back to reading
    ``/proc`` directly, which answers the same question without one.
    """
    if os.name == "nt":
        listing = subprocess.run(
            ["tasklist", "/NH"], capture_output=True, text=True, check=False
        ).stdout
        return sum("mgba" in line.lower() for line in listing.splitlines())
    try:
        listing = subprocess.run(
            ["ps", "-A", "-o", "comm="], capture_output=True, text=True, check=False
        ).stdout
    except OSError:
        listing = ""
    if not listing.strip():
        listing = "\n".join(_proc_commands())
    return sum("mgba" in line.lower() for line in listing.splitlines())


def _proc_commands() -> list[str]:
    """Process command names read from ``/proc``, empty where there is none."""
    proc = Path("/proc")
    if not proc.is_dir():
        return []
    names: list[str] = []
    for entry in proc.iterdir():
        if not entry.name.isdigit():
            continue
        try:
            names.append((entry / "comm").read_text(encoding="utf-8").strip())
        except OSError:
            continue
    return names


def _refuse(call, run_root: Path) -> str:
    """Run ``call`` expecting a refusal, and prove nothing was launched."""
    before = _emulator_processes()
    attempts: list[tuple[object, ...]] = []

    def _forbidden(*args: object, **kwargs: object) -> None:
        attempts.append(args)
        raise AssertionError("a process was created before identity was verified")

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(subprocess, "Popen", _forbidden)
        with pytest.raises((ValueError, OSError)) as caught:
            call()
    after = _emulator_processes()

    assert attempts == [], "the refused path tried to create a process"
    assert not run_root.exists(), "the refused path created its run root"
    assert after == before, "the emulator process count changed on a refused path"
    return str(caught.value)


def _manifest(tmp_path: Path, executable: Path) -> dict[str, object]:
    """A synthetic manifest that passes every check the mutants then break."""
    runtime_bin = tmp_path / "runtime"
    runtime_bin.mkdir(exist_ok=True)
    for library in ("SDL2.dll", "libepoxy-0.dll"):
        (runtime_bin / library).write_bytes(b"")
    return {
        "schema": runtime.BUILD_SCHEMA,
        "source_commit": runtime.SOURCE_COMMIT,
        "patch_sha256": runtime.sha256(runtime.PATCH_PATH),
        "executable_sha256": runtime.sha256(executable),
        "runtime_bin": str(runtime_bin),
    }


def _write(path: Path, manifest: dict[str, object]) -> Path:
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


def _launch(
    module: str,
    *,
    tmp_path: Path,
    mgba_path: Path,
    manifest_path: Path | None,
    run_root: Path,
) -> None:
    common = {
        "rom_path": tmp_path / "rom.gba",
        "state_path": tmp_path / "state.ss1",
        "save_path": tmp_path / "save.sav",
        "state_sha256": "0" * 64,
        "save_sha256": "0" * 64,
        "mgba_path": mgba_path,
        "run_root": run_root,
        "timeout_seconds": 1.0,
    }
    if module == "rom011":
        rom011_live_watch.run_live_session(
            manifest_path=manifest_path,
            profile_path=tmp_path / "profile.yaml",
            **common,  # type: ignore[arg-type]
        )
    else:
        rom012_live_containment.run_live_session(
            manifest_path=manifest_path,  # type: ignore[arg-type]
            **common,  # type: ignore[arg-type]
        )


def _run_root(module: str) -> Path:
    root = ROOT / "build" / module
    return root / f"identity-refusal-{uuid.uuid4().hex}"


def test_the_on_disk_rom011_build_now_matches_the_tracked_patch():
    """RUNTIME-INSTRUMENTED-CAPTURE-CLOSURE-001: rom011 was rebuilt.

    The on-disk rom011 build used to record the superseded revision and be
    refused by name. It has since been rebuilt from the pinned source commit and
    the tracked patch, so the same manifest now carries the current digest. The
    superseded refusal itself is still covered, by the synthetic manifest tests
    below and by the history test that proves the digest is a real revision.
    """
    if not ROM011_MANIFEST.is_file():
        pytest.skip("the rom011 instrumented build tree is not on this machine")
    manifest = json.loads(ROM011_MANIFEST.read_text(encoding="utf-8"))
    assert manifest["patch_sha256"] == runtime.sha256(runtime.PATCH_PATH)
    assert manifest["patch_sha256"] != runtime.SUPERSEDED_PATCH_SHA256


def test_the_on_disk_rom012_build_matches_the_tracked_patch():
    """The control: the other instrumented build is the tracked revision."""
    manifest_path = ROM012_BUILD / "log1-probe-build.json"
    if not manifest_path.is_file():
        pytest.skip("the rom012 instrumented build tree is not on this machine")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["patch_sha256"] == runtime.sha256(runtime.PATCH_PATH)


def test_the_superseded_revision_is_the_tracked_patches_own_history():
    """The superseded digest is a real earlier revision, not a stray value.

    The revision is asserted only where the clone actually carries it. A
    shallow or partial CI clone does not, and reading a missing object returns
    empty bytes, whose digest is the empty-string hash rather than this one.
    """
    if not (MAIN_CHECKOUT / ".git").exists():
        pytest.skip("no repository history on this machine")
    commit = "61f062e7b355fc410c3f7229d8adac1702fedf4d"
    # Plain `-e <sha>`: the `^{commit}` peel is mangled to `^commit` through
    # subprocess on Windows, where git then rejects the name outright.
    present = subprocess.run(
        ["git", "-C", str(MAIN_CHECKOUT), "cat-file", "-e", commit],
        capture_output=True,
        check=False,
    )
    if present.returncode != 0:
        pytest.skip("shallow or partial clone: the earlier revision is absent")
    blob = subprocess.run(
        [
            "git",
            "-C",
            str(MAIN_CHECKOUT),
            "rev-parse",
            f"{commit}:tools/mgba_probe/mgba-0.10.5-log1-read-probe.patch",
        ],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    assert blob, "the earlier patch revision is not in this repository"
    content = subprocess.run(
        ["git", "-C", str(MAIN_CHECKOUT), "cat-file", "blob", blob],
        capture_output=True,
        check=False,
    ).stdout
    if not content:
        pytest.skip("shallow or partial clone: the earlier blob is unavailable")
    assert hashlib.sha256(content).hexdigest() == runtime.SUPERSEDED_PATCH_SHA256


@pytest.mark.parametrize("module", ["rom011", "rom012"])
def test_a_superseded_probe_patch_build_is_refused_by_name(module, tmp_path):
    executable = tmp_path / "mgba-sdl.exe"
    executable.write_bytes(b"instrumented")
    manifest = _manifest(tmp_path, executable)
    manifest["patch_sha256"] = runtime.SUPERSEDED_PATCH_SHA256
    manifest_path = _write(tmp_path / "manifest.json", manifest)
    run_root = _run_root(module)

    message = _refuse(
        lambda: _launch(
            module,
            tmp_path=tmp_path,
            mgba_path=executable,
            manifest_path=manifest_path,
            run_root=run_root,
        ),
        run_root,
    )
    assert "superseded" in message
    assert runtime.SUPERSEDED_PATCH_SHA256 in message


@pytest.mark.parametrize("module", ["rom011", "rom012"])
def test_an_unknown_probe_patch_digest_is_refused_generically(module, tmp_path):
    executable = tmp_path / "mgba-sdl.exe"
    executable.write_bytes(b"instrumented")
    manifest = _manifest(tmp_path, executable)
    manifest["patch_sha256"] = "0" * 64
    manifest_path = _write(tmp_path / "manifest.json", manifest)
    run_root = _run_root(module)

    message = _refuse(
        lambda: _launch(
            module,
            tmp_path=tmp_path,
            mgba_path=executable,
            manifest_path=manifest_path,
            run_root=run_root,
        ),
        run_root,
    )
    assert message == "instrumented mGBA patch hash mismatch"


@pytest.mark.parametrize("module", ["rom011", "rom012"])
def test_a_wrong_source_identity_is_refused(module, tmp_path):
    executable = tmp_path / "mgba-sdl.exe"
    executable.write_bytes(b"instrumented")
    manifest = _manifest(tmp_path, executable)
    manifest["source_commit"] = "1" * 40
    manifest_path = _write(tmp_path / "manifest.json", manifest)
    run_root = _run_root(module)

    message = _refuse(
        lambda: _launch(
            module,
            tmp_path=tmp_path,
            mgba_path=executable,
            manifest_path=manifest_path,
            run_root=run_root,
        ),
        run_root,
    )
    assert message == "instrumented mGBA source commit mismatch"


@pytest.mark.parametrize("module", ["rom011", "rom012"])
def test_a_wrong_executable_digest_is_refused(module, tmp_path):
    described = tmp_path / "described.exe"
    described.write_bytes(b"the build the manifest describes")
    manifest = _manifest(tmp_path, described)
    executable = tmp_path / "mgba-sdl.exe"
    executable.write_bytes(b"a different build entirely")
    manifest_path = _write(tmp_path / "manifest.json", manifest)
    run_root = _run_root(module)

    message = _refuse(
        lambda: _launch(
            module,
            tmp_path=tmp_path,
            mgba_path=executable,
            manifest_path=manifest_path,
            run_root=run_root,
        ),
        run_root,
    )
    assert message == "instrumented mGBA executable hash mismatch"


@pytest.mark.parametrize("module", ["rom011", "rom012"])
def test_a_missing_manifest_file_is_refused(module, tmp_path):
    executable = tmp_path / "mgba-sdl.exe"
    executable.write_bytes(b"instrumented")
    run_root = _run_root(module)

    _refuse(
        lambda: _launch(
            module,
            tmp_path=tmp_path,
            mgba_path=executable,
            manifest_path=tmp_path / "absent-manifest.json",
            run_root=run_root,
        ),
        run_root,
    )


def test_a_native_probe_without_a_manifest_is_refused(tmp_path):
    executable = tmp_path / "mgba-sdl.exe"
    executable.write_bytes(b"instrumented")
    run_root = _run_root("rom011")

    message = _refuse(
        lambda: _launch(
            "rom011",
            tmp_path=tmp_path,
            mgba_path=executable,
            manifest_path=None,
            run_root=run_root,
        ),
        run_root,
    )
    assert message == "native probe requires an instrumented-build manifest"


def test_the_real_instrumented_build_refuses_the_shared_dev_install(tmp_path):
    """The measured machine case: valid rom012 manifest, wrong executable."""
    manifest_path = ROM012_BUILD / "log1-probe-build.json"
    if not manifest_path.is_file() or not DEV_MGBA.is_file():
        pytest.skip("the instrumented build tree or the dev install is absent")
    run_root = _run_root("rom012")

    message = _refuse(
        lambda: _launch(
            "rom012",
            tmp_path=tmp_path,
            mgba_path=DEV_MGBA,
            manifest_path=manifest_path,
            run_root=run_root,
        ),
        run_root,
    )
    assert message == "instrumented mGBA executable hash mismatch"


@pytest.mark.parametrize("relative", INSTRUMENTED_PATH)
def test_no_runtime_metadata_binds_a_literal_version(relative):
    """`mgba_version` must be measured identity, never a written claim."""
    tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
    offenders = [
        f"{relative}:{value.lineno}"
        for node in ast.walk(tree)
        if isinstance(node, ast.Dict)
        for key, value in zip(node.keys, node.values)
        if isinstance(key, ast.Constant)
        and key.value == "mgba_version"
        and isinstance(value, ast.Constant)
    ]
    assert offenders == []
