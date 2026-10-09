"""Project-authored graphic pixels compiled into the one merged build plan.

GRAPHICS-IMPORT-BOUNDARY-001. This is the build domain that turns an authored
PNG in a project into attributed `ByteChange`s. It is the missing production
caller `ActorSprites.import_graphic_png` never had, and it is the only place in
the toolkit that decides where a re-encoded actor-sprite container goes.

**What a project authors.** A graphic's pixels are authored by editing the PNG
extraction wrote, at ``graphics/assets/graphic_NNNN.png``. That is the documented
workflow - ``extract``, edit the PNG, ``validate``, ``build`` - so nothing here
requires a registration step, a research command or a GUI: the extracted
``graphics/graphics.toml`` manifest records the digest of the file extraction
wrote, and a file whose digest no longer matches is an authored override. The
manifest is regenerated output, never authored source, so this adds no second
statement of anything the PNG already says.

**Two paths, one payload.** A re-encoded stream that fits the extent the original
container occupied is written where the payload already is: one `ByteChange`
covering exactly the bytes the re-encoded container needs, with the original
trailing bytes left untouched rather than rewritten. A stream that does not fit
goes through `webfoot.relocation.plan_relocation`, which is the ONE
growth-capable container operation: it allocates through `webfoot.allocation`,
re-encodes every dislodged reference, and emits the relocation and
generated-allocation provenance. This module supplies the payload, the reason
each move is legitimate, and the graphic that names each request; it owns no
allocator, no encoder and no second planning pass of its own.

**What may be rewritten, and what is not claimed.** Relocation rewrites the
references the graphics walk actually published: one CONFIRMED
``ABSOLUTE_ROM_U32_LE`` word per distinct frame piece that names the payload.
That set is not claimed to be every word in the image that equals the payload's
address - no word-aligned scan was run for one - so an undiscovered reference is
possible in principle. Two things keep that honest rather than dangerous:
the original payload bytes are deliberately left intact, so a reference this
toolkit did not find still points at the art it always pointed at; and any
CANDIDATE reference reaching the payload makes the whole graphic refuse to move,
because a partially rewritten consumer set is corruption rather than an
incomplete feature. The batch is atomic: `write.plan_changes` validates every
change before any byte is written, so a graphic either has all of its confirmed
consumers repointed or none of them.

**What the retail engine has and has not been shown to do.** The profile's
declared expansion maps file offset ``0x00800000`` to ``0x08800000`` inside the
Game Pak window, and a piece's ``+0x08`` word is a full 32-bit little-endian
address over all 11,005 canonical piece references, so the field can *encode* an
above-EOF placement. Whether the retail engine *decodes* a container it reaches
there is a runtime claim, owned by the mGBA proof recorded in
``docs/research/GRAPHICS_PIXEL_OVERRIDE.md``, and not by this module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path
from typing import Callable, Mapping

from .allocation import AllocationKind, DEFAULT_ADDRESSABILITY
from .formats import indexed_png
from .layout import AnchorId, OwnedRegion, ReferenceClass
from .project.format import ProjectFormatError, load_toml
from .project.model import (GRAPHICS_FILE, GraphicsOverrides, PixelOverride,
                            ProjectValidationError)
from .relocation import RelocationRequest, plan_relocation
from .write import ByteChange, GeneratedAllocationProvenance, RelocationProvenance

#: The allocation domain name recorded on every generated-allocation provenance
#: this module issues, and the owner prefix every `ByteChange` it emits carries.
DOMAIN = "graphics_authoring"

#: Containers are 4-byte aligned in the canonical corpus, and a piece's ``+0x08``
#: word is a word-aligned ROM address, so a relocated payload keeps that property.
ALIGNMENT = 4

#: The depth keys the manifest records, mapped back to the codec's predicate.
_BIT_DEPTHS = {4: False, 8: True}


class GraphicsAuthoringError(ProjectValidationError):
    """An authored graphic cannot be planned into the build's contract."""


class GraphicsManifestError(GraphicsAuthoringError):
    """The extracted graphics manifest is absent where required, or malformed."""


