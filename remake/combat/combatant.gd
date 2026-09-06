class_name Combatant
extends RefCounted
## HP and damage intake. Raw HP only - the raw->displayed conversion lives in
## FixedPoint.to_displayed_hp and nowhere else.
##
## Overkill is DISCARDED, as recovered: hp_raw is clamped to 0 after subtraction.
##
## Diagnostics: the per-hit trace record belongs to the caller (it knows the tick
## and the actor), so this class logs only the two things it alone can see - the
## lethal transition, and an aggregate hit tally on death. Never per-tick.

## Set false to silence the lethal-transition line (tests that kill in a loop).
static var log_lethal: bool = true

var hp_raw: int = 0
var max_hp_raw: int = 0

## Aggregate diagnostics: how many applications this body absorbed, and their sum.
## Printed once, on the lethal hit - so "four hits kill it" is verifiable from the
## log without reading per-tick spam.
var hits_taken: int = 0
var total_damage_raw: int = 0


func _init(p_max_hp_raw: int = 0) -> void:
	max_hp_raw = p_max_hp_raw
	hp_raw = p_max_hp_raw


func is_alive() -> bool:
	return hp_raw > 0


## Subtract `raw` and clamp. Returns true when this application was lethal.
func take_damage(raw: int) -> bool:
	if hp_raw <= 0:
		return false
	hits_taken += 1
	total_damage_raw += raw
	hp_raw -= raw
	if hp_raw <= 0:
		var overkill: int = -hp_raw
		hp_raw = 0
		if log_lethal:
			print("[Combatant] LETHAL hits=%d total_raw=%d max_hp_raw=%d overkill_raw=%d" % [
				hits_taken, total_damage_raw, max_hp_raw, overkill,
			])
		return true
	return false


func displayed_hp(divisor: int) -> int:
	return FixedPoint.to_displayed_hp(hp_raw, divisor)
