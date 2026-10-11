"""The authored-dialogue registry is read through the ACTIVE profile.

The defect this pins: `textsurface.load_text_surface` took the FIRST registry
entry's `table_offset` for whatever profile was open. With one entry that is
indistinguishable from a profile-scoped read; with a second entry carrying a
different offset the surface would read the wrong container table. These tests
register a second entry and measure which offset each profile is answered with.
"""

from __future__ import annotations

from dataclasses import dataclass

from tools.dragonbyte import textsurface as ts
from tools.webfoot import compressed_dialogue as cd

CANONICAL = "buus_fury_usa_rev0_01c1707f"
OTHER = "legacy_of_goku_usa_a3c8c767"


@dataclass(frozen=True)
class _Profile:
    id: str
    scripts: tuple = ()


class _Maps:
    """The one attribute `PlacementEvents` reads off a map corpus."""

    profile = _Profile("synthetic")


#: A second profile's own record, at an offset that is not the canonical one.
OTHER_TARGET = cd.CompressedDialogueTarget(
    "other-record", 1, 0x123456, 0x02002641, 0x132, 0x20, OTHER,
)


def _registry_with_second_profile(monkeypatch) -> dict:
    registry = dict(cd.AUTHORED_DIALOGUE_TARGETS)
    registry[OTHER_TARGET.name] = OTHER_TARGET
    monkeypatch.setattr(cd, "AUTHORED_DIALOGUE_TARGETS", registry)
    return registry


def _no_string_table(*_args, **_kwargs):
    raise ValueError("this synthetic image carries no string table")


def test_the_registry_entry_count_is_the_live_versus_latent_measurement():
    assert len(cd.AUTHORED_DIALOGUE_TARGETS) == 1
    only = next(iter(cd.AUTHORED_DIALOGUE_TARGETS.values()))
    assert only.name == "goku-greeting"
    assert only.profile_id == CANONICAL
    assert only.table_offset == 0x7B5B64


def test_each_profile_is_answered_with_its_own_entry(monkeypatch):
    _registry_with_second_profile(monkeypatch)

    canonical = cd.authored_dialogue_targets(_Profile(CANONICAL))
    other = cd.authored_dialogue_targets(_Profile(OTHER))

    assert canonical == (cd.AUTHORED_DIALOGUE_TARGETS["goku-greeting"],)
    assert other == (OTHER_TARGET,)
    assert canonical[0].table_offset == 0x7B5B64
    assert other[0].table_offset == 0x123456


def test_a_profile_with_no_entry_gets_no_offset_rather_than_another_profiles(monkeypatch):
    _registry_with_second_profile(monkeypatch)

    assert cd.authored_dialogue_targets(_Profile("legacy_of_goku_ii_usa_rev0_204142e1")) == ()


def test_the_surface_reads_the_active_profiles_table_offset(monkeypatch, tmp_path):
    """The load path itself, which is where the first-entry read lived."""
    _registry_with_second_profile(monkeypatch)
    seen: list[int] = []

    def fake_selectors(image: bytes, table_offset: int) -> tuple[int, ...]:
        seen.append(table_offset)
        return ()

    monkeypatch.setattr(ts, "container_selectors", fake_selectors)
    monkeypatch.setattr(ts, "load_text_strings", _no_string_table)
    monkeypatch.setattr(ts, "load_maps", lambda *a, **k: _Maps())
    monkeypatch.setattr(ts, "script_families", lambda *a, **k: ())
    monkeypatch.setattr(ts, "load_scripts", lambda *a, **k: None)

    for profile, expected in ((_Profile(CANONICAL), 0x7B5B64), (_Profile(OTHER), 0x123456)):
        seen.clear()
        surface = ts.load_text_surface(
            tmp_path / "synthetic.gba", None, None, profile, bytes(0x200000)
        )
        assert surface.container_table_offset == expected
        assert seen == [expected]
