"""The application/service layer: one run, several modules, one safe write.

This is the layer the addendum calls for, and the only thing a window is allowed
to call. It contains no randomization logic of its own: every decision about which
enemy moves where, which stat is scaled and which door leads where belongs to the
module that owns it, and this file answers only the questions a *product* has to
answer around them:

* which image is supported, and is the file the user picked that image?
* what is this run's output called, and what are its companions called?
* is the requested write safe - never the input, never an unconfirmed clobber?
* do the enabled modules compose without writing the same byte?
* what does the finished run report, in the shape a status line needs?

The requested shape and the delivered shape
===========================================

:class:`RandomizerRequest` in, :class:`RandomizerResult` out. The window collects
one and displays the other; it decides nothing. That is what makes the whole
surface testable without Qt, and it is what makes the same run reachable from a
GUI, a test and a script.

Source-ROM safety
=================

The selected image is an input on every path and an output on none:

* the output may not be the input, under any spelling, symlink or hard link;
* the manifest and the spoiler may not alias the input, the output, or each other;
* an existing destination is never replaced without an explicit ``overwrite``;
* an existing destination that is itself a copy of the verified image is refused
  even then, because replacing it would destroy a clean ROM;
* the input is re-identified after the write and the run fails closed if its
  SHA-256 moved.

Composition is fail-closed
==========================

Every enabled module's changes go into ONE
:class:`~tools.webfoot.write.WritePlan`, built by
:func:`~tools.webfoot.write.plan_changes`, which refuses any two changes that
write the same byte. There is no "last module wins" resolution anywhere in this
file, and there cannot be: a plan that overlaps does not get built.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import os
from pathlib import Path
import secrets
from typing import Callable, Mapping

from ..catalog import load_catalog
from ..gba_header import GbaHeaderError
from ..profile import RomProfile, RomProfileCatalog, VerificationStatus
from ..rom import RomIdentification, RomReadError, identify_rom
from ..write import (
    OverlappingChangeError,
    WriteError,
    emit_image,
    paths_are_the_same_file,
    plan_changes,
)
from . import registry
from .context import RandomizerContext
from .errors import (
    ManifestWriteError,
    ModuleConflictError,
    ModuleRefusedError,
    OutputAlreadyExistsError,
    OutputPathRefusedError,
    SeedRefusedError,
    SourceChangedError,
    UnsupportedRomError,
)
from .manifest import build_manifest, canonical_json
from .module import ModulePlan
from .spoiler import build_spoiler

#: ``on_progress(step, total, label)``, step being 1-based.
ProgressCallback = Callable[[int, int, str], None]

#: The manifest that travels with the output ROM.
MANIFEST_SUFFIX = ".manifest.json"

#: The spoiler that may travel with it. Distinct from the manifest suffix so
#: neither can ever be mistaken for the other.
SPOILER_SUFFIX = ".spoiler.json"

#: The user-facing refusal for an image this build cannot randomize.
UNSUPPORTED_ROM_HEADLINE = (
    "This version currently supports the verified US Buu's Fury ROM only."
)

#: Filename safety, not seed policy. See :func:`sanitize_seed_for_filename`.
MAX_SEED_FILENAME_CHARACTERS = 64
FALLBACK_SEED_FILENAME = "seed"

#: Short, shareable random-seed labels - ``<Word>-<4 digits>``. One list for every
#: product, so the two executables cannot drift into generating different-looking
#: seeds.
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

#: The two states a selected file can be in.
VERIFIED = "verified"
UNSUPPORTED = "unsupported"


# --- small pure helpers ------------------------------------------------------


def shorten_hash(value: str) -> str:
    """``940AD5F0...F059E`` - the form a user can compare by eye."""
    text = str(value)
    if len(text) <= 16:
        return text.upper()
    return f"{text[:8].upper()}...{text[-5:].upper()}"


def _filename_safe(character: str) -> str:
    """Keep letters, digits, space, hyphen and underscore; blank the rest."""
    if character.isalnum() or character in " _-":
        return character
    return " "


def sanitize_seed_for_filename(
    seed: str, *, fallback: str = FALLBACK_SEED_FILENAME
) -> str:
    """A deterministic, filename-safe rendering of ``seed``.

    The *algorithm* seed is never touched - this exists only so the default
    output name cannot contain a Windows path separator, a reserved character or
    a trailing dot. Letters and digits survive in every script (``isalnum`` is
    Unicode-aware), so a non-Latin seed still names its own file.
    """
    text = "".join(_filename_safe(character) for character in str(seed))
    text = " ".join(text.split())
    text = text.rstrip(". ")
    if len(text) > MAX_SEED_FILENAME_CHARACTERS:
        text = text[:MAX_SEED_FILENAME_CHARACTERS].strip().rstrip(". ")
    return text or fallback


def default_output_path(rom_path: str | Path, seed: str, template: str) -> Path:
    """``<ROM folder>/<template with the safe seed>``.

    Beside the selected image, which is where a user who just picked a ROM
    expects the result, and never a repository-internal build directory: the app
    is shipped to people who have no checkout.
    """
    directory = Path(rom_path).parent
    return directory / template.format(seed=sanitize_seed_for_filename(seed))


def default_manifest_path(output_rom: str | Path) -> Path:
    """``<output stem>.manifest.json``, beside the output image."""
    output = Path(output_rom)
    return output.with_name(output.stem + MANIFEST_SUFFIX)


def default_spoiler_path(output_rom: str | Path) -> Path:
    """``<output stem>.spoiler.json``, beside the output image."""
    output = Path(output_rom)
    return output.with_name(output.stem + SPOILER_SUFFIX)


def random_seed() -> str:
    """A short, copyable, legal seed: ``Saiyan-4821``.

    Drawn from :mod:`secrets` rather than :mod:`random` so two windows opened in
    the same second cannot agree. It is a *label generator*, not part of the
    deterministic path: whatever it returns is then used verbatim as an ordinary
    seed.
    """
    word = SEED_WORDS[secrets.randbelow(len(SEED_WORDS))]
    return f"{word}-{secrets.randbelow(10000):04d}"


_COMMIT: str | None | bool = False
_DIRTY: bool | None | bool = False


def _git(*arguments: str) -> str | None:
    """Run one read-only git command in the package's directory.

    Started without a console window, because a windowed build that flashed a
    console on every run would be a worse defect than the provenance it was
    fetching.
    """
    import subprocess
    import sys

    creation_flags = 0
    if sys.platform == "win32":
        creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
    try:
        result = subprocess.run(
            ["git", *arguments],
            cwd=Path(__file__).resolve().parent,
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=creation_flags,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def repository_commit() -> str | None:
    """The checkout's commit, or ``None`` when there is no repository to ask.

    Read once and cached, because it is provenance for a manifest rather than an
    input to a run. A **packaged** build returns ``None`` without asking: a one-file
    executable has no checkout and no ``git``, so running the command there would
    either fail slowly or, worse, find some unrelated repository through the
    process's working directory and record a commit that did not produce the build.
    The manifest records the null honestly.

    It is deliberately not part of the reproducibility contract - a seed is
    identified by the tool version and the module algorithm versions, which are
    stated constants - so a missing commit is a gap in the record, not a refusal.
    """
    global _COMMIT
    if _COMMIT is not False:
        return _COMMIT  # type: ignore[return-value]
    import sys

    if getattr(sys, "frozen", False):
        _COMMIT = None
        return None
    text = _git("rev-parse", "HEAD")
    _COMMIT = text or None
    return _COMMIT  # type: ignore[return-value]


def repository_is_dirty() -> bool | None:
    """Whether the checkout had uncommitted changes when the run was planned.

    ``None`` when the question cannot be asked, which is the packaged case. The
    manifest records this beside the commit, because a commit recorded from a
    checkout with uncommitted changes names the commit the files were *based* on
    rather than the bytes that actually produced the build - and a reader
    comparing two manifests deserves to know which of those they are looking at.
    """
    global _DIRTY
    if _DIRTY is not False:
        return _DIRTY  # type: ignore[return-value]
    import sys

    if getattr(sys, "frozen", False):
        _DIRTY = None
        return None
    status = _git("status", "--porcelain")
    _DIRTY = None if status is None else bool(status)
    return _DIRTY  # type: ignore[return-value]


# --- the ROM check -----------------------------------------------------------


@dataclass(frozen=True, slots=True)
class RomVerification:
    """What the selected file is, and whether this build supports it.

    ``problem`` is empty exactly when the file is supported, and is otherwise the
    sentence the window shows - there is no separate "error code" for the GUI to
    translate, because a translation table is one more place for the user-facing
    text to drift from the check that produced it.
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
        if self.ok:
            return "Verified supported ROM \u2713"
        return "Unsupported ROM \u2717"

    def expected_sha256_short(self) -> str:
        return shorten_hash(self.expected_sha256)

    def actual_sha256_short(self) -> str | None:
        return shorten_hash(self.sha256) if self.sha256 else None


