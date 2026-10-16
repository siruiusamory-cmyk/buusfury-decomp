"""Where the ROM profile catalog is loaded from, and which file wins.

The catalog is the table of ROM identities and table addresses every
ROM-addressed reader resolves against. Locating it is a two-line rule, but it is
a rule two very different callers need: the command line, which may be given an
explicit ``--profiles`` file, and the windowed randomizer applications, which are
frozen and have no checkout beside them.

It lives here rather than in :mod:`tools.webfoot.cli` because importing the CLI
brings the whole command surface with it - every editor, atlas and build module
the CLI wires together. A frozen randomizer that imported the CLI for this one
function shipped all of them. Lifting the rule out is the same move
:mod:`tools.webfoot.atlas` already made for the directory it needed, and
``tools.webfoot.cli`` re-exports both names so every existing caller is
unchanged.
"""

from __future__ import annotations

from importlib import resources
from pathlib import Path

from .profile import RomProfileCatalog


def development_profile_path() -> Path:
    """The catalog a checkout carries, used when no path is given."""
    return Path(__file__).resolve().parents[2] / "config" / "roms.yaml"


def load_catalog(profile_path: Path | None) -> RomProfileCatalog:
    """The catalog to use: an explicit file, a checkout's, or the packaged one.

    A frozen build has no checkout, so the packaged ``roms.yaml`` is the branch
    it takes and that file must travel with it.
    """
    if profile_path is not None:
        return RomProfileCatalog.load(profile_path)

    development_path = development_profile_path()
    if development_path.is_file():
        return RomProfileCatalog.load(development_path)

    packaged = resources.files("tools.webfoot.data").joinpath("roms.yaml")
    return RomProfileCatalog.loads(
        packaged.read_text(encoding="utf-8"),
        source="packaged tools.webfoot.data/roms.yaml",
    )