# --- the extracted manifest --------------------------------------------------


@dataclass(frozen=True)
class GraphicAsset:
    """One manifest row: where an asset's PNG is, and the baseline it was cut at.

    ``png_sha256`` is the digest of the PNG file extraction wrote and
    ``pixels_sha256`` the digest of the linear pixels it encoded. Both are
    optional so that a project extracted before this boundary still loads and
    still builds; absent, this module falls back to comparing the authored pixels
    against the base image's own decoded graphic, which is slower and equally
    correct. What is never done is treating an undecidable asset as unedited.
    """

    identity: str
    file: str
    width: int
    height: int
    colour_256: bool
    packed_size: int
    png_sha256: str | None = None
    pixels_sha256: str | None = None


@dataclass(frozen=True)
class GraphicsManifest:
    """The ROM-derived record of what extraction wrote, read back for a build."""

    profile_id: str
    transparent_index: int
    assets: Mapping[str, GraphicAsset] = field(default_factory=dict)

    @property
    def records_a_baseline(self) -> bool:
        """Whether every asset carries the digest a fast comparison needs."""
        return bool(self.assets) and all(
            asset.png_sha256 is not None for asset in self.assets.values()
        )


def read_graphics_manifest(project_dir: str | Path) -> GraphicsManifest | None:
    """Read ``graphics/graphics.toml``, or None when the project has none.

    A project extracted with ``--no-graphics`` has no manifest and therefore
    authors no pixels, which is the same authoring reach the flag already costs.
    Malformed content is refused rather than skipped: a manifest that cannot be
    read is not the same thing as an author who changed nothing.
    """
    path = Path(project_dir) / GRAPHICS_FILE
    if not path.is_file():
        return None
    try:
        document = load_toml(path.read_text(encoding="utf-8"))
    except (ProjectFormatError, OSError) as exc:
        raise GraphicsManifestError(f"{GRAPHICS_FILE} cannot be read: {exc}") from exc
    header = document.get("graphics")
    table = document.get("asset")
    if not isinstance(header, Mapping) or not isinstance(table, Mapping) or not table:
        raise GraphicsManifestError(
            f"{GRAPHICS_FILE} has no [graphics] header or no [asset] table; "
            "re-extract the project to author graphics"
        )
    profile_id = header.get("profile_id")
    if not isinstance(profile_id, str) or not profile_id.strip():
        raise GraphicsManifestError(f"{GRAPHICS_FILE}: [graphics] names no profile_id")
    assets: dict[str, GraphicAsset] = {}
    for identity in sorted(table):
        entry = table[identity]
        if not isinstance(entry, Mapping):
            raise GraphicsManifestError(f"{GRAPHICS_FILE}: asset.{identity} must be a table")
        assets[identity] = _asset_from_document(identity, entry)
    return GraphicsManifest(
        profile_id=profile_id,
        transparent_index=int(header.get("transparent_index", 0)),
        assets=assets,
    )


def _asset_from_document(identity: str, entry: Mapping) -> GraphicAsset:
    try:
        file = entry["file"]
        width = entry["width"]
        height = entry["height"]
        bit_depth = entry["bit_depth"]
        packed_size = entry["packed_size"]
    except KeyError as exc:
        raise GraphicsManifestError(
            f"{GRAPHICS_FILE}: asset.{identity} is missing {exc.args[0]!r}"
        ) from exc
    if not isinstance(file, str) or not file.strip():
        raise GraphicsManifestError(f"{GRAPHICS_FILE}: asset.{identity}.file is not a path")
    colour_256 = _BIT_DEPTHS.get(bit_depth)
    if colour_256 is None:
        raise GraphicsManifestError(
            f"{GRAPHICS_FILE}: asset.{identity}.bit_depth is {bit_depth!r}, not 4 or 8"
        )
    for name, value in (("width", width), ("height", height), ("packed_size", packed_size)):
        if type(value) is not int or value <= 0:
            raise GraphicsManifestError(
                f"{GRAPHICS_FILE}: asset.{identity}.{name} is {value!r}, not a positive integer"
            )
    digests = {}
    for name in ("png_sha256", "pixels_sha256"):
        value = entry.get(name)
        if value is not None and (not isinstance(value, str) or len(value) != 64):
            raise GraphicsManifestError(
                f"{GRAPHICS_FILE}: asset.{identity}.{name} is not a sha256 digest"
            )
        digests[name] = value
    return GraphicAsset(
        identity=identity,
        file=file,
        width=width,
        height=height,
        colour_256=colour_256,
        packed_size=packed_size,
        png_sha256=digests["png_sha256"],
        pixels_sha256=digests["pixels_sha256"],
    )