# --- the request and the result ----------------------------------------------


@dataclass(frozen=True, slots=True)
class RandomizerRequest:
    """One run, as the shell asks for it.

    Everything the application decides is here and nothing is implicit: a module
    never reaches the output path, the manifest path or the overwrite policy, so a
    module cannot become a second application by accident.
    """

    source_rom: Path
    output_rom: Path
    master_seed: str
    #: The resolved enabled module ids.
    enabled: frozenset[str]
    #: The modules the *product* offers. The service enforces this rather than
    #: trusting the caller to have done so: an independent review found the warp
    #: product's window protocol accepting a request that named an enemy module,
    #: which would have run it under the warp tool's name and reported zero counts.
    #: Validation belongs here, where both products get it, rather than in each
    #: product's own method where one of them forgot it.
    allowed_modules: frozenset[str] | None = None
    #: Per-module settings. Missing modules take their declared defaults.
    module_settings: Mapping[str, Mapping[str, object]] = field(default_factory=dict)
    tool_name: str = "Randomizer"
    tool_version: str = "0.0.0"
    progression: str = ""
    spoiler: bool = False
    spoiler_path: Path | None = None
    manifest_path: Path | None = None
    overwrite: bool = False
    sdk_commit: str | None = None
    #: Called as each phase of :func:`tools.webfoot.randomizer.registry.progress_steps`
    #: is entered, from whatever thread is running the call.
    on_progress: ProgressCallback | None = field(default=None, compare=False)


