"""Versioned runtime evidence bundle: one deterministic JSON file per capture.

RUNTIME-FOUNDATION-CONSOLIDATION-001 outcome 6. The schema is frozen by the
ticket contract; this module is its single definition and the only place the
version constant exists. A bundle records what was MEASURED - repository
identity, probe identity, ROM identity, emulator identity, observations and
referenced artifacts - so a later reader can inspect a capture without
relaunching mGBA and without trusting anything a caller asserted.

Identity policy is not re-implemented here. The packaged executable is gated by
``tools.runtime.mgba_identity`` and the instrumented one by
``tools.mgba_probe.runtime.verify_instrumented_mgba``; the bundle reports the
digest those gates accepted.

``emulator.file_version`` stays null on purpose: the accepted digest already
pins the build, and reading a PE version resource would add a platform
dependency for a string no reader consults. The schema permits the null.

Null means UNKNOWN, never clean. ``repository.dirty: null`` says git could not
be asked, which is not the same claim as ``dirty: false``; ``repository.sha:
null`` and ``emulator.file_version: null`` carry the same meaning.

``emulator.label`` for an instrumented build is the manifest's own recorded
``version_output``: a build-time string that the manifest's digest, patch and
source checks attest, NOT a fresh reading. ``verify_instrumented_mgba``
discards the ``--version`` output it checks, so no fresher string exists
without changing that function's return shape.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from tools.mgba_probe.runtime import sha256 as file_sha256
from tools.mgba_probe.runtime import verify_instrumented_mgba
from tools.runtime.mgba_identity import (
    INSTRUMENTED_REQUIRED,
    LAUNCH_CLASSIFICATIONS,
    PACKAGED_0_10_5,
    PACKAGED_REQUIRED,
    require_mgba_build,
)

SCHEMA = "log1-runtime-evidence/1"
EVIDENCE_FILENAME = "evidence.json"

#: The launch-site taxonomy is owned by tools/runtime/mgba_identity.py; the
#: bundle reports one of its values as the measured emulator build class.
BUILD_CLASSES = frozenset(LAUNCH_CLASSIFICATIONS)

REQUIRED_KEYS = (
    "schema",
    "run_id",
    "created_utc",
    "repository",
    "probe",
    "rom",
    "emulator",
    "observations",
    "artifacts",
)


def _git(worktree: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(worktree), *arguments],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    ).stdout.strip()


def repository_identity(worktree: Path) -> dict[str, object]:
    """Measure the worktree commit and dirty flag; null means unknown, not clean.

    A capture that already happened outlives its provenance, so a git that
    cannot answer yields ``{"sha": None, "dirty": None}`` instead of an
    exception: a bundle never fabricates a sha and never reports a clean tree it
    could not look at.
    """
    root = Path(worktree)
    try:
        head = _git(root, "rev-parse", "HEAD")
        dirty = bool(_git(root, "status", "--porcelain"))
    except (OSError, subprocess.SubprocessError):
        return {"sha": None, "dirty": None}
    return {"sha": head or None, "dirty": dirty}


def rom_identity(rom: Path) -> dict[str, object]:
    """Measure the image actually on disk, keeping the path as the caller gave it."""
    rom = Path(rom)
    if not rom.is_file():
        raise RuntimeError(f"ROM image not found: {rom}")
    return {"path": str(rom), "sha256": file_sha256(rom), "bytes": rom.stat().st_size}


def emulator_identity(
    executable: Path, *, instrumented_manifest: Path | None = None
) -> dict[str, object]:
    """Measure which governed build the executable is; never accept a caller's word.

    ``instrumented_manifest`` selects the instrumented policy; without it the
    packaged 0.10.5 digest gate decides. Both raise before any process launch
    when the executable does not match the build they pin.
    """
    if instrumented_manifest is None:
        resolved = require_mgba_build(executable, PACKAGED_0_10_5)
        return {
            "path": str(resolved),
            "sha256": PACKAGED_0_10_5.sha256,
            "build_class": PACKAGED_REQUIRED,
            "label": PACKAGED_0_10_5.label,
            "file_version": None,
            "instrumented": None,
        }
    manifest_path = Path(instrumented_manifest)
    manifest = verify_instrumented_mgba(Path(executable), manifest_path)
    return {
        "path": str(Path(executable).resolve()),
        "sha256": manifest["executable_sha256"],
        "build_class": INSTRUMENTED_REQUIRED,
        "label": manifest.get("version_output"),
        "file_version": None,
        "instrumented": {
            "manifest_path": str(manifest_path),
            "source_commit": manifest["source_commit"],
            "patch_sha256": manifest["patch_sha256"],
        },
    }


def artifact_identity(path: Path, role: str) -> dict[str, object]:
    """Hash one referenced artifact; bulk is referenced, never inlined."""
    path = Path(path)
    if not path.is_file():
        raise RuntimeError(f"artifact not found: {path}")
    return {
        "path": str(path),
        "sha256": file_sha256(path),
        "bytes": path.stat().st_size,
        "role": role,
    }


def build_bundle(
    *,
    run_id: str,
    repository: Mapping[str, object],
    probe: Mapping[str, object],
    rom: Path,
    emulator: Path,
    observations: Mapping[str, object] | None = None,
    artifacts: Mapping[str, str] | None = None,
    instrumented_manifest: Path | None = None,
    created_utc: str | None = None,
) -> dict[str, object]:
    """Assemble one bundle from explicit inputs, measuring ROM and emulator.

    ``artifacts`` maps an artifact path to its role. ``created_utc`` is an
    override for deterministic reproduction; the default is the wall clock.
    """
    document: dict[str, object] = {
        "schema": SCHEMA,
        "run_id": run_id,
        "created_utc": created_utc
        or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repository": dict(repository),
        "probe": dict(probe),
        "rom": rom_identity(rom),
        "emulator": emulator_identity(
            emulator, instrumented_manifest=instrumented_manifest
        ),
        "observations": dict(observations or {}),
        "artifacts": [
            artifact_identity(Path(path), role)
            for path, role in sorted(
                (artifacts or {}).items(), key=lambda item: str(item[0])
            )
        ],
    }
    return validate_bundle(document)


def write_run_bundle(
    run_root: Path,
    *,
    tool: str,
    arguments: Mapping[str, object],
    rom: Path,
    emulator: Path,
    observations: Mapping[str, object] | None = None,
    artifacts: Mapping[Path, str] | None = None,
    instrumented_manifest: Path | None = None,
) -> Path:
    """Emit ``evidence.json`` into a probe run directory, measuring everything.

    The run id is the directory name and the repository identity is measured
    from this module's own worktree, so a probe supplies only what it alone
    knows: its tool id, its arguments, and its observations.
    """
    root = Path(run_root)
    # An artifact that does not exist at write time is omitted, never given a
    # digest that was not measured. Add an artifact-status field only if the
    # offline reader needs "absent" told apart from "not collected".
    present = {
        Path(path): role
        for path, role in (artifacts or {}).items()
        if Path(path).is_file()
    }
    return write_bundle(
        root / EVIDENCE_FILENAME,
        build_bundle(
            run_id=root.name,
            repository=repository_identity(Path(__file__).resolve().parents[2]),
            probe={"tool": tool, "arguments": dict(arguments)},
            rom=rom,
            emulator=emulator,
            observations=observations,
            artifacts=present,
            instrumented_manifest=instrumented_manifest,
        ),
    )


def validate_bundle(document: Mapping[str, Any]) -> dict[str, Any]:
    """Refuse an unsupported schema, a missing required key or an unknown build class.

    Extra top-level keys are preserved and never stripped, and no key is ever
    added: this function reports what the document contains, nothing more.
    """
    if not isinstance(document, Mapping):
        raise ValueError("runtime evidence bundle must be a JSON object")
    missing = [key for key in REQUIRED_KEYS if key not in document]
    if missing:
        raise ValueError(
            "runtime evidence bundle is missing required key(s): " + ", ".join(missing)
        )
    if document["schema"] != SCHEMA:
        raise ValueError(
            f"unsupported runtime evidence schema: {document['schema']!r} "
            f"(expected {SCHEMA!r})"
        )
    emulator = document["emulator"]
    build_class = (
        emulator.get("build_class") if isinstance(emulator, Mapping) else None
    )
    if build_class not in BUILD_CLASSES:
        raise ValueError(
            f"unsupported emulator build_class: {build_class!r} "
            f"(supported: {', '.join(sorted(BUILD_CLASSES))})"
        )
    return dict(document)


def serialize_bundle(document: Mapping[str, Any]) -> str:
    """The frozen byte form: sorted keys, two-space indent, one trailing newline."""
    return json.dumps(validate_bundle(document), sort_keys=True, indent=2) + "\n"


def write_bundle(path: Path, document: Mapping[str, Any]) -> Path:
    """Write the bundle UTF-8 with LF endings and no byte-order mark."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        serialize_bundle(document), encoding="utf-8", newline="\n"
    )
    return target


def read_bundle(path: Path) -> dict[str, Any]:
    """Parse and validate one bundle, refusing anything the schema does not allow."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("runtime evidence bundle must be a JSON object")
    return validate_bundle(data)
