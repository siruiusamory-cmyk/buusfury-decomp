from pathlib import Path

import pytest

from tools.runtime.rom008_object_trace import (
    MANAGER,
    TARGET_DESCRIPTOR,
    TARGET_FACTORY_RAW,
    SUPPORTED_CALLBACK_CALLS,
    ExactObjectTracker,
    LoadIdentity,
    ObjectEvent,
    event_kinds,
    private_working_paths,
    query_caller_from_lr,
    removal_count_commit_is_valid,
    removal_path_reaches_commit,
    reset_count_commit_is_valid,
    same_identity_epoch,
    signed_halfwords,
    thumb_fetch_is_valid,
    validate_complete_timeline,
)


def target_load(*, selector: int = 1) -> LoadIdentity:
    return LoadIdentity(
        map_entry_address=0x0808EB68,
        map_entry_index=39,
        selector=selector,
        variation_source=0x080753F0,
        selected_value=0x08294968,
    )


def live_target() -> tuple[ExactObjectTracker, object]:
    tracker = ExactObjectTracker()
    tracker.begin_population(MANAGER, target_load())
    tracker.accept_factory(TARGET_DESCRIPTOR, TARGET_FACTORY_RAW)
    identity = tracker.commit_insertion(
        manager=MANAGER,
        returned_object=0x0203DEBC,
        old_count=0,
        new_count=1,
        slot=0x03002A68,
    )
    return tracker, identity


def test_target_object_is_discovered_from_factory_return_and_slot():
    tracker, identity = live_target()
    assert identity.object_pointer == 0x0203DEBC
    assert identity.registry_slot == 0x03002A68
    assert identity.factory.raw == TARGET_FACTORY_RAW
    assert identity.factory.fetch_address == 0x08007674
    assert identity.factory.state == "Thumb"
    assert tracker.current == identity
    assert identity.load == target_load()


@pytest.mark.parametrize(
    ("descriptor", "raw", "message"),
    [
        (0x08294930, TARGET_FACTORY_RAW, "descriptor"),
        (TARGET_DESCRIPTOR, 0x080072CD, "factory target"),
    ],
)
def test_wrong_descriptor_or_factory_is_rejected(descriptor, raw, message):
    tracker = ExactObjectTracker()
    tracker.begin_population(MANAGER, target_load())
    with pytest.raises(ValueError, match=message):
        tracker.accept_factory(descriptor, raw)


def test_wrong_manager_slot_or_count_fails_closed():
    tracker = ExactObjectTracker()
    tracker.begin_population(MANAGER, target_load())
    tracker.accept_factory(TARGET_DESCRIPTOR, TARGET_FACTORY_RAW)
    with pytest.raises(ValueError, match="manager"):
        tracker.commit_insertion(
            manager=0x03002A68,
            returned_object=0x0203DEBC,
            old_count=0,
            new_count=1,
            slot=0x03002A6C,
        )

    tracker = ExactObjectTracker()
    tracker.begin_population(MANAGER, target_load())
    tracker.accept_factory(TARGET_DESCRIPTOR, TARGET_FACTORY_RAW)
    with pytest.raises(ValueError, match="slot"):
        tracker.commit_insertion(
            manager=MANAGER,
            returned_object=0x0203DEBC,
            old_count=0,
            new_count=1,
            slot=0x03002A6C,
        )


def test_generation_change_invalidates_stale_object_pointer():
    tracker, old = live_target()
    tracker.begin_population(MANAGER, target_load())
    assert tracker.current is None
    assert not same_identity_epoch(
        old, load_epoch=tracker.load_epoch, object_pointer=old.object_pointer
    )
    with pytest.raises(ValueError, match="no live"):
        tracker.accept_aabb(old.object_pointer)


def test_reset_and_exact_removal_retire_only_current_target():
    tracker, identity = live_target()
    assert not tracker.retire_removal(
        manager=MANAGER, object_pointer=identity.object_pointer + 0x70
    )
    assert tracker.current == identity
    assert tracker.retire_removal(
        manager=MANAGER, object_pointer=identity.object_pointer
    )
    assert tracker.current is None


def test_population_rejects_unverified_selector():
    tracker = ExactObjectTracker()
    with pytest.raises(ValueError, match="verified ROM-008 target"):
        tracker.begin_population(MANAGER, target_load(selector=2))


@pytest.mark.parametrize(
    "load",
    [
        LoadIdentity(0x0808EB30, 39, 1, 0x080753F0, 0x08294968),
        LoadIdentity(0x0808EB68, 38, 1, 0x080753F0, 0x08294968),
        LoadIdentity(0x0808EB68, 39, 1, 0x08075278, 0x08294968),
        LoadIdentity(0x0808EB68, 39, 1, 0x080753F0, 0x08295C58),
    ],
)
def test_population_rejects_map_or_selected_value_provenance_mismatch(load):
    tracker = ExactObjectTracker()
    with pytest.raises(ValueError, match="verified ROM-008 target"):
        tracker.begin_population(MANAGER, load)


def test_registry_count_mismatch_is_rejected():
    tracker = ExactObjectTracker()
    tracker.begin_population(MANAGER, target_load())
    tracker.accept_factory(TARGET_DESCRIPTOR, TARGET_FACTORY_RAW)
    with pytest.raises(ValueError, match="increment"):
        tracker.commit_insertion(
            manager=MANAGER,
            returned_object=0x0203DEBC,
            old_count=0,
            new_count=2,
            slot=0x03002A68,
        )


def test_even_factory_raw_preserves_arm_state_and_is_rejected_for_target():
    tracker = ExactObjectTracker()
    tracker.begin_population(MANAGER, target_load())
    with pytest.raises(ValueError, match="factory target"):
        tracker.accept_factory(TARGET_DESCRIPTOR, 0x08007674)