@dataclass(frozen=True, slots=True)
class RandomizerResult:
    """One finished run, in the shape a status report and a manifest need.

    Every count is a module's own reported value, carried through untouched. A
    window displays these and never a hard-coded expectation, which is what stops
    a policy change from leaving a stale number on screen.
    """

    master_seed: str
    enabled: tuple[str, ...]
    module_seeds: Mapping[str, str]
    module_versions: Mapping[str, int]
    output_path: Path
    output_sha256: str
    output_size: int
    manifest_path: Path
    spoiler_path: Path | None
    changed_byte_count: int
    source_sha256: str
    source_unchanged: bool
    tool_name: str
    tool_version: str
    document: Mapping
    spoiler_document: Mapping | None = None

    def short_output_sha256(self) -> str:
        return shorten_hash(self.output_sha256)

    def module_section(self, module_id: str) -> Mapping:
        return self.document["modules"][module_id]

    def success_lines(self) -> list[str]:
        """The neutral success readout: what ran, what it did, where it went.

        A product may present its own block instead - the warp executable
        reproduces the one it has always shown - but this is the shared form, and
        it is built only from what the service returned.
        """
        # Each module's *published* name, which is what its check box says and what
        # its manifest section records. The registry id (``enemy-placement``) is an
        # implementation name and belongs in the manifest, not in the text a player
        # reads.
        applied = ", ".join(
            registry.module_for(module_id).display_name for module_id in self.enabled
        )
        lines = [
            "Success",
            "ROM verified \u2713",
            f"Seed: {self.master_seed}",
            f"Applied: {applied}",
        ]
        for module_id in self.enabled:
            lines.extend(self.module_section(module_id).get("summary_lines", ()))
        lines.extend(
            [
                f"Output: {self.output_path}",
                f"SHA-256: {self.output_sha256}",
                f"Manifest: {self.manifest_path}",
            ]
        )
        if self.spoiler_path is not None:
            lines.append(f"Spoiler: {self.spoiler_path}")
        lines.append(
            f"Source ROM unchanged: {'yes' if self.source_unchanged else 'NO'}"
        )
        return lines


# --- the service -------------------------------------------------------------


