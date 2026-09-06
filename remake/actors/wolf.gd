class_name Wolf
extends TickNode
## The wolf state machine. Seven states, integer deadlines, no physics.
##
## Two prohibitions this file exists to hold:
##
##   P-007: NO LEASH. Disengagement is recorded as NONE, CONFIRMED BEHAVIOR,
##   verified out to radius 157 and independently by gameplay. The 157 figure is a
##   lower bound on observed engagement, not a leash value. `_acquired` is
##   write-once. Do not add a distance-based exit.
##
##   P-007: NO SEPARATE COOLDOWN. The >=36-tick attack cadence is an EMERGENT
##   consequence of the 35-tick ATTACK state plus one tick to re-decide in HUB.
##   No executable cooldown timer was found; the +0x12 counter was tested and
##   REFUTED. Adding a timer would double-count it.
##
## Diagnostics: every state change prints, and every scheduled moment (reaction
## entry, damage application) prints with its absolute tick - which is what makes
## the three-moment separation observable in stdout, not just in the trace.

## Injected by scenes/test_room.gd.
@export var config: CombatConfig
@export var start_px: Vector2i = Vector2i(520, 300)

## Injected by scenes/test_room.gd. Never the global generator.
var rng: DeterministicRng = null
## The pursuit target. Injected by test_room.gd.
var target: Player = null

var state: int = WolfState.IDLE
var pos_raw: Vector2i = Vector2i.ZERO
var combatant: Combatant = null

## Deadline for timed states; -1 for untimed (IDLE, HUB, PURSUIT, DEAD).
var _state_end_tick: int = -1
## Absolute tick at which `_pending_damage` applies; -1 when nothing is scheduled.
var _damage_tick: int = -1
var _pending_damage: int = 0
var _pending_crit: bool = false
## Latches TRUE forever once set. Write-once by construction.
var _acquired: bool = false
var _last_dist_sq: int = 0
var _attack_entry_ticks: Array[int] = []
## P-003 hit-direction byte from the last contact. Placeholder art only.
var facing_hint: int = MeleeResolver.DIR_DOWN
## P-013 knockback slide. The per-tick delta is computed ONCE at contact and
## re-applied bit-identically every tick, because the measurement says the delta
## is exactly constant within a hit - no decay, no friction, no easing.
var _knockback_step: Vector2i = Vector2i.ZERO
## Absolute tick the slide stops on; -1 when not sliding.
var _knockback_end_tick: int = -1
## Presentation only: consecutive ticks spent closing on the target.
var _walk_counter: int = 0
## TEMP DIAGNOSTIC (2026-08-30): previous tick position, for the [MOVE] log.
var _diag_prev_pos: Vector2i = Vector2i.ZERO


func _ready() -> void:
	super()
	pos_raw = FixedPoint.px_to_raw_v(start_px)
	combatant = Combatant.new(config.wolf_hp_raw)
	_sync_render()
	print("[Wolf] ready start_px=%s hp_raw=%d displayed=%d acquire<=%d attack<=%d" % [
		start_px, combatant.hp_raw, Damage.to_displayed_hp(combatant.hp_raw, config),
		config.wolf_acquire_dist_sq, config.wolf_attack_dist_sq,
	])


func _on_tick(t: int) -> void:
	# Scheduled damage is evaluated FIRST, before any state timeout, so a hit that
	# kills during reaction still applies on its exact scheduled tick.
	_apply_scheduled_damage(t)

	if state == WolfState.DEAD:
		# Presentation only. The node is hidden by _die while
		# temp_death_anim_ticks is 0, so wolf_dead.png is loaded but unseen; this
		# keeps the sprite correct if that TEMP value ever becomes nonzero.
		_sync_sprite()
		return

	if target != null:
		_last_dist_sq = BodyRect.center_dist_sq(body_rect(), target.body_rect())

	match state:
		WolfState.IDLE:
			_tick_idle(t)
		WolfState.HUB:
			_tick_hub(t)
		WolfState.PURSUIT:
			_tick_pursuit(t)
		WolfState.ATTACK:
			_tick_attack(t)
		WolfState.REACTION:
			_tick_reaction(t)
		WolfState.RETREAT:
			_tick_retreat(t)

	# P-013: the slide advances AFTER the state tick, so it is purely additive to
	# whatever REACTION did (which is nothing but count down). It is not a state.
	_tick_knockback(t)

	# TEMP DIAGNOSTIC (2026-08-30): total per-tick motion from ALL sources, so a
	# log line exists even on ticks where no knockback is armed. Distinguishes
	# "the slide did nothing" from "the wolf walked back toward the player".
	if _diag_prev_pos != pos_raw:
		print("[MOVE] t=%d st=%s delta=%s pos=%s" % [
			t, WolfState.name_of(state), pos_raw - _diag_prev_pos, pos_raw,
		])
	_diag_prev_pos = pos_raw

	_sync_render()
	_sync_sprite()


