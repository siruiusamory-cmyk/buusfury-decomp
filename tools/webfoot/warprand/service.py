"""WARPRAND-APP-001 - the application boundary for the warp randomizer.

This module is the **only** thing the standalone *Buu's Fury Warp Randomizer*
application is allowed to call. It contains no randomization logic of its own:
every destination, arrival, facing, permutation and refusal is decided by
:mod:`tools.webfoot.warp_randomizer` and the transition authority beneath it, and
this file only answers the questions a *product* has to answer around that core:

* which image is supported, and is the file the user picked that image?
* what is this run's output called, and what is its manifest called?
* is the requested write safe - never the input, never an unconfirmed clobber?
* what does the finished run report, in the shape a status line needs?

Why a separate boundary rather than the core's own driver
=========================================================

The core already ships ``emit_randomized_rom``, which writes a derivative and a
manifest. It is deliberately *not* used here, for one measured reason: its
manifest is the randomizer's own record and carries no product identity, while
the artefact a user receives has to name the tool and its version so that a
shared ROM can be traced back to the build that produced it. Writing the
product's manifest here - while still building the image through the core's
:func:`~tools.webfoot.warp_randomizer.plan_warp_randomization` and the one writer
:func:`~tools.webfoot.write.emit_image` - keeps the algorithm in exactly one
place and the product metadata in exactly one place.

The core manifest is embedded verbatim under ``randomizer``, so the product
manifest is a superset of it rather than a second, divergent record.

Determinism
===========

A seed is the *exact* string the user typed; nothing here normalizes, trims or
case-folds it on its way to the core, and the core re-derives its permutation
from SHA-256 rather than from a process-randomized hash. The manifest records
the seed verbatim and never an absolute path - only the output's own basename -
so the same input image, tool version, seed and output name produce
byte-identical manifest text anywhere. :func:`sanitize_seed_for_filename`
changes only the *file name*, never the seed the algorithm sees; the two are
separate arguments on purpose and the tests pin the separation.

Source-ROM safety
=================

The selected image is an input on every path and an output on none:

* the output may not be the input, under any spelling, symlink or hard link;
* an existing output is never replaced without an explicit ``overwrite=True``;
* an existing output that is itself a copy of the canonical image is refused
  even then, because replacing it would destroy a clean ROM;
* the input is re-identified after the write and the run fails closed if its
  SHA-256 moved.

Nothing here touches the capability registry. This is a side utility: it ships
an offline artefact and moves no DragonByte Z capability count.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import secrets
from typing import Callable, Mapping

from .. import capability
from ..cli import load_catalog
from ..gba_header import GbaHeaderError
from ..profile import RomProfile, RomProfileCatalog, VerificationStatus
from ..rom import RomIdentification, RomReadError, identify_rom
from ..warp_randomizer import (
    POLICY_ID,
    SEED_DOMAIN,
    WarpRandomization,
    WarpRandomizerError,
    WarpRandomizerSeedError,
    normalize_seed,
    plan_warp_randomization,
)
from ..write import WriteError, WriteManifest, emit_image, paths_are_the_same_file

# --- product identity --------------------------------------------------------

#: The shipped product name. The window title, the manifest and the release
#: notes all read this one string; a second spelling would be a second product.
TOOL_NAME = "Buu's Fury Warp Randomizer"

#: The product version. It belongs in the manifest beside the policy id, because
#: a seed alone does not identify a mapping: the same seed under a new tool
#: version may legitimately produce a different layout, and only the version
#: pair makes that visible rather than silent.
TOOL_VERSION = "0.1.0"

#: The v0.1.0 launch seed. Named as a constant so the window's initial text and
#: the focused tests read the same value instead of agreeing by coincidence.
DEFAULT_SEED = "Goku"

#: The default output name, beside the selected image. ``{seed}`` receives the
#: *filename-safe* seed, never the algorithm seed.
OUTPUT_TEMPLATE = "Buu's Fury - Warp Randomized - {seed}.gba"

#: The manifest that travels with the output ROM.
MANIFEST_SUFFIX = ".manifest.json"

#: The limitation this product does not hide. It is shown in the window and
#: recorded in the manifest, because a shared artifact should carry the caveat
#: even when the window that made it is long gone.
PROGRESSION_DISCLAIMER = (
    "Randomized warps may make the game impossible to complete. Progression, "
    "reachability and beatability are not guaranteed."
)

#: The manifest schema this module writes.
MANIFEST_SCHEMA_VERSION = 1

#: The real phases of one run, in order, for a progress display.
#:
#: These are the boundaries this module actually crosses, not a decorative
#: animation: each entry is reported immediately *before* the work it names
#: begins, so a bar built on them can only ever understate progress, never claim
#: work that has not happened. The steps are unevenly expensive - randomizing
#: 735 transitions dominates - which is why the label, not the percentage, is
#: what tells the user where the run is.
PROGRESS_STEPS: tuple[str, ...] = (
    "Verifying the ROM",
    "Randomizing warp destinations",
    "Writing the randomized ROM",
    "Verifying the source ROM and writing the manifest",
)

#: ``on_progress(step, total, label)``, step being 1-based.
ProgressCallback = Callable[[int, int, str], None]

#: The randomization policies this product ships. Exactly one, and the boundary
#: **refuses** anything else rather than ignoring it: a policy argument that was
#: silently dropped would produce a `/3` mapping under a caller's `/4` label.
SUPPORTED_POLICIES: tuple[str, ...] = (POLICY_ID,)

#: The user-facing refusal for an image this version cannot randomize.
UNSUPPORTED_ROM_HEADLINE = (
    "This version currently supports the verified US Buu's Fury ROM only."
)

#: Filename safety, not seed policy. See :func:`sanitize_seed_for_filename`.
MAX_SEED_FILENAME_CHARACTERS = 64
FALLBACK_SEED_FILENAME = "seed"

#: Short, shareable random-seed labels - `<Word>-<4 digits>`.
SEED_WORDS: tuple[str, ...] = (
    "Saiyan",
    "Capsule",
    "Kame",
    "Dragon",
    "Namek",
    "Zenkai",
    "Scouter",
    "Senzu",
    "Kaioken",
    "Fusion",
    "Korin",
    "Baba",
    "Snake",
    "Turtle",
    "Pilaf",
    "Ox",
)


# --- refusals ----------------------------------------------------------------


class WarpRandomizerAppError(ValueError):
    """Base error for the application boundary. Message is user-facing."""


class UnsupportedRomError(WarpRandomizerAppError):
    """The selected file is not the verified supported image."""


class OutputAlreadyExistsError(WarpRandomizerAppError):
    """The output or its manifest already exists and was not confirmed."""


class OutputPathRefusedError(WarpRandomizerAppError):
    """The requested output location cannot be written, or is not allowed."""


class SeedRefusedError(WarpRandomizerAppError):
    """The seed is one the core cannot use."""


class SourceChangedError(WarpRandomizerAppError):
    """The input image changed during the run; the run fails closed."""


class ManifestWriteError(WarpRandomizerAppError):
    """The ROM was written but its manifest could not be."""


# --- small pure helpers ------------------------------------------------------


def shorten_hash(value: str) -> str:
    """``940AD5F0...F059E`` - the form a user can compare by eye.

    A 64-character digest in a status line is unreadable and unmemorable; the
    first eight and last five characters are enough to confirm two hashes are
    the same at a glance while the full value stays in the manifest.
    """
    text = str(value)
    if len(text) <= 16:
        return text.upper()
    return f"{text[:8].upper()}...{text[-5:].upper()}"


def _filename_safe(character: str) -> str:
    """Keep letters, digits, space, hyphen and underscore; blank the rest."""
    if character.isalnum() or character in " _-":
        return character
    return " "


def sanitize_seed_for_filename(seed: str, *, fallback: str = FALLBACK_SEED_FILENAME) -> str:
    """A deterministic, filename-safe rendering of ``seed``.

    The *algorithm* seed is never touched - this exists only so the default
    output name cannot contain a Windows path separator, a reserved character or
    a trailing dot. Letters and digits survive in every script (``isalnum`` is
    Unicode-aware), so a non-Latin seed still names its own file instead of
    collapsing to the fallback; only punctuation and symbols are folded to
    spaces, and the result is collapsed, trimmed and length-capped.

    ``"Goku: SSJ3?!"`` therefore becomes ``"Goku SSJ3"`` - the exact shape the
    ticket asks for - while the seed handed to the algorithm stays
    ``"Goku: SSJ3?!"``.
    """
    text = "".join(_filename_safe(character) for character in str(seed))
    text = " ".join(text.split())
    text = text.rstrip(". ")
    if len(text) > MAX_SEED_FILENAME_CHARACTERS:
        text = text[:MAX_SEED_FILENAME_CHARACTERS].strip().rstrip(". ")
    return text or fallback


def default_output_path(rom_path: str | Path, seed: str) -> Path:
    """``<ROM folder>/Buu's Fury - Warp Randomized - <safe seed>.gba``.

    Beside the selected image, which is where a user who just picked a ROM
    expects the result, and never a repository-internal build directory: the app
    is shipped to people who have no checkout.
    """
    directory = Path(rom_path).parent
    name = OUTPUT_TEMPLATE.format(seed=sanitize_seed_for_filename(seed))
    return directory / name


def default_manifest_path(output_rom: str | Path) -> Path:
    """``<output stem>.manifest.json``, beside the output image."""
    output = Path(output_rom)
    return output.with_name(output.stem + MANIFEST_SUFFIX)


def random_seed() -> str:
    """A short, copyable, legal seed: ``Saiyan-4821``.

    Drawn from :mod:`secrets` rather than :mod:`random` so two windows opened in
    the same second cannot agree, and shaped as a word plus four digits so it can
    be read out loud, typed and shared. It is a *label generator*, not part of
    the deterministic path: whatever it returns is then used verbatim as an
    ordinary seed.
    """
    word = SEED_WORDS[secrets.randbelow(len(SEED_WORDS))]
    return f"{word}-{secrets.randbelow(10000):04d}"


# --- the ROM check -----------------------------------------------------------

#: The two states a selected file can be in.
VERIFIED = "verified"
UNSUPPORTED = "unsupported"


@dataclass(frozen=True, slots=True)
class RomVerification:
    """What the selected file is, and whether this version supports it.

    ``problem`` is empty exactly when the file is supported, and is otherwise
    the sentence the window shows - there is no separate "error code" for the
    GUI to translate, because a translation table is one more place for the
    user-facing text to drift from the check that produced it.
    """

    path: Path
    status: str
    size: int | None
    sha256: str | None
    expected_size: int
    expected_sha256: str
    problem: str = ""

    @property
    def ok(self) -> bool:
        return self.status == VERIFIED

    @property
    def headline(self) -> str:
        """A one-line summary for the window's verification label."""
        if self.ok:
            return "Verified supported ROM \u2713"
        return "Unsupported ROM \u2717"

    def expected_sha256_short(self) -> str:
        return shorten_hash(self.expected_sha256)

    def actual_sha256_short(self) -> str | None:
        return shorten_hash(self.sha256) if self.sha256 else None