class RandomizerService:
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
    ) -> None:
        self._catalog = catalog
        self._supported_profile = supported_profile
        #: The most recent loaded image, kept so a second run against the same
        #: unchanged file does not re-read and re-index 8 MiB. Keyed by the
        #: filesystem identity tuple, which is the cheapest thing that catches a
        #: rewrite, a truncation and a replacement.
        self._context: RandomizerContext | None = None
        self._context_key: tuple | None = None

    # --- catalog ---------------------------------------------------------

    @property
    def catalog(self) -> RomProfileCatalog:
        if self._catalog is None:
            self._catalog = load_catalog(None)
        return self._catalog

    def supported_profile(self) -> RomProfile:
        """The one profile this build randomizes.

        Resolved from the catalog by the packaged profile id - the same authority
        the ROM-addressed readers use - so every "expected" value in a refusal is
        read from verified profile data rather than restated here. It is
        injectable so the boundary's own tests can drive a synthetic image
        without a private ROM, exactly as the profile contract intends.
        """
        if self._supported_profile is None:
            from ..packaged import packaged_profile

            self._supported_profile = packaged_profile()
        return self._supported_profile

    # --- seed ------------------------------------------------------------

    def normalize_seed(self, seed: str | int) -> str:
        """The exact seed string, or a friendly refusal.

        The same contract every module's seed authority states - ``"01"`` and
        ``"1"`` are different seeds, and the empty string is refused rather than
        silently seeded - expressed as an error the window can present without
        importing a core exception.
        """
        if isinstance(seed, bool) or not isinstance(seed, (str, int)):
            raise SeedRefusedError(f"A seed must be text or a number, got {seed!r}")
        text = str(seed)
        if not text:
            raise SeedRefusedError(
                "The seed is empty. Type a seed, or use Random Seed for one."
            )
        return text

    def generate_seed(self) -> str:
        return random_seed()

    # --- verification ----------------------------------------------------

    def _identify(self, path: str | Path) -> tuple[RomIdentification | None, str]:
        """Identify ``path``, or return ``(None, problem)`` for a user error.

        Three distinct failure families, and all three are ordinary user input
        rather than defects, so all three are turned into a sentence here:
        ``RomReadError`` (missing, a directory, or changed mid-read),
        ``GbaHeaderError`` (too short to carry a GBA header, or non-ASCII header
        fields - the common case for a wrong pick out of an "All files" filter),
        and ``OSError`` (a permission denial or a vanished drive).
        """
        try:
            identification = identify_rom(Path(path), self.catalog)
        except GbaHeaderError as exc:
            return None, f"The selected file is not a Game Boy Advance ROM: {exc}"
        except RomReadError as exc:
            return None, f"The selected file could not be read: {exc}"
        except OSError as exc:
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
        """The verification *and* the identification, from one hash pass."""
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
        # file" - a true statement about the wrong thing.
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
            detail = "; ".join(match.mismatches) or match.reason
            return RomVerification(
                status=UNSUPPORTED,
                problem=f"{UNSUPPORTED_ROM_HEADLINE} {detail}",
                **common,
            ), identification
        return RomVerification(status=VERIFIED, problem="", **common), identification

    # --- naming ----------------------------------------------------------

    def default_output_path(self, rom_path: str | Path, seed: str, template: str) -> Path:
        return default_output_path(rom_path, seed, template)

    def manifest_path_for(self, output_rom: str | Path) -> Path:
        return default_manifest_path(output_rom)

    def spoiler_path_for(self, output_rom: str | Path) -> Path:
        return default_spoiler_path(output_rom)

    def output_is_the_input(self, source_rom: str | Path, output_rom: str | Path) -> bool:
        """Whether the requested output *is* the input, by filesystem identity.

        Exposed for the window, which blocks the run before it starts rather than
        after a refusal comes back from a worker thread. It is the same predicate
        the refusal uses, so the button and the refusal cannot disagree.
        """
        return paths_are_the_same_file(source_rom, output_rom)

    # --- the context cache -----------------------------------------------

    def _context_for(
        self, path: Path, identification: RomIdentification
    ) -> RandomizerContext:
        """The loaded image, reused across runs while the file is unchanged."""
        try:
            current = path.stat()
        except OSError:
            current = None
        key = (
            str(path.resolve()),
            getattr(current, "st_dev", None),
            getattr(current, "st_ino", None),
            getattr(current, "st_size", None),
            getattr(current, "st_mtime_ns", None),
        )
        cached = self._context
        if cached is not None and self._context_key == key:
            return cached
        context = RandomizerContext(
            path, self.catalog, identification=identification
        )
        self._context = context
        self._context_key = key
        return context

    # --- the run ---------------------------------------------------------

    def run(self, request: RandomizerRequest) -> RandomizerResult:
        """Plan, write and record one randomized run.

        Ordering is a safety property here, not a style choice. The path-level
        rules run first - is the output the input under some spelling, is the
        folder writable - because they are cheap, total, and the same ordering
        :func:`~tools.webfoot.write.emit_image` uses: the input path also exists,
        so the alias check has to run before the overwrite policy or writing over
        the input would raise the wrong rule and name the wrong fix.

        The destructive step is deliberately **last before the write**.
        Confirming an overwrite deletes the previous output and its companions,
        and that must not happen until the run is certain to produce a
        replacement - so the input is verified, the image is read, and the whole
        plan is built before anything is removed.
        """
        source = Path(request.source_rom)
        output = Path(request.output_rom)
        if not request.enabled:
            raise ModuleRefusedError(
                "No randomization is selected, so this run would produce an "
                "unmodified copy of your ROM. Choose at least one option."
            )
        if request.allowed_modules is not None:
            # The product's own list, enforced here. A module outside it is refused
            # rather than run, because running it would produce a ROM under a label
            # that never offered it.
            outside = frozenset(request.enabled) - frozenset(request.allowed_modules)
            if outside:
                raise ModuleRefusedError(
                    f"this product does not offer {', '.join(sorted(outside))}; it "
                    f"offers "
                    f"{', '.join(sorted(request.allowed_modules)) or 'no module'}"
                )

        text = self.normalize_seed(request.master_seed)
        expected = self.supported_profile()
        phases = registry.progress_steps(request.enabled)
        total_steps = len(phases)
        on_progress = request.on_progress
        counter = [0]

        def report(label: str) -> None:
            """Report the phase now beginning. Never claims a finished one."""
            counter[0] += 1
            if on_progress is not None:
                on_progress(counter[0], total_steps, label)

        # --- phase A: is this write request legal? (nothing is written yet) ---

        if not str(output).strip():
            raise OutputPathRefusedError("Choose an output file name.")

        if paths_are_the_same_file(source, output):
            raise OutputPathRefusedError(
                "The output file is the input ROM. Choose a different output "
                "name; this tool never writes to the ROM you selected."
            )

        manifest_path = (
            Path(request.manifest_path)
            if request.manifest_path is not None
            else default_manifest_path(output)
        )
        # The spoiler *companion* of this output is always part of the output set,
        # whether or not this run will write one. An independent review found the
        # narrow version leaving a previous seed's spoiler beside a new ROM when
        # the second run had the spoiler switched off, which pairs a ROM with
        # another run's answers. So the path is checked and replaced as a companion;
        # `spoiler_path` (what gets written) stays None when the option is off.
        companion_spoiler = (
            Path(request.spoiler_path)
            if request.spoiler_path is not None
            else default_spoiler_path(output)
        )
        write_targets: list[tuple[Path, str]] = [
            (output, "the output ROM"),
            (manifest_path, "the manifest"),
            (companion_spoiler, "the spoiler log"),
        ]
        spoiler_path = companion_spoiler if request.spoiler else None

        for target, label in write_targets:
            if paths_are_the_same_file(target, source):
                raise OutputPathRefusedError(
                    f"{label} would be the input ROM ({target}). Choose a different "
                    "output name; this tool never writes to the ROM you selected."
                )
        for index, (target, label) in enumerate(write_targets):
            for other, other_label in write_targets[index + 1:]:
                if paths_are_the_same_file(target, other):
                    raise OutputPathRefusedError(
                        f"{label} and {other_label} are the same file ({target}); "
                        "choose different paths so neither result is lost."
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

        occupied = [path for path, _ in write_targets if path.exists()]
        if occupied:
            if not request.overwrite:
                raise OutputAlreadyExistsError(
                    f"{occupied[0].name} already exists in {parent}. Choose another "
                    "name, or confirm that you want to replace it."
                )
            # Refused even with the overwrite confirmed: replacing a copy of the
            # verified image would destroy a clean ROM, the one file this tool
            # exists to protect.
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

        report(phases[0])
        verification, identification = self._inspect(source)
        if not verification.ok or identification is None:
            raise UnsupportedRomError(verification.problem)

        # The context owns the capability gate; the service has just verified the
        # image, so it hands that identification over rather than letting the
        # context hash the same 8 MiB again.
        try:
            context = self._context_for(source, identification)
        except ModuleRefusedError as exc:
            raise UnsupportedRomError(str(exc)) from exc

        # Each enabled module's phase is reported immediately before the planning
        # pass that will run it. A group plans its members in one call, so two
        # labels can precede one call; both phases are genuinely beginning there,
        # and the bar can therefore never claim work that has not started.
        for label in phases[1 : 1 + len(request.enabled)]:
            report(label)

        try:
            plans = registry.plan_modules(
                enabled=request.enabled,
                context=context,
                master_seed=text,
                settings=request.module_settings,
                sdk_commit=request.sdk_commit,
            )
        except ModuleRefusedError:
            raise
        except ValueError as exc:
            raise ModuleRefusedError(
                f"The randomizer refused this run: {exc}"
            ) from exc

        write_plan = self._merge(plans, identification, context)

        # --- the point of no return: the run is known to be producible ---

        self._remove_existing(
            [path for path, _ in write_targets], overwrite=request.overwrite
        )

        report(phases[-2])
        try:
            write_manifest = emit_image(source, output, write_plan)
        except (WriteError, OSError) as exc:
            raise OutputPathRefusedError(
                f"The randomized ROM could not be written: {exc}"
            ) from exc

        report(phases[-1])
        after, _ = self._identify(source)
        source_unchanged = after is not None and after.hashes.sha256 == verification.sha256
        if not source_unchanged:
            raise SourceChangedError(
                "The selected ROM changed while it was being randomized, so the "
                f"output was not accepted. Delete {output} and try again with a "
                "ROM that is not being modified."
            )

        changed_byte_count = write_manifest.to_json()["changed_byte_count"]
        module_seeds = registry.derive_module_seeds(text)

        # The spoiler is built first and may legitimately be ``None``: a run whose
        # enabled modules have nothing to hide has no spoiler to write, and an
        # empty file would read as "there was nothing to randomize". The manifest
        # is then built knowing whether a spoiler will exist, so it never names a
        # file that was not written.
        spoiler_document = (
            build_spoiler(
                tool_name=request.tool_name,
                tool_version=request.tool_version,
                modules=registry.modules(),
                plans=plans,
                master_seed=text,
                profile_id=context.profile.id,
                output_filename=output.name,
                output_sha256=write_manifest.output_sha256,
            )
            if spoiler_path is not None
            else None
        )
        written_spoiler_path = spoiler_path if spoiler_document is not None else None

        document = build_manifest(
            tool_name=request.tool_name,
            tool_version=request.tool_version,
            modules=registry.modules(),
            enabled=request.enabled,
            plans=plans,
            module_seeds=module_seeds,
            profile_id=context.profile.id,
            source_sha256=verification.sha256 or "",
            source_size=verification.size or 0,
            master_seed=text,
            output_filename=output.name,
            output_size=write_manifest.output_size,
            output_sha256=write_manifest.output_sha256,
            changed_byte_count=changed_byte_count,
            progression=request.progression,
            spoiler_filename=(
                written_spoiler_path.name if written_spoiler_path is not None else None
            ),
            module_order=[module.id for module in registry.modules()],
            tool_commit=(
                request.sdk_commit if request.sdk_commit is not None
                else repository_commit()
            ),
            tool_dirty=(
                None if request.sdk_commit is not None else repository_is_dirty()
            ),
        )

        self._write_document(manifest_path, document, kind="manifest", output=output)
        if written_spoiler_path is not None:
            self._write_document(
                written_spoiler_path, spoiler_document, kind="spoiler log", output=output
            )

        return RandomizerResult(
            master_seed=text,
            enabled=tuple(
                module.id
                for module in registry.modules()
                if module.id in request.enabled
            ),
            module_seeds=module_seeds,
            module_versions={
                module.id: module.algorithm_version for module in registry.modules()
            },
            output_path=output,
            output_sha256=write_manifest.output_sha256,
            output_size=write_manifest.output_size,
            manifest_path=manifest_path,
            spoiler_path=written_spoiler_path,
            changed_byte_count=changed_byte_count,
            source_sha256=verification.sha256 or "",
            source_unchanged=source_unchanged,
            tool_name=request.tool_name,
            tool_version=request.tool_version,
            document=document,
            spoiler_document=spoiler_document,
        )

    # --- internals -------------------------------------------------------

    def _merge(
        self,
        plans: tuple[ModulePlan, ...],
        identification: RomIdentification,
        context: RandomizerContext,
    ):
        """Every module's changes in ONE plan, which refuses to overlap.

        Fail closed, and provably so: :func:`tools.webfoot.write.plan_changes`
        raises :class:`~tools.webfoot.write.OverlappingChangeError` when two
        changes write the same byte. There is no "last module wins" branch here
        and there cannot be one - a collision means no plan is built at all, so
        the manifest can never describe an image that only one module planned.
        """
        changes = tuple(change for plan in plans for change in plan.changes)
        try:
            return plan_changes(
                context.image(),
                changes,
                profile_id=context.profile.id,
                base_sha256=identification.hashes.sha256,
            )
        except OverlappingChangeError as exc:
            raise ModuleConflictError(
                "Two enabled modules would write the same bytes, so this run was "
                f"refused rather than resolved by order: {exc}"
            ) from exc
        except WriteError as exc:
            raise ModuleConflictError(
                f"The combined changes could not be validated: {exc}"
            ) from exc

    @staticmethod
    def _write_document(
        path: Path, document: Mapping, *, kind: str, output: Path
    ) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(canonical_json(document), encoding="utf-8")
        except OSError as exc:
            raise ManifestWriteError(
                f"The randomized ROM was created at {output}, but its {kind} could "
                f"not be written to {path} ({exc})."
            ) from exc

    @staticmethod
    def _remove_existing(paths: list[Path], *, overwrite: bool) -> None:
        """Delete the artefacts a confirmed overwrite replaces.

        The only destructive step in this module.

        It runs after the input has been verified, the image read and the whole
        plan built, so a *planning* failure - a bad input, an unsupported image, a
        module refusal, a collision between modules - can no longer destroy the
        user's previous randomized ROM. What it does not survive is a failure in
        the write itself: `emit_image` refuses an existing destination, so the old
        file has to be gone before the new one can be published, and a full disk or
        a permission denial between the two would leave the user with neither. That
        is the irreducible cost of refusing to write over an existing file, and it
        is stated rather than implied.

        The spoiler is in the list on purpose even though the run may not produce
        one: a previous run's spoiler must not be left sitting beside a new ROM, or
        the pair on disk would describe two different runs.

        This is also the step the CLI route was missing: ``webfoot randomize
        --overwrite`` deletes nothing and therefore cannot replace an existing
        output, because ``emit_image`` refuses a destination that exists. Doing it
        here, once, is what makes overwrite work on every route that uses this
        service.
        """
        if not overwrite:
            return
        for path in paths:
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


# --- module-level conveniences ----------------------------------------------

_DEFAULT_SERVICE: RandomizerService | None = None


def default_service() -> RandomizerService:
    """The process-wide service. One catalog load for the whole application."""
    global _DEFAULT_SERVICE
    if _DEFAULT_SERVICE is None:
        _DEFAULT_SERVICE = RandomizerService()
    return _DEFAULT_SERVICE


__all__ = [
    "MANIFEST_SUFFIX",
    "ProgressCallback",
    "RandomizerRequest",
    "RandomizerResult",
    "RandomizerService",
    "RomVerification",
    "SPOILER_SUFFIX",
    "UNSUPPORTED",
    "UNSUPPORTED_ROM_HEADLINE",
    "VERIFIED",
    "default_manifest_path",
    "default_output_path",
    "default_service",
    "default_spoiler_path",
    "random_seed",
    "repository_commit",
    "sanitize_seed_for_filename",
    "shorten_hash",
]
