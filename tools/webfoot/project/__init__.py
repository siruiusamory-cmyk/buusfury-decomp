"""Project serialization: the authored source form of a mod.

TOOLKIT-002. This layer owns the on-disk *authoring* surface and nothing else.
It reads and writes project files; it never opens a ROM, never computes a file
offset, and never emits an image. `webfoot.build` orchestrates, `webfoot.rom`
and `webfoot.write` own the binary, and this package owns the text.
"""

from .format import (
    ProjectFormatError,
    dump_toml,
    load_toml,
)
from .model import (
    PROJECT_FORMAT_VERSION,
    ProjectError,
    ProjectLoadError,
    ProjectMeta,
    ProjectValidationError,
    StatProject,
    read_project,
    write_dialogue_replacements,
    write_project,
)
from .placements import remove_authored_placement

__all__ = [
    "PROJECT_FORMAT_VERSION",
    "ProjectError",
    "ProjectFormatError",
    "ProjectLoadError",
    "ProjectMeta",
    "ProjectValidationError",
    "StatProject",
    "dump_toml",
    "load_toml",
    "read_project",
    "remove_authored_placement",
    "write_dialogue_replacements",
    "write_project",
]
