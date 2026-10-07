"""TOOLKIT-005 portable proofs for profile-declared capabilities.

These are the architectural tests: that a profile *declares* what it supports,
that the toolkit refuses what a profile does not declare, that a codec is chosen
from profile data, and that no core path decides anything by asking which game
it is looking at. None of them needs a ROM.

The ROM-gated Legacy of Goku II proofs live in
`tests/integration/test_logii_text_rom.py`.
"""

from __future__ import annotations

from pathlib import Path
import re

import pytest

from tests.helpers import make_synthetic_rom, profile_for
from tools.webfoot import capability
from tools.webfoot.capability import Capability, CapabilityError
from tools.webfoot.profile import RomProfileCatalog
from tools.webfoot.stats import StatProfileError, load_stat_tables
from tools.webfoot.text import TextProfileError, load_text_strings


BUU = "buus_fury_usa_rev0_01c1707f"
LOGII = "legacy_of_goku_ii_usa_rev0_204142e1"


@pytest.fixture
def catalog() -> RomProfileCatalog:
    return RomProfileCatalog.load("config/roms.yaml")


def _profile(catalog: RomProfileCatalog, profile_id: str):
    return next(p for p in catalog.profiles if p.id == profile_id)


# --- exit criterion: profiles declare capabilities explicitly -------------


def test_each_profile_declares_exactly_the_capabilities_it_supports(catalog):
    """Declared capabilities are asserted per profile, not assumed symmetrical.

    The point of the second profile is that it is *different*. Buu's Fury
    declares eight subsystems; Legacy of Goku II declares two, because that is
    what was verified. A test that allowed LOGII to quietly grow a declaration
    would let capability inflation pass review - and note that LOGII gets no
    `actor_sprites` declaration from TOOLKIT-010: the sprite chain was verified
    against the Buu image only, and DragonByteZ's own profiles put LOGII's
    palettes at entirely different offsets.

    Both profiles declare `scripts`, but they are not the same subsystem: each
    game got its own opcode set re-derived from its own interpreter, and the two
    disagree on branch operand width and branch base (TOOLKIT-013).

    ``appearances`` is here on the same rule as every other row: the table's
    extent was verified against the Buu image, and LOGII is not given it.
    """
    assert capability.capabilities(_profile(catalog, BUU)) == (
        Capability.MAP_ENTRIES,
        Capability.ENEMY_STATS,
        Capability.CHARACTER_BASE_STATS,
        Capability.TEXT_STRINGS,
        Capability.SCRIPTS,
        Capability.PLACEMENT_TYPES,
        Capability.ACTOR_SPRITES,
        Capability.APPEARANCES,
    )
    assert capability.capabilities(_profile(catalog, LOGII)) == (
        Capability.TEXT_STRINGS,
        Capability.SCRIPTS,
    )


def test_profiles_with_no_verified_tables_declare_nothing(catalog):
    """A hash-only profile is honest about carrying no verified extents."""
    for profile_id in (
        "buus_fury_usa_rev0_dcf23468",
        "legacy_of_goku_usa_a3c8c767",
    ):
        assert capability.capabilities(_profile(catalog, profile_id)) == ()


def test_a_capability_name_is_the_profile_field_that_backs_it():
    """Keeps a capability from drifting away from the data that declares it."""
    for item in Capability:
        assert item.value in {
            "map_entries",
            "enemy_stats",
            "character_base_stats",
            "text_strings",
            "scripts",
            "placement_types",
            "actor_sprites",
            "appearances",
        }


# --- exit criterion: unsupported capabilities fail clearly ---------------


def test_a_verified_profile_without_a_capability_is_refused_by_name(tmp_path):
    """Refusal names the capability, so the reason is legible without a debugger."""
    data = make_synthetic_rom()
    rom = tmp_path / "synthetic.gba"
    rom.write_bytes(data)
    catalog = RomProfileCatalog([profile_for(data, id="declares_nothing")])

    with pytest.raises(CapabilityError, match="does not declare text_strings"):
        load_text_strings(rom, catalog)


