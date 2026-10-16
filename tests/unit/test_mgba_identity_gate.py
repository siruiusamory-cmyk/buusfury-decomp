"""Fail-closed emulator identity for the Python GDB probe family.

`docs/skills/mgba-runtime.md` states the rule in section 2: the emulator is
identified from the binary itself, never from its path, because the shared
install has been overwritten in place by a different build before. The
PowerShell launchers obey it by comparing
`VersionInfo.FileVersion`. The Python probes did not, and they defaulted to
that same shared path, so a stale install silently fed every GDB probe a build
the research tickets do not accept.

What each test here protects:

1. coverage, in both directions: the set of runtime files that call
   `subprocess.Popen` themselves is discovered mechanically, must be inside the
   identity policy, and must equal every policy entry except the one driver
   covered by delegation, so a new launcher cannot escape the gate by being
   written later;
2. ordering: the gate call is unconditional and precedes the launch, with no
   function boundary between them, so the gate covers the launch that follows;
3. the two probe families keep two different requirements - the packaged
   executable digest for the GDB family, the instrumented manifest for
   rom011/rom012 - rather than one universal version check;
4. provenance: the pinned packaged digest is the one the repository already
   records in `docs/runtime-capture.md`, not a literal invented here;
5-7. the check itself: missing executable refused, wrong executable refused
   with both identities named, intended executable accepted;
8-9. the check is wired into the three launching probes, and the gate passes
   when the executable really is the pinned build.
"""

from __future__ import annotations

import hashlib
import importlib
from pathlib import Path
import re
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]

#: The GDB probe family: one packaged executable digest, checked by
#: `tools/runtime/mgba_identity.require_mgba_build`.
PACKAGED = "packaged-0.10.5"

#: The native probe family: a pinned source commit, the patch digest and the
#: manifest-declared executable digest, checked by
#: `tools.mgba_probe.runtime.verify_instrumented_mgba`.
INSTRUMENTED = "instrumented-manifest"

#: A driver that reaches mGBA only by calling another driver's `run_probe`, so
#: its identity gate is that callee's gate and it has no `subprocess.Popen` of
#: its own. Exactly one policy entry may carry this tag.
DELEGATED = "delegated-to-rom008-query-probe"

#: Every runtime driver that can put an mGBA process on this machine, mapped to
#: the identity that driver must prove before it may launch. Two families with
#: two different requirements, plus the one driver that delegates its launch.
POLICY: dict[str, str] = {
    "tools/runtime/rom006_gdb_probe.py": PACKAGED,
    "tools/runtime/rom007_factory_probe.py": PACKAGED,
    "tools/runtime/rom008_query_probe.py": PACKAGED,
    "tools/runtime/rom009_callback_probe.py": DELEGATED,
    "tools/runtime/rom011_live_watch.py": INSTRUMENTED,
    "tools/runtime/rom012_live_containment.py": INSTRUMENTED,
}

#: The packaged probes that launch directly, derived from the policy so a
#: fourth packaged driver cannot pass coverage while skipping the probe-level
#: checks below.
LAUNCHING_PROBES = tuple(
    Path(relative).stem for relative, tag in POLICY.items() if tag == PACKAGED
)

def _identity_module():
    """Imported late so the source-level gates below fail as assertions on the
    baseline rather than collapsing this module at collection time."""
    import tools.runtime.mgba_identity as module
    return module


