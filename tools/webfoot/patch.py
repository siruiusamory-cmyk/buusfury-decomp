"""Export a distributable patch for a project's build, and verify one.

This is the product behaviour around :mod:`tools.webfoot.formats.bps`. A creator
builds a modified ROM and has to be able to hand somebody a small file that
reproduces it, without handing over the commercial image the modification was made
against. The patch is that file: it carries the CRC-32 of the exact source image it
was made for, so an applier refuses any other image.

The patch is a difference, not a copy. Regions the build did not touch are re-read
from the source ROM on the other side of the patch, so a patch is a small fraction
of the image. The literal bytes it does carry are the bytes that differ and the
bytes a rebuild moved to a new offset, which is the same property every
difference-based patch format has: it helps somebody who already holds the source
build a modified image, and it cannot reconstruct the source on its own.

The three rules this module exists to enforce:

* **The source is verified, not merely supplied.** The profile catalog must
  recognise the image exactly; an unsupported or altered ROM is refused before
  anything is produced, with the reason stated.
* **The target is the project's own build, rebuilt here.** There is deliberately no
  option to patch a derivative the caller supplies. A built image that is older
  than the project it claims to come from cannot be detected from the image or its
  manifest - nothing in the format records the project revision - so accepting one
  would make "this patch reproduces the project" unprovable. Rebuilding is the only
  way the claim holds, and it also means the derivative lives in a private staging
  directory the caller cannot name, so no output path can alias it.
* **The patch is verified before success is reported.** The bytes are applied back
  in memory before they are published, and the published file is read from disk and
  applied again afterwards. A patch that does not rebuild the built image is not a
  patch, and reporting success without checking would make this the one code path
  in the toolkit that publishes an unverified artefact.

The patch metadata is a small deterministic JSON record. It is a pointer to the
provenance that already exists rather than a copy of it: the build manifest beside
the derivative holds the per-change detail, and duplicating that here would create
a second document that could disagree with the first.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import tempfile

from .build import BuildResult, build_project
from .catalog import RomProfileCatalog
from .formats.bps import (
    BpsError,
    BpsSourceError,
    apply as apply_bps,
    crc32,
    encode as encode_bps,
    inspect as inspect_bps,
)
from .profile import VerificationStatus
from .release_identity import build_identity, release_identity
from .rom import RomIdentification, identify_rom
from .write import ensure_new_destination, ensure_not_source_alias, publish_new_files

#: The metadata schema this module writes, and the highest it will read.
PATCH_METADATA_SCHEMA = 1


class PatchError(ValueError):
    """Base error for exporting or verifying a distributable patch."""


class PatchSourceError(PatchError):
    """The supplied source image is not a supported, exactly verified image."""


class PatchVerificationError(PatchError):
    """A patch does not rebuild the image it claims to describe."""


@dataclass(frozen=True, slots=True)
class PatchResult:
    """One exported patch and the identities it was made from."""

    patch_path: Path
    patch_sha256: str
    patch_size: int
    base_profile_id: str
    base_sha256: str
    base_size: int
    base_crc32: int
    target_sha256: str
    target_size: int
    target_crc32: int
    project_name: str
    metadata: bytes


@dataclass(frozen=True, slots=True)
class PatchVerification:
    """What a patch was proved to do, without writing anything."""

    patch_path: Path
    patch_sha256: str
    patch_size: int
    source_sha256: str
    source_size: int
    target_sha256: str
    target_size: int
    target_crc32: int
    metadata: bytes


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _withdraw(path: Path, digest: str) -> bool:
    """Remove the file this call published, and only while it is still that file.

    A published patch that fails its own verification must not be left behind for
    somebody to distribute. The digest guard is what keeps this from deleting a
    file another writer put there in the meantime. Returns whether the file is gone,
    so the refusal that follows can say what actually happened rather than assume
    the removal succeeded.
    """
    try:
        if path.is_file() and _digest(path.read_bytes()) == digest:
            path.unlink()
    except OSError:
        return not path.exists()
    return not path.exists()


def _raise_withdrawn(
    path: Path, digest: str, reason: str, cause: BaseException | None = None
) -> None:
    """Refuse, and say what actually happened to the artefact this call wrote."""
    removed = _withdraw(path, digest)
    if removed:
        state = f"{path} was removed rather than left as an artefact that cannot be applied"
    else:
        state = (
            f"{path} was not removed: the file there is no longer the one this run "
            "published, so it is not this run's to delete"
        )
    error = PatchVerificationError(f"the published patch {reason}; {state}")
    if cause is None:
        raise error
    raise error from cause


def require_verified_source(
    rom_path: str | Path, catalog: RomProfileCatalog
) -> RomIdentification:
    """Identify the source image and require it to be exactly the catalogued one.

    The single source gate for this module: verification is the profile catalog's
    answer, never a checksum invented here. A patch made against a near-miss image
    would apply to it and produce a ROM nobody can reproduce.
    """
    identification = identify_rom(rom_path, catalog)
    match = identification.profile_match
    if match.status is not VerificationStatus.VERIFIED or match.profile is None:
        raise PatchSourceError(
            f"a patch is exported only from an exactly verified source image; "
            f"{rom_path} is {match.status.value}, so no patch was produced"
        )
    return identification


def _read_verified_source(
    rom_path: str | Path, identification: RomIdentification
) -> bytes:
    """The source bytes, with the identity that was verified over them.

    The digest is recomputed over the bytes actually held, so a file that changed
    between identification and this read is refused rather than hashed into a patch
    that names an image it was not made from.
    """
    source = Path(rom_path).read_bytes()
    digest = _digest(source)
    if digest != identification.hashes.sha256:
        raise PatchSourceError(
            f"the source image changed while it was being read: {rom_path} verified "
            f"as sha256 {identification.hashes.sha256} and now reads {digest}"
        )
    return source


def patch_metadata(
    *,
    project_name: str,
    project_format_version: int,
    identification: RomIdentification,
    base_bytes: bytes,
    target_sha256: str,
    target_size: int,
    target_crc32: int,
) -> bytes:
    """The provenance a patch carries, as deterministic JSON.

    Deliberately free of paths, user names and timestamps: the patch is a public
    artefact, and two exports of the same project must produce the same file. The
    build identity is the commit this tool was built from - a fact about the
    producer, not a clock reading - so it does not break that property.
    """
    identity = release_identity()
    build = build_identity()
    document = {
        "schema_version": PATCH_METADATA_SCHEMA,
        "patch_format": "bps",
        "product": {"name": identity.product_name, "version": identity.version},
        "tool": {"commit": build.commit, "dirty": build.dirty},
        "project": {"name": project_name, "format_version": project_format_version},
        "base": {
            "profile_id": identification.profile_match.profile.id,
            "sha256": identification.hashes.sha256,
            "size": len(base_bytes),
            "crc32": f"{crc32(base_bytes):08x}",
        },
        "target": {
            "sha256": target_sha256,
            "size": target_size,
            "crc32": f"{target_crc32:08x}",
        },
    }
    return json.dumps(document, sort_keys=True, separators=(",", ":")).encode("utf-8")


def read_patch_metadata(patch: bytes) -> dict:
    """The provenance document a patch carries.

    A patch whose metadata is absent or is not a JSON object is refused: an
    artefact this module produced always has one, and treating a missing record as
    acceptable would let a stripped patch pass as a provenanced one. A patch from
    another tool carries its own metadata, which the format says may be anything,
    so this is the strict reader for our own record rather than the check that
    decides whether a patch may be applied.
    """
    try:
        header = inspect_bps(patch)
    except BpsError as exc:
        raise PatchVerificationError(str(exc)) from exc
    try:
        document = json.loads(header.metadata.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PatchVerificationError(
            f"the patch carries no readable provenance record: {exc}"
        ) from exc
    if not isinstance(document, dict):
        raise PatchVerificationError("the patch provenance record is not an object")
    schema = document.get("schema_version")
    if not isinstance(schema, int) or isinstance(schema, bool):
        raise PatchVerificationError(
            f"the patch provenance record has no integer schema version: {schema!r}"
        )
    if schema > PATCH_METADATA_SCHEMA:
        raise PatchVerificationError(
            f"the patch provenance record is schema {schema}, which is newer than "
            f"this toolkit understands ({PATCH_METADATA_SCHEMA})"
        )
    return document


def _named_digest(value: object) -> str | None:
    """One digest from a record, or a refusal when it is present and is not one."""
    if value is None:
        return None
    if not isinstance(value, str):
        raise PatchVerificationError(
            f"the patch provenance record names a sha256 that is not a string: "
            f"{value!r}"
        )
    return value


def _recorded_image_hashes(metadata: bytes) -> tuple[str | None, str | None] | None:
    """The image digests a provenance record names, or None when it names none.

    Deliberately tolerant about the *shape* of a record and deliberately independent
    of our schema version. A patch from another tool carries metadata the format
    allows to be anything, and refusing those would make the verifier useless for
    the patches a creator is most likely to be handed. What must never happen is
    the opposite: a record that DOES name digests, names the wrong ones, and is
    shown as if it were proved.
    """
    try:
        document = json.loads(metadata.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(document, dict):
        return None
    base = document.get("base")
    target = document.get("target")
    base_sha256 = _named_digest(base.get("sha256")) if isinstance(base, dict) else None
    target_sha256 = (
        _named_digest(target.get("sha256")) if isinstance(target, dict) else None
    )
    if base_sha256 is None and target_sha256 is None:
        return None
    return (base_sha256, target_sha256)


def export_patch(
    project_dir: str | Path,
    rom_path: str | Path,
    output_path: str | Path,
    catalog: RomProfileCatalog,
) -> PatchResult:
    """Build the project, then export the patch that reproduces that build.

    Nothing is written until the source is verified, the project has built, and the
    patch has been applied back in memory. See the module docstring for why the
    derivative is rebuilt here instead of being supplied by the caller.
    """
    output = Path(output_path)
    # The output-path policy is total and cheap, so it runs before anything is
    # read: a refused destination leaves the source ROM untouched and says which
    # rule it broke.
    ensure_not_source_alias(rom_path, output)
    ensure_new_destination(output)

    identification = require_verified_source(rom_path, catalog)

    with tempfile.TemporaryDirectory(prefix="webfoot-patch-") as staging:
        derivative = Path(staging) / "derivative.gba"
        build: BuildResult = build_project(
            project_dir, rom_path, derivative, catalog, manifest_path=None
        )
        target = derivative.read_bytes()
    provenance = build.manifest.project
    if provenance is None:
        # `build_project` always records it; if that ever changes, the patch must
        # not quietly ship without the project it came from.
        raise PatchError("the build recorded no project provenance")

    source = _read_verified_source(rom_path, identification)
    if source == target:
        raise PatchError(
            f"the project builds to an image identical to its base ROM, so there is "
            f"nothing to distribute: {output.name} would describe no modification"
        )

    target_crc32 = crc32(target)
    metadata = patch_metadata(
        project_name=provenance.name,
        project_format_version=provenance.format_version,
        identification=identification,
        base_bytes=source,
        target_sha256=_digest(target),
        target_size=len(target),
        target_crc32=target_crc32,
    )
    patch = encode_bps(source, target, metadata)

    if apply_bps(source, patch) != target:
        raise PatchVerificationError(
            "the encoded patch does not rebuild the image it was made from, so it "
            "was not published"
        )

    publish_new_files([(output, patch)])

    published_digest = _digest(patch)
    try:
        verification = verify_patch(output, rom_path, catalog)
        reproduced = verification.target_sha256 == _digest(target)
    except PatchError as error:
        _raise_withdrawn(
            output, published_digest, f"does not verify ({error})", cause=error
        )
    if not reproduced:
        _raise_withdrawn(output, published_digest, "does not rebuild the built image")

    return PatchResult(
        patch_path=output,
        patch_sha256=published_digest,
        patch_size=len(patch),
        base_profile_id=identification.profile_match.profile.id,
        base_sha256=identification.hashes.sha256,
        base_size=len(source),
        base_crc32=crc32(source),
        target_sha256=_digest(target),
        target_size=len(target),
        target_crc32=target_crc32,
        project_name=provenance.name,
        metadata=metadata,
    )


def verify_patch(
    patch_path: str | Path,
    rom_path: str | Path,
    catalog: RomProfileCatalog,
) -> PatchVerification:
    """Apply a patch to a source image and report what it reproduces.

    The whole verification path, and the one the export path calls after writing:
    the patch's own checksum, the source's identity, and a rebuild whose size and
    CRC-32 must match what the patch declares. Any disagreement is a refusal.
    """
    path = Path(patch_path)
    patch = path.read_bytes()
    try:
        header = inspect_bps(patch)
    except BpsError as exc:
        # The codec's errors are translated here so that every refusal this module
        # makes is a `PatchError`: a caller that catches the family, the command line
        # included, must not meet a bare codec error and print a traceback.
        raise PatchVerificationError(str(exc)) from exc
    identification = require_verified_source(rom_path, catalog)
    source = _read_verified_source(rom_path, identification)
    try:
        target = apply_bps(source, patch)
    except BpsSourceError as exc:
        raise PatchSourceError(str(exc)) from exc
    except BpsError as exc:
        raise PatchVerificationError(str(exc)) from exc

    # A provenance record that names different images than the ones just proved is
    # a lying record, and a distributed patch is only worth anything if its
    # provenance can be believed. A record that names no digests of ours is not a
    # refusal: verification is about the bytes, and the format lets a patch made
    # elsewhere carry anything at all.
    recorded = _recorded_image_hashes(header.metadata)
    if recorded is not None:
        base_sha256, target_sha256 = recorded
        if base_sha256 is not None and base_sha256 != identification.hashes.sha256:
            raise PatchVerificationError(
                f"the patch provenance record names source sha256 {base_sha256} and "
                f"this source is {identification.hashes.sha256}"
            )
        rebuilt = _digest(target)
        if target_sha256 is not None and target_sha256 != rebuilt:
            raise PatchVerificationError(
                f"the patch provenance record names target sha256 {target_sha256} "
                f"and the patch rebuilds {rebuilt}"
            )

    return PatchVerification(
        patch_path=path,
        patch_sha256=_digest(patch),
        patch_size=len(patch),
        source_sha256=identification.hashes.sha256,
        source_size=len(source),
        target_sha256=_digest(target),
        target_size=header.target_size,
        target_crc32=header.target_crc32,
        metadata=header.metadata,
    )