# --- resolving authored pixels -----------------------------------------------


class CanonicalGraphics:
    """The base image's own decoded graphics, walked at most once, on demand.

    The corpus walk is the expensive half of this domain (about 14 s on the
    canonical image), and most builds author nothing, so it must not happen
    merely because a project has a graphics manifest. It happens when the
    resolution below actually needs the base pixels, or when the build needs the
    corpus anyway to plan a palette or pixel override.
    """

    def __init__(self, image: bytes, identification) -> None:
        self.image = image
        self.identification = identification
        self._sprites = None
        self._by_name: dict[str, object] | None = None

    @property
    def sprites(self):
        if self._sprites is None:
            from .graphics import load_actor_sprites

            self._sprites = load_actor_sprites(self.image, self.identification)
        return self._sprites

    def pixels_of(self, identity: str) -> bytes | None:
        """The base image's decoded pixels for one graphic, or None if unknown."""
        if self._by_name is None:
            self._by_name = {str(g.identity): g for g in self.sprites.graphics()}
        graphic = self._by_name.get(identity)
        return None if graphic is None else graphic.pixels


def resolve_pixel_overrides(
    project_dir: str | Path,
    manifest: GraphicsManifest | None,
    canonical_pixels: Callable[[str], bytes | None],
) -> dict[str, PixelOverride]:
    """The graphics a project authors, keyed by identity.

    This is the ONE derivation, shared by ``validate`` and ``build``, so the two
    cannot disagree about which graphics are authored. Its order of decisions is
    what keeps a normal build fast and a stale project correct:

    1. a project with no manifest authors no pixels;
    2. an asset's PNG whose recorded ``png_sha256`` still matches is untouched, and
       is decided by hashing a file rather than decoding it;
    3. otherwise the PNG is decoded and checked against the manifest's recorded
       dimensions and bit depth - a resized or re-depth-ed asset is refused here,
       naming the contract it violates;
    4. a decoded image whose ``pixels_sha256`` still matches is untouched - this is
       an editor that re-saved identical art, not an edit;
    5. otherwise the pixels are compared against the base image's own decoded
       graphic, because a project extracted before digests existed has no other
       baseline. Equal means untouched; different means authored.

    A PNG that cannot be decoded, or an asset whose file is missing, is a
    `GraphicsAuthoringError` naming the asset. Nothing is ever guessed.
    """
    if manifest is None or not manifest.assets:
        return {}
    root = Path(project_dir)
    resolved: dict[str, PixelOverride] = {}
    for identity in sorted(manifest.assets):
        asset = manifest.assets[identity]
        path = root / asset.file
        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise GraphicsAuthoringError(
                f"{identity}: the extracted manifest names {asset.file}, but the "
                f"project has no readable file there ({exc.strerror}); a build "
                "cannot tell an authored asset from a deleted one"
            ) from exc
        if asset.png_sha256 is not None and sha256(raw).hexdigest() == asset.png_sha256:
            continue
        pixels = _decode_asset(identity, asset, raw)
        if asset.pixels_sha256 is not None:
            if sha256(pixels).hexdigest() == asset.pixels_sha256:
                continue
        else:
            base = canonical_pixels(identity)
            if base is None:
                raise GraphicsAuthoringError(
                    f"{identity}: the project authors a PNG the base image has no "
                    "graphic for"
                )
            if base == pixels:
                continue
        resolved[identity] = PixelOverride(
            identity=identity,
            file=asset.file,
            pixels=pixels,
            width=asset.width,
            height=asset.height,
            colour_256=asset.colour_256,
        )
    return resolved


