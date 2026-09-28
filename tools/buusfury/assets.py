"""Rebuild the asset-backed regions and compare them to the canonical ROM.

This is the part of the pipeline that does NOT need ARM Developer Suite. It is
also the only part of the reference project's rebuild that makes a real claim:
the asset blobs in the shipping ROM can be regenerated from the project's source
BMPs with grit plus the JCALG1 compressor.

Every asset here was verified byte-identical against the canonical ROM on
2026-09-28. See docs/VALIDATION_REPORT.md.

Nothing ROM-derived is committed by this repository. The source assets are
fetched on demand into reference/ (gitignored) by scripts/fetch-reference.ps1.
"""

from __future__ import annotations

import dataclasses
import os
import shutil
import subprocess
from pathlib import Path

from . import identity as _identity
from . import regions as _regions
from . import toolchain as _toolchain

#: Exactly the grit arguments the reference build uses, for every asset.
GRIT_ARGS = ("-gB8", "-p!", "-ftb", "-gb")


class AssetError(RuntimeError):
    """Raised when an asset cannot be rebuilt or does not match the ROM."""


@dataclasses.dataclass(frozen=True)
class AssetSpec:
    """How to regenerate one region from a source asset."""

    region_id: str
    source: str
    kind: str  # "grit" | "grit+jcalg1" | "copy"
    #: Explicit minimum output size passed to the JCALG1 front-end, exactly as
    #: the reference build passes it. None means "no padding".
    min_size: int | None = None
    note: str = ""


#: The ten asset regions of the baseline map.
#:
#: The source paths are the reference project's own filenames - including the
#: misspelling 'cornet_top_left.bmp', which is load-bearing: the file on disk
#: really is spelled that way and the build output really is 'corner_top_left'.
ASSET_SPECS: tuple[AssetSpec, ...] = (
    AssetSpec(
        region_id="asset_intro",
        source="assets/intro.bmp",
        kind="grit+jcalg1",
        min_size=None,
        note="no minimum size is passed for the intro",
    ),
    AssetSpec(
        region_id="bmp_corner_top_left",
        source="assets/cornet_top_left.bmp",
        kind="grit",
        note="upstream filename is misspelled 'cornet'",
    ),
    AssetSpec(
        region_id="bmp_corner_top_right",
        source="assets/corner_top_right.bmp",
        kind="grit",
    ),
    AssetSpec(
        region_id="bmp_corner_bottom_left",
        source="assets/corner_bottom_left.bmp",
        kind="grit",
    ),
    AssetSpec(
        region_id="bmp_corner_bottom_right",
        source="assets/corner_bottom_right.bmp",
        kind="grit",
    ),
    AssetSpec(region_id="palette_bg", source="assets/palettes/bg.pal", kind="copy"),
    AssetSpec(
        region_id="palette_sprite", source="assets/palettes/sprite.pal", kind="copy"
    ),
    AssetSpec(
        region_id="asset_dialogbox",
        source="assets/dialogbox.bmp",
        kind="grit+jcalg1",
        min_size=788,
        note="788 is exactly the uncompressed stream's own length",
    ),
    AssetSpec(
        region_id="asset_dialogbox_small",
        source="assets/dialogbox_small.bmp",
        kind="grit+jcalg1",
        min_size=None,
    ),
    AssetSpec(
        region_id="asset_splash",
        source="assets/splash.bmp",
        kind="grit+jcalg1",
        min_size=20516,
    ),
)

SPECS_BY_REGION = {spec.region_id: spec for spec in ASSET_SPECS}


@dataclasses.dataclass
class AssetResult:
    region_id: str
    ok: bool
    source_exists: bool
    rebuilt_length: int
    expected_length: int
    first_difference: int | None
    detail: str

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)


def default_reference_dir(repo_root: Path | None = None) -> Path | None:
    """Where the fetched reference checkout is expected to live."""
    env = os.environ.get("BUUSFURY_REFERENCE", "").strip()
    if env:
        p = Path(env)
        return p if p.is_dir() else None
    root = repo_root or _identity.REPO_ROOT
    for candidate in (root / "reference" / "buusfury", root / "reference"):
        if (candidate / "assets").is_dir():
            return candidate
    return None


