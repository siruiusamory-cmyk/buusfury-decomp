extends RefCounted
## R8-R11: inclusive acquisition, no leash, the exact 35-tick ATTACK, and the
## >=36-tick cadence emerging from it with no cooldown field anywhere.
## R16: the P-012 pursuit-exit gate and the HUB dwell that reads as the pause.
## R17: the P-013 constant-velocity knockback slide.
## R18: the P-014 RETREAT - proximity gate plus a roll, backing away, HUB on exit.
##
## Body geometry, so the placements below are readable:
##   player 16x26 px anchored top-left -> center (px.x + 8, px.y + 13)
##   wolf   16x32 px anchored top-left -> center (px.x + 8, px.y + 16)
## P-015 recovered extents. The player's WIDTH is direction-dependent (16 facing
## UP/DOWN, 8 in profile); these suites never leave the default DIR_DOWN, so 16 is
## the width in play and the centre-x offset is 8 throughout.
## Both centers are `(lo + hi) >> 1` on the BODY rect (core/body_rect.gd).

## Player anchor whose body centre sits at (8, 13).
const PLAYER_PX := Vector2i(0, 0)


func run(h: TestHarness) -> void:
	h.begin_suite("test_wolf_ai (R8-R11, R16-R18, P-015)")
	_r8_acquisition_inclusive(h)
	_r9_no_leash(h)
	_r10_attack_duration(h)
	_r11_cadence_emerges(h)
	_r16_pursuit_exit_gate(h)
	_r16_hub_dwell(h)
	_r17_knockback_constant_velocity(h)
	_r18_retreat_gate_and_motion(h)
	_p015_body_extents(h)
	h.end_suite()


## Wolf anchor placing its centre `dx, dy` pixels from the player's (8, 13).
func _wolf_px_for(dx: int, dy: int) -> Vector2i:
	return Vector2i(8 + dx - 8, 13 + dy - 16)


## Spawn a paired player/wolf at a chosen centre separation, one tick unstepped.
##
## `p.targets` is deliberately left EMPTY: this suite tests the wolf's own state
## machine, and a player swing would knock the wolf into REACTION and mask the
## ATTACK timings. Isolating it also makes the suite independent of leftover
## Input state — `Input.is_action_just_pressed` latches true for the life of a
## headless run that never renders a frame, so a Player with targets would swing
## forever once any earlier suite pressed `attack`.
func _pair(h: TestHarness, c: CombatConfig, dx: int, dy: int) -> Array[Node]:
	var rng := DeterministicRng.new(11)
	var p: Player = h.spawn_player(c, rng, PLAYER_PX)
	var w: Wolf = h.spawn_wolf(c, rng, _wolf_px_for(dx, dy))
	w.target = p
	p.targets = []
	return [p, w]


## As `_pair`, but with the WOLF's rng injected so a ScriptedRng can force the
## P-012 pursuit-exit gate. The player deliberately gets a SEPARATE generator:
## `Input.is_action_just_pressed` latches true for the life of a headless run, so
## a shared instance would let the player's `melee_variant` roll eat the queued
## gate values and make the wolf's roll count untestable.
func _pair_with_rng(
	h: TestHarness, c: CombatConfig, rng: DeterministicRng, dx: int, dy: int
) -> Array[Node]:
	var p: Player = h.spawn_player(c, DeterministicRng.new(11), PLAYER_PX)
	var w: Wolf = h.spawn_wolf(c, rng, _wolf_px_for(dx, dy))
	w.target = p
	p.targets = []
	return [p, w]


