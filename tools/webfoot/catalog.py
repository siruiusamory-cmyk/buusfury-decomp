
from __future__ import annotations

from importlib import resources
from pathlib import Path

from .profile import RomProfileCatalog


def development_profile_path() -> Path:
    """The catalog a checkout carries, used when no path is given."""
    return Path(__file__).resolve().parents[2] / "config" / "roms.yaml"


def load_catalog(profile_path: Path | None) -> RomProfileCatalog:
    """The explicit profile file wins, then the checkout's config/roms.yaml, then the packaged copy that must travel with a frozen build."""
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
