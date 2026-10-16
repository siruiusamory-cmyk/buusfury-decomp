"""Fail-closed ROM destination safety: identity, not digest.

OWNER R3, 2026-10-09. A digest check answers "does this file hold the canonical
bytes", which is the wrong question for a destination: a derivative has a
different digest and therefore passes, and a hardlink to a protected ROM *is*
protected no matter what its name says. This module asks the other question -
**is this path a protected input, or would it occupy one's path** - and it answers
with the filesystem's own identity where one exists.

Three shapes are refused, and the message names which one:

* the destination IS a protected input, by file identity or by resolved path;
* the destination is a HARD LINK to one - a different name, one file, so writing
  the name truncates the protected ROM. `os.path.samefile` is the only check that
  catches this, and it is why identity rather than content is the rule here;
* the destination lies inside a protected input directory, including one reached
  through a directory junction or symlink, because the destination directory is
  resolved before it is compared and the junction is therefore not a way around
  the rule. A listed name is protected whether or not the directory exists yet:
  the writers create a destination's parent directory, so a name that stopped
  being protected until something created it could be created by the write it was
  meant to refuse, and in a fresh checkout none of these directories exists.

**What is deliberately NOT refused.** A distinct derivative file whose directory
merely *contains* a protected input: a new `<profile>_modified.gba` beside the ROM
is not the ROM. The comparison is per path - the destination's resolved directory
plus file name against the protected directory plus that entry's name - so it
never becomes "no output may live in a directory holding a ROM", which would
refuse the ordinary release workflow and is not what the owner asked for.

The protected set has two sources and no third: the caller's own input, which
needs no policy to be protected, and the directories listed in
:data:`PROTECTED_INPUT_DIRECTORIES`. That tuple is the authoritative list; the
tracked ignore rules are consulted only to confirm a listed name is still
declared there, so a directory dropped from the ignore file stops being protected
and a newly ignored one is not protected until it is listed. A parser that tried
to infer the set from the ignore file alone could not tell an input directory from
an output one, because `build/` is ignored as output.
"""

from __future__ import annotations

import os
from pathlib import Path

from .write import WriteError

#: The tracked file whose rules designate the repository's protected inputs. Its
#: own comment states why both `roms/` and the bare `roms` are listed: the
#: directory covers the ROMs and the bare name covers a symlink or junction to it.
IGNORE_FILE = ".gitignore"

#: The directories this rule treats as protected ROM inputs. ROM-input
#: directories only: `build/` is ignored as generated OUTPUT and is a legal place
#: to emit an image, so protecting it here would forbid the activity the ignore
#: rule exists to keep out of version control.
#:
#: This tuple is the AUTHORITATIVE set. The tracked ignore rules are consulted only
#: to confirm each name is still declared there, so a directory removed from
#: `IGNORE_FILE` stops being protected. The reverse direction is deliberately not
#: supported: a newly ignored directory is not protected until it is listed here,
#: because "ignored" also covers output directories and no parser can tell the two
#: apart. Adding a name is a one-line decision, and that is the point.
PROTECTED_INPUT_DIRECTORIES = (
    "roms",
    "extracted",
    "dump",
    "dumps",
    "stock",
    "exports",
)

#: One protected-input index per checkout root. A destination check runs on every
#: emitted image, and the walk below covers every file in `roms/`, so it is
#: computed once per process per root rather than once per write.
_PROTECTED_CACHE: dict[str, tuple[tuple[Path, ...], tuple[Path, ...]]] = {}


def repository_root() -> Path:
    """The checkout this module shipped in."""
    return Path(__file__).resolve().parents[2]


def _declared_protected_directories(root: Path) -> tuple[Path, ...]:
    """The protected input directories this checkout declares, resolved.

    Read from `IGNORE_FILE`, restricted to the candidate list above, and resolved
    so a junction or symlink to the directory IS the directory. A declared name is
    returned whether or not the directory exists yet - see the module docstring -
    and `resolve()` on a name that does not exist resolves the nearest existing
    ancestor and keeps the remaining components, which is the spelling a
    destination under it has to be compared against.
    """
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
    """Every protected input file this checkout holds, and its directories."""
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
    """Whether two paths name one existing file, by the filesystem's identity.

    `os.path.samefile` answers by volume serial and file index on Windows and by
    device and inode on POSIX, so a hard link - two names, one file - compares
    equal where no path spelling could. False when either path cannot be stat'd,
    which is the ordinary case for an output that does not exist yet.
    """
    try:
        return os.path.samefile(left, right)
    except OSError:
        return False


def refuse_rom_destination(rom_path: str | Path, destination: str | Path) -> None:
    """Refuse a destination that would overwrite a protected ROM input.

    Raises `WriteError`, the family every existing caller of this write path
    already turns into a non-zero exit or a GUI error, and the message names the
    protected input the destination collides with and the rule that refuses it.
    """
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

    # `normcase` folds case exactly where the platform does - a path component is
    # case-insensitive on Windows, so `EXPORTS` and `exports` are one directory -
    # and leaves a case-sensitive filesystem alone. `resolved.parents` starts at
    # `resolved.parent`, so this covers a file directly inside the directory and
    # every path nested deeper below it.
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