## R16: the P-012 pursuit exit is a per-tick GATE ROLL, not a distance test. A
## failing roll keeps the wolf closing; a passing roll parks it in HUB without
## moving it that tick.
func _r16_pursuit_exit_gate(h: TestHarness) -> void:
	var c: CombatConfig = TestHarness.make_config()
	c.temp_wall_clamp_enabled = false
	h.assert_eq(c.temp_wolf_pursuit_exit_threshold, 1310, "R16 configured exit threshold")
	h.assert_true(c.is_temp("temp_wolf_pursuit_exit_threshold"),
		"R16 the exit threshold is registered TEMP - 1310 is consistent, not proven")

	# dx 100 acquires (dist_sq exactly 10000) and is far outside attack range, so
	# tick 1 is IDLE->HUB, tick 2 is the untimed HUB falling through to PURSUIT,
	# and every tick after that is a PURSUIT tick that rolls the gate.
	# 65535 fails the gate (65535 < 1310 is false); 0 passes it.
	var failing := DeterministicRng.ScriptedRng.new([65535, 65535])
	var pair: Array[Node] = _pair_with_rng(h, c, failing, 100, 0)
	var w: Wolf = pair[1]
	Clock.step(2)
	h.assert_eq(w.state, WolfState.PURSUIT, "R16 in PURSUIT before the first gate roll")

	var before: Vector2i = w.pos_raw
	Clock.step(1)
	h.assert_eq(failing.popped_count(), 1, "R16 a PURSUIT tick draws exactly one gate roll")
	h.assert_eq(w.state, WolfState.PURSUIT, "R16 a FAILING gate roll stays in PURSUIT")
	h.assert_ne(w.pos_raw, before, "R16 a failing roll still closes on the target")
	h.despawn(pair)

	# Same placement, but the gate passes on the first PURSUIT tick.
	var passing := DeterministicRng.ScriptedRng.new([0])
	var pair2: Array[Node] = _pair_with_rng(h, c, passing, 100, 0)
	var w2: Wolf = pair2[1]
	Clock.step(2)
	h.assert_eq(w2.state, WolfState.PURSUIT, "R16 second wolf in PURSUIT before the roll")

	var before2: Vector2i = w2.pos_raw
	Clock.step(1)
	h.assert_eq(w2.state, WolfState.HUB, "R16 a PASSING gate roll enters HUB")
	h.assert_eq(w2.pos_raw, before2, "R16 the wolf does NOT move on the tick it exits to HUB")
	h.assert_true(passing.is_drained(), "R16 exactly one gate roll was consumed")
	h.despawn(pair2)


## R16: HUB entered from the pursuit gate DWELLS `temp_wolf_hub_dwell_ticks` and
## does not move, then resumes PURSUIT - unless the player is in attack range, in
## which case the attack pre-empts the dwell entirely.
func _r16_hub_dwell(h: TestHarness) -> void:
	var c: CombatConfig = TestHarness.make_config()
	c.temp_wall_clamp_enabled = false
	h.assert_eq(c.temp_wolf_hub_dwell_ticks, 7, "R16 configured hub dwell")
	h.assert_true(c.is_temp("temp_wolf_hub_dwell_ticks"),
		"R16 the hub dwell is registered TEMP - 7 is a measured median, not a constant")

	# One passing roll on the first PURSUIT tick, then enough failing rolls that
	# the wolf never exits again for the rest of the run.
	var scripted := DeterministicRng.ScriptedRng.new([0])
	scripted.push_values([65535, 65535, 65535, 65535])
	var pair: Array[Node] = _pair_with_rng(h, c, scripted, 100, 0)
	var w: Wolf = pair[1]
	Clock.step(3)
	h.assert_eq(w.state, WolfState.HUB, "R16 gate roll put the wolf in HUB")
	var entered: int = Clock.current_tick
	var parked: Vector2i = w.pos_raw

	# Still dwelling, still stationary, at entry + 6.
	Clock.step(6)
	h.assert_eq(Clock.current_tick, entered + 6, "R16 clock is at hub entry+6")
	h.assert_eq(w.state, WolfState.HUB, "R16 still HUB at entry+6 (dwell of 7 not elapsed)")
	h.assert_eq(w.pos_raw, parked, "R16 the wolf never moves during the hub dwell")
	h.assert_eq(scripted.popped_count(), 1,
		"R16 no gate rolls are drawn while dwelling - HUB does not roll")

	# The dwell expires at entry + 7 and PURSUIT resumes.
	Clock.step(1)
	h.assert_eq(Clock.current_tick, entered + 7, "R16 clock is at hub entry+7")
	h.assert_eq(w.state, WolfState.PURSUIT, "R16 PURSUIT resumes at exactly entry+dwell")
	h.despawn(pair)

	# Attack range OUTRANKS the dwell: a wolf parked in HUB with the player inside
	# dist_sq 524 attacks on its very next tick rather than waiting out the 7.
	var scripted2 := DeterministicRng.ScriptedRng.new([0])
	var pair2: Array[Node] = _pair_with_rng(h, c, scripted2, 100, 0)
	var p2: Player = pair2[0]
	var w2: Wolf = pair2[1]
	Clock.step(3)
	h.assert_eq(w2.state, WolfState.HUB, "R16 second wolf parked in HUB")
	var entered2: int = Clock.current_tick

	# Teleport the player onto the wolf, well inside the 524 attack threshold.
	p2.pos_raw = w2.pos_raw
	Clock.step(1)
	h.assert_true(w2.dist_sq() <= c.wolf_attack_dist_sq, "R16 player really is in attack range")
	h.assert_eq(w2.state, WolfState.ATTACK,
		"R16 attack range PRE-EMPTS the hub dwell - no waiting out the 7 ticks")
	h.assert_true(Clock.current_tick < entered2 + c.temp_wolf_hub_dwell_ticks,
		"R16 and it attacked BEFORE the dwell would have expired")
	h.despawn(pair2)


