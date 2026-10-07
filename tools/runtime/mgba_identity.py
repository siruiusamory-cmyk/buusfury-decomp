"""Fail-closed build identity for the mGBA executables the Python probes launch.

The runtime authority requires the emulator to be identified from the binary
itself and never from its path, because the shared install has been overwritten
in place by a different build before. The PowerShell launchers compare
VersionInfo.FileVersion; a Python driver has no equivalent without a platform
dependency, so these probes pin the stronger identity the repository already
records for the packaged build: the executable SHA-256 that
docs/runtime-capture.md stores beside its FileVersion. Each probe calls
require_mgba_build before it can reach a process launch.

The same module carries `LAUNCH_SITES`, the registry of every
repository-controlled place an mGBA process can start: one frozen
classification, the mechanism that actually proves identity there (`proof`), and
a written rationale each. It is the input to the coverage predicate for launch
sites, so an audit reads a structured field instead of grepping prose for one.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class MgbaBuild:
    """One accepted emulator build, named and pinned by its executable digest."""

    label: str
    sha256: str


PACKAGED_0_10_5 = MgbaBuild(
    "packaged mGBA 0.10.5 (win64)",
    "5A3C98C2984DD04BD0D7C9378CDFAE937AE0D73A196C880BB2EECF3B254AF247",
)

DEFAULT_PACKAGED_MGBA = (
    Path(__file__).resolve().parents[2]
    / "build"
    / "tools"
    / "mgba-0.10.5"
    / "extracted"
    / "mGBA-0.10.5-win64"
    / "mGBA.exe"
)


def _sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest().upper()


def require_mgba_build(executable: Path, build: MgbaBuild) -> Path:
    """Return the resolved executable, or refuse before anything is launched."""
    resolved = Path(executable).resolve()
    if not resolved.is_file():
        raise RuntimeError(
            f"mGBA executable not found: {resolved} "
            f"(required {build.label}, sha256 {build.sha256})"
        )
    observed = _sha256(resolved)
    if observed != build.sha256:
        raise RuntimeError(
            f"mGBA identity mismatch: required {build.label} sha256 "
            f"{build.sha256}, found sha256 {observed} at {resolved}"
        )
    return resolved


#: The frozen launch-site taxonomy. Exactly one of these per registered site.
PACKAGED_REQUIRED = "packaged-0.10.5-required"
INSTRUMENTED_REQUIRED = "instrumented-required"
USER_SELECTED_PERMITTED = "user-selected-permitted"
NON_RUNTIME_TEST_ONLY = "non-runtime-test-only"
OBSOLETE_UNREACHABLE = "obsolete-unreachable"

LAUNCH_CLASSIFICATIONS = (
    PACKAGED_REQUIRED,
    INSTRUMENTED_REQUIRED,
    USER_SELECTED_PERMITTED,
    NON_RUNTIME_TEST_ONLY,
    OBSOLETE_UNREACHABLE,
)

#: HOW identity is proved at a site. The taxonomy string says what is required;
#: this says which mechanism proves it, so an enforcement predicate keys off the
#: mechanism instead of assuming one from the class name.
EXECUTABLE_DIGEST = "executable-digest"
INSTRUMENTED_MANIFEST = "instrumented-manifest"
FILE_VERSION = "file-version"
NO_PROOF = "none"

PROOF_KINDS = (EXECUTABLE_DIGEST, INSTRUMENTED_MANIFEST, FILE_VERSION, NO_PROOF)


@dataclass(frozen=True, slots=True)
class LaunchSite:
    """One repository-controlled place an mGBA process can start."""

    path: str
    anchor: str
    classification: str
    proof: str
    rationale: str


_PACKAGED_PROBE = (
    "require_mgba_build(PACKAGED_0_10_5) is the first statement of run_probe, "
    "before any stat, port probe or mkdir."
)

_INSTRUMENTED_PROBE = (
    "verify_instrumented_mgba checks the manifest schema, the pinned source "
    "commit, the tracked patch digest and the executable digest before the "
    "launch is reached."
)

_DEV_SESSION = (
    "The Lua-scripted instrumentation and human-play vehicle. It starts the dev "
    "build named by its own -MGBPath default, refuses anything whose "
    "VersionInfo.FileVersion does not match its version parameter "
    "(-RequiredMGBVersion or -MGBVersion, 0.11), and exits holding no wait loop."
)

_POWERSHELL_PACKAGED = (
    "The resolved executable is hashed with Get-FileHash -Algorithm SHA256 and "
    "must equal the pinned packaged digest, which -MGBSha256 carries as an "
    "exact equality test with no accept-anything value. -RequiredMGBVersion is "
    "compared against VersionInfo.FileVersion first, for the better error "
    "message."
)

_TEST_ONLY = (
    "Replaces subprocess.Popen with a failing stub, so this module can never "
    "start a real emulator; it exists to prove a gate refuses before the stub "
    "is reached."
)

LAUNCH_SITES: tuple[LaunchSite, ...] = (
    LaunchSite("tools/runtime/rom006_gdb_probe.py", "run_probe",
               PACKAGED_REQUIRED, EXECUTABLE_DIGEST, _PACKAGED_PROBE),
    LaunchSite("tools/runtime/rom007_factory_probe.py", "run_probe",
               PACKAGED_REQUIRED, EXECUTABLE_DIGEST, _PACKAGED_PROBE),
    LaunchSite("tools/runtime/rom008_query_probe.py", "run_probe",
               PACKAGED_REQUIRED, EXECUTABLE_DIGEST, _PACKAGED_PROBE),
    LaunchSite("tools/runtime/rom009_callback_probe.py",
               "run_probe imported from rom008_query_probe",
               PACKAGED_REQUIRED, EXECUTABLE_DIGEST,
               "This driver has no launch of its own: it imports run_probe from "
               "rom008_query_probe, so that callee's gate is this driver's gate."),
    LaunchSite("tools/runtime/rom011_live_watch.py", "run_live_session",
               INSTRUMENTED_REQUIRED, INSTRUMENTED_MANIFEST, _INSTRUMENTED_PROBE),
    LaunchSite("tools/runtime/rom012_live_containment.py", "run_live_session",
               INSTRUMENTED_REQUIRED, INSTRUMENTED_MANIFEST, _INSTRUMENTED_PROBE),
    LaunchSite("tools/mgba_probe/runtime.py", "verify_instrumented_mgba",
               INSTRUMENTED_REQUIRED, INSTRUMENTED_MANIFEST,
               "Not an emulator launch: it runs <instrumented> --version to "
               "finish the instrumented identity gate before any run starts."),
    LaunchSite("tools/mgba_probe/benchmark.py", "run_gate instrumented cases",
               INSTRUMENTED_REQUIRED, INSTRUMENTED_MANIFEST,
               "The disarmed and armed cases reach _measure, and run_gate "
               "verifies the instrumented manifest first. Classification only "
               "for this ticket, so the stock control below keeps its own "
               "weaker gate."),
    LaunchSite("tools/mgba_probe/benchmark.py", "run_gate stock control",
               PACKAGED_REQUIRED, EXECUTABLE_DIGEST,
               "run_gate calls require_mgba_build(stock, PACKAGED_0_10_5) before "
               "_measure launches the stock control, the same pinned executable "
               "digest the GDB probes use. The instrumented cases are "
               "manifest-gated above it."),
    LaunchSite("tools/webfoot/workbench/launcher.py", "LauncherTab._launch",
               USER_SELECTED_PERMITTED, NO_PROOF,
               "Recorded product decision: a version is display-only and never "
               "gates launch, so any user-chosen mGBA must start. Pinned by "
               "tests/unit/test_mgba_launch_sites.py."),
    LaunchSite("tools/runtime/run_mgba_capture.ps1", "Start-Process $resolvedMGB",
               PACKAGED_REQUIRED, EXECUTABLE_DIGEST, _POWERSHELL_PACKAGED),
    LaunchSite("tools/runtime/load_mgba_lua.ps1", "Start-Process $resolvedMgb",
               PACKAGED_REQUIRED, EXECUTABLE_DIGEST, _POWERSHELL_PACKAGED),
    LaunchSite("tools/runtime/run_toolkit031_watch.ps1", "Start-Process $resolvedMGB",
               INSTRUMENTED_REQUIRED, FILE_VERSION, _DEV_SESSION),
    LaunchSite("tools/runtime/start_toolkit031_session.ps1", "Start-Process $resolvedMGB",
               INSTRUMENTED_REQUIRED, FILE_VERSION, _DEV_SESSION),
    LaunchSite("tools/runtime/start_spritenew001_session.ps1", "Start-Process $resolvedMGB",
               INSTRUMENTED_REQUIRED, FILE_VERSION, _DEV_SESSION),
    LaunchSite("tools/runtime/start_tilepaint001_session.ps1", "Start-Process $resolvedMGB",
               INSTRUMENTED_REQUIRED, FILE_VERSION, _DEV_SESSION),
    LaunchSite("tools/runtime/start_tilepaint001_live.ps1", "Start-Process $resolvedMGB",
               INSTRUMENTED_REQUIRED, FILE_VERSION, _DEV_SESSION),
    LaunchSite("tools/runtime/start_placementpos001_session.ps1", "Start-Process $resolvedMGB",
               INSTRUMENTED_REQUIRED, FILE_VERSION, _DEV_SESSION),
    LaunchSite("tools/runtime/start_placementpos002_session.ps1", "Start-Process $resolvedMGB",
               INSTRUMENTED_REQUIRED, FILE_VERSION, _DEV_SESSION),
    LaunchSite("tools/runtime/start_gfximport001_live.ps1", "Start-Process $resolvedMGB",
               INSTRUMENTED_REQUIRED, FILE_VERSION, _DEV_SESSION),
    LaunchSite("tools/runtime/start_warpedit001_live.ps1", "Start-Process $resolvedMGB",
               INSTRUMENTED_REQUIRED, FILE_VERSION, _DEV_SESSION),
    LaunchSite("tools/runtime/start_capacity001_expansion_session.ps1", "Start-Process $resolvedMGB",
               INSTRUMENTED_REQUIRED, FILE_VERSION, _DEV_SESSION),
    LaunchSite("tools/runtime/run_capacity001_expansion.ps1", "Start-Process $resolvedMGB",
               INSTRUMENTED_REQUIRED, FILE_VERSION, _DEV_SESSION),
    LaunchSite("tools/runtime/capture_tilepaint001_pair.ps1", "Start-Process $resolvedMGB",
               INSTRUMENTED_REQUIRED, FILE_VERSION, _DEV_SESSION),
    LaunchSite("tools/runtime/capture_tilepaint001_afterrebuild.ps1", "Start-Process $resolvedMGB",
               INSTRUMENTED_REQUIRED, FILE_VERSION, _DEV_SESSION),
    LaunchSite("tools/runtime/capture_chunkauth001_afterrebuild.ps1", "Start-Process $resolvedMGB",
               INSTRUMENTED_REQUIRED, FILE_VERSION, _DEV_SESSION),
    LaunchSite("scripts/smoke-combined-rom.ps1", "Start-Process $mgba",
               USER_SELECTED_PERMITTED, NO_PROOF,
               "No emulator identity is checked: -MGBPath is operator-supplied "
               "and the claim is only that the image boots and reports its own "
               "game code, so requiring a particular build would invent a "
               "requirement the check does not have."),
    LaunchSite("tests/unit/test_mgba_identity_gate.py", "_forbidden_popen",
               NON_RUNTIME_TEST_ONLY, NO_PROOF, _TEST_ONLY),
    LaunchSite("tests/unit/test_workbench_launcher_settings.py",
               "monkeypatch.setattr(launcher.subprocess, Popen)",
               NON_RUNTIME_TEST_ONLY, NO_PROOF, _TEST_ONLY),
    LaunchSite("tests/unit/test_workbench_run_config_rom_picker.py",
               "monkeypatch.setattr(launcher_module.subprocess, Popen)",
               NON_RUNTIME_TEST_ONLY, NO_PROOF, _TEST_ONLY),
)