## Optional runtime sprite. Absent art leaves the ColorRect placeholder visible
## and this is a no-op. Driven from the gameplay tick, never from _process.
func _sync_sprite() -> void:
	var sprite: Sprite2D = get_node_or_null(^"Sprite") as Sprite2D
	if sprite == null:
		return
	# RETREAT walks too - it just walks backwards. `_tick_retreat` has already
	# pointed facing_hint along the step, so the sprite reads as a wolf backing
	# off rather than a wolf standing still.
	var moving: bool = state == WolfState.PURSUIT or state == WolfState.RETREAT
	_walk_counter = (_walk_counter + 1) if moving else 0
	var tex: Texture2D = null
	if state == WolfState.DEAD:
		tex = SpriteSet.get_texture("wolf_dead")
	elif state == WolfState.REACTION:
		# `facing_hint` carries the P-003 hit direction from contact, so the
		# flinch faces the way the wolf was struck. SpriteSet.hurt falls back to
		# the non-directional frame, then null, which drops through to `frame()`.
		tex = SpriteSet.hurt("wolf", facing_hint)
	if tex == null:
		tex = SpriteSet.frame(
			"wolf", facing_hint, moving, state == WolfState.ATTACK,
			SpriteSet.step_phase(_walk_counter)
		)
	sprite.texture = tex
	sprite.visible = tex != null
	sprite.position = SpriteSet.sprite_offset(tex, body_size_px())
	var body: ColorRect = get_node_or_null(^"Body") as ColorRect
	if body != null:
		body.visible = tex == null


# --- states ------------------------------------------------------------------

## Acquisition: inclusive `<=`, because the recovered branch is a signed bgt to
## failure. Once acquired, `_acquired` never goes back to false.
func _tick_idle(t: int) -> void:
	if _last_dist_sq <= config.wolf_acquire_dist_sq:
		_acquired = true
		print("[Wolf] ACQUIRED t=%d dist_sq=%d threshold=%d (latched, NO LEASH)" % [
			t, _last_dist_sq, config.wolf_acquire_dist_sq,
		])
		_set_state(t, WolfState.HUB)


## P-012: HUB DWELLS. The pause players see mid-pursuit IS this hub visit - in the
## reference, ~71% of each pause is spent in the hub selector, which does not move
## the actor. Attack range still wins outright: an in-range wolf attacks on the
## spot rather than waiting the dwell out.
func _tick_hub(t: int) -> void:
	if _last_dist_sq <= config.wolf_attack_dist_sq:
		_enter_attack(t)
		return
	if _state_end_tick >= 0 and t < _state_end_tick:
		return
	_set_state(t, WolfState.PURSUIT)


func _tick_pursuit(t: int) -> void:
	if _last_dist_sq <= config.wolf_attack_dist_sq:
		_enter_attack(t)
		return
	# P-012: memoryless per-tick exit through the reference chance gate. NOT a
	# leash and NOT a timer - the roll is independent every tick and ignores
	# distance entirely. The heading change players notice on the far side is
	# EMERGENT: HUB re-targets the player's CURRENT position after a stationary
	# gap, so no separate reposition behavior exists or is wanted.
	if rng.gate_roll(config.temp_wolf_pursuit_exit_threshold):
		_enter_hub(t)
		return
	# P-014: back off instead of closing. Proximity is NECESSARY BUT NOT
	# SUFFICIENT - the wolf is inside this band for half of its pursuit time and
	# mostly keeps coming - so a chance gate sits behind the distance test. The
	# threshold is TEMP: P-014 proved a roll exists but never measured its rate.
	if (_last_dist_sq <= config.wolf_retreat_max_dist_sq
			and rng.gate_roll(config.temp_wolf_retreat_threshold)):
		_enter_retreat(t)
		return
	_close_on_target()


## RETREAT with the P-014 deadline armed, on the same `_state_end_tick`
## mechanism ATTACK, REACTION and the hub dwell already use.
func _enter_retreat(t: int) -> void:
	_set_state(t, WolfState.RETREAT)
	_state_end_tick = t + config.wolf_retreat_ticks