def default_compress_exe(repo_root: Path | None = None) -> Path | None:
    """Locate the JCALG1 front-end binary."""
    env = os.environ.get("BUUSFURY_COMPRESS", "").strip()
    if env and Path(env).is_file():
        return Path(env)
    root = repo_root or _identity.REPO_ROOT
    for candidate in (
        root / "build" / "tools" / "compress.exe",
        root / "toolchain" / "compress.exe",
    ):
        if candidate.is_file():
            return candidate
    found = shutil.which("compress")
    return Path(found) if found else None


def build_compress_exe(
    reference_dir: Path,
    out_dir: Path,
    cmake_exe: Path | None = None,
) -> Path:
    """Configure and build the JCALG1 front-end with the reference build's settings.

    Reproduces the reference invocation, INCLUDING its inconsistency: CMake is
    configured with -DCMAKE_BUILD_TYPE=Release but the build config is Debug and
    build.bat then invokes build/Debug/compress.exe. With a Visual Studio
    generator CMAKE_BUILD_TYPE is ignored anyway, so the reference works only by
    accident. We keep Debug because that is the binary path the reference script
    actually consumes.
    """
    source = reference_dir / "tools" / "compress"
    if not (source / "CMakeLists.txt").is_file():
        raise AssetError(
            f"cannot build the JCALG1 front-end: {source / 'CMakeLists.txt'} not found. "
            "Fetch the reference checkout first (scripts/fetch-reference.ps1)."
        )

    cmake = cmake_exe or _toolchain.find_cmake_with_vs_generator()
    if cmake is None:
        raise AssetError(
            "no CMake with a Visual Studio generator was found. The MSYS2/MinGW "
            "CMake shipped by devkitPro cannot configure this project "
            "('Could not create named generator Visual Studio 17 2022'). "
            "Install the Visual Studio CMake component, or set CMAKE to its path."
        )

    build_dir = out_dir / "compress-build"
    build_dir.parent.mkdir(parents=True, exist_ok=True)
    configure = [
        str(cmake),
        "-B",
        str(build_dir),
        "-S",
        str(source),
        "-G",
        "Visual Studio 17 2022",
        "-A",
        "Win32",
        "-DCMAKE_EXE_LINKER_FLAGS=/SAFESEH:NO",
    ]
    compile_cmd = [str(cmake), "--build", str(build_dir), "--config", "Debug"]
    for cmd in (configure, compile_cmd):
        completed = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
        if completed.returncode != 0:
            raise AssetError(
                f"command failed ({completed.returncode}): {' '.join(cmd)}\n"
                f"{completed.stdout}\n{completed.stderr}"
            )

    for candidate in build_dir.rglob("compress.exe"):
        if candidate.is_file():
            target = out_dir / "compress.exe"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(candidate, target)
            return target

    raise AssetError(f"compress.exe was not produced under {build_dir}")


def _run(cmd: list[str], cwd: Path | None = None) -> None:
    completed = subprocess.run(
        cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True, errors="replace"
    )
    if completed.returncode != 0:
        raise AssetError(
            f"command failed ({completed.returncode}): {' '.join(cmd)}\n"
            f"{completed.stdout}\n{completed.stderr}"
        )


