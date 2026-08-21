"""Dynamic exact-object identity for the bounded ROM-009 runtime trace."""

from __future__ import annotations

from tools.runtime.rom007_factory_probe import execution_target
from tools.runtime.rom008_object_trace import (
    MANAGER,
    TARGET_FACTORY_RAW,
    ExactObjectTracker,
    LoadIdentity,
    ObjectEvent,
)


POINT_QUERY_CALLSITE_TARGETS = {
    0x08006E4E: 0x080126D4,
    0x08021DFE: 0x080126D4,
    0x08021E06: 0x080126D4,
    0x08012AEC: 0x080127AE,
    0x08022142: 0x08012846,
}
SCHEDULER_PREDECESSOR_CALLSITE_TARGETS = {
    0x08012DCA: 0x08012A24,
    0x08012F84: 0x08012A24,
    0x08013196: 0x08012A24,
    0x08013306: 0x08012A24,
    0x0801A2DC: 0x080220D8,
}
POINT_SCHEDULER_GUARD_PC = 0x08021DF0
QUERY_CAPABLE_CALLER_ENTRIES = (0x08006E3C, 0x08012A24, 0x08021CC0, 0x080220D8)
PRECALLER_GUARD_PCS = (0x08012A36, 0x08021CC8)
SCHEDULER_FLAG_GATES = {
    0x08012DC2: (0x08012DCA, 0x08012DD0),
    0x08012F7C: (0x08012F84, 0x08012F8C),
    0x0801318E: (0x08013196, 0x0801319C),
    0x080132FE: (0x08013306, 0x0801330C),
}


def point_scheduler_guard_rejects(
    manager: int, register_counter: int, stored_counter: int
) -> bool:
    """Validate and classify the counter guard immediately before two point queries."""

    if manager != MANAGER:
        raise ValueError("scheduler guard does not reference the target registry manager")
    if register_counter != stored_counter:
        raise ValueError("scheduler guard register disagrees with its backing counter")
    return register_counter != 0


def classify_precaller_guard(pc: int, manager: int, operand: int) -> dict[str, object]:
    if manager != MANAGER:
        raise ValueError("pre-caller guard does not reference the target registry manager")
    if pc == 0x08012A36:
        rejects = operand == 0
        return {
            "guard": "0x08012A36/0x08012A3A",
            "manager": f"0x{manager:08X}",
            "operand": operand,
            "condition": "r0 == 0",
            "rejects": rejects,
            "target_attributed": True,
            "taken_path": "0x08012B20" if rejects else "0x08012A3C",
        }
    if pc == 0x08021CC8:
        rejects = operand != 0
        return {
            "guard": "0x08021CC8/0x08021CCA",
            "manager": f"0x{manager:08X}",
            "operand": operand,
            "condition": "r0 != 0",
            "rejects": rejects,
            "target_attributed": True,
            "taken_path": "0x08021CCC" if rejects else "0x08021CD0",
        }
    raise ValueError("unknown pre-caller guard PC")


def classify_scheduler_flag_gate(pc: int, halfword: int) -> dict[str, object]:
    if pc not in SCHEDULER_FLAG_GATES:
        raise ValueError("unknown scheduler flag gate PC")
    if isinstance(halfword, bool) or not isinstance(halfword, int):
        raise ValueError("scheduler flag operand must be an integer")
    if not 0 <= halfword <= 0xFFFF:
        raise ValueError("scheduler flag operand must fit u16")
    callsite, skip_target = SCHEDULER_FLAG_GATES[pc]
    rejects = not bool(halfword & 1)
    return {
        "guard": f"0x{pc:08X}",
        "operand_halfword": halfword,
        "condition": "u16[r0 + 4] bit 0 == 0",
        "rejects": rejects,
        "target_attributed": False,
        "taken_path": f"0x{skip_target:08X}" if rejects else f"0x{callsite:08X}",
        "paired_callsite": f"0x{callsite:08X}",
    }


class DynamicExactObjectTracker(ExactObjectTracker):
    """Capture the first target-family descriptor in each verified load epoch."""

    def __init__(self) -> None:
        super().__init__(
            manager=MANAGER,
            descriptor=None,  # type: ignore[arg-type]
            factory_raw=TARGET_FACTORY_RAW,
        )

    def begin_population(self, manager: int, load: LoadIdentity) -> int:
        if manager != self.manager:
            raise ValueError("unexpected registry manager")
        if load.selector != 1:
            raise ValueError("runtime load did not use selector 1")
        self.load_epoch += 1
        self._pending = False
        self.current = None
        self._load = load
        self.descriptor = None
        self.events.append(ObjectEvent("population", self.load_epoch))
        return self.load_epoch

    def accept_factory(self, descriptor: int, raw_target: int):
        if self.load_epoch == 0:
            raise ValueError("factory observed before registry population")
        if not 0x08000000 <= descriptor < 0x08800000 or descriptor % 4:
            raise ValueError("factory descriptor is not an aligned trusted-ROM address")
        target = execution_target(raw_target)
        if target != self.factory:
            raise ValueError("factory target does not match ROM-009 target family")
        if self.descriptor is None:
            self.descriptor = descriptor
        elif descriptor != self.descriptor:
            raise ValueError("factory descriptor changed within one load epoch")
        self._pending = True
        self.events.append(ObjectEvent("factory", self.load_epoch))
        return target