## HUB with the P-012 dwell deadline armed. Uses the same `_state_end_tick`
## mechanism ATTACK and REACTION already use rather than a second timer.
func _enter_hub(t: int) -> void:
	_set_state(t, WolfState.HUB)
	_state_end_tick = t + config.temp_wolf_hub_dwell_ticks


func _tick_attack(t: int) -> void:
	# Exactly 35 ticks (exact in 52/52 observed episodes), then HUB. The next
	# ATTACK can therefore begin no sooner than entry+36 - emergent, not timed.
	if t >= _state_end_tick:
		_set_state(t, WolfState.HUB)


func _tick_reaction(t: int) -> void:
	if t >= _state_end_tick:
		EventLog.emit_reaction_exit(t)
		_set_state(t, WolfState.HUB)


func _enter_attack(t: int) -> void:
	_set_state(t, WolfState.ATTACK)
	_state_end_tick = t + config.wolf_attack_duration_ticks
	var spacing: int = -1
	if not _attack_entry_ticks.is_empty():
		spacing = t - _attack_entry_ticks[_attack_entry_ticks.size() - 1]
	_attack_entry_ticks.append(t)
	print("[Wolf] ATTACK entry t=%d end_tick=%d dist_sq=%d spacing_since_prev=%d" % [
		t, _state_end_tick, _last_dist_sq, spacing,
	])


## P-011: the wolf caps its RESULTANT step at `wolf_move_raw_per_tick` (153) and
## splits it across the axes, so a diagonal is no faster than a cardinal. This is
## deliberately NOT the player's model, whose per-axis 352 is unnormalized and
## therefore faster on the diagonal (P-002). Both are confirmed; do not unify them.
func _close_on_target() -> void:
	if target == null:
		return
	var step: int = config.wolf_move_raw_per_tick
	var d: Vector2i = target.pos_raw - pos_raw
	# PRESENTATION ONLY. Points the sprite along the step it is about to take, by
	# the same rule player.gd uses for its own movement. Nothing in the simulation
	# reads facing_hint - not the reach test, not a state transition - so this
	# cannot feed back into pursuit, attack range, or melee resolution.
	if absi(d.y) < absi(d.x):
		facing_hint = MeleeResolver.DIR_LEFT if d.x < 1 else MeleeResolver.DIR_RIGHT
	else:
		facing_hint = MeleeResolver.DIR_UP if d.y < 1 else MeleeResolver.DIR_DOWN
	if d.length_squared() <= step * step:
		# Close enough to land exactly this tick; moving further would overshoot.
		pos_raw = target.pos_raw
		return
	# Scale d down to length `step`. Integer truncation keeps the resultant at or
	# just under the cap and never lets either axis exceed it.
	var len_raw: float = sqrt(float(d.length_squared()))
	pos_raw.x += int(float(d.x) * float(step) / len_raw)
	pos_raw.y += int(float(d.y) * float(step) / len_raw)


## The `_close_on_target` scaling, INVERTED: a step of length `step` pointing
## from `from_raw` towards this wolf, i.e. directly away from whatever is at
## `from_raw`. Shared by the P-013 knockback slide and the P-014 retreat so there
## is exactly one direction convention in this file. Zero when the two positions
## coincide and no direction exists.
func _step_away_from(from_raw: Vector2i, step: int) -> Vector2i:
	var d: Vector2i = pos_raw - from_raw
	var len_sq: int = d.length_squared()
	if len_sq == 0:
		return Vector2i.ZERO
	var len_raw: float = sqrt(float(len_sq))
	return Vector2i(
		int(float(d.x) * float(step) / len_raw),
		int(float(d.y) * float(step) / len_raw),
	)


## PRESENTATION ONLY, same rule as `_close_on_target`: point the sprite along the
## step being taken. Nothing in the simulation reads facing_hint.
func _face_along(d: Vector2i) -> void:
	if absi(d.y) < absi(d.x):
		facing_hint = MeleeResolver.DIR_LEFT if d.x < 1 else MeleeResolver.DIR_RIGHT
	else:
		facing_hint = MeleeResolver.DIR_UP if d.y < 1 else MeleeResolver.DIR_DOWN