def rebuild_one(
    region: _regions.Region,
    spec: AssetSpec,
    reference_dir: Path,
    workdir: Path,
    grit_exe: Path | None,
    compress_exe: Path | None,
) -> bytes:
    """Produce the bytes for one asset region from its source asset."""
    source = reference_dir / spec.source
    if not source.is_file():
        raise AssetError(f"source asset not found: {source}")

    if spec.kind == "copy":
        return source.read_bytes()

    if grit_exe is None:
        raise AssetError(
            "grit is required to rebuild this region but was not found on PATH"
        )

    workdir.mkdir(parents=True, exist_ok=True)
    prefix = workdir / f"{region.id}"
    _run(
        [str(grit_exe), str(source), *GRIT_ARGS, "-o", str(prefix)],
        cwd=reference_dir,
    )
    image = prefix.with_suffix(".img.bin")
    if not image.is_file():
        produced = sorted(p.name for p in workdir.glob(f"{region.id}*"))
        raise AssetError(
            f"grit produced no {region.id}.img.bin (produced: {produced})"
        )

    if spec.kind == "grit":
        return image.read_bytes()

    if spec.kind != "grit+jcalg1":
        raise AssetError(f"unknown asset kind: {spec.kind}")

    if compress_exe is None:
        raise AssetError(
            "the JCALG1 compress front-end is required for this region but was not "
            "found. Build it with scripts/fetch-reference.ps1 -BuildTools, or set "
            "BUUSFURY_COMPRESS."
        )

    compressed = workdir / f"{region.id}.compressed"
    cmd = [str(compress_exe), str(image), str(compressed)]
    if spec.min_size is not None:
        cmd.append(str(spec.min_size))
    _run(cmd)
    if not compressed.is_file():
        raise AssetError(f"compress produced no output for {region.id}")
    return compressed.read_bytes()


def verify_assets(
    baserom: Path,
    regions: list[_regions.Region],
    reference_dir: Path | None = None,
    workdir: Path | None = None,
    grit_exe: Path | None = None,
    compress_exe: Path | None = None,
) -> list[AssetResult]:
    """Rebuild every asset region and compare it to the canonical ROM.

    Missing sources are reported as failures in the result list rather than
    raised, so one run reports the whole picture.
    """
    ref = reference_dir or default_reference_dir()
    work = workdir or (_identity.REPO_ROOT / "build" / "assets")
    grit = grit_exe or _toolchain.find_grit()
    compress = compress_exe or default_compress_exe()

    data = baserom.read_bytes()
    results: list[AssetResult] = []

    for spec in ASSET_SPECS:
        region = next((r for r in regions if r.id == spec.region_id), None)
        if region is None:
            results.append(
                AssetResult(
                    region_id=spec.region_id,
                    ok=False,
                    source_exists=False,
                    rebuilt_length=0,
                    expected_length=0,
                    first_difference=None,
                    detail="region is absent from the region map",
                )
            )
            continue

        expected = data[region.start : region.end]

        if ref is None:
            results.append(
                AssetResult(
                    region_id=spec.region_id,
                    ok=False,
                    source_exists=False,
                    rebuilt_length=0,
                    expected_length=region.length,
                    first_difference=None,
                    detail=(
                        "no reference checkout found; run scripts/fetch-reference.ps1 "
                        "or set BUUSFURY_REFERENCE"
                    ),
                )
            )
            continue

        source = ref / spec.source
        if not source.is_file():
            results.append(
                AssetResult(
                    region_id=spec.region_id,
                    ok=False,
                    source_exists=False,
                    rebuilt_length=0,
                    expected_length=region.length,
                    first_difference=None,
                    detail=f"source asset missing: {source}",
                )
            )
            continue

        try:
            rebuilt = rebuild_one(region, spec, ref, work, grit, compress)
        except AssetError as exc:
            results.append(
                AssetResult(
                    region_id=spec.region_id,
                    ok=False,
                    source_exists=True,
                    rebuilt_length=0,
                    expected_length=region.length,
                    first_difference=None,
                    detail=str(exc),
                )
            )
            continue

        diff = _first_difference(expected, rebuilt)
        results.append(
            AssetResult(
                region_id=spec.region_id,
                ok=(diff is None and len(rebuilt) == len(expected)),
                source_exists=True,
                rebuilt_length=len(rebuilt),
                expected_length=len(expected),
                first_difference=diff,
                detail=(
                    "byte-identical"
                    if diff is None and len(rebuilt) == len(expected)
                    else f"length {len(rebuilt)} vs expected {len(expected)}"
                    if diff is None
                    else f"first difference at +0x{diff:X}"
                ),
            )
        )

    return results


def _first_difference(expected: bytes, actual: bytes) -> int | None:
    for index in range(min(len(expected), len(actual))):
        if expected[index] != actual[index]:
            return index
    if len(expected) != len(actual):
        return min(len(expected), len(actual))
    return None


def _which(name: str) -> Path | None:
    found = shutil.which(name)
    return Path(found) if found else None
