"""Shared mutable model for the WORKBENCH-001 GUI.

`Session` is the one object every tab reads and writes: the Atlas browser fills
it via `open_rom`, and the Inspector, Build and Launcher tabs read what it holds.

This is deliberately a THIN model. It calls the SDK by its public functions and
carries the values they return; it holds no ROM-format knowledge of its own - no
bitfield masks, no offset literals, no record-type constants. The ROM is
identified by SHA-256 through the SDK's existing catalog mechanism
(`rom.identify_rom`), the same one `build.py`/`atlas_build.py` and the CLI use,
so a profile id is never hard-coded here. No Qt is imported: a raised
`SessionError` is what a tab turns into a `QMessageBox`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..atlas import Atlas
from ..atlas_build import load_atlas, load_decoded_text
from ..build import BuildResult
from ..cli import _default_atlas_directory
from ..formats.map_entry import MapEntryProfileError
from ..graphics import ActorSprites, GraphicsError, load_actor_sprites
from ..map_layout_provenance import AuthoredRom, ProvenanceError, verify_authored_rom
from ..maps import Maps, load_maps
from ..profile import (
    AtlasIdentityMismatch,
    RomProfile,
    RomProfileCatalog,
    VerificationStatus,
)
from ..rom import RomIdentification, identify_rom
from ..text import TextProfileError, TextStrings, TextTableError, load_text_strings


class SessionError(Exception):
    """A ROM cannot be opened for the workbench; the message names the reason.

    Catchable and typed so a tab shows one `QMessageBox` instead of a traceback.
    """


class RomNotRecognizedError(SessionError):
    """The ROM's SHA-256 matched no profile in the catalog, and it is not a
    verified DragonByte Z-authored layout derivative either."""


@dataclass
class Session:
    rom_path: Path | None = None
    profile: RomProfile | None = None
    atlas: Atlas | None = None
    decoded_text: list[dict] = field(default_factory=list)
    rom_image: bytes | None = None
    # The loaded map domain, populated in `open_rom` the same way `atlas` is, or
    # None when the open ROM's profile declares no readable map table (Legacy of
    # Goku's variant layout). The Scene tab reads this through `tools.webfoot.scene`.
    maps: Maps | None = None
    # Semantic text identities/previews used by specialized script editors.
    # None means this profile exposes no supported text table.
    text_strings: TextStrings | None = None
    # The map the Scene tab is authoring against, by `map:NNNN` identity string.
    selected_map: str | None = None
    project_dir: Path | None = None
    selected_result: dict | None = None
    output_dir: Path | None = None
    last_build: BuildResult | None = None
    project_revision: int = 0
    validation_revision: int | None = None
    build_revision: int | None = None
    # Full identification kept so the actor-sprite corpus can be loaded lazily
    # (it needs the RomIdentification, not just the matched profile).
    identification: RomIdentification | None = None
    #: Set when the open image is a verified DragonByte Z-authored layout
    #: derivative rather than the canonical ROM. It carries the reconstructed
    #: canonical bytes (which every accepted reader runs against) and the verified
    #: layout edits (which the Map Browser applies as preview overrides), so a
    #: derivative is never interpreted as if it were the canonical image.
    authored: AuthoredRom | None = None
    #: Why a non-canonical image was refused, for a message that names the reason.
    provenance_error: str | None = None
    # Cached decoded actor-sprite corpus for the open ROM. Lazy because building
    # it walks all ~7k graphics once; None when unbuilt or the profile declares
    # no actor_sprites. Reached only through `sprites`.
    _sprites: ActorSprites | None = None
    _sprites_loaded: bool = False

    @property
    def sprites(self) -> ActorSprites | None:
        """The decoded actor-sprite corpus, or None when unavailable.

        Loaded on first read, the same way `maps`/`atlas` are obtained through
        the public SDK: `load_actor_sprites(rom_image, identification)`. A
        profile that declares no actor_sprites raises `GraphicsError`, which is a
        supported state (that ROM simply has no sprites to edit) and yields None,
        not a failure. Result is cached until the next `open_rom`.
        """
        if self._sprites_loaded:
            return self._sprites
        self._sprites_loaded = True
        if self.rom_image is None or self.identification is None:
            self._sprites = None
            return None
        try:
            self._sprites = load_actor_sprites(self.rom_image, self.identification)
        except GraphicsError:
            self._sprites = None
        return self._sprites

    @property
    def map_image(self) -> bytes | None:
        """The bytes the accepted map readers run against.

        The canonical image for a verified canonical ROM; the reconstructed
        canonical bytes for a verified DragonByte Z-authored derivative. Every
        reader that resolves profile-specific addresses uses this, never the
        derivative's own bytes.
        """
        if self.authored is not None:
            return self.authored.canonical_image
        return self.rom_image

    def layout_overrides(self, map_index: int) -> dict[tuple[int, int], int]:
        """The verified layout edits a derivative carries for one map.

        Empty for the canonical ROM, whose layout is already its own.
        """
        if self.authored is None:
            return {}
        return self.authored.overrides_for(map_index)

    @property
    def validation_current(self) -> bool:
        return self.validation_revision == self.project_revision

    @property
    def build_current(self) -> bool:
        return self.build_revision == self.project_revision and self.last_build is not None

    def set_project(self, path: Path) -> None:
        """Select project source and invalidate results tied to prior source."""
        self.project_dir = Path(path)
        self.project_mutated()

    def project_mutated(self) -> None:
        """Advance project state and make prior validation/build unusable."""
        self.project_revision += 1
        self.validation_revision = None
        self.build_revision = None
        self.last_build = None

    def scene_mutated(self) -> None:
        """A scene edit committed; invalidate prior validation/build.

        Routes through the existing `project_mutated()` rather than inventing a
        second invalidation path: a scene edit changes the project on disk (via
        `scene.add_authored_npc`), so it is a project mutation like any other.
        """
        self.project_mutated()

    def record_validation(self, passed: bool) -> None:
        self.validation_revision = self.project_revision if passed else None
        if not passed:
            self.build_revision = None
            self.last_build = None

    def record_build(self, result: BuildResult) -> None:
        if not self.validation_current:
            raise SessionError("project validation is stale; validate again before building")
        self.last_build = result
        self.build_revision = self.project_revision

    def open_rom(self, path: Path, catalog: RomProfileCatalog) -> None:
        """Identify `path` against `catalog`, load its atlas, and cache its bytes.

        Raises `RomNotRecognizedError` when no profile matches by SHA-256, and
        `SessionError` when the atlas artifact the CLI would read is missing.
        On success, populates `profile`, `atlas`, `decoded_text`, `rom_path`,
        `rom_image`.
        """
        path = Path(path)
        # Same SHA-256 identify path the CLI uses (cli.py identify -> identify_rom).
        identification = identify_rom(path, catalog)
        match = identification.profile_match
        authored: AuthoredRom | None = None
        match_profile = match.profile
        self.provenance_error = None
        if match.status is not VerificationStatus.VERIFIED or match.profile is None:
            # A DragonByte Z-authored layout derivative is the one supported
            # non-canonical image: it is accepted only once it has been proved to be
            # the canonical ROM plus declared, policy-legal layout edits, and the
            # profile it derives from must be one this catalog verifies.
            authored = self._verify_derivative(path)
            if authored is None:
                reason = match.reason
                if self.provenance_error:
                    reason = f"{match.reason}; {self.provenance_error}"
                raise RomNotRecognizedError(f"{path} was not recognized: {reason}")
            # The manifest must name the profile *of the canonical image it derives
            # from*, not merely a profile this installation happens to configure: a
            # canonical base with some other game's profile id is a contradiction.
            match_profile = next(
                (
                    profile
                    for profile in catalog.profiles
                    if profile.id == authored.profile_id
                ),
                None,
            )
            if match_profile is None or match_profile.sha256 != authored.canonical_sha256:
                self.provenance_error = (
                    f"the manifest names base profile {authored.profile_id!r}, which is "
                    "not the profile of the canonical image it claims to derive from"
                )
                raise RomNotRecognizedError(
                    f"{path} was not recognized: {self.provenance_error}"
                )

        # The atlas is a single assembled artifact, located the way the CLI's
        # atlas commands locate it by default (cli._default_atlas_directory).
        atlas_dir = _default_atlas_directory()
        atlas_path = atlas_dir / "atlas.jsonl"
        if not atlas_path.is_file():
            raise SessionError(
                f"atlas artifact missing: {atlas_path}. Build it with "
                f"`python -m tools.webfoot atlas build` (or `atlas regenerate`)."
            )
        atlas = load_atlas(atlas_path)
        # The atlas records the base image it was built for. Pairing it with a
        # different image - another catalogued profile, or the same profile's
        # bytes at another revision - would make every offset, coverage class
        # and VERIFIED_FREE span a claim about bytes that are not here, which is
        # the evidence the capacity work would read. One comparison, owned by
        # the profile, refuses before the atlas becomes session state and before
        # any atlas-backed surface can read it. The manifest already required a
        # derivative's profile to be the profile *of* its canonical base, so
        # this covers that path too.
        #
        # Never regenerated here: an atlas is evidence-producing work and stays
        # explicit. A mismatch is a refusal with both identities named, not a
        # silent rebuild and not a silent accept.
        try:
            match_profile.require_identity(atlas, subject=f"atlas {atlas_path}")
        except AtlasIdentityMismatch as exc:
            raise SessionError(str(exc)) from exc
        # load_decoded_text treats a missing index as empty, not an error.
        decoded_text = load_decoded_text(atlas_dir)

        rom_image = path.read_bytes()

        # Maps are loaded the same way the atlas is: through the public SDK read,
        # from the same path/catalog the identify used. A profile that declares no
        # readable map table (`MapEntryProfileError`) is a supported state - that
        # ROM simply has no scene to author - not a failure. A derivative's scene
        # and text readers identify the file by SHA-256, so it simply has none of
        # these domains here; the Map Browser renders it from the reconstructed
        # canonical bytes instead.
        maps: Maps | None = None
        text_strings: TextStrings | None = None
        if authored is None:
            try:
                maps = load_maps(path, catalog)
            except MapEntryProfileError:
                maps = None
            try:
                text_strings = load_text_strings(path, catalog)
            except TextProfileError:
                text_strings = None
            except TextTableError as exc:
                raise SessionError(f"could not load semantic text content: {exc}") from exc

        self.profile = match_profile
        self.identification = identification if authored is None else None
        self.authored = authored
        self.atlas = atlas
        self.decoded_text = decoded_text
        self.maps = maps
        self.text_strings = text_strings
        self.selected_map = None
        self.rom_path = path
        self.rom_image = rom_image
        # Drop the prior ROM's sprite corpus; the next `sprites` read rebuilds it.
        self._sprites = None
        self._sprites_loaded = False
        # A newly opened base changes what any existing project result represents.
        self.validation_revision = None
        self.build_revision = None
        self.last_build = None

    def _verify_derivative(self, path: Path) -> AuthoredRom | None:
        """Prove a non-canonical image is a DragonByte Z derivative, or say why not."""
        try:
            return verify_authored_rom(path)
        except ProvenanceError as exc:
            self.provenance_error = str(exc)
            return None
