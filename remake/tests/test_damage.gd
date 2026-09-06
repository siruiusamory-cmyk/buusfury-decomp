extends RefCounted
## R12-R13: the three-moment separation with damage landing at reaction entry + 3,
## and the exactly-3/2 critical with one centralized rounding site.
##
## Plus the contract guard on FixedPoint.to_displayed_hp (ceiling divide).
##
## Every roll is forced with a ScriptedRng. `Wolf.on_contact` draws in this order:
##   1. Damage.roll_base_raw -> rng.damage_raw(lo, hi)
##   2. rng.crit_roll(permille)     -- true when the popped value <= permille
## ScriptedRng ignores the requested range and pops the queue, so [base, 1001]
## forces a non-crit of `base` and [base, 1] forces a crit.

const NO_CRIT: int = 1001
const FORCE_CRIT: int = 1


func run(h: TestHarness) -> void:
	h.begin_suite("test_damage (R12-R13 + HP display guard)")
	_r12_damage_at_entry_plus_three(h)
	_r13_critical_three_halves(h)
	_guard_displayed_hp(h)
	h.end_suite()


## R12: contact, reaction entry, and damage application are three distinct
## moments. HP is unchanged at entry, entry+1 and entry+2, and changes at exactly
## entry+3. The trace carries three separate records.
func _r12_damage_at_entry_plus_three(h: TestHarness) -> void:
	var c: CombatConfig = TestHarness.make_config()
	h.assert_eq(c.wolf_reaction_damage_offset_ticks, 3, "R12 configured damage offset")

	var base: int = 50996
	var rng := DeterministicRng.ScriptedRng.new([base, NO_CRIT])
	var w: Wolf = h.spawn_wolf(c, rng, Vector2i(200, 200))
	var hp_before: int = w.combatant.hp_raw
	h.assert_eq(hp_before, 179200, "R12 wolf starts at the confirmed 179200 raw")

	EventLog.clear()
	Clock.step(1)
	var entry: int = Clock.current_tick
	w.on_contact(entry, MeleeResolver.DIR_LEFT)

	h.assert_eq(w.state, WolfState.REACTION, "R12 contact enters REACTION on the same tick")
	h.assert_eq(w.damage_tick(), entry + 3, "R12 damage scheduled for entry+3")
	h.assert_eq(w.combatant.hp_raw, hp_before, "R12 hp unchanged AT reaction entry")

	Clock.step(1)
	h.assert_eq(w.combatant.hp_raw, hp_before, "R12 hp unchanged at entry+1")
	Clock.step(1)
	h.assert_eq(w.combatant.hp_raw, hp_before, "R12 hp unchanged at entry+2")
	Clock.step(1)
	h.assert_eq(Clock.current_tick, entry + 3, "R12 clock is at entry+3")
	h.assert_eq(w.combatant.hp_raw, hp_before - base, "R12 hp changed at EXACTLY entry+3")

	# Three distinct trace records, at their own ticks.
	var enters: Array[Dictionary] = EventLog.records_of(EventLog.KIND_REACTION_ENTER)
	var applied: Array[Dictionary] = EventLog.records_of(EventLog.KIND_DAMAGE_APPLIED)
	h.assert_eq(enters.size(), 1, "R12 one REACTION_ENTER record")
	h.assert_eq(applied.size(), 1, "R12 one DAMAGE_APPLIED record")
	h.assert_eq(enters[0]["tick"], entry, "R12 REACTION_ENTER at the contact tick")
	h.assert_eq(applied[0]["tick"], entry + 3, "R12 DAMAGE_APPLIED at entry+3")
	h.assert_ne(applied[0]["tick"], enters[0]["tick"],
		"R12 application and entry are DISTINCT ticks")
	h.assert_eq(enters[0]["data"]["damage_tick"], entry + 3,
		"R12 REACTION_ENTER already names the application tick")
	h.assert_eq(applied[0]["data"]["raw"], base, "R12 the applied raw damage")
	h.assert_eq(applied[0]["data"]["hp_after"], hp_before - base, "R12 traced hp_after")
	h.assert_true(rng.is_drained(), "R12 exactly the queued rolls were consumed")

	# REACTION runs 24 ticks and the damage moment is inside it, not at its end.
	h.assert_eq(enters[0]["data"]["end_tick"], entry + c.wolf_reaction_duration_ticks,
		"R12 REACTION ends at entry+24, well after the damage at entry+3")
	h.despawn([w])


