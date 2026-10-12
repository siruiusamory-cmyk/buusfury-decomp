"""Every artifact that states a published map figure states the registry's one.

The 2026-10-12 retro named the 440/12 maps class: a published map count that
silently stopped matching what the measuring code computes. The registry is the
authority for the figures, the site and the coverage census quote it, so this
half of the guard is ROM-free and runs in CI. The other half,
``tests/integration/test_published_numbers_rom.py``, holds the registry itself
to the canonical image.
"""

from __future__ import annotations

from tests import published_numbers as published


def test_the_registry_states_one_map_triple_that_adds_up() -> None:
    """One number per fact, and the parts account for the whole."""
    layout = published.capability("layout")["measurements"]
    browser = published.capability("map-browser")["measurements"]
    figures = published.registry_figures()

    assert layout["mapsViewable"] == browser["mapsViewable"], (
        "two capabilities state a different number of viewable maps")
    assert layout["editableMaps"] + layout["readOnlyMaps"] == layout["mapsViewable"], (
        "the editable and read-only map counts do not account for the viewable maps")
    assert figures["editable"] + figures["read_only"] == figures["maps"]
    assert figures["dominant_slots"] <= figures["layer_slots"], (
        "the dominant chunk-grid form cannot outnumber the layer slots")
    for name, value in layout.items():
        assert isinstance(value, int) and value > 0, (name, value)


def test_every_published_map_figure_quotes_the_registry() -> None:
    """The site and the census may restate a figure, never recompute one."""
    missing = published.missing_quotes(published.registry_figures())
    assert not missing, (
        "a published figure is no longer the registry's, so the artifact was "
        "written by hand and has drifted:\n  " + "\n  ".join(missing)
    )


def test_the_census_states_the_registry_it_read() -> None:
    """The census baseline is a published statement about this registry."""
    registry = published.registry()
    capabilities = registry["capabilities"]
    baseline = published.coverage()["baseline"]["capability_registry"]

    assert registry["track"]["capabilityTotal"] == len(capabilities), (
        "the registry's track total is not the number of capabilities it lists")
    counted = {
        "capabilities": len(capabilities),
        "state_shipped": sum(1 for one in capabilities if one["state"] == "shipped"),
        "proof_runtime": sum(1 for one in capabilities if one.get("proof") == "runtime"),
        "proof_application": sum(
            1 for one in capabilities if one.get("proof") == "application"),
    }
    for name, value in counted.items():
        assert baseline[name] == value, (
            f"the coverage census states {name}={baseline[name]}, "
            f"the registry has {value}")