## R17 (P-013): a hit slides the wolf at CONSTANT VELOCITY - the same integer
## delta every tick for `wolf_knockback_ticks`, directed away from the attacker -
## and then stops dead. Not an impulse, not a decay curve: the capture shows the
## per-tick delta bit-identical within a hit (wx stepped by exactly 112 each tick).
func _r17_knockback_constant_velocity(h: TestHarness) -> void:
	var c: CombatConfig = TestHarness.make_config()
	c.temp_wall_clamp_enabled = false
	# Freeze pursuit so the ONLY thing moving the wolf is the slide.
	c.wolf_move_raw_per_tick = 0
	h.assert_eq(c.wolf_knockback_ticks, 23, "R17 configured knockback duration")
	h.assert_eq(c.wolf_knockback_speed_raw, 129, "R17 configured knockback speed")
	h.assert_true(c.wolf_knockback_ticks < c.wolf_reaction_duration_ticks,
		"R17 the 23-tick slide fits INSIDE the 24-tick REACTION - it is not a second state")

	# The slide direction is derived from raw ANCHOR positions, the same coordinate
	# reasoning `_close_on_target` uses. Under the P-015 extents (player 16x26,
	# wolf 16x32) the anchors are player (0, 0) and wolf (dx, dy - 3), so dy = 3
	# makes the anchor separation purely horizontal and the expected away-step
	# exactly (+129, 0), checkable by hand. dx 60 keeps the wolf outside attack
	# range (centre dist_sq 3609 > 524) so it cannot enter ATTACK and confuse the
	# timing.
	#
	# The queue: on_contact draws base damage then the crit decision. After the
	# 24-tick REACTION the wolf resumes HUB/PURSUIT and starts rolling the exit and
	# retreat gates again, so failing rolls are queued to cover the tail of the run.
	var scripted := DeterministicRng.ScriptedRng.new([c.wolf_damage_raw_min, 1000])
	for _i: int in 64:
		scripted.push_values([65535])
	var pair: Array[Node] = _pair_with_rng(h, c, scripted, 60, 3)
	var p: Player = pair[0]
	var w: Wolf = pair[1]
	Clock.step(1)

	var before: Vector2i = w.pos_raw
	w.on_contact(Clock.current_tick, MeleeResolver.DIR_RIGHT)
	h.assert_eq(w.state, WolfState.REACTION, "R17 the hit put the wolf in REACTION")

	# The attacker's position AT CONTACT: the slide was fixed against this and must
	# not track the player afterwards.
	var attacker_at_contact: Vector2i = p.pos_raw

	var deltas: Array[Vector2i] = []
	for _i: int in c.wolf_knockback_ticks:
		var prev: Vector2i = w.pos_raw
		Clock.step(1)
		deltas.append(w.pos_raw - prev)

	h.assert_eq(deltas.size(), c.wolf_knockback_ticks,
		"R17 sampled one delta per knockback tick")
	h.assert_eq(deltas[0], Vector2i(c.wolf_knockback_speed_raw, 0),
		"R17 the first step is exactly wolf_knockback_speed_raw, straight away from the attacker")

	var all_identical: bool = true
	for d: Vector2i in deltas:
		if d != deltas[0]:
			all_identical = false
	h.assert_true(all_identical,
		"R17 EVERY per-tick delta is the SAME integer - constant velocity, no decay (%s)" % [deltas[0]])

	h.assert_true(w.pos_raw.x > before.x,
		"R17 the wolf ended up further from the attacker than it started")
	h.assert_eq(w.pos_raw.y, before.y, "R17 a purely horizontal hit slides purely horizontally")
	h.assert_eq(w.pos_raw - before, deltas[0] * c.wolf_knockback_ticks,
		"R17 total displacement is exactly speed x ticks")
	h.assert_true(w.pos_raw.x > attacker_at_contact.x,
		"R17 the slide is directed AWAY from where the attacker stood at contact")

	# And it STOPS. The 24th REACTION tick moves nothing. The wolf is still in
	# REACTION here (23 < 24), so nothing else can move it either.
	var settled: Vector2i = w.pos_raw
	h.assert_eq(w.state, WolfState.REACTION, "R17 still in REACTION when the slide ends")
	Clock.step(1)
	h.assert_eq(w.pos_raw, settled, "R17 the slide stops dead at wolf_knockback_ticks")

	# wolf_move_raw_per_tick is already 0 for this test, and retreat is silenced
	# too, so the only thing that could move the wolf now is a residual slide.
	c.wolf_retreat_speed_raw = 0
	Clock.step(30)
	h.assert_eq(w.pos_raw, settled, "R17 and stays stopped - there is no residual velocity")
	h.despawn(pair)


