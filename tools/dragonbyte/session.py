"""The session: which image, which project, and where the user has been.

This is deliberately a THIN model with one job each for the image and the
project. It calls the SDK by its public functions and carries the values they
return; it holds no ROM-format knowledge of its own - no bitfield mask, no
offset literal, no record stride. The image is identified by SHA-256 through the
SDK's own catalog mechanism, so a profile id is never hard-coded here.

What this session deliberately does NOT own is as important as what it does.
There is no staged-work registry, no unsaved-edit count, no dirty flag, no
revision counter and no undo stack: those belong to the edit journal, which this
step does not build. One answer to "is there unwritten work" is the rule, and
inventing a second one here would be the defect that rule exists to prevent.

No Qt is imported: a raised `SessionError` is what a window turns into a
message box.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from tools.webfoot.catalog import load_catalog
from tools.webfoot.gba_header import GbaHeaderError
from tools.webfoot.profile import (
    ProfileConfigError,
    RomProfile,
    RomProfileCatalog,
    VerificationStatus,
)
from tools.webfoot.project import (
    ProjectError,
    ProjectFormatError,
    StatProject,
    read_project,
)
from tools.webfoot.rom import RomIdentification, RomReadError, identify_rom

from .navigation import NavigationHistory


class SessionError(Exception):
    """An image or project could not be opened; the message names the reason.

    Catchable and typed, so a window shows one message box that states the
    reason instead of a traceback.
    """


class RomNotRecognizedError(SessionError):
    """The image's SHA-256 matched no verified profile in the catalog."""


#: The SDK families `Session.open_rom` converts into `SessionError`.
#:
#: Read from the three calls the open makes. `identify_rom` raises
#: `RomReadError` (an `OSError`) and hashes through an `OSError`-raising read;
#: parsing that file's header raises `GbaHeaderError`, whose ancestry is
#: `ValueError` but which is a declared failure of this path - a truncated or
#: non-Game-Boy file is a fact about the input, not a defect in this module;
#: loading the catalog raises `ProfileConfigError`, whose subclass
#: `AmbiguousProfileError` is raised when a digest matches two profiles. They
#: share no parent narrower than `ValueError`, so each is named explicitly -
#: and `ValueError` itself is deliberately NOT caught, because that WOULD
#: report a programmer error here as "your image could not be opened".
#: `OSError` is listed beside `RomReadError` because the image stat and read
#: raise it directly.
_OPEN_ROM_ERRORS = (RomReadError, OSError, GbaHeaderError, ProfileConfigError)

#: The project families `Session.open_project` converts into `SessionError`.
#:
#: `ProjectError` is the family root and covers `ProjectLoadError` and
#: `ProjectValidationError`; `ProjectFormatError` is a separate root, because
#: the TOML codec does not share the model's ancestry. `OSError` is named for
#: the project files `read_project` reads.
_OPEN_PROJECT_ERRORS = (ProjectError, ProjectFormatError, OSError)


@dataclass
class Session:
    """The one mutable model the window reads: image, project and history."""

    rom_path: Path | None = None
    identification: RomIdentification | None = None
    profile: RomProfile | None = None
    project_dir: Path | None = None
    project: StatProject | None = None
    navigation: NavigationHistory = field(default_factory=NavigationHistory)
    #: The catalog resolved once, on the first open, through the SDK's own
    #: default resolution. Lazy because a session that opens no image reads no
    #: configuration at all.
    _catalog: RomProfileCatalog | None = field(default=None, repr=False)

    @property
    def has_rom(self) -> bool:
        return self.identification is not None

    @property
    def has_project(self) -> bool:
        return self.project is not None

    @property
    def rom_identity(self) -> str:
        """The image as one short, copyable line: file name and digest prefix."""
        if self.rom_path is None or self.identification is None:
            return "No ROM open"
        digest = self.identification.hashes.sha256
        return f"{self.rom_path.name} sha256:{digest[:12]}"

    @property
    def project_identity(self) -> str:
        """The project as one short, copyable line: its name and directory."""
        if self.project is None or self.project_dir is None:
            return "No project open"
        return f"{self.project.meta.name} ({self.project_dir.name})"

    def open_rom(self, path: Path) -> None:
        """Identify `path` against the catalog and hold the result.

        TOTAL over the SDK's declared failure families: every expected failure
        leaves as `SessionError`, or as `RomNotRecognizedError` when the digest
        matched no verified profile. A caller therefore catches one type at the
        surface, and the reason it shows is the SDK's own wording.

        The image is read only. Nothing here writes, moves or deletes it.
        """
        path = Path(path)
        try:
            self._open_rom(path)
        except SessionError:
            # Already the boundary type, including `RomNotRecognizedError`,
            # which must pass through unchanged with its own precise wording.
            raise
        except _OPEN_ROM_ERRORS as exc:
            raise SessionError(str(exc)) from exc

    def _open_rom(self, path: Path) -> None:
        """The open itself; `open_rom` owns the failure boundary around it."""
        catalog = self._catalog
        if catalog is None:
            catalog = load_catalog(None)
        identification = identify_rom(path, catalog)
        match = identification.profile_match
        if match.status is not VerificationStatus.VERIFIED or match.profile is None:
            raise RomNotRecognizedError(match.reason)
        # Held only once the open has fully succeeded, so a refused image never
        # leaves a half-open session behind it.
        self._catalog = catalog
        self.rom_path = path
        self.identification = identification
        self.profile = match.profile

    def open_project(self, directory: Path) -> None:
        """Read and hold the authored project at `directory`.

        TOTAL over the project families: a missing directory, unreadable TOML,
        a bad document or a structurally invalid record all leave as
        `SessionError` with the SDK's own reason.
        """
        directory = Path(directory)
        try:
            project = read_project(directory)
        except _OPEN_PROJECT_ERRORS as exc:
            raise SessionError(str(exc)) from exc
        self.project_dir = directory
        self.project = project