## P-014: RETREAT backs straight away from the target at `wolf_retreat_speed_raw`
## until the `_state_end_tick` deadline, then returns to HUB so the existing hub
## dwell applies. Attack range is tested FIRST, exactly as HUB and PURSUIT do, so
## a player who closes in during the retreat is attacked rather than fled from.
func _tick_retreat(t: int) -> void:
	if _last_dist_sq <= config.wolf_attack_dist_sq:
		_enter_attack(t)
		return
	if t >= _state_end_tick:
		_enter_hub(t)
		return
	if target == null:
		return
	var step: Vector2i = _step_away_from(target.pos_raw, config.wolf_retreat_speed_raw)
	_face_along(step)
	pos_raw += step


## P-013: the slide. Runs CONCURRENTLY with REACTION off its own deadline rather
## than as a state, because the measurement puts the 23-tick slide inside the
## 24-tick hitstun, not beside it. Constant velocity: the same integer delta,
## every tick, then a dead stop.
func _tick_knockback(t: int) -> void:
	if _knockback_end_tick < 0:
		return
	if t >= _knockback_end_tick:
		_knockback_end_tick = -1
		_knockback_step = Vector2i.ZERO
		print("[KB] t=%d SLIDE END pos_raw=%s" % [t, pos_raw])
		return
	# TEMP DIAGNOSTIC (2026-08-30): the maintainer reports the wolf does not visibly travel
	# on hit. Isolated probes show the slide applying correctly, so this logs the
	# LIVE per-tick truth - position before and after the slide, plus the wolf's
	# own state - to separate knockback from the wolf's own walking. Remove once
	# the question is settled.
	var before: Vector2i = pos_raw
	pos_raw += _knockback_step
	print("[KB] t=%d st=%s step=%s pos %s -> %s dist_px=%.1f" % [
		t, WolfState.name_of(state), _knockback_step, before, pos_raw,
		sqrt(float(_last_dist_sq)),
	])


# --- the three moments -------------------------------------------------------

## MOMENT 1 -> 2. Called by the player on the accepted-attack tick, after the
## reach test passed. CONTACT already went to the trace; this schedules REACTION
## ENTRY (same tick, distinct moment) and the damage application at entry + 3.
## Damage is ROLLED here and held; it is NOT applied.
##
## REACTION supersedes ATTACK: a hit landing mid-attack cancels it and restarts
## the 24-tick reaction. Entering REACTION never clears `_acquired`.
func on_contact(t: int, dir: int) -> void:
	if state == WolfState.DEAD:
		return
	var base_raw: int = Damage.roll_base_raw(config, rng)
	# Critical is decided at CONTACT and rides along with the pending damage, so
	# the number-popup asset choice is derivable without re-rolling.
	var crit: bool = rng.crit_roll(config.temp_crit_chance_permille)
	var raw: int = Damage.apply_critical(base_raw, config) if crit else base_raw

	_pending_damage = raw
	_pending_crit = crit
	_state_end_tick = t + config.wolf_reaction_duration_ticks
	_damage_tick = t + config.wolf_reaction_damage_offset_ticks
	facing_hint = dir
	# P-013: arm the constant-velocity slide, directly away from the attacker's
	# position AT CONTACT. Computed once here and never recomputed, so a moving
	# attacker cannot bend the slide mid-flight - the measured deltas are constant.
	if target != null:
		_knockback_step = _step_away_from(target.pos_raw, config.wolf_knockback_speed_raw)
		# `t` is the CONTACT tick, which has already run its movement; the first
		# tick that actually slides is t+1. The deadline therefore carries a +1 so
		# the wolf takes exactly `wolf_knockback_ticks` steps, matching the measured
		# slide length rather than one short of it.
		_knockback_end_tick = t + 1 + config.wolf_knockback_ticks
	_set_state(t, WolfState.REACTION)
	EventLog.emit_reaction_enter(t, _state_end_tick, _damage_tick)
	print("[Wolf] REACTION entry t=%d end=%d damage_tick=%d pending_raw=%d crit=%s" % [
		t, _state_end_tick, _damage_tick, raw, crit,
	])


## MOMENT 3. Evaluated at the TOP of _on_tick, before any state timeout.
func _apply_scheduled_damage(t: int) -> void:
	if _damage_tick < 0 or t < _damage_tick:
		return
	var raw: int = _pending_damage
	var crit: bool = _pending_crit
	_damage_tick = -1
	_pending_damage = 0
	_pending_crit = false

	var lethal: bool = combatant.take_damage(raw)
	EventLog.emit_damage_applied(
		t, raw, Damage.to_displayed_hp(raw, config), crit, combatant.hp_raw
	)
	if lethal:
		_die(t)