## R18 (P-014): RETREAT needs BOTH the proximity band and a passing roll; it backs
## the wolf away for `wolf_retreat_ticks`, exits to HUB, and yields to attack range.
func _r18_retreat_gate_and_motion(h: TestHarness) -> void:
	var c: CombatConfig = TestHarness.make_config()
	c.temp_wall_clamp_enabled = false
	h.assert_eq(c.wolf_retreat_ticks, 12, "R18 configured retreat duration")
	h.assert_eq(c.wolf_retreat_speed_raw, 163, "R18 configured retreat speed")
	h.assert_eq(c.wolf_retreat_max_dist_sq, 4709, "R18 configured retreat proximity band")
	h.assert_true(c.is_temp("temp_wolf_retreat_threshold"),
		"R18 the retreat chance is registered TEMP - P-014 proved a roll, not its rate")
	h.assert_eq(WolfState.name_of(WolfState.RETREAT), "RETREAT", "R18 the enum and NAMES agree")

	# dx 68 -> dist_sq 4624, INSIDE the 4709 band and outside attack range (524).
	# Each PURSUIT tick draws the exit gate FIRST, then the retreat gate, so the
	# queue is read in pairs: [exit, retreat].
	# 65535 fails a gate; 0 passes it.
	var inside := DeterministicRng.ScriptedRng.new([65535, 0])
	var pair: Array[Node] = _pair_with_rng(h, c, inside, 68, 0)
	var p: Player = pair[0]
	var w: Wolf = pair[1]
	Clock.step(2)
	h.assert_eq(w.state, WolfState.PURSUIT, "R18 in PURSUIT before the retreat roll")
	h.assert_eq(w.dist_sq(), 4624, "R18 placement really is inside the band")

	Clock.step(1)
	h.assert_eq(w.state, WolfState.RETREAT, "R18 in-band + passing roll enters RETREAT")
	h.assert_eq(inside.popped_count(), 2,
		"R18 a PURSUIT tick draws the exit gate and then the retreat gate")
	var entered: int = Clock.current_tick

	# It moves AWAY on every tick. Measured in the RAW anchor space the retreat step
	# is computed in: `dist_sq()` is pixel-space centre distance, and 163 raw is
	# 0.64 px, so consecutive ticks can land in the same pixel and read as equal
	# there without the wolf having stopped or turned.
	var strictly_increasing: bool = true
	var prev_raw: int = (w.pos_raw - p.pos_raw).length_squared()
	for _i: int in c.wolf_retreat_ticks - 1:
		Clock.step(1)
		var now_raw: int = (w.pos_raw - p.pos_raw).length_squared()
		if now_raw <= prev_raw:
			strictly_increasing = false
		prev_raw = now_raw
	h.assert_true(strictly_increasing,
		"R18 raw distance to the target strictly increases on every RETREAT tick")
	h.assert_true(w.dist_sq() > 4624,
		"R18 and the pixel-space centre distance ended up larger than it started (%d)" % w.dist_sq())
	h.assert_eq(w.state, WolfState.RETREAT,
		"R18 still RETREAT at entry+%d" % (c.wolf_retreat_ticks - 1))
	h.assert_eq(Clock.current_tick, entered + c.wolf_retreat_ticks - 1, "R18 clock is at entry+11")

	# Expiry goes to HUB, not straight back to PURSUIT, so the hub dwell applies.
	Clock.step(1)
	h.assert_eq(Clock.current_tick, entered + c.wolf_retreat_ticks, "R18 clock is at entry+12")
	h.assert_eq(w.state, WolfState.HUB, "R18 RETREAT expires into HUB, not PURSUIT")
	h.assert_eq(w.ticks_remaining(Clock.current_tick), c.temp_wolf_hub_dwell_ticks,
		"R18 and the hub dwell is armed on arrival")
	h.despawn(pair)

	# A PASSING roll OUT of band does NOT retreat. dx 100 -> dist_sq 10000 > 4709.
	var outside := DeterministicRng.ScriptedRng.new([65535])
	var pair2: Array[Node] = _pair_with_rng(h, c, outside, 100, 0)
	var w2: Wolf = pair2[1]
	Clock.step(3)
	h.assert_eq(w2.state, WolfState.PURSUIT,
		"R18 out of band the wolf keeps pursuing - proximity is NECESSARY")
	h.assert_eq(outside.popped_count(), 1,
		"R18 out of band the retreat gate is never even rolled (distance short-circuits)")
	h.despawn(pair2)

	# In band, FAILING roll: proximity alone is NOT SUFFICIENT.
	var failing := DeterministicRng.ScriptedRng.new([65535, 65535])
	var pair3: Array[Node] = _pair_with_rng(h, c, failing, 68, 0)
	var w3: Wolf = pair3[1]
	Clock.step(2)
	var before3: Vector2i = w3.pos_raw
	Clock.step(1)
	h.assert_eq(w3.state, WolfState.PURSUIT,
		"R18 in band with a FAILING roll stays in PURSUIT - proximity is NOT sufficient")
	h.assert_ne(w3.pos_raw, before3, "R18 and it closes on the target that tick")
	h.assert_true(failing.is_drained(), "R18 exactly the two gate rolls were consumed")
	h.despawn(pair3)

	# Attack range PRE-EMPTS an in-flight RETREAT.
	var scripted4 := DeterministicRng.ScriptedRng.new([65535, 0])
	var pair4: Array[Node] = _pair_with_rng(h, c, scripted4, 68, 0)
	var p4: Player = pair4[0]
	var w4: Wolf = pair4[1]
	Clock.step(3)
	h.assert_eq(w4.state, WolfState.RETREAT, "R18 fourth wolf is retreating")
	var entered4: int = Clock.current_tick

	p4.pos_raw = w4.pos_raw
	Clock.step(1)
	h.assert_true(w4.dist_sq() <= c.wolf_attack_dist_sq, "R18 player really closed into attack range")
	h.assert_eq(w4.state, WolfState.ATTACK,
		"R18 attack range PRE-EMPTS RETREAT - the wolf turns and attacks")
	h.assert_true(Clock.current_tick < entered4 + c.wolf_retreat_ticks,
		"R18 and it attacked BEFORE the retreat would have expired")
	h.despawn(pair4)


