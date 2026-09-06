class_name CombatConfig
extends Resource
## The ONLY place a gameplay constant is declared.
##
## Two visibly separated blocks:
##   CONFIRMED — recovered from the ROM during tickets P-002..P-010. Frozen.
##   TEMP      — invented for the slice. Every name begins `temp_`. Not reference accurate.
##
## The tick rate is the one constant that does NOT live here: it belongs to the
## clock that owns it, `Clock.TICKS_PER_SECOND` (= 60; GBA is ~59.7275 Hz and 60
## is the deliberate approximation, provenance ROM-011). Do not duplicate it.

## Exactly the `temp_`-prefixed field names. The debug overlay asks `is_temp()`;
## there is no second list to drift, because `_init()` cross-checks this against
## `get_property_list()` in debug builds.
const TEMP_FIELDS: PackedStringArray = [
	"temp_crit_chance_permille",
	"temp_knockback_px",
	"temp_drop_chance_permille",
	"temp_wolf_damage_to_player_raw",
	"temp_player_facing_mode",
	"temp_wall_clamp_enabled",
	"temp_room_bounds_px",
	"temp_death_anim_ticks",
	"temp_wolf_pursuit_exit_threshold",
	"temp_wolf_hub_dwell_ticks",
	"temp_wolf_retreat_threshold",
]

## Facing modes for `temp_player_facing_mode`. Facing was never sampled (P-002
## records it explicitly UNKNOWN), so the mode itself is a guess.
enum FacingMode { LAST_INPUT }

@export_group("CONFIRMED")

## P-002: position fixed point, 8 fractional bits.
@export var raw_units_per_pixel: int = 256
## P-002: per-axis raw displacement per tick = 1.375 px. UNNORMALIZED on diagonals.
@export var move_raw_per_tick: int = 352
## P-002: input->motion latency. Observed 2-3 ticks; low bound taken (see DEVIATION).
@export var input_delay_ticks: int = 2

## P-008: presentation variants, chosen uniformly. Clips 0x0851C680 / 0x0851C6C0 /
## 0x0851C6A0 are VARIANTS, not combo steps.
@export var melee_variant_count: int = 3
## P-008: animation length, zero variance.
@export var melee_duration_ticks: int = 16
## P-006C: minimum ticks between ACCEPTED attacks. 20 is not 16 — the gate is on
## acceptance, not on the animation, so mashing and holding give the same rate.
@export var attack_accept_interval_ticks: int = 20

## P-015: body extents, recovered from the per-direction body-rect tables the
## reference builder 0x0800FE78 reads (actor +0x58 holds the table pointer, the
## hit-direction byte at +0x10 indexes it, 16-byte int32 entries x0/y0/x1/y1 in
## LOCAL space, and the four direction entries begin at table_ptr + 16 — the word
## at +0 is a header). Captured live (20260830-124917-aa90fbac) and then CONFIRMED
## by reading the same tables statically out of the ROM.
##
## The reference rects are ORIGIN-anchored with a negative y0; the remake is
## TOP-LEFT anchored throughout (ColorRect placeholders, `Sprite2D centered=false`,
## the arena clamp, the gizmo outline). Only the EXTENTS carry over — x1-x0 and
## y1-y0 — which is all the reach test and the center-distance thresholds read.
##
## PLAYER table 0x086AD30C. Direction-dependent WIDTH: dirs 0/1 (UP/DOWN) are
## (0,-20)..(16,6) = 16 wide, dirs 2/3 (LEFT/RIGHT) are (5,-20)..(13,6) = 8 wide.
## The player narrows in profile. Height is 26 in all four directions.
@export var player_body_w_facing_px: int = 16
@export var player_body_w_profile_px: int = 8
@export var player_body_h_px: int = 26
## P-015: WOLF tables 0x086B1DE8 and 0x086B1FE0 (two different wolves, identical
## values — independent confirmation). All four directions (0,-24)..(16,8), so the
## wolf body is UNIFORM 16x32 and does not consult its facing.
@export var wolf_body_w_px: int = 16
@export var wolf_body_h_px: int = 32

## P-003: target left edge pushed OUT by 4.
@export var melee_expand_x0: int = 4
## P-003: target right edge pushed OUT by 3.
@export var melee_expand_x1: int = 3
## P-003: target top edge unchanged.
@export var melee_expand_y0: int = 0
## P-003: target bottom edge pulled IN by 6. Asymmetric on purpose.
@export var melee_shrink_y1: int = 6