def _decode_asset(identity: str, asset: GraphicAsset, raw: bytes) -> bytes:
    """Decode one authored PNG, refusing anything this write path cannot keep."""
    try:
        pixels, width, height, _palette, _transparent = indexed_png.decode(raw)
    except indexed_png.PngError as exc:
        raise GraphicsAuthoringError(
            f"{identity}: {asset.file} is not an indexed PNG this toolkit can "
            f"read: {exc}. Import requires the same indexed PNG form "
            "`webfoot graphics export` writes; a truecolour or interlaced image "
            "is refused rather than quantised"
        ) from exc
    if (width, height) != (asset.width, asset.height):
        raise GraphicsAuthoringError(
            f"{identity}: {asset.file} is {width}x{height}, but the piece record "
            f"declares {asset.width}x{asset.height}; this write path does not "
            "resize, and resizing belongs to sprite authoring"
        )
    limit = 255 if asset.colour_256 else 15
    for index, value in enumerate(pixels):
        if value > limit:
            raise GraphicsAuthoringError(
                f"{identity}: {asset.file} uses index {value} at pixel {index}, "
                f"above the {limit} a {8 if asset.colour_256 else 4}bpp graphic "
                "can address; the retail decoder would truncate it"
            )
    return pixels


# --- planning ----------------------------------------------------------------


@dataclass(frozen=True)
class GraphicMaterialization:
    """Everything this domain contributes to the one merged build plan."""

    changes: tuple[ByteChange, ...] = ()
    reserved: tuple[OwnedRegion, ...] = ()
    generated_allocations: tuple[GeneratedAllocationProvenance, ...] = ()
    relocations: tuple[RelocationProvenance, ...] = ()


def plan_graphic_overrides(
    image: bytes,
    identification,
    overrides: Mapping[str, PixelOverride],
    *,
    reserved: tuple[OwnedRegion, ...] = (),
    sprites=None,
) -> GraphicMaterialization:
    """Compile authored pixels into `ByteChange`s. Pure; raises on any doubt.

    ``reserved`` is the build-scoped reservation set every allocating domain
    shares: the spans earlier domains already took are subtracted before this
    domain places anything, and the spans it places are returned for the domains
    after it. No free space is searched for here - the allocator decides, from
    the profile's own declarations, exactly as it does for every other domain.
    """
    if not overrides:
        return GraphicMaterialization()
    if sprites is None:
        from .graphics import load_actor_sprites

        sprites = load_actor_sprites(image, identification)
    profile = sprites.profile
    by_name = {str(graphic.identity): graphic for graphic in sprites.graphics()}
    document = sprites.reference_document()

    changes: list[ByteChange] = []
    requests: list[RelocationRequest] = []
    for identity in sorted(overrides):
        override = overrides[identity]
        graphic = by_name.get(identity)
        if graphic is None:
            raise GraphicsAuthoringError(
                f"{identity}: the project authors pixels for a graphic this ROM "
                "does not contain; the project and the base image disagree"
            )
        payload = sprites.encode_pixels(graphic.identity, override.pixels)
        owner = str(graphic.identity)
        if len(payload) <= graphic.packed_size:
            offset = graphic.file_offset
            changes.append(
                ByteChange(
                    offset=offset,
                    old=image[offset : offset + len(payload)],
                    new=payload,
                    owner=owner,
                    reason=(
                        f"authored pixels fit the {graphic.packed_size}-byte original "
                        f"container extent; {len(payload)} bytes written in place, "
                        "the original trailing bytes are left untouched"
                    ),
                )
            )
            continue
        anchor, consumers, payload = _relocation_candidate(
            document, identity, graphic, payload, image
        )
        requests.append(
            RelocationRequest(
                AnchorId(identity),
                payload,
                addressability=DEFAULT_ADDRESSABILITY[AllocationKind.GRAPHICS_CONTAINER],
                generated=(DOMAIN, identity,
                           min(reference.source.value for reference in consumers)),
            )
        )

    if not requests:
        return GraphicMaterialization(changes=tuple(changes))
    return _relocated(document, requests, changes, reserved)