## R13: the critical multiplier is EXACTLY 3/2. Forced crit on base 50996 gives
## 76494; the same base without a crit gives 50996 unchanged.
func _r13_critical_three_halves(h: TestHarness) -> void:
	var c: CombatConfig = TestHarness.make_config()
	h.assert_eq(c.crit_multiplier_num, 3, "R13 crit numerator")
	h.assert_eq(c.crit_multiplier_den, 2, "R13 crit denominator (NOT 2x damage)")

	var base: int = 50996
	# Pure arithmetic first.
	h.assert_eq(Damage.apply_critical(base, c), 76494, "R13 apply_critical(50996) exact 3/2")
	h.assert_ne(Damage.apply_critical(base, c), base * 2, "R13 a crit is NOT double damage")

	# Then end to end, through the wolf, forced by the scripted rolls.
	var crit_rng := DeterministicRng.ScriptedRng.new([base, FORCE_CRIT])
	var w_crit: Wolf = h.spawn_wolf(c, crit_rng, Vector2i(200, 200))
	var hp0: int = w_crit.combatant.hp_raw
	EventLog.clear()
	Clock.step(1)
	w_crit.on_contact(Clock.current_tick, MeleeResolver.DIR_LEFT)
	Clock.step(3)
	var crit_recs: Array[Dictionary] = EventLog.records_of(EventLog.KIND_DAMAGE_APPLIED)
	h.assert_eq(crit_recs.size(), 1, "R13 one crit damage record")
	h.assert_true(crit_recs[0]["data"]["crit"], "R13 the forced roll produced a critical")
	h.assert_eq(crit_recs[0]["data"]["raw"], 76494, "R13 forced crit on base 50996")
	h.assert_eq(w_crit.combatant.hp_raw, hp0 - 76494, "R13 crit hp delta")
	h.despawn([w_crit])

	var plain_rng := DeterministicRng.ScriptedRng.new([base, NO_CRIT])
	var w_plain: Wolf = h.spawn_wolf(c, plain_rng, Vector2i(200, 200))
	var hp1: int = w_plain.combatant.hp_raw
	EventLog.clear()
	Clock.step(1)
	w_plain.on_contact(Clock.current_tick, MeleeResolver.DIR_LEFT)
	Clock.step(3)
	var plain_recs: Array[Dictionary] = EventLog.records_of(EventLog.KIND_DAMAGE_APPLIED)
	h.assert_eq(plain_recs.size(), 1, "R13 one non-crit damage record")
	h.assert_false(plain_recs[0]["data"]["crit"], "R13 the same base without a crit roll")
	h.assert_eq(plain_recs[0]["data"]["raw"], 50996, "R13 non-crit of base 50996 is unchanged")
	h.assert_eq(w_plain.combatant.hp_raw, hp1 - 50996, "R13 non-crit hp delta")
	h.despawn([w_plain])

	# Rounding is CENTRALIZED: `round_crit` is the only division in damage.gd.
	# Source scan, so a second `/` operator added anywhere in that file fails this
	# test. Comments and string literals are stripped first — damage.gd's crit log
	# line contains a literal "x%d/%d" that is text, not arithmetic.
	var src: String = FileAccess.get_file_as_string("res://combat/damage.gd")
	h.assert_true(src.length() > 0, "R13 read combat/damage.gd source")
	var divisions: int = 0
	var division_lines: Array[String] = []
	for raw_line: String in src.split("\n"):
		var line: String = _strip_comment_and_strings(raw_line)
		if line.contains("/"):
			divisions += 1
			division_lines.append(line.strip_edges())
	h.assert_eq(divisions, 1,
		"R13 exactly ONE division site in combat/damage.gd (found %s)" % [division_lines])
	h.assert_true(src.contains("static func round_crit(numerator: int, denominator: int) -> int:"),
		"R13 that site is round_crit")
	# And the crit path routes through it rather than dividing inline.
	h.assert_true(src.contains("round_crit(base_raw * c.crit_multiplier_num, c.crit_multiplier_den)"),
		"R13 apply_critical delegates to round_crit")
	h.assert_eq(Damage.round_crit(base * 3, 2), 76494, "R13 round_crit computes the value directly")


## Remove `"..."` / `'...'` string bodies and any trailing `#` comment, so an
## operator scan sees only code. Deliberately simple: GDScript source, no escaped
## quotes inside the strings in question.
func _strip_comment_and_strings(raw_line: String) -> String:
	var out: String = ""
	var quote: String = ""
	for i: int in raw_line.length():
		var ch: String = raw_line[i]
		if quote != "":
			if ch == quote:
				quote = ""
			continue
		if ch == "\"" or ch == "'":
			quote = ch
			continue
		if ch == "#":
			break
		out += ch
	return out


## Contract guard: raw HP -> displayed HP is a CEILING divide by 1024, so 1 raw of
## HP still shows as 1.
func _guard_displayed_hp(h: TestHarness) -> void:
	h.assert_eq(FixedPoint.to_displayed_hp(179200), 175, "GUARD to_displayed_hp(179200)")
	h.assert_eq(FixedPoint.to_displayed_hp(141884), 139, "GUARD to_displayed_hp(141884)")
	h.assert_eq(FixedPoint.to_displayed_hp(51338), 51, "GUARD to_displayed_hp(51338)")
	h.assert_eq(FixedPoint.to_displayed_hp(1), 1, "GUARD to_displayed_hp(1) — ceiling, not floor")
	h.assert_eq(FixedPoint.to_displayed_hp(0), 0, "GUARD to_displayed_hp(0)")
	# A floor divide would give 138 and 50 here; the ceiling is the whole point.
	h.assert_ne(FixedPoint.to_displayed_hp(141884), 141884 / 1024,
		"GUARD 141884 ceilings up, unlike a floor divide")
	h.assert_eq(FixedPoint.HP_RAW_PER_POINT, 1024, "GUARD HP scale is 10 fractional bits")
	h.assert_ne(FixedPoint.HP_RAW_PER_POINT, FixedPoint.RAW_UNITS_PER_PIXEL,
		"GUARD the HP and POSITION scales are never conflated")
