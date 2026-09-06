extends RefCounted
## R19: the debug playtest tooling - several wolves at once, and the F7 respawn.
##
## These cover TOOLING, not behaviour: no threshold, duration or config value is
## asserted here that another suite owns. What they pin down is that the scalar
## single-wolf bindings became collections without changing what combat does.
##
## Body geometry, matching the other suites:
##   player 16x26 px anchored top-left -> center (px.x + 8, px.y + 13)
##   wolf   16x32 px anchored top-left -> center (px.x + 8, px.y + 16)
## P-015 recovered extents. The player's WIDTH is direction-dependent (16 facing
## UP/DOWN, 8 in profile); these suites never leave the default DIR_DOWN, so 16 is
## the width in play and the centre-x offset is 8 throughout.

## Forces a non-critical roll through ScriptedRng: `on_contact` draws base damage
## first, then the crit permille, and crit_roll passes when the popped value is
## <= permille. 1001 is above every permille the config carries.
const NO_CRIT: int = 1001
const BASE_DAMAGE: int = 50996


func run(h: TestHarness) -> void:
	h.begin_suite("test_multi_wolf (R19 debug tooling)")
	_r19_targets_hold_multiple_wolves(h)
	_r19_reach_picks_the_wolf_in_range(h)
	_r19_dead_wolf_is_skipped_not_crashed(h)
	_r19_respawn_restores_hp(h)
	_r19_respawn_clears_state_and_position(h)
	h.end_suite()


## Wolf anchor placing its centre `dx, dy` pixels from a player centred at (8, 13).
func _wolf_px_for(dx: int, dy: int) -> Vector2i:
	return Vector2i(8 + dx - 8, 13 + dy - 16)


## R19: `player.targets` is an array and the reach loop walks all of it. Two
## wolves both sitting in the list is the state test_room now builds at startup.
func _r19_targets_hold_multiple_wolves(h: TestHarness) -> void:
	var c: CombatConfig = TestHarness.make_config()
	c.temp_wall_clamp_enabled = false
	var rng := DeterministicRng.new(19)
	var p: Player = h.spawn_player(c, rng, Vector2i(0, 0))
	# Both far enough away that neither is in reach; this case is about the
	# BINDING, not about contact.
	var a: Wolf = h.spawn_wolf(c, rng, _wolf_px_for(300, 0))
	var b: Wolf = h.spawn_wolf(c, rng, _wolf_px_for(-300, 0))
	p.targets = [a, b]

	h.assert_eq(p.targets.size(), 2, "R19 targets holds both wolves")
	h.assert_true(p.targets.has(a), "R19 targets includes wolf a")
	h.assert_true(p.targets.has(b), "R19 targets includes wolf b")
	h.assert_true(a.is_hittable(), "R19 wolf a starts hittable")
	h.assert_true(b.is_hittable(), "R19 wolf b starts hittable")
	h.despawn([p, a, b])


## R19: with two wolves present, an accepted swing hits the one actually in reach
## and leaves the far one untouched. This is the multi-target reach test: the
## single-wolf version could not distinguish "hits the only wolf" from "hits the
## right wolf".
func _r19_reach_picks_the_wolf_in_range(h: TestHarness) -> void:
	var c: CombatConfig = TestHarness.make_config()
	c.temp_wall_clamp_enabled = false
	# The player's variant roll is drawn from its own generator so the queued
	# damage values below are consumed only by the wolf that is actually hit.
	var p: Player = h.spawn_player(c, DeterministicRng.new(19), Vector2i(0, 0))
	# NEAR sits on top of the player, comfortably inside the expanded melee box.
	var near: Wolf = h.spawn_wolf(
		c, DeterministicRng.ScriptedRng.new([BASE_DAMAGE, NO_CRIT]), _wolf_px_for(0, 0)
	)
	# FAR is 300 px away on the x axis - outside any reach the config describes.
	var far: Wolf = h.spawn_wolf(
		c, DeterministicRng.ScriptedRng.new([BASE_DAMAGE, NO_CRIT]), _wolf_px_for(300, 0)
	)
	# Deliberately FAR first in the list: a loop that only ever looked at entry 0
	# would find nothing in reach and silently pass a single-wolf test.
	p.targets = [far, near]

	var near_hp: int = near.combatant.hp_raw
	var far_hp: int = far.combatant.hp_raw
	h.assert_true(MeleeResolver.in_reach(p.body_rect(), near.body_rect(), c),
		"R19 the near wolf is inside the expanded melee box")
	h.assert_false(MeleeResolver.in_reach(p.body_rect(), far.body_rect(), c),
		"R19 the far wolf is outside it")

	Input.action_press(&"attack")
	Clock.step(1)
	Input.action_release(&"attack")

	h.assert_eq(near.state, WolfState.REACTION,
		"R19 the in-reach wolf took the hit even though it is second in targets")
	h.assert_ne(far.state, WolfState.REACTION, "R19 the far wolf was not hit")
	h.assert_eq(far.combatant.hp_raw, far_hp, "R19 the far wolf's hp is untouched")

	# One swing = one hit: the damage lands on the near wolf at entry+3 only.
	Clock.step(c.wolf_reaction_damage_offset_ticks)
	h.assert_ne(near.combatant.hp_raw, near_hp, "R19 the near wolf took damage")
	h.assert_eq(far.combatant.hp_raw, far_hp, "R19 the far wolf still took none")
	h.despawn([p, near, far])


