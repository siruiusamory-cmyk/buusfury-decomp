import pytest

from tools.runtime.rom008_object_trace import LoadIdentity, MANAGER, TARGET_FACTORY_RAW
from tools.runtime.rom009_object_trace import (
    POINT_QUERY_CALLSITE_TARGETS,
    DynamicExactObjectTracker,
    classify_precaller_guard,
    point_scheduler_guard_rejects,
)


def dynamic_load(*, selector: int = 1) -> LoadIdentity:
    return LoadIdentity(
        map_entry_address=0x0808E2E0,
        map_entry_index=0,
        selector=selector,
        variation_source=0x08070000,
        selected_value=0x08200000,
    )


def test_dynamic_tracker_accepts_runtime_derived_load_and_first_target_descriptor():
    tracker = DynamicExactObjectTracker()
    assert tracker.begin_population(MANAGER, dynamic_load()) == 1
    assert tracker.descriptor is None

    target = tracker.accept_factory(0x08290000, TARGET_FACTORY_RAW)

    assert tracker.descriptor == 0x08290000
    assert target.raw == TARGET_FACTORY_RAW
    assert target.fetch_address == 0x08007674


def test_dynamic_tracker_rediscovers_descriptor_for_each_load_epoch():
    tracker = DynamicExactObjectTracker()
    tracker.begin_population(MANAGER, dynamic_load())
    tracker.accept_factory(0x08290000, TARGET_FACTORY_RAW)

    tracker.begin_population(
        MANAGER,
        LoadIdentity(0x0808E318, 1, 1, 0x08070010, 0x08200020),
    )

    assert tracker.descriptor is None
    tracker.accept_factory(0x08290020, TARGET_FACTORY_RAW)
    assert tracker.descriptor == 0x08290020


@pytest.mark.parametrize("descriptor", [0x02000000, 0x08290002, 0x08800000])
def test_dynamic_tracker_rejects_non_rom_or_unaligned_descriptor(descriptor):
    tracker = DynamicExactObjectTracker()
    tracker.begin_population(MANAGER, dynamic_load())
    with pytest.raises(ValueError, match="aligned trusted-ROM"):
        tracker.accept_factory(descriptor, TARGET_FACTORY_RAW)


def test_dynamic_tracker_rejects_unverified_selector():
    tracker = DynamicExactObjectTracker()
    with pytest.raises(ValueError, match="selector 1"):
        tracker.begin_population(MANAGER, dynamic_load(selector=2))


def test_verified_query_callsite_targets_are_exact():
    assert POINT_QUERY_CALLSITE_TARGETS == {
        0x08006E4E: 0x080126D4,
        0x08021DFE: 0x080126D4,
        0x08021E06: 0x080126D4,
        0x08012AEC: 0x080127AE,
        0x08022142: 0x08012846,
    }


def test_point_scheduler_guard_requires_manager_and_counter_provenance():
    assert point_scheduler_guard_rejects(MANAGER, 1, 1)
    assert not point_scheduler_guard_rejects(MANAGER, 0, 0)
    with pytest.raises(ValueError, match="registry manager"):
        point_scheduler_guard_rejects(MANAGER + 4, 1, 1)
    with pytest.raises(ValueError, match="backing counter"):
        point_scheduler_guard_rejects(MANAGER, 1, 0)


def test_precaller_guard_classification_is_pc_specific_and_fail_closed():
    assert classify_precaller_guard(0x08012A36, MANAGER, 0)["rejects"]
    assert not classify_precaller_guard(0x08012A36, MANAGER, 1)["rejects"]
    assert classify_precaller_guard(0x08021CC8, MANAGER, 1)["rejects"]
    assert not classify_precaller_guard(0x08021CC8, MANAGER, 0)["rejects"]
    with pytest.raises(ValueError, match="registry manager"):
        classify_precaller_guard(0x08012A36, MANAGER + 4, 0)
    with pytest.raises(ValueError, match="unknown"):
        classify_precaller_guard(0x08000000, MANAGER, 0)