## P-007: acquisition threshold, radius 100, compared inclusively with `<=`.
@export var wolf_acquire_dist_sq: int = 10000
## P-007: attack decision threshold, radius ~22.9, compared inclusively with `<=`.
@export var wolf_attack_dist_sq: int = 524
## P-007: ATTACK length, exact in 52/52 observed episodes. The >=36-tick cadence is
## an EMERGENT consequence of this plus one HUB tick — do not add a cooldown timer.
@export var wolf_attack_duration_ticks: int = 35
## P-006: REACTION length.
@export var wolf_reaction_duration_ticks: int = 24
## P-006: damage applies at reaction entry + 3.
@export var wolf_reaction_damage_offset_ticks: int = 3
## P-011: wolf pursuit speed, measured from the runtime capture (88835 rows, two
## live wolves). RESULTANT-capped, not per-axis: per-axis |dx| max and p99 are both
## exactly 153 and 153 is the modal value, while only 1.8% of diagonal rows have
## both axes at 153 - so the wolf caps its total step at 153 and splits it across
## the axes. This is the OPPOSITE of the player, whose 352 (`move_raw_per_tick`)
## is UNNORMALIZED on diagonals (P-002). The two models differ for real; do not
## unify them. 153/256 = 0.598 px/tick, about 43% of the player's cardinal rate.
@export var wolf_move_raw_per_tick: int = 153
## P-013: knockback slide length, 23 ticks in 7 of 9 clean single-hit events
## (outliers 17 and 21). REACTION is 24, so the slide runs the whole hitstun and
## stops with it — it is NOT a separate timer.
@export var wolf_knockback_ticks: int = 23
## P-013: knockback is a CONSTANT-VELOCITY slide, not an impulse. The per-tick
## position delta is bit-identical every tick (wx stepped 39813->39925->40037->
## 40149->40261, exactly 112 each time); there is no friction, decay or easing.
## 129 is the median of the observed 117..163 raw/tick. Carried momentum was
## REFUTED (hits from a standing victim still slid at 117..163) and damage does
## not drive it (damage was near-constant while speed varied). What varies the
## speed is UNKNOWN.
@export var wolf_knockback_speed_raw: int = 129
## P-014: RETREAT duration, median of the 30 observed selector-436 occurrences.
@export var wolf_retreat_ticks: int = 12
## P-014: RETREAT speed, median of selector 436 (163 raw/tick — indistinguishable
## from pursuit's 161). Selector 439 is a SEPARATE, rarer, ~35% faster retreat
## (median 217 raw/tick over 9 occurrences) and is deliberately not modelled.
@export var wolf_retreat_speed_raw: int = 163
## P-014: proximity gate for RETREAT. All 31 observed selector-436 entries occur
## at dist_sq <= 4709. NECESSARY, NOT SUFFICIENT: the wolf spends 50.4% of its
## pursuit time inside this band and mostly does not retreat, which is why a roll
## sits behind this test (temp_wolf_retreat_threshold).
@export var wolf_retreat_max_dist_sq: int = 4709

## P-009: critical numerator. Multiplier is EXACTLY 3/2.
@export var crit_multiplier_num: int = 3
## P-009: critical denominator. Exactly 3/2 — NOT 2. The documented "double damage"
## was EXTERNAL_BEHAVIOR that runtime evidence overturned.
@export var crit_multiplier_den: int = 2
## P-009: 1024 raw = 1 displayed HP, ten fractional bits. Distinct from
## `raw_units_per_pixel` (eight) — never conflate the two scales.
@export var hp_raw_per_point: int = 1024
## DATA-001: player starting HP. Goku's base-stat record gives 135 displayed HP
## (file offset 0x006FDA4C, GBA 0x086FDA4C), and 135 * 1024 = 138240 raw. Layout
## documented by yoav74/BuusFuryToolkit and verified against the canonical ROM
## buus_fury_usa_rev0_01c1707f before promotion. Static-table value, not runtime.
@export var player_hp_raw: int = 138240

