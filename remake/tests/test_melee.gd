extends RefCounted
## R4-R6: uniform variant selection, no combo, the 20-tick acceptance gate.

const TestMovement := preload("res://tests/test_movement.gd")


func run(h: TestHarness) -> void:
	h.begin_suite("test_melee (R4-R6)")
	TestMovement.ensure_actions()
	TestMovement.release_all()
	_r4_uniform_variants(h)
	_r5_no_combo(h)
	_r6_acceptance_gate(h)
	TestMovement.release_all()
	h.end_suite()


## Accepted-attack variants over a long hold. Attack is held for the whole run:
## the gate, not the button, decides the rate.
##
## Variants are read from `Player.attack_variant()` on each accepted tick rather
## than from the trace, because EventLog is a 4096-record RING and a 60000-tick
## run evicts its own early records long before the end.
func _collect_variants(h: TestHarness, rng: DeterministicRng, ticks: int) -> Array[int]:
	var c: CombatConfig = TestHarness.make_config()
	# No wolf is spawned, so no contact resolves and no damage roll is drawn — the
	# only rolls the run consumes are melee_variant, one per accepted attack.
	var p: Player = h.spawn_player(c, rng, Vector2i(100, 300))
	Input.action_press(&"attack")
	var out: Array[int] = []
	var last_accept: int = -1
	for _i: int in ticks:
		Clock.step(1)
		# ticks_since_accept == 0 exactly on a tick whose attack was accepted.
		if p.ticks_since_accept(Clock.current_tick) == 0 and Clock.current_tick != last_accept:
			last_accept = Clock.current_tick
			out.append(p.attack_variant())
	Input.action_release(&"attack")
	h.despawn([p])
	return out


## R4: uniform over 3. A seeded DeterministicRng across 3000 accepted attacks —
## every variant appears, none dominates, and immediate repeats occur (they must:
## an avoid-repeat filter would be a combo rule).
func _r4_uniform_variants(h: TestHarness) -> void:
	# 3000 accepted attacks at one per 20 ticks.
	var variants: Array[int] = _collect_variants(h, DeterministicRng.new(20260829), 3000 * 20)
	h.assert_eq(variants.size(), 3000, "R4 accepted attack count over 60000 ticks")

	var counts: Array[int] = [0, 0, 0]
	var repeats: int = 0
	var out_of_range: int = 0
	for i: int in variants.size():
		var v: int = variants[i]
		if v < 0 or v > 2:
			out_of_range += 1
			continue
		counts[v] += 1
		if i > 0 and variants[i - 1] == v:
			repeats += 1
	h.assert_eq(out_of_range, 0, "R4 every variant is inside 0..2")

	for v: int in 3:
		# Uniform over 3 of 3000 draws has mean 1000, sd ~25.8. [850,1150] is ~6sd
		# — wide enough never to flake, tight enough that a 2-way or skewed
		# distribution fails.
		h.assert_range(counts[v], 850, 1150, "R4 variant %d count" % v)
	h.assert_eq(counts[0] + counts[1] + counts[2], 3000, "R4 counts sum to the draw count")
	h.assert_true(repeats > 0, "R4 immediate repeats occur (%d) — no avoid-repeat filter" % repeats)


## R5: no combo. A ScriptedRng forces the variant sequence [0,0,0,1]; the engine
## accepts the repeats verbatim and carries no state between attacks — every
## accepted swing is decided only by the gate and by the roll.
func _r5_no_combo(h: TestHarness) -> void:
	var c: CombatConfig = TestHarness.make_config()
	var rng := DeterministicRng.ScriptedRng.new([0, 0, 0, 1])
	var p: Player = h.spawn_player(c, rng, Vector2i(100, 300))
	EventLog.clear()
	Input.action_press(&"attack")
	Clock.step(4 * c.attack_accept_interval_ticks - 1)
	Input.action_release(&"attack")

	var recs: Array[Dictionary] = EventLog.records_of(EventLog.KIND_ATTACK_ACCEPTED)
	var seq: Array[int] = []
	var ticks: Array[int] = []
	for r: Dictionary in recs:
		seq.append(r["data"]["variant"])
		ticks.append(r["tick"])

	h.assert_eq(seq, [0, 0, 0, 1] as Array[int], "R5 forced repeat sequence accepted verbatim")
	h.assert_true(rng.is_drained(), "R5 the engine consumed exactly the queued rolls")
	# No state carried: the spacing after three identical variants is the same 20
	# as after the first. A combo counter would shorten or lengthen a follow-up.
	var spacings: Array[int] = []
	for i: int in range(1, ticks.size()):
		spacings.append(ticks[i] - ticks[i - 1])
	h.assert_eq(spacings, [20, 20, 20] as Array[int],
		"R5 spacing is constant across a repeat run — no combo state")
	# The 16-tick clip is over well before the next accept, and the variant is
	# cleared between attacks: nothing survives an attack boundary.
	h.assert_false(p.is_attacking(), "R5 attack state cleared between swings")
	h.assert_eq(p.attack_variant(), -1, "R5 variant reset between swings")
	h.despawn([p])