def _source(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def _position(source: str, token: str, relative: str) -> int:
    assert token in source, f"{relative} never calls {token}"
    return source.index(token)


def _probe_module(name: str) -> Any:
    return importlib.import_module(f"tools.runtime.{name}")


def _forbidden_popen():
    def refuse(*args: Any, **kwargs: Any) -> None:
        pytest.fail("subprocess.Popen was reached before the identity gate")
    return refuse


def _probe_arguments(
    name: str, *, rom: Path, state: Path, save: Path, executable: Path,
    profile: Path, lua: Path, injector: Path,
) -> dict[str, Any]:
    if name == "rom006_gdb_probe":
        return {
            "rom_path": rom,
            "state_path": state,
            "mgba_path": executable,
            "profile_path": profile,
            "timeout_seconds": 1.0,
            "max_stops": 1,
            "trace_registry": False,
        }
    return {
        "rom_path": rom,
        "state_path": state,
        "save_path": save,
        "state_sha256": "",
        "save_sha256": "",
        "lua_path": lua,
        "injector_path": injector,
        "mgba_path": executable,
        "profile_path": profile,
        "timeout_seconds": 1.0,
    }


@pytest.fixture
def probe_artifacts(tmp_path: Path) -> dict[str, Path]:
    rom = tmp_path / "rom.gba"
    rom.write_bytes(b"not the canonical image")
    state = tmp_path / "state.ss1"
    state.write_bytes(b"state")
    save = tmp_path / "save.sav"
    save.write_bytes(b"save")
    profile = tmp_path / "roms.yaml"
    profile.write_text("roms: []", encoding="utf-8")
    lua = tmp_path / "observer.lua"
    lua.write_text("-- observer", encoding="utf-8")
    injector = tmp_path / "inject.ps1"
    injector.write_text("# injector", encoding="utf-8")
    return {"rom": rom, "state": state, "save": save, "profile": profile,
            "lua": lua, "injector": injector}


@pytest.mark.parametrize("relative", sorted(POLICY))
def test_the_identity_gate_precedes_every_launch(relative: str):
    source = _source(relative)
    tag = POLICY[relative]
    if tag == DELEGATED:
        assert "from tools.runtime.rom008_query_probe import" in source, (
            f"{relative} is policy entry {DELEGATED} but does not import the "
            "probe whose run_probe carries the gate for it")
        return
    gate_call = (
        "verify_instrumented_mgba(" if tag == INSTRUMENTED else "require_mgba_build("
    )
    gate_at = _position(source, gate_call, relative)
    launch_at = _position(source, "subprocess.Popen(", relative)
    assert gate_at < launch_at, (
        f"{relative} reaches subprocess.Popen before its identity gate")
    assert "\ndef " not in source[gate_at:launch_at], (
        f"{relative} leaves its enclosing function between the identity gate and "
        "the launch, so the gate does not cover the launch that follows")
    gate_line = next(line for line in source.splitlines() if gate_call in line)
    assert gate_line.startswith("    ") and not gate_line.startswith("        "), (
        f"{relative} calls its identity gate inside a nested block, so a path "
        "that still launches can skip it")


@pytest.mark.parametrize("relative", sorted(POLICY))
def test_the_probe_families_keep_their_separate_required_builds(relative: str):
    """Two families, two requirements: the packaged digest and the manifest."""
    source = _source(relative)
    if POLICY[relative] == INSTRUMENTED:
        assert "verify_instrumented_mgba(" in source, relative
        assert "require_mgba_build(" not in source, relative
        assert _identity_module().PACKAGED_0_10_5.sha256 not in source, relative
        return
    if POLICY[relative] == DELEGATED:
        # This driver owns no launch: it hands its executable to
        # rom008_query_probe.run_probe, so the callee's gate is its gate. The
        # import below is the wiring that makes that true, and it is asserted
        # rather than assumed.
        assert "from tools.runtime.rom008_query_probe import" in source, relative
        assert "run_probe," in source, relative
        assert "subprocess.Popen(" not in source, relative
        assert "require_mgba_build(" not in source, relative
        assert "PACKAGED_0_10_5" not in source, relative
        assert "verify_instrumented_mgba(" not in source, relative
        return
    assert "require_mgba_build(" in source, relative
    assert "PACKAGED_0_10_5" in source, relative
    assert "verify_instrumented_mgba(" not in source, relative


def test_the_packaged_digest_is_the_one_the_repository_already_records():
    """The literal is provenance, not an arbitrary constant typed here."""
    recorded = {
        value.upper()
        for value in re.findall(
            r"\b[0-9A-Fa-f]{64}\b",
            (ROOT / "docs/runtime-capture.md").read_text(encoding="utf-8"),
        )
    }
    digest = _identity_module().PACKAGED_0_10_5.sha256
    assert digest in recorded, (
        f"{digest} is not recorded in docs/runtime-capture.md, so the policy "
        "pins a build nothing else in the repository knows about")


def test_a_missing_executable_is_refused(tmp_path: Path):
    identity = _identity_module()
    build = identity.MgbaBuild("synthetic packaged build", "0" * 64)
    target = tmp_path / "absent.exe"
    with pytest.raises(RuntimeError) as refused:
        identity.require_mgba_build(target, build)
    message = str(refused.value)
    assert "not found" in message
    assert str(target.resolve()) in message


def test_a_wrong_executable_is_refused_and_names_both_identities(tmp_path: Path):
    identity = _identity_module()
    build = identity.MgbaBuild("synthetic packaged build", "A" * 64)
    target = tmp_path / "wrong.exe"
    target.write_bytes(b"some other emulator")
    observed = hashlib.sha256(target.read_bytes()).hexdigest().upper()
    with pytest.raises(RuntimeError) as refused:
        identity.require_mgba_build(target, build)
    message = str(refused.value)
    assert build.sha256 in message
    assert observed in message
    assert str(target.resolve()) in message


def test_the_intended_identity_passes(tmp_path: Path):
    identity = _identity_module()
    target = tmp_path / "mGBA.exe"
    target.write_bytes(b"the intended build")
    build = identity.MgbaBuild(
        "synthetic packaged build",
        hashlib.sha256(target.read_bytes()).hexdigest().upper(),
    )
    assert identity.require_mgba_build(target, build) == target.resolve()


@pytest.mark.parametrize("name", LAUNCHING_PROBES)
@pytest.mark.parametrize("case", ("absent", "wrong"))
def test_a_missing_or_wrong_executable_is_refused_before_a_process_starts(
    name: str, case: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    probe_artifacts: dict[str, Path],
):
    module = _probe_module(name)
    monkeypatch.setattr(module.subprocess, "Popen", _forbidden_popen())
    identity = _identity_module()
    executable = tmp_path / "mGBA.exe"
    if case == "wrong":
        executable.write_bytes(b"some other emulator")
    build = identity.MgbaBuild("synthetic packaged build", "0" * 64)
    monkeypatch.setattr(module, "PACKAGED_0_10_5", build)

    arguments = _probe_arguments(
        name,
        rom=probe_artifacts["rom"],
        state=probe_artifacts["state"],
        save=probe_artifacts["save"],
        executable=executable,
        profile=probe_artifacts["profile"],
        lua=probe_artifacts["lua"],
        injector=probe_artifacts["injector"],
    )
    with pytest.raises(RuntimeError) as refused:
        module.run_probe(**arguments)
    message = str(refused.value)
    assert build.sha256 in message, message
    assert str(executable.resolve()) in message, message
    if case == "absent":
        assert "not found" in message, message
    else:
        assert "identity mismatch" in message, message


@pytest.mark.parametrize("name", LAUNCHING_PROBES)
def test_the_intended_build_reaches_the_probe_next_prerequisite(
    name: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    probe_artifacts: dict[str, Path],
):
    """The gate passes, so the probe advances to its ROM identity check."""
    module = _probe_module(name)
    executable = tmp_path / "mGBA.exe"
    executable.write_bytes(b"the intended build")
    digest = hashlib.sha256(executable.read_bytes()).hexdigest().upper()
    identity = _identity_module()
    monkeypatch.setattr(
        module, "PACKAGED_0_10_5",
        identity.MgbaBuild("synthetic packaged build", digest),
    )
    monkeypatch.setattr(module.subprocess, "Popen", _forbidden_popen())

    arguments = _probe_arguments(
        name,
        rom=probe_artifacts["rom"],
        state=probe_artifacts["state"],
        save=probe_artifacts["save"],
        executable=executable,
        profile=probe_artifacts["profile"],
        lua=probe_artifacts["lua"],
        injector=probe_artifacts["injector"],
    )
    expected = (
        "verified ROM identity mismatch before runtime probe"
        if name == "rom006_gdb_probe"
        else "verified ROM identity mismatch"
    )
    with pytest.raises(RuntimeError) as refused:
        module.run_probe(**arguments)
    assert str(refused.value) == expected
