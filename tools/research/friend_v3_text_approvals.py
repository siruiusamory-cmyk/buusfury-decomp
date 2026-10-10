"""The owner-approved text-table edits, as tracked constants.

WHY A TRACKED CONSTANT RATHER THAN A MANIFEST FIELD. A verifier that reads the expected text
out of the manifest is checking the artifact against itself: the builder wrote both. The
approved wording therefore lives here, where a verifier and a test can recompute it, and the
manifest's own copy of it is treated as provenance rather than as authority.

Each entry carries the slot, the text the image held before the approval (the guard that the
write lands where the approval says), the approved replacement, and the approval's own
identity so a reader can trace the wording back to the decision it came from.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ApprovedTextSlot:
    """One approved text-table slot: its identity, its old text and its approved text."""

    slot: int
    old: str
    new: str
    label: str
    approval: str


#: Slot 1083, Bulma's scanner biography. Owner decision relayed by the coordinator on
#: 2026-10-10, quoted verbatim; the Adja node that recorded the owner's wording is named in
#: the string so the approval can be found again.
APPROVED_TEXT_SLOTS: tuple[ApprovedTextSlot, ...] = (
    ApprovedTextSlot(
        slot=1083,
        old="Bulma is Yamcha's wife and Krillin and Videl's mother. She is the daughter of "
            "the Ox-King.",
        new="Bulma is Yamcha's wife and Krillin and Videl's mother. A genius inventor, she "
            "is the heiress of Capsule Corporation.",
        label="biography, Bulma",
        approval="FRIEND-V3-WT-SPLIT-CONTAINER-001 release 2.1 owner decision, 2026-10-10",
    ),
)

#: The replacements by slot, for a caller that wants the approved wording alone.
APPROVED_REPLACEMENTS = {edit.slot: edit.new for edit in APPROVED_TEXT_SLOTS}


@dataclass(frozen=True, slots=True)
class ApprovedBossRetune:
    """One approved enemy-stat retune: the record, its measured baseline, its new values."""

    selector: int
    name: str
    baseline_hp: int
    baseline_strength: int
    baseline_power: int
    baseline_endurance: int
    hp: int
    strength: int
    power: int
    approval: str

    @property
    def file_offset(self) -> int:
        return 0x711274 + self.selector * 0x1C


@dataclass(frozen=True, slots=True)
class ApprovedBossProfile:
    """One approved behaviour profile: the records it covers and the values it sets."""

    name: str
    selectors: tuple[int, ...]
    gate_radius_squared: int
    attack_radius_squared: int
    attack_percent: float
    attack_first: bool
    attack_action_row: int | None
    approval: str


#: The profile both bosses run, measured into place over five fights on 2026-10-10 and locked when
#: the owner beat it and called it good. What each value survived:
#:   gate radius 22500 (r150)  - the enemy enters the fight from further out, so he is on the
#:                               player instead of standing about.
#:   attack radius 22500       - he swings from r150. Whiffs rise, but measured landed blows rise
#:                               with them, and the owner preferred it to the tighter r60.
#:   chance 50 percent         - retail is 12. The measured cadence does NOT respond to this above
#:                               retail grade, so 50 is kept for pressure per approach, not rate.
#:   attack arm first          - THE decisive change. The hub is a first-true OR and retail puts a
#:                               passive branch in front of the attack, which is why a build that
#:                               only raised the attack's own numbers measured one landed blow in
#:                               twenty seconds.
#:   action row 204            - THE cadence change. Retail's row 206 animates at about 36 frames
#:                               per swing; row 204 measured 19.8 frames per swing with four landed
#:                               blows at 29 to 30 in the same window. The player's own cadence is
#:                               about 25 frames, so this is the owner's "chain at my speed".
#: Rows 205 and 207 to 209 were never measured, so 204 is the fastest MEASURED row, not the fastest
#: that exists. A profile is per-enemy: it copies the family's own nodes into an appended block and
#: repoints only these records' behaviour rows, so no other enemy changes.
APPROVED_BOSS_PROFILES: tuple[ApprovedBossProfile, ...] = (
    ApprovedBossProfile(
        name="relentless-fast-swing",
        selectors=(45, 85),
        gate_radius_squared=22500,
        attack_radius_squared=22500,
        attack_percent=50.0,
        attack_first=True,
        attack_action_row=204,
        approval="FRIEND-V3-WT-SPLIT-CONTAINER-001 release 3 owner scope, 2026-10-10: built by "
                 "the coordinator's instruction, measured by sweep, and accepted by the owner "
                 "after he fought it and lost",
    ),
)


#: The record's `+0x08` is the only per-enemy behaviour lever that exists: the constructor reads
#: it once and the controller push turns it into an entry in the table at 0x0870F514. Nothing
#: else in the 28 bytes carries a timing, speed or aggression value. Repointing a record's `+0x08`
#: is therefore still an unmeasured experiment and this list stays empty; the profile above
#: changes behaviour by repointing the record's behaviour ROW at a copied tree instead.
APPROVED_BOSS_BEHAVIOURS: tuple[ApprovedBossBehaviour, ...] = ()


#: The two boss retunes, sized from three measured Olibu fights (2026-10-10). A normally
#: levelled character deals 46 to 50 hit points per blow and took 4 to 9 from the retail record
#: (strength 13), 88 to 90 from strength 35, and 603 from strength 72, which killed the player in
#: two blows and so brackets their maximum hit points between 91 and 178. The bite is close to
#: cubic in the strength byte: damage is about 88 * (strength / 35) ** 3. The values below put a
#: blow at about 22 hit points, 12 to 24 percent of that bar, and the hit points at about twenty
#: of the player's blows at the measured 48 per blow. Both attack bytes are raised together
#: because which one a given attack reads is chosen by the attack descriptor, not the enemy;
#: branch A, the strength byte, is the one this enemy's attacks were measured to use.
#: Endurance is left alone: it is the DEFENDER's term, so raising it would shorten the player's
#: own damage and double-count the length the hit points already set.
APPROVED_BOSS_RETUNES: tuple[ApprovedBossRetune, ...] = (
    ApprovedBossRetune(
        selector=45, name="Hercule",
        baseline_hp=20, baseline_strength=5, baseline_power=5, baseline_endurance=5,
        hp=2500, strength=40, power=30,
        approval="FRIEND-V3-WT-SPLIT-CONTAINER-001 release 3 owner scope, 2026-10-10; his "
                 "chapter comes LATER than Olibu's. The owner fought and beat 2000/30/22 in a "
                 "cold-boot run on his own battery save, then set 2500/40/30 and locked it. "
                 "Sized from the measured Olibu bite, strength 40 predicts roughly 174 hit "
                 "points a landed blow against strength 22's measured 29; only one point of "
                 "that curve (22 -> 29) has been measured, so the prediction is arithmetic, "
                 "not a measurement, and the owner accepted it as the locked value",
    ),
    ApprovedBossRetune(
        selector=85, name="Olibu",
        baseline_hp=565, baseline_strength=13, baseline_power=0, baseline_endurance=21,
        hp=1500, strength=22, power=16,
        approval="FRIEND-V3-WT-SPLIT-CONTAINER-001 release 3 owner scope, 2026-10-10, "
                 "strength set from the measured 88 damage at strength 35 and confirmed by "
                 "the owner in play; hit points taken to 2000 then reduced by a quarter to "
                 "1500; strength taken to 15 while the relentless profile was introduced and "
                 "restored to 22 on the owner's instruction after he beat the 15 build",
    ),
)


@dataclass(frozen=True, slots=True)
class ApprovedDialogueRow:
    """One approved dialogue record: its identity, its old text and its approved wording."""

    selector: int
    start: int
    length: int
    old: str
    new: str
    label: str
    approval: str

    @property
    def key(self) -> str:
        return f"{self.selector}:{self.start}:{self.length}"


#: The two registry-scene rows the owner authored on 2026-10-10, quoted verbatim. The slot is
#: the identity: the speaker was identified from play and the record's own portrait operand
#: places it in the same conversation as the Bulma/Tulma rewrite at `2:60182` and `2:60310`.
APPROVED_DIALOGUE_ROWS: tuple[ApprovedDialogueRow, ...] = (
    ApprovedDialogueRow(
        selector=2, start=60922, length=140,
        old="I have a feeling that this is not going to be your typical tournament.",
        new="Oolong and I are debating, I say Bulma is the hotter twin!",
        label="registration scene, Master Roshi",
        approval="FRIEND-V3-WT-SPLIT-CONTAINER-001 release 2.1 owner lines, 2026-10-10",
    ),
    ApprovedDialogueRow(
        selector=2, start=60432, length=98,
        old="Good luck, you guys! This is just like old times!",
        new="It's definitely Tulma. Just look at her in that dress! Yowza.",
        label="registration scene, Oolong",
        approval="FRIEND-V3-WT-SPLIT-CONTAINER-001 release 2.1 owner lines, 2026-10-10",
    ),
)