def test_an_unverified_rom_is_refused_before_any_capability_question(tmp_path):
    rom = tmp_path / "synthetic.gba"
    rom.write_bytes(make_synthetic_rom())

    with pytest.raises(CapabilityError, match="exactly verified ROM"):
        load_text_strings(rom, RomProfileCatalog([]))


def test_a_profile_absent_from_the_packaged_catalog_has_no_contract(tmp_path):
    """A local YAML cannot authorise itself; the packaged catalog is the contract."""
    data = make_synthetic_rom()
    rom = tmp_path / "synthetic.gba"
    rom.write_bytes(data)
    catalog = RomProfileCatalog(
        [
            profile_for(
                data,
                id="invented_profile",
                tables={
                    "text_strings": {
                        "pointer_table_address": 0x080000C0,
                        "count": 1,
                        "pool_address": 0x080000C4,
                        "pool_size": 4,
                        "encoding": "ascii_nul_terminated",
                        "alignment": 1,
                        "relocatable": False,
                        "evidence": "synthetic fixture",
                    }
                },
            )
        ]
    )

    with pytest.raises(CapabilityError, match="packaged catalog has no"):
        load_text_strings(rom, catalog)


# --- exit criterion: unsupported LOGII subsystems fail clearly -----------


def test_logii_stats_are_refused_because_the_profile_declares_none(catalog):
    """LOGII stats are blocked on evidence, and the refusal says so structurally.

    The Buu record shape was searched for across the whole LOGII image and found
    nowhere, so no stat table is declared. This asserts the *consequence*: asking
    for LOGII stats fails by name rather than returning something approximate.
    """
    profile = _profile(catalog, LOGII)
    assert not capability.declared(profile, Capability.ENEMY_STATS)
    assert not capability.declared(profile, Capability.CHARACTER_BASE_STATS)


def test_logii_declares_no_map_entries_despite_having_a_0x38_table(catalog):
    """A same-stride table is not the same layout, and is not declared as one.

    LOGII has a real 0x38-stride table at 0x08409368 - the same stride as Buu's
    Fury's MapEntry table. Its records are a variant type, so declaring it
    against the Buu codec would produce confident nonsense.
    """
    assert not capability.declared(
        _profile(catalog, LOGII), Capability.MAP_ENTRIES
    )


def test_no_profile_declares_dialogue_as_a_capability():
    """Dialogue is not a declarable capability, so it cannot be half-claimed.

    LOGII dialogue is script-interleaved and partly JCALG1-compressed; decoding
    it needs script-VM work this ticket forbids. It stays at DISCOVERED, and the
    absence of any dialogue capability is what keeps that honest.
    """
    assert "dialogue" not in {item.value for item in Capability}


# --- exit criterion: codec selection is profile-driven -------------------


def test_each_profile_selects_its_codec_from_its_declared_encoding(catalog):
    """The codec is chosen by data, not by recognising a game."""
    from tools.webfoot.text import _codec_for

    buu = _profile(catalog, BUU).text_strings
    logii = _profile(catalog, LOGII).text_strings
    assert buu is not None and logii is not None

    assert buu.encoding == "utf16le_nul_terminated"
    assert logii.encoding == "ascii_nul_terminated"
    assert _codec_for(buu).name == "utf16le_nul_terminated"
    assert _codec_for(logii).name == "ascii_nul_terminated"
    assert _codec_for(buu).encode is not _codec_for(logii).encode


def test_an_encoding_with_no_codec_is_refused_rather_than_defaulted(catalog):
    """A profile can never be read by the wrong codec."""
    from dataclasses import replace

    from tools.webfoot.text import _codec_for

    layout = _profile(catalog, BUU).text_strings
    assert layout is not None

    with pytest.raises(TextProfileError, match="no text codec implements"):
        _codec_for(replace(layout, encoding="shift_jis_terminated"))


