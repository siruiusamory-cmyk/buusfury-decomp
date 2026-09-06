extends RefCounted
## R1-R3: cardinal rate, unnormalized diagonals, immediate acceleration.
##
## Movement is driven through the real input path (InputMap + Input.action_press)
## rather than by poking pos_raw, so the input-delay ring is exercised too. The
## clock is stepped by hand; nothing here awaits a frame.

const ACTIONS: Array[StringName] = [
	&"move_up", &"move_down", &"move_left", &"move_right", &"attack",
]


## The project ships no InputMap entries (scenes/test_room.gd creates them at
## runtime), so the suite registers bare actions. No key events are needed:
## Input.action_press/action_release drive the action directly.
static func ensure_actions() -> void:
	for a: StringName in ACTIONS:
		if not InputMap.has_action(a):
			InputMap.add_action(a)


static func release_all() -> void:
	for a: StringName in ACTIONS:
		if InputMap.has_action(a):
			Input.action_release(a)


func run(h: TestHarness) -> void:
	h.begin_suite("test_movement (R1-R3)")
	ensure_actions()
	release_all()
	_r1_cardinal(h)
	_r2_diagonal_unnormalized(h)
	_r3_immediate_acceleration(h)
	release_all()
	h.end_suite()


## R1: holding Right for 10 APPLIED ticks moves exactly 10 * 352 = 3520 raw on x
## and nothing on y. The ring adds input_delay_ticks of latency, so the run is
## delay + 10 ticks long and the delta is measured across the whole run.
func _r1_cardinal(h: TestHarness) -> void:
	var c: CombatConfig = TestHarness.make_config()
	c.temp_wall_clamp_enabled = false  # a clamp would mask the real displacement
	var p: Player = h.spawn_player(c, DeterministicRng.new(1), Vector2i(100, 300))
	var before: Vector2i = p.pos_raw

	Input.action_press(&"move_right")
	Clock.step(c.input_delay_ticks + 10)
	Input.action_release(&"move_right")

	var delta: Vector2i = p.pos_raw - before
	h.assert_eq(delta.x, 3520, "R1 hold Right 10 applied ticks -> delta.x raw")
	h.assert_eq(delta.y, 0, "R1 cardinal move leaves the other axis alone")
	h.assert_eq(c.move_raw_per_tick, 352, "R1 configured rate is 352 raw/tick")
	h.despawn([p])


## R2: Right+Down moves BOTH axes the full 352 in ONE applied tick. The diagonal
## resultant therefore exceeds the cardinal one — it is NOT normalized.
func _r2_diagonal_unnormalized(h: TestHarness) -> void:
	var c: CombatConfig = TestHarness.make_config()
	c.temp_wall_clamp_enabled = false
	var p: Player = h.spawn_player(c, DeterministicRng.new(2), Vector2i(100, 100))
	var before: Vector2i = p.pos_raw

	Input.action_press(&"move_right")
	Input.action_press(&"move_down")
	Clock.step(c.input_delay_ticks + 1)
	Input.action_release(&"move_right")
	Input.action_release(&"move_down")

	var delta: Vector2i = p.pos_raw - before
	h.assert_eq(delta.x, 352, "R2 diagonal x moves the FULL cardinal rate")
	h.assert_eq(delta.y, 352, "R2 diagonal y moves the FULL cardinal rate")
	# Squared magnitudes, so the comparison stays integer: 352^2 * 2 = 247808 vs
	# the cardinal 352^2 = 123904. A normalized diagonal would give 123904.
	var diag_mag_sq: int = delta.x * delta.x + delta.y * delta.y
	var card_mag_sq: int = 352 * 352
	h.assert_eq(diag_mag_sq, 247808, "R2 diagonal resultant magnitude squared")
	h.assert_true(diag_mag_sq > card_mag_sq,
		"R2 diagonal (%d) exceeds cardinal (%d) — unnormalized" % [diag_mag_sq, card_mag_sq])
	h.despawn([p])


## R3: no ramp. The FIRST tick that moves at all already moves the full 352, and
## the second moves the same 352 — an accelerating implementation would produce a
## smaller first step than second.
func _r3_immediate_acceleration(h: TestHarness) -> void:
	var c: CombatConfig = TestHarness.make_config()
	c.temp_wall_clamp_enabled = false
	var p: Player = h.spawn_player(c, DeterministicRng.new(3), Vector2i(100, 300))

	Input.action_press(&"move_right")
	# Ticks 1..input_delay_ticks apply the pre-filled neutral entries: no motion.
	Clock.step(c.input_delay_ticks)
	h.assert_eq(p.pos_raw.x - FixedPoint.px_to_raw_v(Vector2i(100, 300)).x, 0,
		"R3 no motion during the %d-tick input delay" % c.input_delay_ticks)

	var a: int = p.pos_raw.x
	Clock.step(1)
	var first_step: int = p.pos_raw.x - a
	Clock.step(1)
	var second_step: int = p.pos_raw.x - a - first_step
	Input.action_release(&"move_right")

	h.assert_eq(first_step, 352, "R3 first moving tick is already full magnitude")
	h.assert_eq(second_step, first_step, "R3 second tick equals the first — no ramp")
	h.despawn([p])
