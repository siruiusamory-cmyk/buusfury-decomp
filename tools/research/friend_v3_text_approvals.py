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
        attack_action_row=None,
        approval="FRIEND-V3-WT-SPLIT-CONTAINER-001 release 3 owner scope, 2026-10-10: accepted by "
                 "the owner after he fought the build. The action-row change is NOT part of it: "
                 "review B1 then measured that the appended copy's probability leaf pointed at the "
                 "retail shared spawn in every build, so the lever never ran and its apparent "
                 "cadence gain was an artifact of holding the player still. What the owner actually "
                 "approved is this profile with the retail swing chain",
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
class ApprovedDialogueTextEdit:
    """One approved wording change inside a packed or stored dialogue container record."""

    selector: int
    start: int
    length: int
    old: str
    new: str
    approval: str


#: Wording inside dialogue containers, from the owner decision log (2026-10-10). The spans are
#: positions in the release-3 build, and the tool that applies them refuses unless the record
#: holds the old text exactly once.
#:
#: SPANS ARE IN BYTES. `tools/webfoot/handles.py:unpack_handle` already returns decoded start and
#: length in bytes, so a record's span is `stream[start:start+length]` with no further scaling. An
#: earlier version of the wording tool multiplied by the two-byte unit a second time, which doubled
#: every window and damaged 28 records; the coordinates below were re-derived with a byte-correct
#: search after that defect was found by review.
#:
#: The five edits are one spacing repair and the tail of the rename pass:
#:   * "Great Soy Man" -> "Great Soyman" in the record that carries the spaced form, so the name
#:     reads the same everywhere. Twenty-odd records already read "Great Soyman" and four table
#:     slots do too.
#:   * Four phrases where the canonical ROM says "Kakarot" and this image says "Yamcha" now say
#:     "Bandit", which covers seven of the ten Kakarot records; the other three carry a fifth phrase
#:     whose spans cannot be edited in place and are deferred. Each replacement also absorbs the
#:     double space the earlier rename left behind it.
APPROVED_DIALOGUE_TEXT_EDITS: tuple[ApprovedDialogueTextEdit, ...] = (
    ApprovedDialogueTextEdit(
        selector=1, start=38856, length=252,
        old="Great Soy Man", new="Great Soyman",
        approval="owner decision 2026-10-10: the spaced form becomes the name used everywhere else",
    ),
    # The longer record 1:37530:2416 covers this span, so one edit serves both readers; editing the
    # covering record as well would be refused because the phrase is already replaced by then.
    ApprovedDialogueTextEdit(
        selector=1, start=58162, length=46, old="Yamcha", new="Bandit",
        approval="owner decision 2026-10-10: retail says Kakarot here",
    ),
    ApprovedDialogueTextEdit(
        selector=1, start=62104, length=138, old="Yamcha  also", new="Bandit also",
        approval="owner decision 2026-10-10: retail says Kakarot here, pad absorbed",
    ),
    ApprovedDialogueTextEdit(
        selector=1, start=44704, length=468, old="Yamcha's  boy", new="Bandit's boy",
        approval="owner decision 2026-10-10: retail says Kakarot's boy, pad absorbed",
    ),
    ApprovedDialogueTextEdit(
        selector=2, start=59518, length=102, old="Yamcha  once", new="Bandit once",
        approval="owner decision 2026-10-10: retail says Kakarot here, pad absorbed",
    ),
    # NOT APPLIED YET: "If Yamcha  is coming back to fight in the World Tournament" (retail says
    # Kakarot). Every span that carries it has another live record's boundary inside it - 2:1948:252
    # contains 1976:128, and the chained records 2:528:2450 and 2:560:3562 have the same problem -
    # so the replacement's shift would cut that record. The wording tool refuses it by name, and it
    # moves to release 4 with the container rebuild. Three of the ten Kakarot lines keep "Yamcha".
)


@dataclass(frozen=True, slots=True)
class ApprovedCharacterRename:
    """One approved rename of a character, with the test that fixes which occurrences it covers."""

    old: str
    new: str
    retail_test: str
    relocated_slots: tuple[int, ...]
    approval: str


