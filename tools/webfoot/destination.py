
from __future__ import annotations

import os
from pathlib import Path

from .write import WriteError

IGNORE_FILE = ".gitignore"

PROTECTED_INPUT_DIRECTORIES = (
    "roms",
    "extracted",
    "dump",
    "dumps",
    "stock",
    "exports",
)

_PROTECTED_CACHE: dict[str, tuple[tuple[Path, ...], tuple[Path, ...]]] = {}


def repository_root() -> Path:
    """The checkout this module shipped in."""
    return Path(__file__).resolve().parents[2]


# resolve() on a name that does not exist keeps the remaining components, which is the spelling a destination under it is compared against.
def _declared_protected_directories(root: Path) -> tuple[Path, ...]:
    try:
        text = (root / IGNORE_FILE).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        text = ""
    declared = set()
    for line in text.splitlines():
        entry = line.strip()
        if not entry or entry.startswith(("#", "!")):
            continue
        if entry.rstrip("/") in PROTECTED_INPUT_DIRECTORIES:
            declared.add(entry.rstrip("/"))
    directories = []
    for name in PROTECTED_INPUT_DIRECTORIES:
        if name in declared:
            directories.append((root / name).resolve())
    return tuple(directories)


def _index(root: Path) -> tuple[tuple[Path, ...], tuple[Path, ...]]:
    key = str(root.resolve())
    cached = _PROTECTED_CACHE.get(key)
    if cached is not None:
        return cached
    directories = _declared_protected_directories(root)
    files: list[Path] = []
    for directory in directories:
        for walked, _, names in os.walk(directory):
            for name in names:
                try:
                    files.append((Path(walked) / name).resolve())
                except OSError:
                    continue
    index = (directories, tuple(files))
    _PROTECTED_CACHE[key] = index
    return index


def _same_file(left: Path, right: Path) -> bool:
    try:
        return os.path.samefile(left, right)
    except OSError:
        return False


def refuse_rom_destination(rom_path: str | Path, destination: str | Path) -> None:
    source = Path(rom_path)
    target = Path(destination)
    try:
        resolved = target.resolve()
    except OSError as exc:
        raise WriteError(
            f"the destination {target} could not be resolved, so it could not be "
            f"checked against the protected ROM inputs: {exc}"
        ) from exc

    directories, files = _index(repository_root())
    protected = files + (source,)

    for candidate in protected:
        if _same_file(target, candidate):
            raise WriteError(
                f"refusing to write {target}: it is the protected ROM input "
                f"{candidate} (the same file under a different name, or another "
                "hard link to it), and a protected ROM is read-only on every write "
                "path"
            )
        try:
            other = candidate.resolve()
        except OSError:
            continue
        if other == resolved:
            raise WriteError(
                f"refusing to write {target}: it resolves to the protected ROM "
                f"input {other}, which is read-only on every write path"
            )

    for directory in directories:
        key = os.path.normcase(str(directory))
        if any(os.path.normcase(str(parent)) == key for parent in resolved.parents):
            raise WriteError(
                f"refusing to write {target}: its resolved path {resolved} is "
                f"inside the protected ROM input directory {directory}, and that "
                "covers every path inside it whether or not the directory exists "
                "yet and however it is reached - a junction or symlink to it "
                "resolves here; choose an output path outside it"
            )
