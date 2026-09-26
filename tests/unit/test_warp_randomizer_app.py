"""The application boundary for the warp randomizer: the rules around the core.

WARPRAND-APP-001. This file proves what the *application* adds and nothing about
the randomizer's own policy - the permutation, the reciprocal pairing and the
dead-end guard are already proved, against the canonical image, by
``tests/unit/test_warp_randomizer.py`` and
``tests/integration/test_warp_randomizer_rom.py``. Duplicating that corpus here
would slow the portable gate down to re-prove a neighbour's claim.

What is proved here, all of it without a commercial ROM:

* the launch seed is ``Goku``, and the image the app demands is the canonical
  one - read from the packaged profile, so the app cannot be checking a stale
  hard-coded hash;
* a wrong size, a wrong hash, a missing file and a directory are refused with a
  user-facing sentence rather than an exception trace;
* the output may not be the input, under any spelling - including a hard link,
  which only a filesystem identity check catches;
* a collision is never silently resolved: the run refuses until overwrite is
  confirmed, and even then refuses to destroy a copy of the clean ROM;
* the seed is sanitised for the *filename* only, and the exact string the user
  typed reaches the core;
* a core refusal arrives as a friendly message, not as a core exception.

The synthetic image below exists because the boundary's rules are about
*identity and paths*, not about map data: a small synthetic profile lets the
portable gate exercise acceptance, collision and seed pass-through with no ROM
on the machine. The canonical image's own end-to-end run - counts, golden hash,
manifest determinism, source immutability - is
``tests/integration/test_warp_randomizer_app_rom.py``.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from tools.webfoot.binary import GbaRomAddress
from tools.webfoot.gba_header import calculate_header_checksum
from tools.webfoot.profile import (
    MapEntryTableProfile,
    RomProfile,
    RomProfileCatalog,
)
from tools.webfoot.warp_randomizer import WarpRandomizerError
from tools.webfoot.warprand import service as warprand

#: The canonical United States image this product supports, stated here - in a
#: test - rather than in production code. The boundary reads both values from the
#: packaged profile, and this pins the contract they must keep describing.
CANONICAL_SIZE = 8_388_608
CANONICAL_SHA256 = (
    "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e"
)

#: The synthetic stand-in's game code, four alphanumeric ASCII characters.
SYNTHETIC_GAME_CODE = "ZTST"
SYNTHETIC_IMAGE_SIZE = 0x1000


def synthetic_image(
    *, size: int = SYNTHETIC_IMAGE_SIZE, version: int = 0, fill: int = 0
) -> bytes:
    """A small file carrying a parseable minimal GBA header.

    Only what identification reads is set: a non-empty title, the game code, the
    maker code, the fixed value and a correct header checksum. No map data,
    because nothing in this file randomizes anything.
    """
    data = bytearray([fill]) * size
    data[0xA0:0xAC] = b"SYNTHETIC   "
    data[0xAC:0xB0] = SYNTHETIC_GAME_CODE.encode("ascii")
    data[0xB0:0xB2] = b"01"
    data[0xB2] = 0x96
    data[0xBC] = version
    data[0xBD] = calculate_header_checksum(bytes(data))
    return bytes(data)


def synthetic_profile(image: bytes) -> RomProfile:
    """The profile that describes ``synthetic_image()``.

    It declares ``map_entries`` so the capability gate has a real declaration to
    read, which is the same shape a shipping profile has minus the addresses.
    """
    return RomProfile(
        id="synthetic_boundary_image",
        game="synthetic",
        region="TEST",
        revision=0,
        game_code=SYNTHETIC_GAME_CODE,
        size=len(image),
        crc32=None,
        md5=None,
        sha1=None,
        sha256=hashlib.sha256(image).hexdigest(),
        sources=(),
        notes="WARPRAND-APP-001 boundary fixture; not a real image.",
        map_entries=MapEntryTableProfile(GbaRomAddress(0x08000000), 1, 4),
        enemy_stats=None,
        character_base_stats=None,
    )


@pytest.fixture
def boundary(tmp_path: Path):
    """A service over a synthetic supported image, plus the image and its profile."""
    image = synthetic_image()
    profile = synthetic_profile(image)
    catalog = RomProfileCatalog([profile])
    service = warprand.WarpRandomizerService(
        catalog=catalog, supported_profile=profile
    )
    source = tmp_path / "synthetic.gba"
    source.write_bytes(image)
    return service, source, profile


@pytest.fixture
def canonical() -> warprand.WarpRandomizerService:
    """The default service: the real packaged profile, no image touched."""
    return warprand.WarpRandomizerService()


# --- identity ----------------------------------------------------------------


def test_the_default_launch_seed_is_goku():
    """The ticket's v0.1.0 launch seed, stated once and asserted here."""
    assert warprand.DEFAULT_SEED == "Goku"