## R8: acquisition compares INCLUSIVELY. dist_sq exactly 10000 acquires; 10001
## does not. (100^2 = 10000; 100^2 + 1^2 = 10001.)
func _r8_acquisition_inclusive(h: TestHarness) -> void:
	var c: CombatConfig = TestHarness.make_config()
	c.temp_wall_clamp_enabled = false
	h.assert_eq(c.wolf_acquire_dist_sq, 10000, "R8 configured acquisition threshold")

	var at: Array[Node] = _pair(h, c, 100, 0)
	var w_at: Wolf = at[1]
	Clock.step(1)
	h.assert_eq(w_at.dist_sq(), 10000, "R8 placement really is dist_sq 10000")
	h.assert_true(w_at.is_acquired(), "R8 acquires AT the threshold (<= is inclusive)")
	h.assert_ne(w_at.state, WolfState.IDLE, "R8 left IDLE at exactly 10000")
	h.despawn(at)

	var over: Array[Node] = _pair(h, c, 100, 1)
	var w_over: Wolf = over[1]
	Clock.step(1)
	h.assert_eq(w_over.dist_sq(), 10001, "R8 placement really is dist_sq 10001")
	h.assert_false(w_over.is_acquired(), "R8 does NOT acquire one unit over the threshold")
	h.assert_eq(w_over.state, WolfState.IDLE, "R8 still IDLE at 10001")
	# And it stays IDLE: this is a threshold, not a delay.
	Clock.step(120)
	h.assert_eq(w_over.state, WolfState.IDLE, "R8 still IDLE at 10001 after 120 more ticks")
	h.despawn(over)