# --- the result --------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class RandomizationOutcome:
    """One finished run, in the shape a status report and a manifest need.

    Every count is the core's own reported value, carried through untouched. The
    window displays these and never a hard-coded expectation, which is what stops
    a policy change from leaving a stale number on screen.
    """

    seed: str
    policy_id: str
    tool_version: str
    supported: int
    randomized: int
    destinations_moved: int
    skipped: int
    skipped_reasons: Mapping[str, int]
    class_counts: Mapping[str, int]
    output_path: Path
    output_sha256: str
    output_size: int
    manifest_path: Path
    changed_byte_count: int
    source_sha256: str
    source_unchanged: bool
    randomizer_manifest: Mapping

    def short_output_sha256(self) -> str:
        return shorten_hash(self.output_sha256)

    def status_lines(self) -> list[str]:
        """The success text, in the order the ticket specifies."""
        return [
            "Success",
            f"Seed: {self.seed}",
            f"Randomized: {self.randomized}",
            f"Skipped: {self.skipped}",
            f"Output: {self.output_path}",
            f"SHA-256: {self.output_sha256}",
        ]


# --- the boundary ------------------------------------------------------------


class WarpRandomizerService:
    """The application boundary. GUI-free, so it is testable without Qt.

    One instance owns one ROM profile catalog, loaded once. The catalog is the
    authority for *which* image is supported: the expected size and SHA-256 in
    every refusal come out of the verified profile rather than from a literal in
    this file, so a profile change cannot leave the app checking yesterday's
    image.
    """

    def __init__(
        self,
        *,
        catalog: RomProfileCatalog | None = None,
        supported_profile: RomProfile | None = None,
        policy_id: str = POLICY_ID,
        tool_version: str = TOOL_VERSION,
    ) -> None:
        self._catalog = catalog
        self._supported_profile = supported_profile
        self.policy_id = policy_id
        self.tool_version = tool_version

    # --- catalog ---------------------------------------------------------

    @property
    def catalog(self) -> RomProfileCatalog:
        if self._catalog is None:
            self._catalog = load_catalog(None)
        return self._catalog

    # --- supported image -------------------------------------------------

    def supported_profile(self) -> RomProfile:
        """The one profile this product randomizes.

        Resolved from the catalog by the packaged profile id - the same
        authority the ROM-addressed readers use - so every "expected" value in a
        refusal is read from verified profile data rather than restated here. It
        is injectable so the boundary's own tests can drive a synthetic image
        without a private ROM, exactly as the profile contract intends.
        """
        if self._supported_profile is None:
            from ..packaged import packaged_profile

            self._supported_profile = packaged_profile()
        return self._supported_profile

    # --- seed ------------------------------------------------------------

    def normalize_seed(self, seed: str | int) -> str:
        """The exact seed string, or a friendly refusal.

        Delegates to the core so there is one definition of "a usable seed"; the
        boundary only changes the *error type* into one the window can present
        without importing core exceptions.
        """
        try:
            return normalize_seed(seed)
        except WarpRandomizerSeedError as exc:
            raise SeedRefusedError(str(exc)) from exc

    def generate_seed(self) -> str:
        return random_seed()

    # --- verification ----------------------------------------------------

    def _identify(self, path: str | Path) -> tuple[RomIdentification | None, str]:
        """Identify ``path``, or return ``(None, problem)`` for a user error.

        Three distinct failure families, and all three are ordinary user input
        rather than defects, so all three are turned into a sentence here:

        * ``RomReadError`` - the file is missing, is a directory, or changed
          while it was being read;
        * ``GbaHeaderError`` - the file is too short to carry a GBA header, or
          its header text fields are not ASCII. A user who picks a text file, a
          save, a savestate or an empty file out of the dialog's "All files"
          filter lands here, and it is the *common* case for a wrong pick;
        * ``OSError`` - a permission denial or a vanished drive.

        ``GbaHeaderError`` is a ``ValueError`` raised out of
        :func:`tools.webfoot.rom.identify_rom`, and it was initially uncaught,
        which broke this module's "never raises" contract: the window then kept
        the *previous* file's "Verified supported ROM" verdict on screen for a
        file that is not a ROM at all, with Randomize enabled. It is caught
        explicitly rather than as a bare ``ValueError`` so a genuine programmer
        error still escapes to the crash surface.
        """
        try:
            identification = identify_rom(Path(path), self.catalog)
        except GbaHeaderError as exc:
            return None, f"The selected file is not a Game Boy Advance ROM: {exc}"
        except RomReadError as exc:
            return None, f"The selected file could not be read: {exc}"
        except OSError as exc:  # a permission denial, a vanished drive
            return None, f"The selected file could not be read: {exc}"
        return identification, ""

    def verify_rom(self, path: str | Path) -> RomVerification:
        """Check a selected file against the supported image. Never raises.

        Called the moment a file is chosen, so the window can say "unsupported"
        before the user presses anything. The size is reported before the hash
        because "this file is 4,194,304 bytes" is actionable and "the hash does
        not match" is not.
        """
        return self._inspect(path)[0]

    def _inspect(
        self, path: str | Path
    ) -> tuple[RomVerification, RomIdentification | None]:
        """The verification *and* the identification, from one hash pass.

        The run needs both - the verdict to refuse early, the identification to
        reach the matched profile - and re-identifying would hash the image a
        second time for no extra evidence. ``None`` for the identification means
        the file could not be read at all.
        """
        profile = self.supported_profile()
        empty = dict(
            path=Path(path),
            expected_size=profile.size,
            expected_sha256=profile.sha256,
            size=None,
            sha256=None,
        )
        # An empty *string* is checked before ``Path()`` sees it: ``Path("")`` is
        # ``Path(".")``, which would otherwise be reported as "a folder, not a
        # file" - a true statement about the wrong thing. A ``Path("")`` passed
        # in directly is indistinguishable from ``Path(".")`` by the time it
        # arrives, and correctly reports the folder.
        if isinstance(path, str) and not path.strip():
            return RomVerification(
                status=UNSUPPORTED, problem="Choose a ROM file first.", **empty
            ), None
        identification, problem = self._identify(path)
        if identification is None:
            return RomVerification(status=UNSUPPORTED, problem=problem, **empty), None

        actual_size = identification.size
        actual_sha256 = identification.hashes.sha256
        common = dict(
            path=Path(path),
            expected_size=profile.size,
            expected_sha256=profile.sha256,
            size=actual_size,
            sha256=actual_sha256,
        )
        if actual_size != profile.size:
            return RomVerification(
                status=UNSUPPORTED,
                problem=(
                    f"{UNSUPPORTED_ROM_HEADLINE} This file is {actual_size:,} bytes; "
                    f"the supported image is {profile.size:,} bytes. Expected "
                    f"SHA-256: {shorten_hash(profile.sha256)}"
                ),
                **common,
            ), identification
        if actual_sha256 != profile.sha256:
            return RomVerification(
                status=UNSUPPORTED,
                problem=(
                    f"{UNSUPPORTED_ROM_HEADLINE} This file's SHA-256 is "
                    f"{shorten_hash(actual_sha256)}. Expected SHA-256: "
                    f"{shorten_hash(profile.sha256)}"
                ),
                **common,
            ), identification
        match = identification.profile_match
        if match.status is not VerificationStatus.VERIFIED or match.profile is None:
            # The digest matched a configured identity but its metadata did not,
            # or nothing matched at all. Either way the image is not supported.
            detail = "; ".join(match.mismatches) or match.reason
            return RomVerification(
                status=UNSUPPORTED,
                problem=f"{UNSUPPORTED_ROM_HEADLINE} {detail}",
                **common,
            ), identification
        return RomVerification(status=VERIFIED, problem="", **common), identification

    # --- naming ----------------------------------------------------------

    def default_output_path(self, rom_path: str | Path, seed: str) -> Path:
        return default_output_path(rom_path, seed)

    def manifest_path_for(self, output_rom: str | Path) -> Path:
        return default_manifest_path(output_rom)

    def output_is_the_input(self, source_rom: str | Path, output_rom: str | Path) -> bool:
        """Whether the requested output *is* the input, by filesystem identity.

        Exposed for the window, which blocks the run before it starts rather than
        after a refusal comes back from a worker thread. It is the same
        predicate the refusal uses - ``webfoot.write`` documents this exact use
        ("a GUI enabling a button, a report") - so the button and the refusal
        cannot disagree.
        """
        return paths_are_the_same_file(source_rom, output_rom)

    # --- the run ---------------------------------------------------------

    def randomize_warps(
        self,
        source_rom: str | Path,
        output_rom: str | Path,
        seed: str | int = DEFAULT_SEED,
        *,
        policy: str = POLICY_ID,
        overwrite: bool = False,
        on_progress: "ProgressCallback | None" = None,
    ) -> RandomizationOutcome:
        """Randomize ``source_rom`` into ``output_rom`` and record the run.

        The signature the ticket names, and the whole surface the window uses.

        Ordering is a safety property here, not a style choice. The path-level
        rules run first - is the output the input under some spelling, is the
        folder writable - because they are cheap, total, and the same ordering
        ``webfoot.write.emit_image`` uses: the input path also exists, so the
        alias check has to run before the overwrite policy or writing over the
        input would raise the wrong rule and name the wrong fix.

        The destructive step is deliberately **last**. Confirming an overwrite
        deletes the previous output and its manifest, and that must not happen
        until the run is certain to produce a replacement - so the input is
        verified, the image is read, and the whole mapping is planned *before*
        anything is removed. An earlier ordering cleared the destination in the
        path phase and could therefore destroy a user's previous randomized ROM
        and then refuse the run on account of a bad input.

        ``policy`` is validated and refused when unknown - it is not a knob.
        Only :data:`SUPPORTED_POLICIES` may be passed, and the window offers no
        control for it.

        ``on_progress`` is optional and called with ``(step, total, label)`` as
        each entry of :data:`PROGRESS_STEPS` is **entered**, from whatever thread
        is running this call. ``step`` is therefore the phase now beginning and
        ``step - 1`` phases are complete: a bar fed from these reports shows
        ``step - 1`` and can never claim work that has not finished. It exists so
        a window can show real progress without the core growing a callback it
        does not need; a caller that passes nothing pays nothing.
        """
        total_steps = len(PROGRESS_STEPS)

        def report(step: int) -> None:
            if on_progress is not None:
                on_progress(step, total_steps, PROGRESS_STEPS[step - 1])

        if policy not in SUPPORTED_POLICIES:
            raise WarpRandomizerAppError(
                f"unsupported randomization policy {policy!r}; this version "
                f"supports only {', '.join(SUPPORTED_POLICIES)}"
            )
        text = self.normalize_seed(seed)
        expected = self.supported_profile()

        source = Path(source_rom)
        output = Path(output_rom)
        if not str(output).strip():
            raise OutputPathRefusedError("Choose an output file name.")

        # --- phase A: is this write request legal? (nothing is written yet) ---

        # The input is read-only on every path, including a hard-link or
        # symlink alias of it, which only a filesystem identity check catches.
        if paths_are_the_same_file(source, output):
            raise OutputPathRefusedError(
                "The output file is the input ROM. Choose a different output "
                "name; this tool never writes to the ROM you selected."
            )

        manifest_path = default_manifest_path(output)
        for other, label in ((source, "the input ROM"), (output, "the output ROM")):
            if paths_are_the_same_file(manifest_path, other):
                raise OutputPathRefusedError(
                    f"The manifest would overwrite {label}: {manifest_path}. "
                    "Choose a different output name."
                )

        parent = output.parent if str(output.parent) else Path(".")
        try:
            parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise OutputPathRefusedError(
                f"The output folder could not be created: {parent} ({exc})"
            ) from exc
        if not os.access(parent, os.W_OK):
            raise OutputPathRefusedError(f"The output folder is not writable: {parent}")

        # A collision is *detected and refused* here so the cheapest answer wins,
        # but nothing is destroyed yet: the unlink waits until the replacement is
        # known to be producible (see the point of no return below).
        occupied = [path for path in (output, manifest_path) if path.exists()]
        if occupied:
            if not overwrite:
                raise OutputAlreadyExistsError(
                    f"{output.name} already exists in {parent}. Choose another name, "
                    "or confirm that you want to replace it."
                )
            # Refused even with the overwrite confirmed: replacing a copy of the
            # verified image would destroy a clean ROM, the one file this tool
            # exists to protect. Checked here, early, so the refusal is cheap.
            for path in occupied:
                if self._is_canonical_copy(
                    path,
                    expected_sha256=expected.sha256 or "",
                    expected_size=expected.size,
                ):
                    raise OutputPathRefusedError(
                        f"{path} is a copy of the verified ROM, so it is not "
                        "replaced. Choose a different output name."
                    )

        # --- phase B: is the input the supported image? ---

        report(1)
        verification, identification = self._inspect(source)
        if not verification.ok or identification is None:
            raise UnsupportedRomError(verification.problem)

        profile = self._profile_for(identification)
        try:
            image = source.read_bytes()
        except OSError as exc:
            raise UnsupportedRomError(
                f"The selected file could not be read: {exc}"
            ) from exc

        report(2)
        try:
            randomization = plan_warp_randomization(image, profile, text)
        except WarpRandomizerError as exc:
            raise WarpRandomizerAppError(
                f"The randomizer refused this run: {exc}"
            ) from exc

        # --- the point of no return: the run is known to be producible ---

        # Only now may a confirmed overwrite remove the previous artefacts. The
        # canonical-copy guard already ran in the path phase; what is left is the
        # deletion, which must not happen a moment before a replacement exists.
        self._remove_existing(output, manifest_path, overwrite=overwrite)

        report(3)
        try:
            # The one writer, with no sidecar of its own: this product publishes
            # exactly the ROM and the manifest beside it.
            write_manifest = emit_image(source, output, randomization.write_plan)
        except (WriteError, OSError) as exc:
            raise OutputPathRefusedError(
                f"The randomized ROM could not be written: {exc}"
            ) from exc

        report(4)
        after, _ = self._identify(source)
        source_unchanged = (
            after is not None and after.hashes.sha256 == verification.sha256
        )
        if not source_unchanged:
            raise SourceChangedError(
                "The selected ROM changed while it was being randomized, so the "
                f"output was not accepted. Delete {output} and try again with a "
                "ROM that is not being modified."
            )

        document = self._manifest_document(
            seed=text,
            verification=verification,
            profile=profile,
            randomization=randomization,
            write_manifest=write_manifest,
            output=output,
        )
        try:
            manifest_path.write_text(
                json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        except OSError as exc:
            raise ManifestWriteError(
                f"The randomized ROM was created at {output}, but its manifest "
                f"could not be written to {manifest_path} ({exc})."
            ) from exc

        summary = randomization.manifest.summary(
            output_sha256=write_manifest.output_sha256
        )
        return RandomizationOutcome(
            seed=text,
            policy_id=self.policy_id,
            tool_version=self.tool_version,
            supported=summary["supported_transitions"],
            randomized=summary["randomized"],
            destinations_moved=summary["destinations_changed"],
            skipped=summary["skipped"],
            skipped_reasons=dict(summary["skipped_by_reason"]),
            class_counts=dict(summary["class_counts"]),
            output_path=output,
            output_sha256=write_manifest.output_sha256,
            output_size=write_manifest.output_size,
            manifest_path=manifest_path,
            changed_byte_count=write_manifest.to_json()["changed_byte_count"],
            source_sha256=verification.sha256 or "",
            source_unchanged=source_unchanged,
            randomizer_manifest=document["randomizer"],
        )

    # --- internals -------------------------------------------------------

    def _profile_for(self, identification: RomIdentification) -> RomProfile:
        """The verified profile of an already-identified image.

        The same capability gate the core's own driver applies, so this product
        cannot randomize a profile the toolkit would refuse to read: a wrong ROM
        fails here for the same reason it fails there, not for a second,
        app-local reason that could drift.
        """
        profile = identification.profile_match.profile
        if profile is None:
            raise UnsupportedRomError(
                identification.profile_match.reason or UNSUPPORTED_ROM_HEADLINE
            )
        try:
            capability.require(
                identification,
                capability.Capability.MAP_ENTRIES,
                subsystem="warp randomization",
                error_type=WarpRandomizerAppError,
                check_header=True,
            )
        except WarpRandomizerAppError:
            raise
        except ValueError as exc:
            raise UnsupportedRomError(str(exc)) from exc
        return profile

    @staticmethod
    def _remove_existing(output: Path, manifest_path: Path, *, overwrite: bool) -> None:
        """Delete the artefacts a confirmed overwrite replaces.

        The only destructive step in this module, and it is called at the point of
        no return - after the input has been verified, the image read and the whole
        mapping planned - so it can only run when a replacement is certain to be
        producible. An earlier ordering deleted here *before* validating the input
        and could therefore destroy a user's previous randomized ROM and then
        refuse the run.

        Detection and refusal of the collision, including the canonical-copy
        guard, happens earlier in the path phase where it is cheap.
        """
        if not overwrite:
            return
        for path in (output, manifest_path):
            if not path.exists():
                continue
            try:
                path.unlink()
            except OSError as exc:
                raise OutputPathRefusedError(
                    f"The existing file {path} could not be replaced: {exc}"
                ) from exc

    @staticmethod
    def _is_canonical_copy(path: Path, *, expected_sha256: str, expected_size: int) -> bool:
        """Whether ``path`` hashes to the supported image."""
        if not expected_sha256:
            return False
        try:
            if path.stat().st_size != expected_size:
                return False
            digest = hashlib.sha256()
            with path.open("rb") as stream:
                for block in iter(lambda: stream.read(1 << 20), b""):
                    digest.update(block)
            return digest.hexdigest() == expected_sha256
        except OSError:
            return False

    def _manifest_document(
        self,
        *,
        seed: str,
        verification: RomVerification,
        profile: RomProfile,
        randomization: WarpRandomization,
        write_manifest: WriteManifest,
        output: Path,
    ) -> dict:
        """The product manifest: identity, provenance, counts, then the core's own.

        No absolute path appears anywhere in this document. The output contributes
        its basename only, so two runs of the same image, seed and output name in
        two different folders produce identical bytes - which is what lets a
        published manifest be compared with a locally produced one.
        """
        core = json.loads(
            randomization.manifest.to_json(
                output_sha256=write_manifest.output_sha256,
                output_size=write_manifest.output_size,
            )
        )
        summary = randomization.manifest.summary(
            output_sha256=write_manifest.output_sha256
        )
        return {
            "schema_version": MANIFEST_SCHEMA_VERSION,
            "tool": {"name": TOOL_NAME, "version": self.tool_version},
            "policy": self.policy_id,
            "policy_seed_domain": SEED_DOMAIN.decode("ascii"),
            "seed": seed,
            "input": {
                "profile": profile.id,
                "size": verification.size,
                "sha256": verification.sha256,
            },
            "output": {
                "filename": output.name,
                "size": write_manifest.output_size,
                "sha256": write_manifest.output_sha256,
                "changed_byte_count": write_manifest.to_json()["changed_byte_count"],
            },
            "counts": {
                "supported": summary["supported_transitions"],
                "randomized": summary["randomized"],
                "destinations_moved": summary["destinations_changed"],
                "destinations_unchanged": summary["destinations_unchanged"],
                "skipped": summary["skipped"],
            },
            "skipped_reasons": summary["skipped_by_reason"],
            "class_counts": summary["class_counts"],
            "forced_dead_end_links": summary["forced_dead_end_links"],
            "progression": PROGRESSION_DISCLAIMER,
            # The randomizer's own full record, verbatim: every transition row,
            # its retail and randomized bundle, its pair and its skip reason.
            "randomizer": core,
        }


# --- module-level conveniences ----------------------------------------------

_DEFAULT_SERVICE: WarpRandomizerService | None = None


def default_service() -> WarpRandomizerService:
    """The process-wide service. One catalog load for the whole application."""
    global _DEFAULT_SERVICE
    if _DEFAULT_SERVICE is None:
        _DEFAULT_SERVICE = WarpRandomizerService()
    return _DEFAULT_SERVICE


def verify_rom(path: str | Path) -> RomVerification:
    return default_service().verify_rom(path)


def randomize_warps(
    source_rom: str | Path,
    output_rom: str | Path,
    seed: str | int = DEFAULT_SEED,
    *,
    policy: str = POLICY_ID,
    overwrite: bool = False,
    on_progress: "ProgressCallback | None" = None,
) -> RandomizationOutcome:
    """``randomize_warps(source_rom, output_rom, seed, policy)``, standalone."""
    return default_service().randomize_warps(
        source_rom,
        output_rom,
        seed,
        policy=policy,
        overwrite=overwrite,
        on_progress=on_progress,
    )
