"""Fail-closed identity helpers for the ROM-008 exact-object runtime trace.

The target object is discovered from the factory return in each replay.  A raw
EWRAM address is never treated as a stable identity across registry population,
reset, or removal events.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from tools.runtime.rom007_factory_probe import (
    ExecutionTarget,
    execution_target,
    registry_slot,
)
from tools.runtime.rom006_gdb_probe import THUMB_STATE_BIT


MANAGER = 0x03002A64
TARGET_DESCRIPTOR = 0x08294948
TARGET_FACTORY_RAW = 0x08007675
TARGET_MAP_ENTRY_ADDRESS = 0x0808EB68
TARGET_MAP_ENTRY_INDEX = 39
TARGET_SELECTOR = 1
TARGET_VARIATION_SOURCE = 0x080753F0
TARGET_SELECTED_VALUE = 0x08294968

RESET_PC = 0x08048488
POPULATION_PC = 0x08012664
FACTORY_VENEER_PC = 0x08046AA2
FACTORY_RETURN_PC = 0x08012678
INSERTION_COMMIT_PC = 0x08012682
REMOVAL_PC = 0x0801268A
REMOVAL_COMMIT_PC = 0x080126AC

POINT_QUERY_ENTRY_PC = 0x080126D4
POINT_QUERY_PRECURSOR_PC = 0x080126F4
POINT_QUERY_PRECURSOR_RETURN_PC = 0x080126F8
SECOND_QUERY_ENTRY_PC = 0x080127AE
EXPANDED_QUERY_ENTRY_PC = 0x08012846

AABB_CANDIDATE_PCS = (0x0801273C, 0x080127F4, 0x08012864)
CALLBACK_CALLS = {
    0x08012784: (3, 0x08012788, "point_predicate"),
    0x0801279C: (3, 0x080127A0, "point_action"),
    0x08012832: (2, 0x08012836, "second_predicate"),
    0x080128B2: (1, 0x080128B6, "expanded_predicate"),
}
SUPPORTED_CALLBACK_CALLS = {
    0x08012784: CALLBACK_CALLS[0x08012784],
    0x0801279C: CALLBACK_CALLS[0x0801279C],
}


@dataclass(frozen=True, slots=True)
class LoadIdentity:
    map_entry_address: int
    map_entry_index: int
    selector: int
    variation_source: int
    selected_value: int


@dataclass(frozen=True, slots=True)
class ObjectIdentity:
    manager: int
    load_epoch: int
    load: LoadIdentity
    insertion_serial: int
    descriptor: int
    factory: ExecutionTarget
    object_pointer: int
    registry_slot: int
    old_count: int
    new_count: int


@dataclass(frozen=True, slots=True)
class ObjectEvent:
    kind: str
    load_epoch: int
    object_pointer: int | None = None


def target_load_is_valid(load: LoadIdentity) -> bool:
    return load == LoadIdentity(
        map_entry_address=TARGET_MAP_ENTRY_ADDRESS,
        map_entry_index=TARGET_MAP_ENTRY_INDEX,
        selector=TARGET_SELECTOR,
        variation_source=TARGET_VARIATION_SOURCE,
        selected_value=TARGET_SELECTED_VALUE,
    )


def reset_count_commit_is_valid(count_after: int) -> bool:
    return count_after == 0


def removal_count_commit_is_valid(count_before: int, count_after: int) -> bool:
    return count_before > 0 and count_after == count_before - 1


def thumb_fetch_is_valid(pc: int, cpsr: int, expected_pc: int) -> bool:
    return pc == expected_pc and bool(cpsr & THUMB_STATE_BIT)


def removal_path_reaches_commit(pcs: Sequence[int]) -> bool:
    if not pcs or len(pcs) > 128 or pcs[-1] != REMOVAL_COMMIT_PC:
        return False
    forbidden = {RESET_PC, POPULATION_PC, REMOVAL_PC}
    return not any(pc in forbidden for pc in pcs[:-1])


class ExactObjectTracker:
    """Track one factory instance and reject stale or unrelated objects."""

    def __init__(
        self,
        *,
        manager: int = MANAGER,
        descriptor: int = TARGET_DESCRIPTOR,
        factory_raw: int = TARGET_FACTORY_RAW,
    ) -> None:
        self.manager = manager
        self.descriptor = descriptor
        self.factory = execution_target(factory_raw)
        self.load_epoch = 0
        self._serial = 0
        self._pending = False
        self._load: LoadIdentity | None = None
        self.current: ObjectIdentity | None = None
        self.events: list[ObjectEvent] = []

    def begin_population(self, manager: int, load: LoadIdentity) -> int:
        if manager != self.manager:
            raise ValueError("unexpected registry manager")
        if not target_load_is_valid(load):
            raise ValueError("load identity does not match the verified ROM-008 target")
        self.load_epoch += 1
        self._pending = False
        self.current = None
        self._load = load
        self.events.append(ObjectEvent("population", self.load_epoch))
        return self.load_epoch

    def accept_factory(self, descriptor: int, raw_target: int) -> ExecutionTarget:
        if self.load_epoch == 0:
            raise ValueError("factory observed before registry population")
        if descriptor != self.descriptor:
            raise ValueError("factory descriptor does not match ROM-008 target")
        target = execution_target(raw_target)
        if target != self.factory:
            raise ValueError("factory target does not match ROM-008 target")
        self._pending = True
        self.events.append(ObjectEvent("factory", self.load_epoch))
        return target

    def commit_insertion(
        self,
        *,
        manager: int,
        returned_object: int,
        old_count: int,
        new_count: int,
        slot: int,
    ) -> ObjectIdentity:
        if not self._pending:
            raise ValueError("registry insertion has no accepted target factory")
        if manager != self.manager:
            raise ValueError("registry insertion used an unexpected manager")
        if not 0x02000000 <= returned_object < 0x02040000:
            raise ValueError("factory return is outside EWRAM")
        if new_count != old_count + 1:
            raise ValueError("registry count did not increment by one")
        if slot != registry_slot(manager, old_count):
            raise ValueError("registry slot does not match manager and old count")
        if self._load is None:
            raise ValueError("registry insertion has no verified load identity")
        self._serial += 1
        identity = ObjectIdentity(
            manager=manager,
            load_epoch=self.load_epoch,
            load=self._load,
            insertion_serial=self._serial,
            descriptor=self.descriptor,
            factory=self.factory,
            object_pointer=returned_object,
            registry_slot=slot,
            old_count=old_count,
            new_count=new_count,
        )
        self.current = identity
        self._pending = False
        self.events.append(ObjectEvent("live", self.load_epoch, returned_object))
        return identity

    def retire_reset(self) -> ObjectIdentity | None:
        retired = self.current
        self._pending = False
        self.current = None
        self.events.append(
            ObjectEvent(
                "reset",
                self.load_epoch,
                retired.object_pointer if retired is not None else None,
            )
        )
        return retired

    def retire_removal(self, *, manager: int, object_pointer: int) -> bool:
        if manager != self.manager:
            raise ValueError("registry removal used an unexpected manager")
        if self.current is None or object_pointer != self.current.object_pointer:
            return False
        self.events.append(ObjectEvent("removal", self.load_epoch, object_pointer))
        self.current = None
        self._pending = False
        return True

    def require_current_object(self, object_pointer: int) -> ObjectIdentity:
        if self.current is None:
            raise ValueError("no live target object exists in this load epoch")
        if object_pointer != self.current.object_pointer:
            raise ValueError("runtime object does not match current target identity")
        return self.current

    def accept_aabb(self, object_pointer: int) -> ObjectIdentity:
        identity = self.require_current_object(object_pointer)
        self.events.append(ObjectEvent("aabb", self.load_epoch, object_pointer))
        return identity

    def accept_callback(
        self, object_pointer: int, *, followup: bool = False
    ) -> ObjectIdentity:
        identity = self.require_current_object(object_pointer)
        expected_kind = "callback" if followup else "aabb"
        if not self.events or self.events[-1] != ObjectEvent(
            expected_kind, self.load_epoch, object_pointer
        ):
            raise ValueError("callback is not immediately attributable to a target AABB event")
        self.events.append(ObjectEvent("callback", self.load_epoch, object_pointer))
        return identity


def validate_complete_timeline(events: Sequence[ObjectEvent]) -> bool:
    """Require one same-epoch factory/live/AABB/callback chain in order."""

    required = ("population", "factory", "live", "aabb", "callback")
    position = 0
    load_epoch: int | None = None
    object_pointer: int | None = None
    for event in events:
        if event.kind == "reset" or event.kind == "removal":
            if load_epoch == event.load_epoch and position < len(required):
                position = 0
                load_epoch = None
                object_pointer = None
            continue
        if event.kind != required[position]:
            continue
        if position == 0:
            load_epoch = event.load_epoch
        elif event.load_epoch != load_epoch:
            position = 0
            load_epoch = None
            object_pointer = None
            continue
        if event.kind == "live":
            object_pointer = event.object_pointer
        if event.kind in ("aabb", "callback") and event.object_pointer != object_pointer:
            position = 0
            load_epoch = None
            object_pointer = None
            continue
        position += 1
        if position == len(required):
            return True
    return False


def query_caller_from_lr(raw_lr: int) -> int:
    if isinstance(raw_lr, bool) or not isinstance(raw_lr, int):
        raise ValueError("LR must be an integer execution address")
    fetch_lr = raw_lr & ~1
    if fetch_lr < 4:
        raise ValueError("LR is too small to contain a call return")
    return fetch_lr - 4


def signed_halfwords(payload: bytes) -> tuple[int, ...]:
    if len(payload) % 2:
        raise ValueError("signed-halfword payload must have even length")
    return tuple(
        int.from_bytes(payload[index : index + 2], "little", signed=True)
        for index in range(0, len(payload), 2)
    )


def private_working_paths(
    *, state_source: Path, save_source: Path, run_root: Path, rom_name: str
) -> tuple[Path, Path]:
    state = state_source.resolve()
    save = save_source.resolve()
    root = run_root.resolve()
    if root == state.parent or root == save.parent:
        raise ValueError("working directory must not be an original artifact directory")
    state_work = root / "input.ss1"
    save_work = root / "save" / Path(rom_name).with_suffix(".sav").name
    if state_work in (state, save) or save_work in (state, save):
        raise ValueError("working paths must not overwrite original artifacts")
    return state_work, save_work


def same_identity_epoch(
    identity: ObjectIdentity, *, load_epoch: int, object_pointer: int
) -> bool:
    return (
        identity.load_epoch == load_epoch
        and identity.object_pointer == object_pointer
    )


def event_kinds(events: Iterable[ObjectEvent]) -> tuple[str, ...]:
    return tuple(event.kind for event in events)