## R9: NO LEASH. Once acquired, moving the player far away for 600+ ticks never
## returns the wolf to IDLE and never clears `_acquired`.
func _r9_no_leash(h: TestHarness) -> void:
	var c: CombatConfig = TestHarness.make_config()
	c.temp_wall_clamp_enabled = false
	# Freeze the wolf so it cannot simply chase the player back into range; the
	# separation stays enormous for the whole run.
	c.wolf_move_raw_per_tick = 0

	var pair: Array[Node] = _pair(h, c, 100, 0)
	var p: Player = pair[0]
	var w: Wolf = pair[1]
	Clock.step(1)
	h.assert_true(w.is_acquired(), "R9 acquired before the leash test")

	# Teleport far beyond any plausible leash: dist_sq 4,000,000 (2000 px).
	p.pos_raw = FixedPoint.px_to_raw_v(Vector2i(2000, 0))
	var returned_to_idle: bool = false
	var lost_acquired: bool = false
	var min_seen_dist_sq: int = 1 << 62
	for _i: int in 600:
		Clock.step(1)
		if w.state == WolfState.IDLE:
			returned_to_idle = true
		if not w.is_acquired():
			lost_acquired = true
		min_seen_dist_sq = mini(min_seen_dist_sq, w.dist_sq())

	h.assert_true(min_seen_dist_sq > c.wolf_acquire_dist_sq,
		"R9 the wolf stayed far outside acquisition range (min dist_sq %d)" % min_seen_dist_sq)
	h.assert_false(returned_to_idle, "R9 never returned to IDLE across 600 far ticks")
	h.assert_false(lost_acquired, "R9 _acquired never cleared")
	h.assert_true(w.is_acquired(), "R9 still acquired at the end")
	h.despawn(pair)