## R6: the gate is 20 ticks and it is on ACCEPTANCE, not on the button. Holding,
## mashing every tick, and pressing only every fifth tick all give the SAME
## accepted count, because none of them can beat the 20-tick interval.
##
## The third arm is the one that discriminates: if acceptance were driven by
## button EDGES rather than by the interval, pressing 40 times in 200 ticks would
## accept up to 40 swings instead of 10.
func _r6_acceptance_gate(h: TestHarness) -> void:
	var c: CombatConfig = TestHarness.make_config()
	h.assert_eq(c.attack_accept_interval_ticks, 20, "R6 configured accept interval")

	var held_ticks: Array[int] = []
	var held: int = _accepted_ticks_for(h, c, "hold", held_ticks)
	var scratch: Array[int] = []
	var mashed: int = _accepted_ticks_for(h, c, "mash", scratch)
	var sparse_ticks: Array[int] = []
	var sparse: int = _accepted_ticks_for(h, c, "sparse", sparse_ticks)

	# 200 ticks, first accepted immediately, then one per 20: 1 + 199/20 = 10.
	h.assert_eq(held, 10, "R6 accepted count while HELD for 200 ticks")
	h.assert_eq(mashed, held, "R6 mashing every tick yields the same count as holding")
	h.assert_eq(sparse, held, "R6 pressing every 5th tick yields the same count too")
	h.assert_true(sparse < 40, "R6 40 presses did not produce 40 accepts (%d)" % sparse)

	h.assert_eq(_gaps(held_ticks), [20, 20, 20, 20, 20, 20, 20, 20, 20] as Array[int],
		"R6 every accepted gap while held is exactly 20 ticks")
	var sparse_gaps: Array[int] = _gaps(sparse_ticks)
	var sparse_min: int = 1 << 30
	for g: int in sparse_gaps:
		sparse_min = mini(sparse_min, g)
	h.assert_true(sparse_min >= 20,
		"R6 sparse presses never beat the interval (min gap %d)" % sparse_min)
	h.assert_ne(c.attack_accept_interval_ticks, c.melee_duration_ticks,
		"R6 the gate (20) is not the animation length (16)")


## Run 200 ticks under one input pattern and return the accepted count, filling
## `out_ticks` with the accepted ticks.
##
## Accepts are read from `ticks_since_accept()`, not from the trace, so the
## measurement is independent of EventLog's ring capacity.
func _accepted_ticks_for(h: TestHarness, c: CombatConfig, mode: String,
		out_ticks: Array[int]) -> int:
	var p: Player = h.spawn_player(c, DeterministicRng.new(7), Vector2i(100, 300))
	var last: int = -1
	if mode == "hold":
		Input.action_press(&"attack")
	for i: int in 200:
		if mode == "mash":
			Input.action_release(&"attack")
			Input.action_press(&"attack")
		elif mode == "sparse":
			if i % 5 == 0:
				Input.action_press(&"attack")
			else:
				Input.action_release(&"attack")
		Clock.step(1)
		if p.ticks_since_accept(Clock.current_tick) == 0 and Clock.current_tick != last:
			last = Clock.current_tick
			out_ticks.append(Clock.current_tick)
	Input.action_release(&"attack")
	h.despawn([p])
	return out_ticks.size()


func _gaps(ticks: Array[int]) -> Array[int]:
	var out: Array[int] = []
	for i: int in range(1, ticks.size()):
		out.append(ticks[i] - ticks[i - 1])
	return out