def test_lifecycle_retirement_requires_committed_count_transition():
    assert reset_count_commit_is_valid(0)
    assert not reset_count_commit_is_valid(1)
    assert removal_count_commit_is_valid(2, 1)
    assert not removal_count_commit_is_valid(2, 2)
    assert not removal_count_commit_is_valid(0, 0)


def test_removal_path_token_rejects_interleaved_or_incomplete_invocation():
    assert removal_path_reaches_commit([0x0801268C, 0x08012690, 0x080126AC])
    assert not removal_path_reaches_commit([0x0801268C, 0x08048488, 0x080126AC])
    assert not removal_path_reaches_commit([0x0801268C, 0x08012690])


def test_known_reset_and_callback_fetches_require_thumb_state():
    assert thumb_fetch_is_valid(0x08048488, 0x20, 0x08048488)
    assert thumb_fetch_is_valid(0x08012784, 0x20, 0x08012784)
    assert not thumb_fetch_is_valid(0x08048488, 0, 0x08048488)
    assert not thumb_fetch_is_valid(0x08012784, 0, 0x08012784)
    assert not thumb_fetch_is_valid(0x08012786, 0x20, 0x08012784)


def test_only_callbacks_with_direct_object_argument_are_supported():
    assert set(SUPPORTED_CALLBACK_CALLS) == {0x08012784, 0x0801279C}
    assert 0x08012832 not in SUPPORTED_CALLBACK_CALLS
    assert 0x080128B2 not in SUPPORTED_CALLBACK_CALLS

    tracker, identity = live_target()
    assert tracker.retire_reset() == identity
    assert tracker.current is None


def test_wrong_object_aabb_and_callback_are_rejected():
    tracker, identity = live_target()
    with pytest.raises(ValueError, match="does not match"):
        tracker.accept_aabb(identity.object_pointer + 0x70)
    with pytest.raises(ValueError, match="AABB"):
        tracker.accept_callback(identity.object_pointer)
    tracker.accept_aabb(identity.object_pointer)
    with pytest.raises(ValueError, match="does not match"):
        tracker.accept_callback(identity.object_pointer + 0x70)


def test_exact_aabb_then_callback_completes_same_object_timeline():
    tracker, identity = live_target()
    tracker.accept_aabb(identity.object_pointer)
    tracker.accept_callback(identity.object_pointer)
    assert validate_complete_timeline(tracker.events)
    assert event_kinds(tracker.events) == (
        "population",
        "factory",
        "live",
        "aabb",
        "callback",
    )


def test_followup_callback_requires_prior_exact_callback():
    tracker, identity = live_target()
    tracker.accept_aabb(identity.object_pointer)
    with pytest.raises(ValueError, match="AABB"):
        tracker.accept_callback(identity.object_pointer, followup=True)
    tracker.accept_callback(identity.object_pointer)
    tracker.accept_callback(identity.object_pointer, followup=True)


def test_incomplete_or_wrong_object_timeline_is_rejected():
    assert not validate_complete_timeline(
        [
            ObjectEvent("population", 1),
            ObjectEvent("factory", 1),
            ObjectEvent("live", 1, 0x0203DEBC),
            ObjectEvent("aabb", 1, 0x0203DDD4),
            ObjectEvent("callback", 1, 0x0203DDD4),
        ]
    )
    assert not validate_complete_timeline(
        [
            ObjectEvent("population", 1),
            ObjectEvent("factory", 1),
            ObjectEvent("live", 1, 0x0203DEBC),
        ]
    )


def test_reset_between_live_and_callback_rejects_old_generation_chain():
    events = [
        ObjectEvent("population", 1),
        ObjectEvent("factory", 1),
        ObjectEvent("live", 1, 0x0203DEBC),
        ObjectEvent("reset", 1, 0x0203DEBC),
        ObjectEvent("aabb", 1, 0x0203DEBC),
        ObjectEvent("callback", 1, 0x0203DEBC),
    ]
    assert not validate_complete_timeline(events)


def test_query_caller_preserves_thumb_semantics_only_for_execution_address():
    assert query_caller_from_lr(0x08006E53) == 0x08006E4E
    assert query_caller_from_lr(0x08006E52) == 0x08006E4E
    with pytest.raises(ValueError, match="integer"):
        query_caller_from_lr(True)


def test_signed_halfword_decoder_handles_runtime_bounds():
    payload = b"\x50\x02\x88\x00\x59\x02\xf1\x00"
    assert signed_halfwords(payload) == (592, 136, 601, 241)
    with pytest.raises(ValueError, match="even"):
        signed_halfwords(b"\x00")


def test_private_working_paths_never_return_original_sources(tmp_path: Path):
    originals = tmp_path / "private"
    run_root = tmp_path / "build" / "rom008" / "run"
    state = originals / "original.ss1"
    save = originals / "original.sav"
    state_work, save_work = private_working_paths(
        state_source=state,
        save_source=save,
        run_root=run_root,
        rom_name="verified.gba",
    )
    assert state_work != state.resolve()
    assert save_work != save.resolve()
    assert state_work.is_relative_to(run_root.resolve())
    assert save_work.is_relative_to(run_root.resolve())


def test_private_working_paths_reject_original_artifact_directory(tmp_path: Path):
    state = tmp_path / "original.ss1"
    save = tmp_path / "original.sav"
    with pytest.raises(ValueError, match="original artifact directory"):
        private_working_paths(
            state_source=state,
            save_source=save,
            run_root=tmp_path,
            rom_name="verified.gba",
        )