def _relocated(document, requests, changes, reserved) -> GraphicMaterialization:
    """The relocation half, compiled by the ONE shared growth operation.

    ``relocation.plan_relocation`` is the general form of what this domain used
    to do in private: it allocates through the one allocator, encodes every
    dislodged reference against the image the placement was authorized against,
    records the placement as `relocation` provenance and authorizes an above-EOF
    span with `generated_allocations`. Nothing about a graphic is special to it
    except the request this function hands it.
    """
    result = plan_relocation(document, requests, reserved=reserved)
    return GraphicMaterialization(
        changes=tuple(changes) + result.plan.changes,
        reserved=tuple(OwnedRegion(a.range, a.request.owner) for a in result.allocations),
        generated_allocations=result.plan.generated_allocations,
        relocations=result.plan.relocations,
    )


def _relocation_candidate(document, identity: str, graphic, payload: bytes, image: bytes):
    """The confirmed consumer set for one graphic, or a refusal naming why not.

    A relocation is only legitimate when the reference graph has actually decoded
    every consumer of the payload. Three ways that can fail, and each is refused
    rather than worked around:

    * the published anchor's extent disagrees with the decoded container, so no
      placement can be justified from the graph;
    * the anchor is not published relocatable, which means the shared eligibility
      rule could not establish the payload's inbound surface;
    * nothing confirmed reaches it, so there is no owner to rewrite and moving it
      would silently orphan whatever really does reach it - this is also the shape
      an undiscovered reference takes;
    * a CANDIDATE reference reaches it, which is an unresolved numeric hit this
      toolkit will not rewrite and will not ignore.

    ``plan_relocation`` re-enforces the last three from the same graph; they are
    checked here as well so the accounting message names the graphic rather than
    the anchor.
    """
    anchor = document.anchor(AnchorId(identity))
    if anchor.range.size != graphic.packed_size:
        raise GraphicsAuthoringError(
            f"{identity}: the published anchor spans {anchor.range.size} bytes but the "
            f"decoded container extent is {graphic.packed_size}; the graph and the "
            "codec disagree, so no placement can be justified"
        )
    if not anchor.relocatable:
        raise GraphicsAuthoringError(
            f"{identity}: the re-encoded payload needs {len(payload)} bytes but its "
            f"original container extent is only {graphic.packed_size}, and this graphic "
            "is not published relocatable, so the build will not guess where else it "
            "could go"
        )
    consumers = tuple(
        reference
        for reference in document.references
        if reference.target == anchor.identity
    )
    if not consumers:
        raise GraphicsAuthoringError(
            f"{identity}: no confirmed reference reaches this payload, so a relocation "
            "has no consumer set to rewrite and is refused rather than orphaned"
        )
    for reference in consumers:
        if reference.classification is not ReferenceClass.CONFIRMED_REFERENCE:
            raise GraphicsAuthoringError(
                f"{identity}: reference at 0x{reference.source.value:08X} is a "
                f"{reference.classification.value}, not a confirmed reference; a "
                "partially decodable consumer set is refused rather than partially "
                "rewritten"
            )
    return anchor, consumers, payload


def graphics_overrides_with_pixels(
    project_dir: str | Path,
    overrides: GraphicsOverrides,
    manifest: GraphicsManifest | None,
    canonical_pixels: Callable[[str], bytes | None],
) -> GraphicsOverrides:
    """`overrides` with its derived pixel half filled in.

    The model's `pixels` field is the authored pixel state every caller reads;
    this is the one place it is derived, so a caller never has to know whether the
    state came from a digest comparison, a pixel comparison or a decode.
    """
    return GraphicsOverrides(
        palette=dict(overrides.palette),
        pixels=resolve_pixel_overrides(project_dir, manifest, canonical_pixels),
    )