## R10: ATTACK lasts EXACTLY 35 ticks. Still ATTACK at entry+34, HUB at entry+35.
func _r10_attack_duration(h: TestHarness) -> void:
	var c: CombatConfig = TestHarness.make_config()
	c.temp_wall_clamp_enabled = false
	c.wolf_move_raw_per_tick = 0
	h.assert_eq(c.wolf_attack_duration_ticks, 35, "R10 configured ATTACK duration")

	# dist_sq 400 (dx 20) is inside the 524 attack threshold, so IDLE -> HUB on the
	# first tick and HUB -> ATTACK on the second.
	var pair: Array[Node] = _pair(h, c, 20, 0)
	var w: Wolf = pair[1]
	var entry: int = -1
	for _i: int in 5:
		Clock.step(1)
		if w.state == WolfState.ATTACK:
			entry = Clock.current_tick
			break
	h.assert_ne(entry, -1, "R10 entered ATTACK")

	Clock.step(34)
	h.assert_eq(Clock.current_tick, entry + 34, "R10 clock is at entry+34")
	h.assert_eq(w.state, WolfState.ATTACK, "R10 still ATTACK at entry+34")
	h.assert_eq(WolfState.name_of(w.state), "ATTACK", "R10 state name at entry+34")

	Clock.step(1)
	h.assert_eq(Clock.current_tick, entry + 35, "R10 clock is at entry+35")
	h.assert_eq(w.state, WolfState.HUB, "R10 back to HUB at exactly entry+35")
	h.despawn(pair)


## R11: the >=36-tick cadence EMERGES from the 35-tick state plus one HUB tick.
## No cooldown field exists to produce it separately.
func _r11_cadence_emerges(h: TestHarness) -> void:
	var c: CombatConfig = TestHarness.make_config()
	c.temp_wall_clamp_enabled = false
	c.wolf_move_raw_per_tick = 0

	# Held permanently inside dist_sq 400 for 400 ticks.
	var pair: Array[Node] = _pair(h, c, 20, 0)
	var w: Wolf = pair[1]
	EventLog.clear()
	Clock.step(400)

	var entries: Array[int] = []
	for r: Dictionary in EventLog.records_of(EventLog.KIND_WOLF_STATE_CHANGE):
		if r["data"]["to"] == WolfState.ATTACK:
			entries.append(r["tick"])
	h.assert_true(entries.size() >= 5,
		"R11 saw enough ATTACK entries to measure cadence (%d)" % entries.size())

	var min_gap: int = 1 << 30
	var all_36: bool = true
	for i: int in range(1, entries.size()):
		var gap: int = entries[i] - entries[i - 1]
		min_gap = mini(min_gap, gap)
		if gap != 36:
			all_36 = false
	h.assert_true(min_gap >= 36, "R11 every ATTACK-to-ATTACK gap is >= 36 (min %d)" % min_gap)
	h.assert_true(all_36, "R11 the emergent cadence is exactly 36 = 35 ATTACK + 1 HUB")
	h.assert_eq(min_gap, c.wolf_attack_duration_ticks + 1,
		"R11 cadence equals attack duration + one HUB tick — derived, not configured")
	h.despawn(pair)

	# No cooldown field exists. If someone adds one, the cadence would be
	# double-counted; this is the guard that makes that a test failure.
	var cooldownish: PackedStringArray = PackedStringArray()
	for p: Dictionary in c.get_property_list():
		var n: String = p["name"]
		if n.to_lower().contains("cooldown") or n.to_lower().contains("recover"):
			cooldownish.append(n)
	h.assert_eq(cooldownish.size(), 0,
		"R11 CombatConfig declares NO cooldown field (found %s)" % [cooldownish])