#: Release 3.1: retail Videl's actor becomes Lazuli. THE OCCURRENCE TEST IS THE APPROVAL. This image
#: displays the name "Videl" on TWO different actors - measured, retail's appearance records 65 to
#: 70 (Goten's art) were renamed to "Videl" by the earlier pass, and records 214 and 215 are retail
#: Videl herself - so a rename that matched the spelling everywhere would merge two characters. The
#: owner's rule fixes which is which without guessing: an occurrence is retail Videl only where the
#: CANONICAL ROM says "Videl" at the same place. Where the canonical ROM says "Goten", the word
#: belongs to the other actor and stays. Where there is no retail counterpart, nothing is written.
#: Measured coverage: 3 text-table slots and 34 dialogue records; 12 slots and 57 records left; 3
#: records listed for the owner because they live in the container an earlier release appended and
#: retail has no counterpart to compare.
APPROVED_CHARACTER_RENAMES: tuple[ApprovedCharacterRename, ...] = (
    ApprovedCharacterRename(
        old="Videl",
        new="Lazuli",
        retail_test="an occurrence is renamed only where the canonical ROM says 'Videl' at the same "
                    "place; where it says 'Goten' the word stays, and an occurrence with no retail "
                    "counterpart is left and listed",
        relocated_slots=(138, 172, 1066),
        approval="owner decision 2026-10-10: 'a rename of retail Videl to Lazuli, swapped in all "
                 "dialogue and appropriate stuff like all the other names were', with the "
                 "clarification 'Not every Videl, the retail Videl. Not the Goten > Videl Videl.'",
    ),
)


@dataclass(frozen=True, slots=True)
class ApprovedRelease:
    """One shipped release: the image it was cut from, the chain, and the digest it must equal."""

    name: str
    base_sha256: str
    base_bytes: int
    output_sha256: str
    output_bytes: int
    stages: tuple[str, ...]
    notes: str


#: Release 3's frozen identity. The builder asserts this digest, so a byte that drifts anywhere in
#: the chain fails the build rather than shipping quietly. The intermediate digests are recorded
#: beside it: retune, then profile, then wording.
APPROVED_RELEASES: tuple[ApprovedRelease, ...] = (
    ApprovedRelease(
        name="release-3",
        base_sha256="018757c4e0dda9f463364675f32b307dff9e5ad89c7a0b932939aec320032389",
        base_bytes=10146000,
        output_sha256="521bd0fa0a8bc198f36430e3419184807e335fa588bd718152996c076a8f15fd",
        output_bytes=10146136,
        stages=("boss-retune", "behaviour-profile", "dialogue-wording"),
        notes="Hercule's and Olibu's encounters retuned and given the profile the owner fought, "
              "the Great Soyman spacing repaired, and seven of the ten Kakarot lines reading "
              "Bandit. Review B1 measured that the action-row change was never reachable (the "
              "appended copy's leaf pointed at the retail shared spawn), so the profile ships with "
              "the retail swing chain, and one phrase (\"If Yamcha is coming back\", three records) "
              "cannot be edited in place because a record boundary sits inside every span that "
              "carries it. Interior double spaces and that phrase are release 4, which needs a "
              "container rebuild with every handle rewritten.",
    ),
    ApprovedRelease(
        name="release-3.1",
        base_sha256="521bd0fa0a8bc198f36430e3419184807e335fa588bd718152996c076a8f15fd",
        base_bytes=10146136,
        output_sha256="b8ee65657986d05d57911ade9ce4b2bf9f216811b874756aec5de8df06351dd5",
        output_bytes=10169986,
        stages=("character-rename",),
        notes="Retail Videl's actor is renamed to Lazuli by the retail-side occurrence test: 34 "
              "dialogue records copied into the selector-7 container with its payload carried "
              "forward, and 3 text-table slots relocated. The Goten-turned-Videl actor and every "
              "occurrence retail does not spell 'Videl' are untouched, and 3 records with no retail "
              "counterpart are listed for the owner. The renamed container's declared size grows "
              "from 2,266 to 23,794 bytes, which is why the image grows by 23,850 bytes.",
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