## R19: a DEAD wolf must not break the collections that reference it. wolf.gd
## hides the node rather than freeing it, so the reference stays valid and the
## guard that matters is `is_hittable`, which the reach loop already applies.
func _r19_dead_wolf_is_skipped_not_crashed(h: TestHarness) -> void:
	var c: CombatConfig = TestHarness.make_config()
	c.temp_wall_clamp_enabled = false
	var p: Player = h.spawn_player(c, DeterministicRng.new(19), Vector2i(0, 0))
	# Enough queued pairs to kill: base damage repeated, never critical.
	var rng := DeterministicRng.ScriptedRng.new([])
	for _i: int in 8:
		rng.push_values([BASE_DAMAGE, NO_CRIT])
	var w: Wolf = h.spawn_wolf(c, rng, _wolf_px_for(0, 0))
	p.targets = [w]

	# Four confirmed hits kill the wolf; drive contacts directly so the test does
	# not depend on the 20-tick acceptance gate. Each iteration lands one contact
	# and then waits out the FULL reaction, because a hit landing mid-REACTION
	# restarts the 24-tick window rather than stacking a second kill's worth of
	# damage - stepping only to the +3 damage tick would loop forever.
	var guard: int = 0
	while w.is_hittable() and guard < 8:
		w.on_contact(Clock.current_tick, MeleeResolver.DIR_LEFT)
		Clock.step(c.wolf_reaction_duration_ticks + 1)
		guard += 1
	h.assert_eq(w.state, WolfState.DEAD, "R19 the wolf reached DEAD")
	h.assert_false(w.is_hittable(), "R19 a DEAD wolf is not hittable")
	h.assert_true(is_instance_valid(w),
		"R19 death HIDES the node rather than freeing it, so references stay valid")

	# The node is still valid, so every collection that holds it is still safe to
	# read - this is what keeps _draw from touching a freed object.
	h.assert_ne(w.body_rect(), null, "R19 body_rect on a dead wolf is still callable")

	# A swing with only a dead wolf in targets resolves to nothing and must not
	# error: the reach loop skips it on is_hittable.
	Input.action_press(&"attack")
	Clock.step(1)
	Input.action_release(&"attack")
	h.assert_eq(w.state, WolfState.DEAD, "R19 a dead wolf is skipped by the reach test")
	h.despawn([p, w])


## R19: F7 restores full HP. The core of the respawn contract.
func _r19_respawn_restores_hp(h: TestHarness) -> void:
	var c: CombatConfig = TestHarness.make_config()
	var rng := DeterministicRng.ScriptedRng.new([BASE_DAMAGE, NO_CRIT])
	var w: Wolf = h.spawn_wolf(c, rng, Vector2i(200, 200))
	var full: int = w.combatant.hp_raw
	h.assert_eq(full, c.wolf_hp_raw, "R19 the wolf starts at the configured full hp")

	Clock.step(1)
	w.on_contact(Clock.current_tick, MeleeResolver.DIR_LEFT)
	Clock.step(c.wolf_reaction_damage_offset_ticks)
	h.assert_true(w.combatant.hp_raw < full, "R19 the wolf is damaged before the respawn")

	w.reset_to_start()
	h.assert_eq(w.combatant.hp_raw, full, "R19 respawn restores FULL hp")
	h.assert_eq(Damage.to_displayed_hp(w.combatant.hp_raw, c),
		Damage.to_displayed_hp(c.wolf_hp_raw, c), "R19 displayed hp is back to full too")
	h.despawn([w])


## R19: respawn also clears the state machine and puts the wolf back at its start
## position - an F7 that restored HP but left the wolf mid-REACTION with a pending
## damage tick would not give the repeatable observation the key exists for.
func _r19_respawn_clears_state_and_position(h: TestHarness) -> void:
	var c: CombatConfig = TestHarness.make_config()
	c.temp_wall_clamp_enabled = false
	var start := Vector2i(200, 200)
	var rng := DeterministicRng.ScriptedRng.new([BASE_DAMAGE, NO_CRIT])
	var w: Wolf = h.spawn_wolf(c, rng, start)
	# The P-013 slide is armed from the ATTACKER's position at contact, so
	# `on_contact` computes a zero step when `target` is null. A player placed away
	# from the wolf is what makes the knockback actually move it.
	var p: Player = h.spawn_player(c, DeterministicRng.new(19), Vector2i(120, 200))
	p.targets = []
	w.target = p
	var start_raw: Vector2i = w.pos_raw

	Clock.step(1)
	w.on_contact(Clock.current_tick, MeleeResolver.DIR_LEFT)
	h.assert_eq(w.state, WolfState.REACTION, "R19 the wolf is mid-REACTION before respawn")
	h.assert_ne(w.damage_tick(), -1, "R19 a damage tick is scheduled before respawn")
	# The knockback slide has moved it off its start position.
	Clock.step(2)
	h.assert_ne(w.pos_raw, start_raw, "R19 the wolf has been knocked off its start")

	w.reset_to_start()
	h.assert_eq(w.state, WolfState.IDLE, "R19 respawn returns the wolf to IDLE")
	h.assert_eq(w.pos_raw, start_raw, "R19 respawn returns it to its start position")
	h.assert_eq(w.damage_tick(), -1, "R19 respawn disarms the scheduled damage")
	h.assert_eq(w.ticks_remaining(Clock.current_tick), -1,
		"R19 respawn disarms the state deadline")
	h.assert_false(w.is_acquired(), "R19 respawn clears the acquisition latch")
	h.assert_true(w.is_hittable(), "R19 a respawned wolf is hittable again")
	h.assert_true(w.visible, "R19 a respawned wolf is visible again")

	# A respawned wolf still runs its normal state machine: nothing about the reset
	# disables the AI.
	h.despawn([p, w])