## P-015: the recovered body extents. The PLAYER's width is direction-dependent -
## 16 facing UP/DOWN, 8 in profile facing LEFT/RIGHT (table 0x086AD30C) - while the
## WOLF is uniform 16x32 in all four directions (tables 0x086B1DE8 / 0x086B1FE0,
## two wolves with identical entries). Asserting the wolf does NOT vary is the half
## that catches a "make everything directional" regression.
##
## Anchoring: the reference rects are origin-anchored with a negative y0
## ((0,-20)..(16,6) and (0,-24)..(16,8)); the remake is top-left anchored, so only
## the EXTENTS carry over. The rect must therefore start AT the actor's pos_raw.
func _p015_body_extents(h: TestHarness) -> void:
	var c: CombatConfig = TestHarness.make_config()
	c.temp_wall_clamp_enabled = false
	var rng := DeterministicRng.new(15)
	var p: Player = h.spawn_player(c, rng, Vector2i(100, 100))
	var w: Wolf = h.spawn_wolf(c, rng, Vector2i(300, 100))

	h.assert_eq(c.player_body_w_facing_px, 16, "P-015 player width facing up/down")
	h.assert_eq(c.player_body_w_profile_px, 8, "P-015 player width in profile")
	h.assert_eq(c.player_body_h_px, 26, "P-015 player height, all directions")
	h.assert_eq(c.wolf_body_w_px, 16, "P-015 wolf width")
	h.assert_eq(c.wolf_body_h_px, 32, "P-015 wolf height")
	h.assert_false(c.is_temp("player_body_w_facing_px"),
		"P-015 the player width is CONFIRMED, not TEMP")
	h.assert_false(c.is_temp("wolf_body_h_px"), "P-015 the wolf height is CONFIRMED, not TEMP")

	# The player NARROWS in profile and keeps its height.
	p.facing = MeleeResolver.DIR_DOWN
	h.assert_eq(p.body_size_px(), Vector2i(16, 26), "P-015 player facing DOWN is 16x26")
	p.facing = MeleeResolver.DIR_UP
	h.assert_eq(p.body_size_px(), Vector2i(16, 26), "P-015 player facing UP is 16x26")
	p.facing = MeleeResolver.DIR_LEFT
	h.assert_eq(p.body_size_px(), Vector2i(8, 26), "P-015 player facing LEFT narrows to 8x26")
	p.facing = MeleeResolver.DIR_RIGHT
	h.assert_eq(p.body_size_px(), Vector2i(8, 26), "P-015 player facing RIGHT narrows to 8x26")

	# And the rect follows the facing, not just the reported size.
	p.facing = MeleeResolver.DIR_DOWN
	var wide: BodyRect = p.body_rect()
	p.facing = MeleeResolver.DIR_LEFT
	var narrow: BodyRect = p.body_rect()
	h.assert_eq(wide.x1 - wide.x0, 16, "P-015 the DOWN-facing body rect is 16 wide")
	h.assert_eq(narrow.x1 - narrow.x0, 8, "P-015 the LEFT-facing body rect is 8 wide")
	h.assert_eq(wide.y1 - wide.y0, narrow.y1 - narrow.y0,
		"P-015 turning changes width only - the height is the same in both")
	h.assert_eq(wide.x0, narrow.x0,
		"P-015 both rects still start at the actor anchor - narrowing does not shift the box")

	# The WOLF does not vary. Every direction, same 16x32.
	for dir: int in [MeleeResolver.DIR_UP, MeleeResolver.DIR_DOWN,
			MeleeResolver.DIR_LEFT, MeleeResolver.DIR_RIGHT]:
		w.facing_hint = dir
		h.assert_eq(w.body_size_px(), Vector2i(16, 32),
			"P-015 the wolf body is 16x32 with facing_hint %d - uniform, not directional" % dir)
		var r: BodyRect = w.body_rect()
		h.assert_eq(r.x1 - r.x0, 16, "P-015 wolf rect width is 16 at facing_hint %d" % dir)
		h.assert_eq(r.y1 - r.y0, 32, "P-015 wolf rect height is 32 at facing_hint %d" % dir)

	# C4 anchoring, asserted directly: the rect starts AT pos_raw's pixel, it is not
	# displaced upward by the reference's negative y0.
	var px: Vector2i = FixedPoint.raw_to_px_v(w.pos_raw)
	var wr: BodyRect = w.body_rect()
	h.assert_eq(Vector2i(wr.x0, wr.y0), px,
		"P-015 the body rect is TOP-LEFT anchored at pos_raw, not origin-anchored")
	h.despawn([p, w])
