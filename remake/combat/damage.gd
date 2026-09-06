class_name Damage
extends RefCounted
## Damage arithmetic, all integer. `round_crit` is the ONE division site.
##
## Diagnostics: a critical is rare (the rate was never established - only 2 crits
## in 59 hits observed) and it is the one place a rounding bug could hide, so
## every crit multiply prints its exact inputs and output. Non-crit damage is
## already carried by the DAMAGE_APPLIED trace record and is not logged twice.

## Set false to silence the per-crit line.
static var log_crit: bool = true


## P-010: base damage, inclusive of both confirmed bounds.
static func roll_base_raw(c: CombatConfig, rng: DeterministicRng) -> int:
	return rng.damage_raw(c.wolf_damage_raw_min, c.wolf_damage_raw_max)


## P-009: the multiplier is EXACTLY 3/2. The documented "double damage" was
## EXTERNAL_BEHAVIOR that runtime evidence OVERTURNED. Do not use 2.
static func apply_critical(base_raw: int, c: CombatConfig) -> int:
	var out: int = round_crit(base_raw * c.crit_multiplier_num, c.crit_multiplier_den)
	if log_crit:
		var exact: bool = (base_raw * c.crit_multiplier_num) % c.crit_multiplier_den == 0
		print("[Damage] CRIT base_raw=%d x%d/%d -> %d exact=%s" % [
			base_raw, c.crit_multiplier_num, c.crit_multiplier_den, out, exact,
		])
	return out


## TODO(P-009): exact odd-base rounding.
## Both observed criticals had EVEN bases on the 38-raw lattice, so the 1.5
## multiply landed exactly and NO fractional case was ever observed. This is the
## ONE place the rounding decision lives. Change it here only - nothing else in
## the project divides a damage value.
static func round_crit(numerator: int, denominator: int) -> int:
	return numerator / denominator


## Raw -> displayed HP. Routed through FixedPoint so the ceiling divide exists
## exactly once; this wrapper only carries the configured scale.
static func to_displayed_hp(raw: int, c: CombatConfig) -> int:
	return FixedPoint.to_displayed_hp(raw, c.hp_raw_per_point)
