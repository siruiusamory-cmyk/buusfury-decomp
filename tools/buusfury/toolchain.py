"""Toolchain discovery and the doctor report.

Answers one question per tool: can this machine run it right now, and if not,
what exactly is missing? The pipeline never guesses: a tool that cannot be found
is reported as missing and the stages that need it fail closed.

No tool is ever bundled with this repository. ARM Developer Suite 1.2 in
particular is commercial software whose licence does not permit redistribution;
it is located through ADS12_ROOT (or PATH) and never committed.
"""

from __future__ import annotations

import dataclasses
import json
import os
import shutil
import subprocess
from pathlib import Path

from . import identity as _identity


class ToolchainError(RuntimeError):
    """Raised when a required tool is unavailable."""


@dataclasses.dataclass(frozen=True)
class ToolStatus:
    id: str
    family: str
    purpose: str
    path: Path | None
    version: str
    required_for: tuple[str, ...]
    blocks_full_reproduction: bool

    @property
    def available(self) -> bool:
        return self.path is not None

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "family": self.family,
            "available": self.available,
            "path": str(self.path) if self.path else None,
            "version": self.version,
            "required_for": list(self.required_for),
            "blocks_full_reproduction": self.blocks_full_reproduction,
        }


def load_manifest(path: Path | None = None) -> dict:
    config_path = path or (_identity.CONFIG_DIR / "toolchain.json")
    return json.loads(config_path.read_text(encoding="utf-8"))


def ads_root(explicit: str | Path | None = None) -> Path | None:
    """Resolve ADS12_ROOT. Returns None when unset; never invents a path."""
    if explicit is not None:
        p = Path(explicit)
        return p if p.is_dir() else None
    env = os.environ.get("ADS12_ROOT", "").strip()
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    return None


def _ads_executable(tool_id: str, root: Path | None) -> Path | None:
    """Look for an ADS tool under ADS12_ROOT/Bin, then on PATH."""
    exe = f"{tool_id}.exe"
    if root is not None:
        for sub in ("Bin", "bin"):
            candidate = root / sub / exe
            if candidate.is_file():
                return candidate
        candidate = root / exe
        if candidate.is_file():
            return candidate
    found = shutil.which(tool_id)
    return Path(found) if found else None