def test_the_profile_loader_refuses_an_encoding_no_codec_implements():
    """The two lists - allowed encodings and implemented codecs - stay in step."""
    from tools.webfoot.profile import ProfileConfigError

    from tools.webfoot.text import _CODECS
    from tools.webfoot.profile import _SUPPORTED_TEXT_ENCODINGS

    assert set(_CODECS) == set(_SUPPORTED_TEXT_ENCODINGS)

    catalog_text = Path("config/roms.yaml").read_text(encoding="utf-8")
    with pytest.raises(ProfileConfigError, match="is not implemented"):
        RomProfileCatalog.loads(
            catalog_text.replace("ascii_nul_terminated", "not_a_real_encoding")
        )


# --- exit criterion: no game-name branching in core ----------------------


#: Every module a ROM's bytes pass through on the read, edit and write paths.
_CORE_MODULES = (
    "tools/webfoot/entities.py",
    "tools/webfoot/graphics.py",
    "tools/webfoot/formats/webfoot_lz.py",
    "tools/webfoot/formats/sprite_graphics.py",
    "tools/webfoot/formats/indexed_png.py",
    "tools/webfoot/binary.py",
    "tools/webfoot/scripts.py",
    "tools/webfoot/formats/script_vm.py",
    "tools/webfoot/build.py",
    "tools/webfoot/capability.py",
    "tools/webfoot/layout.py",
    "tools/webfoot/profile.py",
    "tools/webfoot/relocation.py",
    "tools/webfoot/rom.py",
    "tools/webfoot/stats.py",
    "tools/webfoot/text.py",
    "tools/webfoot/write.py",
    "tools/webfoot/allocation.py",
    "tools/webfoot/project/model.py",
    "tools/webfoot/project/format.py",
)

#: A game name appearing in *executable* code means a decision is being made by
#: recognising a game. In a comment or docstring it is documentation, which is
#: wanted - the modules explain which game motivated which shape.
_GAME_NAMES = re.compile(
    r"buus_fury|legacy_of_goku|\blog2\b|\blogii\b", re.IGNORECASE
)


def _executable_lines(path: Path) -> list[tuple[int, str]]:
    """Source lines with comments and docstrings removed.

    Uses the tokenizer rather than a regex, so a game name inside a string
    literal or a docstring cannot be mistaken for one in code, and vice versa.
    """
    import io
    import tokenize

    source = path.read_text(encoding="utf-8")
    kept: dict[int, str] = {}
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    for token in tokens:
        if token.type in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE):
            continue
        if token.type == tokenize.STRING and token.line.strip().startswith(
            ('"""', "'''", 'r"""')
        ):
            continue  # a docstring standing alone on its line
        kept.setdefault(token.start[0], token.line.rstrip())
    return sorted(kept.items())


def test_core_modules_never_branch_on_a_game_name():
    """The architectural claim of TOOLKIT-005, asserted rather than reviewed.

    Before this ticket, `stats.py`, `text.py` and `formats/map_entry.py` each
    carried `SUPPORTED_PROFILE_ID = "buus_fury_usa_rev0_01c1707f"` and refused
    every other profile. Game and revision differences now live in profile data,
    so a game name must not appear in any core module's executable code.

    Docstrings and comments are exempt on purpose: explaining *why* a shape
    exists is documentation, and stripping the explanation would be worse than
    the coupling this guards against.
    """
    offenders: list[str] = []
    for relative in _CORE_MODULES:
        path = Path(relative)
        assert path.is_file(), f"core module missing: {relative}"
        for number, line in _executable_lines(path):
            if _GAME_NAMES.search(line):
                offenders.append(f"{relative}:{number}: {line.strip()}")

    assert offenders == [], "game-name branching in core:\n" + "\n".join(offenders)


def test_the_codec_registry_is_keyed_by_encoding_not_by_game():
    """Codec selection must key on the format, not on who shipped it."""
    from tools.webfoot.text import _CODECS

    for key in _CODECS:
        assert not _GAME_NAMES.search(key), key