def test_the_supported_image_is_the_canonical_us_image(canonical):
    """The app's expectation is read from the packaged profile, not restated.

    If production code ever grows its own copy of the hash, this test cannot
    notice - but if the *profile* stops describing the canonical image, every
    refusal the user sees starts quoting the wrong expectation, and that is what
    this catches.
    """
    profile = canonical.supported_profile()
    assert profile.size == CANONICAL_SIZE
    assert profile.sha256 == CANONICAL_SHA256


def test_the_tool_and_policy_identity_are_the_shipped_ones():
    assert warprand.TOOL_NAME == "Buu's Fury Warp Randomizer"
    assert warprand.TOOL_VERSION == "0.1.0"
    assert warprand.POLICY_ID == "reciprocal-door-pairs/3"
    assert warprand.SUPPORTED_POLICIES == (warprand.POLICY_ID,)


# --- the ROM check -----------------------------------------------------------


def test_a_valid_image_is_verified(boundary):
    service, source, _ = boundary
    verification = service.verify_rom(source)

    assert verification.ok
    assert verification.status == warprand.VERIFIED
    assert verification.problem == ""
    assert verification.size == SYNTHETIC_IMAGE_SIZE
    assert verification.headline == "Verified supported ROM \u2713"


def test_a_wrong_size_is_refused_with_the_expected_hash(boundary, tmp_path):
    service, _, _ = boundary
    wrong = tmp_path / "short.gba"
    wrong.write_bytes(synthetic_image(size=SYNTHETIC_IMAGE_SIZE // 4))

    verification = service.verify_rom(wrong)

    assert not verification.ok
    assert "supports the verified US Buu's Fury ROM only" in verification.problem
    assert f"{SYNTHETIC_IMAGE_SIZE // 4:,} bytes" in verification.problem
    assert f"SHA-256: {warprand.shorten_hash(verification.expected_sha256)}" in (
        verification.problem
    )


def test_a_wrong_hash_is_refused_with_the_expected_hash(boundary, tmp_path):
    """Right size, wrong bytes: the size check must not be the only gate."""
    service, _, _ = boundary
    wrong = tmp_path / "same-size.gba"
    wrong.write_bytes(synthetic_image(fill=0x5A))

    verification = service.verify_rom(wrong)

    assert not verification.ok
    assert verification.size == SYNTHETIC_IMAGE_SIZE
    assert "Expected SHA-256:" in verification.problem
    assert verification.expected_sha256_short() in verification.problem
    assert verification.actual_sha256_short() in verification.problem


def test_a_missing_file_is_refused_rather_than_raising(canonical, tmp_path):
    verification = canonical.verify_rom(tmp_path / "absent.gba")

    assert not verification.ok
    assert "could not be read" in verification.problem
    assert verification.size is None


def test_a_directory_is_refused_rather_than_raising(canonical, tmp_path):
    verification = canonical.verify_rom(tmp_path)

    assert not verification.ok
    assert verification.problem
    assert verification.headline == "Unsupported ROM \u2717"


def test_an_empty_path_is_refused(canonical):
    verification = canonical.verify_rom("")

    assert not verification.ok
    assert verification.problem == "Choose a ROM file first."


def test_shorten_hash_is_the_form_the_ticket_shows():
    assert (
        warprand.shorten_hash(CANONICAL_SHA256) == "940AD5F0...F059E"
    )
    # A short value is returned whole rather than sliced into nonsense.
    assert warprand.shorten_hash("abc") == "ABC"


# --- source immutability -----------------------------------------------------


def test_the_output_may_not_be_the_input(boundary):
    """The one file this tool exists to protect is never a write target."""
    service, source, _ = boundary

    with pytest.raises(warprand.OutputPathRefusedError) as caught:
        service.randomize_warps(source, source, "Goku")

    assert "is the input ROM" in str(caught.value)
    assert source.read_bytes() == synthetic_image()


def test_the_output_may_not_be_a_hard_link_to_the_input(boundary, tmp_path):
    """Two names, one file: only the filesystem's own identity catches this."""
    service, source, _ = boundary
    alias = tmp_path / "alias.gba"
    try:
        alias.hardlink_to(source)
    except OSError:  # pragma: no cover - a filesystem without hard links
        pytest.skip("this filesystem does not support hard links")

    with pytest.raises(warprand.OutputPathRefusedError):
        service.randomize_warps(alias, source, "Goku")

    assert source.read_bytes() == synthetic_image()


# --- naming ------------------------------------------------------------------


def test_the_default_output_name_is_derived_from_the_seed(boundary):
    service, source, _ = boundary

    assert service.default_output_path(source, "Goku").name == (
        "Buu's Fury - Warp Randomized - Goku.gba"
    )
    assert service.default_output_path(source, "Goku").parent == source.parent


def test_the_manifest_name_is_derived_from_the_output(boundary):
    service, source, _ = boundary
    output = service.default_output_path(source, "Goku")

    assert service.manifest_path_for(output).name == (
        "Buu's Fury - Warp Randomized - Goku.manifest.json"
    )


@pytest.mark.parametrize(
    ("seed", "expected"),
    (
        ("Goku", "Goku"),
        ("Goku: SSJ3?!", "Goku SSJ3"),
        ("a/b\\c", "a b c"),
        ("  spaced  out  ", "spaced out"),
        ("trailing dot.", "trailing dot"),
        ("Namek\u00e9n", "Namek\u00e9n"),
    ),
)
def test_a_seed_is_sanitised_for_the_filename(seed, expected):
    assert warprand.sanitize_seed_for_filename(seed) == expected


def test_a_seed_with_nothing_usable_falls_back_deterministically():
    assert warprand.sanitize_seed_for_filename("///???") == (
        warprand.FALLBACK_SEED_FILENAME
    )
    assert warprand.sanitize_seed_for_filename("///???") == (
        warprand.sanitize_seed_for_filename("!!!***")
    )


def test_a_very_long_seed_is_capped_without_crashing():
    sanitised = warprand.sanitize_seed_for_filename("A" * 500)

    assert len(sanitised) == warprand.MAX_SEED_FILENAME_CHARACTERS
    assert sanitised == "A" * warprand.MAX_SEED_FILENAME_CHARACTERS


# --- the seed the algorithm sees --------------------------------------------


def test_the_exact_seed_string_reaches_the_core(boundary, monkeypatch):
    """Sanitising is a filename concern; the core gets the user's own string.

    The planner is replaced with a recorder so the argument is observed rather
    than inferred from a resulting layout, and it raises so the run stops before
    the write - this test is about the argument, not about the output. The
    output name beside it is built from the *same* seed and does carry the
    sanitised form, which is the separation being proved.
    """
    service, source, profile = boundary
    seed = "Goku: SSJ3?!"
    output = warprand.default_output_path(source, seed)
    seen: dict[str, object] = {}

    def recorder(image, matched_profile, seed_argument):
        seen["seed"] = seed_argument
        seen["profile"] = matched_profile
        seen["image"] = image
        raise WarpRandomizerError("recorder stops the run here")

    # The capability gate looks a profile up in the *packaged* catalog, which a
    # synthetic profile is deliberately absent from; the boundary's own seam is
    # the honest place to stand in for it.
    monkeypatch.setattr(
        warprand.WarpRandomizerService, "_profile_for", lambda self, ident: profile
    )
    monkeypatch.setattr(warprand, "plan_warp_randomization", recorder)

    with pytest.raises(warprand.WarpRandomizerAppError):
        service.randomize_warps(source, output, seed)

    assert seen["seed"] == "Goku: SSJ3?!"
    assert seen["profile"] is profile
    assert seen["image"] == synthetic_image()
    # ... while the file name it produced carries the sanitised form.
    assert output.name == "Buu's Fury - Warp Randomized - Goku SSJ3.gba"


def test_an_empty_seed_is_refused_cleanly(boundary):
    service, source, _ = boundary
    output = warprand.default_output_path(source, "Goku")

    with pytest.raises(warprand.SeedRefusedError) as caught:
        service.randomize_warps(source, output, "")

    assert "must not be empty" in str(caught.value)


def test_a_seed_is_not_trimmed_or_case_folded(boundary):
    """``"Goku "`` and ``"goku"`` are different seeds and must stay different."""
    service, _, _ = boundary

    assert service.normalize_seed("  Goku  ") == "  Goku  "
    assert service.normalize_seed("goku") == "goku"


def test_a_random_seed_is_short_shareable_and_legal():
    service = warprand.WarpRandomizerService()
    seeds = {warprand.random_seed() for _ in range(40)}

    # Not a claim that 40 draws are all distinct, which would be flaky; a claim
    # that the generator varies at all, which a constant would fail.
    assert len(seeds) > 1
    for seed in seeds:
        word, _, digits = seed.partition("-")
        assert word in warprand.SEED_WORDS
        assert len(digits) == 4 and digits.isdigit()
        assert len(seed) <= 16
        # Legible, copyable and accepted by the core's own seed rule.
        assert service.normalize_seed(seed) == seed
        assert warprand.sanitize_seed_for_filename(seed) == seed


# --- policy ------------------------------------------------------------------


def test_an_unknown_policy_is_refused(boundary):
    """A policy argument is not a knob: it either matches or the run stops."""
    service, source, _ = boundary
    output = warprand.default_output_path(source, "Goku")

    with pytest.raises(warprand.WarpRandomizerAppError) as caught:
        service.randomize_warps(source, output, "Goku", policy="reciprocal-door-pairs/4")

    assert "unsupported randomization policy" in str(caught.value)
    assert warprand.POLICY_ID in str(caught.value)


# --- output collisions -------------------------------------------------------


def test_an_existing_output_is_refused_until_overwrite_is_confirmed(boundary, tmp_path):
    service, source, _ = boundary
    output = tmp_path / "Buu's Fury - Warp Randomized - Goku.gba"
    output.write_bytes(b"a previous randomized ROM")

    with pytest.raises(warprand.OutputAlreadyExistsError) as caught:
        service.randomize_warps(source, output, "Goku")

    assert "already exists" in str(caught.value)
    # Nothing was destroyed by the refusal.
    assert output.read_bytes() == b"a previous randomized ROM"


def test_an_existing_manifest_is_refused_until_overwrite_is_confirmed(boundary, tmp_path):
    service, source, _ = boundary
    output = tmp_path / "out.gba"
    manifest = service.manifest_path_for(output)
    manifest.write_text("{}", encoding="utf-8")

    with pytest.raises(warprand.OutputAlreadyExistsError):
        service.randomize_warps(source, output, "Goku")

    assert manifest.read_text(encoding="utf-8") == "{}"


def test_confirmed_overwrite_clears_the_previous_artifacts(boundary, tmp_path, monkeypatch):
    service, source, profile = boundary
    output = tmp_path / "out.gba"
    output.write_bytes(b"stale")
    service.manifest_path_for(output).write_text("{}", encoding="utf-8")

    monkeypatch.setattr(
        warprand.WarpRandomizerService, "_profile_for", lambda self, ident: profile
    )

    def recorder(image, matched_profile, seed):
        raise WarpRandomizerError("recorder stops the run here")

    monkeypatch.setattr(warprand, "plan_warp_randomization", recorder)

    with pytest.raises(warprand.WarpRandomizerAppError):
        service.randomize_warps(source, output, "Goku", overwrite=True)

    # Confirmation means the confirmed overwrite really did make room - the run
    # got past the collision and failed later, in the planner.
    assert not output.exists()
    assert not service.manifest_path_for(output).exists()


def test_a_copy_of_the_canonical_image_is_never_replaced(boundary, tmp_path):
    """Even a confirmed overwrite may not destroy a clean ROM.

    An output that *is* the supported image under another name is the one
    collision that must fail closed: confirming "replace it?" must not be enough
    to throw away the user's clean dump.
    """
    service, source, _ = boundary
    output = tmp_path / "looks-like-a-copy.gba"
    output.write_bytes(synthetic_image())

    with pytest.raises(warprand.OutputPathRefusedError) as caught:
        service.randomize_warps(source, output, "Goku", overwrite=True)

    assert "copy of the verified ROM" in str(caught.value)
    assert output.read_bytes() == synthetic_image()


# --- the core's refusals reach the user --------------------------------------


def test_a_randomizer_refusal_is_reported_as_a_friendly_message(
    boundary, monkeypatch
):
    """A core refusal is a sentence, not a traceback and not a core exception."""
    service, source, profile = boundary
    output = warprand.default_output_path(source, "Goku")

    def refusing_planner(image, matched_profile, seed):
        raise WarpRandomizerError("this record needs a field the authority refuses")

    monkeypatch.setattr(
        warprand.WarpRandomizerService, "_profile_for", lambda self, ident: profile
    )
    monkeypatch.setattr(warprand, "plan_warp_randomization", refusing_planner)

    with pytest.raises(warprand.WarpRandomizerAppError) as caught:
        service.randomize_warps(source, output, "Goku")

    assert not isinstance(caught.value, WarpRandomizerError)
    assert "The randomizer refused this run:" in str(caught.value)
    assert "the authority refuses" in str(caught.value)


def test_a_programmer_error_is_not_swallowed(boundary, monkeypatch):
    """Unexpected failures stay unexpected, so the window can offer details."""
    service, source, profile = boundary
    output = warprand.default_output_path(source, "Goku")

    def buggy_planner(image, matched_profile, seed):
        raise TypeError("a real bug")

    monkeypatch.setattr(
        warprand.WarpRandomizerService, "_profile_for", lambda self, ident: profile
    )
    monkeypatch.setattr(warprand, "plan_warp_randomization", buggy_planner)

    with pytest.raises(TypeError):
        service.randomize_warps(source, output, "Goku")


# --- progress ----------------------------------------------------------------


def test_progress_reports_the_real_phases_in_order(boundary, monkeypatch):
    """The bar is fed real boundaries, reported before the work they name.

    The planner is stubbed to refuse, so this proves the reports that lead up to
    it are emitted in order and that a run which stops early stops reporting -
    the bar can understate progress but can never claim work that did not
    happen.
    """
    service, source, profile = boundary
    output = warprand.default_output_path(source, "Goku")
    seen: list[tuple[int, int, str]] = []

    def refusing_planner(image, matched_profile, seed):
        raise WarpRandomizerError("stop at the long phase")

    monkeypatch.setattr(
        warprand.WarpRandomizerService, "_profile_for", lambda self, ident: profile
    )
    monkeypatch.setattr(warprand, "plan_warp_randomization", refusing_planner)

    with pytest.raises(warprand.WarpRandomizerAppError):
        service.randomize_warps(
            source, output, "Goku", on_progress=lambda *a: seen.append(a)
        )

    assert [step for step, _total, _label in seen] == [1, 2]
    assert [total for _step, total, _label in seen] == [4, 4]
    assert seen[0][2] == warprand.PROGRESS_STEPS[0]
    assert seen[1][2] == warprand.PROGRESS_STEPS[1]


def test_a_run_without_a_progress_callback_pays_nothing(boundary, monkeypatch):
    """Every existing caller keeps working, and the core gains no callback."""
    service, source, profile = boundary
    output = warprand.default_output_path(source, "Goku")

    def refusing_planner(image, matched_profile, seed):
        raise WarpRandomizerError("stop at the long phase")

    monkeypatch.setattr(
        warprand.WarpRandomizerService, "_profile_for", lambda self, ident: profile
    )
    monkeypatch.setattr(warprand, "plan_warp_randomization", refusing_planner)

    with pytest.raises(warprand.WarpRandomizerAppError):
        service.randomize_warps(source, output, "Goku")