def _probe_version(exe: Path, timeout: float = 10.0) -> str:
    """Ask a tool for its banner. Never fatal: an unprobeable tool is 'unknown'."""
    try:
        completed = subprocess.run(
            [str(exe)],
            capture_output=True,
            text=True,
            timeout=timeout,
            errors="replace",
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown (could not execute)"
    blob = (completed.stdout or "") + (completed.stderr or "")
    for line in blob.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped[:200]
    return "unknown (no banner)"


def _which_any(names: tuple[str, ...]) -> Path | None:
    for name in names:
        found = shutil.which(name)
        if found:
            return Path(found)
    return None


def find_grit() -> Path | None:
    """Locate grit.

    devkitPro ships grit in its tools/bin directory but does NOT put that
    directory on PATH by default, so a bare shutil.which("grit") misses an
    otherwise perfectly good installation. Checked in order:

    1. $GRIT
    2. PATH
    3. $DEVKITPRO/tools/bin/grit.exe
    4. <devkitPro default>/tools/bin/grit.exe
    """
    override = os.environ.get("GRIT", "").strip()
    if override and Path(override).is_file():
        return Path(override)

    found = shutil.which("grit")
    if found:
        return Path(found)

    roots: list[Path] = []
    devkitpro = os.environ.get("DEVKITPRO", "").strip()
    if devkitpro:
        roots.append(Path(devkitpro))
    roots.append(Path(r"C:\devkitPro"))
    for root in roots:
        for name in ("grit.exe", "grit"):
            candidate = root / "tools" / "bin" / name
            if candidate.is_file():
                return candidate
    return None


def find_executable(tool_id: str) -> Path | None:
    """Locate a non-ADS tool by id, honouring the project's own discovery rules."""
    if tool_id == "grit":
        return find_grit()
    if tool_id == "cmake":
        override = os.environ.get("CMAKE", "").strip()
        if override and Path(override).is_file():
            return Path(override)
        # Prefer the Visual Studio CMake: the MSYS2/MinGW one that devkitPro puts
        # on PATH cannot name a Visual Studio generator, so it cannot configure
        # the JCALG1 front-end at all.
        vs_cmake = find_cmake_with_vs_generator()
        if vs_cmake is not None:
            return vs_cmake
        return _which_any(("cmake",))
    if tool_id == "python":
        return _which_any(("python", "python3", "py"))
    if tool_id == "msvc-x86":
        return _find_msvc()
    return _which_any((tool_id,))


def doctor(ads12_root: str | Path | None = None, probe_versions: bool = True) -> list[ToolStatus]:
    """Report the availability of every tool the baseline pipeline declares."""
    manifest = load_manifest()
    root = ads_root(ads12_root)
    statuses: list[ToolStatus] = []

    for entry in manifest["tools"]:
        tool_id = entry["id"]
        entry_family = entry["family"]
        path: Path | None = None

        if entry_family == "ads12":
            path = _ads_executable(tool_id, root)
        else:
            path = find_executable(tool_id)

        version = ""
        if path is not None and probe_versions:
            if tool_id == "python":
                import platform

                version = f"Python {platform.python_version()}"
            elif path.suffix.lower() in (".bat", ".cmd"):
                # A batch file has no version banner; running it only prints noise.
                version = "present"
            else:
                version = _probe_version(path)

        statuses.append(
            ToolStatus(
                id=tool_id,
                family=entry_family,
                purpose=entry["purpose"],
                path=path,
                version=version,
                required_for=tuple(entry.get("required_for", ())),
                blocks_full_reproduction=bool(
                    entry.get("blocks_full_reproduction", False)
                ),
            )
        )

    return statuses


def _find_msvc() -> Path | None:
    """Locate the x86 MSVC environment script (32-bit: jcalg1_static.lib is x86)."""
    candidates: list[Path] = []
    vswhere = (
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))
        / "Microsoft Visual Studio"
        / "Installer"
        / "vswhere.exe"
    )
    roots: list[Path] = []
    if vswhere.is_file():
        try:
            completed = subprocess.run(
                [str(vswhere), "-products", "*", "-property", "installationPath"],
                capture_output=True,
                text=True,
                timeout=20,
                errors="replace",
            )
            for line in completed.stdout.splitlines():
                line = line.strip()
                if line:
                    roots.append(Path(line))
        except (OSError, subprocess.SubprocessError):
            pass
    for base in (
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))
        / "Microsoft Visual Studio",
        Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
        / "Microsoft Visual Studio",
    ):
        if base.is_dir():
            roots.extend(p for p in base.rglob("BuildTools") if p.is_dir())

    for root in roots:
        candidates.append(root / "VC" / "Auxiliary" / "Build" / "vcvars32.bat")
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def find_cmake_with_vs_generator() -> Path | None:
    """Locate a CMake that can name a Visual Studio generator.

    The MSYS2/MinGW CMake that devkitPro ships CANNOT - it fails with
    'Could not create named generator Visual Studio 17 2022'. The CMake bundled
    with Visual Studio can. This is a real, previously undocumented failure mode
    of the reference build, so it is handled explicitly rather than hoped away.
    """
    override = os.environ.get("CMAKE", "").strip()
    if override and Path(override).is_file():
        return Path(override)
    vswhere = (
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))
        / "Microsoft Visual Studio"
        / "Installer"
        / "vswhere.exe"
    )
    if vswhere.is_file():
        try:
            completed = subprocess.run(
                [str(vswhere), "-products", "*", "-property", "installationPath"],
                capture_output=True,
                text=True,
                timeout=20,
                errors="replace",
            )
            for line in completed.stdout.splitlines():
                line = line.strip()
                if not line:
                    continue
                candidate = (
                    Path(line)
                    / "Common7"
                    / "IDE"
                    / "CommonExtensions"
                    / "Microsoft"
                    / "CMake"
                    / "CMake"
                    / "bin"
                    / "cmake.exe"
                )
                if candidate.is_file():
                    return candidate
        except (OSError, subprocess.SubprocessError):
            pass
    return None


def require(tool_id: str, statuses: list[ToolStatus] | None = None) -> ToolStatus:
    """Return a tool's status or raise with an actionable message."""
    found = None
    for status in statuses if statuses is not None else doctor():
        if status.id == tool_id:
            found = status
            break
    if found is None:
        raise ToolchainError(f"unknown tool id: {tool_id}")
    if not found.available:
        raise ToolchainError(
            f"required tool {tool_id!r} is not available. "
            f"Purpose: {found.purpose} "
            "Set ADS12_ROOT (for ARM Developer Suite tools) or put it on PATH."
        )
    return found