func _die(t: int) -> void:
	_set_state(t, WolfState.DEAD)
	_state_end_tick = -1
	EventLog.emit_death(t)

	# The reward AMOUNT is fixed HERE, from the bonus items of whoever is active
	# at the kill. The RECIPIENT is deliberately not recorded - Party resolves it
	# at payout, one tick later.
	var bonus_items: int = 0
	var killer: Character = Party.active_character()
	if killer != null:
		bonus_items = killer.equipment_bonus_items
	var reward: Reward = Reward.create(config.wolf_base_exp, bonus_items, config, t)
	EventLog.emit_reward_created(t, reward.amount, reward.payout_tick)
	Party.queue_reward(reward)

	_roll_drop(t)
	# temp_death_anim_ticks = 0: the duration was never measured, so the wolf
	# vanishes immediately and the overlay flags it TEMP.
	visible = config.temp_death_anim_ticks > 0


## TEMP: the drop roll producer is UNKNOWN (P-010); this roll is invented and the
## overlay labels the drop line TEMP. Nothing is spawned or picked up.
## `crit_roll` is DeterministicRng's only permille primitive; it is reused here
## rather than adding a near-duplicate method, and it routes through the same
## injected `next_int` so a ScriptedRng still controls the outcome.
func _roll_drop(t: int) -> void:
	if rng.crit_roll(config.temp_drop_chance_permille):
		var denoms: PackedInt32Array = config.zeni_denominations
		var amount: int = denoms[rng.drop_index(denoms.size())]
		EventLog.emit_drop(t, "zeni", amount)


# --- helpers -----------------------------------------------------------------

func _set_state(t: int, next: int) -> void:
	if next == state:
		return
	var prev: int = state
	state = next
	# RETREAT joins ATTACK and REACTION as a state whose caller arms the deadline
	# immediately after this call; HUB's dwell is armed the same way by _enter_hub,
	# which re-arms after the clear.
	if (next != WolfState.ATTACK and next != WolfState.REACTION
			and next != WolfState.RETREAT):
		_state_end_tick = -1
	EventLog.emit_wolf_state_change(t, prev, next)
	print("[Wolf] state t=%d %s -> %s dist_sq=%d acquired=%s hp_raw=%d" % [
		t, WolfState.name_of(prev), WolfState.name_of(next), _last_dist_sq,
		_acquired, combatant.hp_raw,
	])


## DEBUG TOOLING ONLY (F7). Puts this wolf back exactly where `_ready` left it:
## full HP at `start_px`, IDLE, every deadline disarmed and every latch cleared.
## Behaviour is untouched - no threshold, duration or config value is read here
## that `_ready` does not already read, and nothing calls this from the simulation.
##
## `_acquired` is cleared deliberately and this is NOT a leash: P-007 forbids a
## DISTANCE-based exit during a life, and this runs only when the playtester asks
## for a fresh observation, which is the same fresh start a newly spawned wolf gets.
func reset_to_start() -> void:
	pos_raw = FixedPoint.px_to_raw_v(start_px)
	combatant = Combatant.new(config.wolf_hp_raw)
	state = WolfState.IDLE
	_state_end_tick = -1
	_damage_tick = -1
	_pending_damage = 0
	_pending_crit = false
	_acquired = false
	_last_dist_sq = 0
	_attack_entry_ticks.clear()
	facing_hint = MeleeResolver.DIR_DOWN
	_knockback_step = Vector2i.ZERO
	_knockback_end_tick = -1
	_walk_counter = 0
	visible = true
	_sync_render()
	_sync_sprite()


## P-015: UNIFORM 16x32 across all four directions — both recovered wolf tables
## (0x086B1DE8, 0x086B1FE0) carry identical entries for every direction, so unlike
## the player this body does NOT consult `facing_hint`.
func body_size_px() -> Vector2i:
	return Vector2i(config.wolf_body_w_px, config.wolf_body_h_px)


func body_rect() -> BodyRect:
	return BodyRect.from_raw(pos_raw, body_size_px())


func is_hittable() -> bool:
	return state != WolfState.DEAD


func is_acquired() -> bool:
	return _acquired


func dist_sq() -> int:
	return _last_dist_sq


func damage_tick() -> int:
	return _damage_tick


## Ticks left in a timed state, or -1 when the state is untimed.
func ticks_remaining(t: int) -> int:
	if _state_end_tick < 0:
		return -1
	return _state_end_tick - t


func _sync_render() -> void:
	position = FixedPoint.raw_to_render_px(pos_raw)