## P-010: wolf HP, 175 displayed.
@export var wolf_hp_raw: int = 179200
## P-010: observed damage floor.
@export var wolf_damage_raw_min: int = 47956
## P-010: observed damage ceiling.
@export var wolf_damage_raw_max: int = 52250
## P-010: base EXP award.
@export var wolf_base_exp: int = 225
## P-010: payout lands exactly 1 tick after lethal damage.
@export var exp_payout_delay_ticks: int = 1
## P-010: ADDITIVE per qualifying item. Multiplicative was REFUTED (225/248/271).
@export var equipment_exp_bonus_per_item: int = 23
## P-010: level cap.
@export var level_cap: int = 200
## P-010: zeni denominations.
@export var zeni_denominations: PackedInt32Array = PackedInt32Array([5, 25, 50, 100])
## P-010: inventory capacity; adding past it is a silent no-op.
@export var item_inventory_cap: int = 250

@export_group("TEMP — NOT REFERENCE ACCURATE")

## GUESS. Critical probability was never established — only 2 crits in 59 hits
## observed, and that is a raw count, explicitly not a rate (P-009).
@export var temp_crit_chance_permille: int = 50
## SUPERSEDED and UNUSED. Knockback was unresolved at P-007/P-008 and this field
## held zero as the honest answer. P-013 then MEASURED it: see the CONFIRMED
## `wolf_knockback_ticks` / `wolf_knockback_speed_raw`, which are what the wolf
## actually reads. Kept only so the TEMP registry and the overlay keep their shape.
@export var temp_knockback_px: int = 0
## GUESS. Drop roll producer unlocated (P-010). Always dropping keeps the path testable.
@export var temp_drop_chance_permille: int = 1000
## GUESS. Player damage taken was never established (P-010).
@export var temp_wolf_damage_to_player_raw: int = 10240
## GUESS. Facing was never sampled (P-002 explicitly UNKNOWN).
@export var temp_player_facing_mode: FacingMode = FacingMode.LAST_INPUT
## GUESS. Collision/clamping never observed (P-002 explicitly UNKNOWN). Room bounds only.
@export var temp_wall_clamp_enabled: bool = true
## GUESS. Invented for the slice; no room geometry was recovered.
@export var temp_room_bounds_px: Rect2i = Rect2i(0, 0, 800, 600)
## GUESS. Death-animation duration not measured (P-010).
@export var temp_death_anim_ticks: int = 0
## P-012, CONSISTENT BUT UNPROVEN. The wolf leaves PURSUIT on a memoryless
## per-tick roll through the reference chance gate (probability = threshold/65536).
## Measured mean run 46.82 ticks (n=201 uncensored, MLE p=0.02136, 95% CI on the
## mean [40.80, 52.83]). 1310 = exactly 2.00% predicts a 50.0-tick mean, +1.04 SE
## from the measurement — consistent, NOT recovered: 21 ROM template nodes share
## param 1310 and the CI admits roughly [1240, 1606]. TEMP until one is isolated.
@export var temp_wolf_pursuit_exit_threshold: int = 1310
## P-012, MEASURED MEDIAN, not a recovered constant. The pause players see IS the
## hub visit: ~71% of each pause is spent in the reference hub selector, which does
## not move the actor. Hub-only pauses n=226, median 7, mean 9.6, max 71 — the
## distribution is broad, so a single fixed dwell is a stand-in for its shape.
@export var temp_wolf_hub_dwell_ticks: int = 7
## GUESS. P-014 established that RETREAT needs a proximity gate PLUS a roll — the
## wolf is inside `wolf_retreat_max_dist_sq` for 50.4% of pursuit but retreats
## only 30 times — but it did NOT identify the chance. 1310 (= exactly 2.00%) is
## BORROWED from the P-012 pursuit-exit gate as a placeholder; it is NOT a
## measured retreat value and no evidence links the two gates.
@export var temp_wolf_retreat_threshold: int = 1310


func _init() -> void:
	if OS.is_debug_build():
		_assert_temp_registry()


## True when `field_name` names a TEMP (guessed) field. The debug overlay calls
## this rather than hardcoding a list.
func is_temp(field_name: String) -> bool:
	return TEMP_FIELDS.has(field_name)


func _assert_temp_registry() -> void:
	var declared: PackedStringArray = PackedStringArray()
	for p: Dictionary in get_property_list():
		var n: String = p["name"]
		if n.begins_with("temp_"):
			declared.append(n)
	for n: String in declared:
		assert(TEMP_FIELDS.has(n), "temp_ field '%s' missing from TEMP_FIELDS" % n)
	for n: String in TEMP_FIELDS:
		assert(declared.has(n), "TEMP_FIELDS names '%s' which is not a property" % n)
