class_name Player
extends TickNode
## The player. Integers only: `pos_raw` (8.8 fixed point, matching player+0x1A0 /
## +0x1A4) is authoritative and `position` is assigned once per tick for
## RENDERING ONLY.
##
## No velocity, no acceleration, no lerp, no move_and_slide, no CharacterBody2D.
##
## Diagnostics: EventLog carries the per-event trace (INPUT / MOVE /
## ATTACK_ACCEPTED / ATTACK_REJECTED / CONTACT). This script adds one throttled
## once-per-second aggregate so a stuck input ring or a broken acceptance gate is
## visible in plain stdout without reading the trace.

## Injected by scenes/test_room.gd. CombatConfig is a Resource, not an autoload.
@export var config: CombatConfig
## Starting position in pixels; converted to raw once, in _ready.
@export var start_px: Vector2i = Vector2i(360, 300)

## Injected by scenes/test_room.gd. Never the global generator.
var rng: DeterministicRng = null
## Targets the melee resolver tests. Injected by test_room.gd.
var targets: Array[Wolf] = []

var pos_raw: Vector2i = Vector2i.ZERO
## 0..3 through the P-003 direction encoding. TEMP semantics - facing was never
## sampled (P-002 records it explicitly UNKNOWN) and it does NOT feed the reach
## test.
var facing: int = MeleeResolver.DIR_DOWN

## Ring of the last N desired directions. Latency is expressed in TICKS and so
## cannot drift with framerate.
var _input_history: Array[Vector2i] = []
## -1 when not attacking. Presentation only: the swing already resolved.
var _attack_end_tick: int = -1
## Tick of the last ACCEPTED attack. Far negative so the first press is accepted.
var _last_accept_tick: int = -9999
## 0..2, valid only during an attack.
var _attack_variant: int = -1
var _clamped_last_tick: bool = false
## Presentation only: did the APPLIED direction move the player this tick?
var _moved_last_tick: bool = false
## Presentation only: consecutive moving ticks, for the walk-frame phase.
var _walk_counter: int = 0
## Presentation only: did the CURRENT swing connect? Latched on the accepted-attack
## tick, cleared when the swing is armed. Never read by the simulation.
var _attack_hit: bool = false

# Once-per-second aggregate counters.
var _acc_accepted: int = 0
var _acc_rejected: int = 0
var _acc_contacts: int = 0
var _acc_moved_ticks: int = 0


func _ready() -> void:
	super()
	pos_raw = FixedPoint.px_to_raw_v(start_px)
	# Pre-fill the ring with neutral input so the FIRST tick already carries the
	# full delay. Without this the first press would apply immediately and only
	# later presses would be delayed - a latency that drifts with uptime.
	_input_history.clear()
	for _i: int in config.input_delay_ticks:
		_input_history.push_back(Vector2i.ZERO)
	_sync_render()
	print("[Player] ready start_px=%s body=%s input_delay=%d" % [
		start_px, body_size_px(), config.input_delay_ticks,
	])


func _on_tick(t: int) -> void:
	var desired: Vector2i = _read_input_dir()
	var attack_pressed: bool = _pressed_now(&"attack")
	# INPUT is a section-27 kind, but a neutral stick every tick is 60 empty
	# records a second that push real events out of the ring buffer. Only actual
	# input is recorded.
	if desired != Vector2i.ZERO or attack_pressed:
		EventLog.emit_input(t, desired, attack_pressed)

	_apply_movement(t, desired)
	_try_attack(t, attack_pressed)

	if _attack_end_tick >= 0 and t >= _attack_end_tick:
		_attack_end_tick = -1
		_attack_variant = -1
		_attack_hit = false

	_sync_render()
	_sync_sprite(_moved_last_tick)
	# Placeholder art is drawn from simulation state, so it advances on the tick
	# like everything else. No _process, no delta, no Timer.
	queue_redraw()
	_log_aggregate(t)


## Optional runtime sprite. Absent art leaves the ColorRect placeholder visible
## and this is a no-op. Driven from the gameplay tick, never from _process.
func _sync_sprite(moving: bool) -> void:
	var sprite: Sprite2D = get_node_or_null(^"Sprite") as Sprite2D
	if sprite == null:
		return
	_walk_counter = (_walk_counter + 1) if moving else 0
	var tex: Texture2D = SpriteSet.frame(
		"player", facing, moving, is_attacking(), SpriteSet.step_phase(_walk_counter)
	)
	sprite.texture = tex
	sprite.visible = tex != null
	sprite.position = SpriteSet.sprite_offset(tex, body_size_px())
	var body: ColorRect = get_node_or_null(^"Body") as ColorRect
	if body != null:
		body.visible = tex == null


## Raw desired direction in {-1,0,1}^2. Diagonals are NOT normalized here or
## anywhere - see _apply_movement.
func _read_input_dir() -> Vector2i:
	var d: Vector2i = Vector2i.ZERO
	if _held(&"move_right"):
		d.x += 1
	if _held(&"move_left"):
		d.x -= 1
	if _held(&"move_down"):
		d.y += 1
	if _held(&"move_up"):
		d.y -= 1
	return d


## The InputMap is registered by scenes/test_room.gd. A harness that instantiates
## Player on its own has no actions bound, and an unguarded read would spew one
## engine error PER TICK PER ACTION. Reading "not bound" as "not pressed" is the
## correct headless behaviour.
func _held(action: StringName) -> bool:
	return InputMap.has_action(action) and Input.is_action_pressed(action)


func _pressed_now(action: StringName) -> bool:
	return InputMap.has_action(action) and Input.is_action_just_pressed(action)


func _apply_movement(t: int, desired: Vector2i) -> void:
	# The applied direction is the one that entered the ring `input_delay_ticks`
	# ticks ago. The ring is pre-filled in _ready, so its length is invariant and
	# the delay is exact from tick 1. P-002 observed 2-3 ticks; the CONFIRMED
	# block carries the low bound.
	_input_history.push_back(desired)
	var applied: Vector2i = _input_history.pop_front()

	# UNNORMALIZED: on a diagonal BOTH axes move the full 352 raw simultaneously.
	# P-002: the diagonal resultant is ~498 raw (~1.945 px/tick) = sqrt(2)x the
	# cardinal rate. Do NOT normalize.
	# P-002: acceleration is IMMEDIATE, no ramp. Do not add one.
	var before: Vector2i = pos_raw
	pos_raw.x += applied.x * config.move_raw_per_tick
	pos_raw.y += applied.y * config.move_raw_per_tick

	_clamped_last_tick = false
	_moved_last_tick = applied != Vector2i.ZERO
	if config.temp_wall_clamp_enabled:
		# TEMP: collision was never observed (P-002 explicitly UNKNOWN). Room
		# bounds only, and the overlay marks the clamp TEMP whenever it fires.
		var b: Rect2i = config.temp_room_bounds_px
		var lo: Vector2i = FixedPoint.px_to_raw_v(b.position)
		# The WIDEST body, deliberately fixed rather than the current directional
		# one: a clamp bound that shrank in profile would let the player walk flush
		# to the right wall facing LEFT and then jut 8 px out of bounds the instant
		# they turned. Clamping to 16 always is the conservative bound - never out
		# of the room in any facing, and never a bound that moves under the player.
		var body: Vector2i = Vector2i(config.player_body_w_facing_px, config.player_body_h_px)
		var hi: Vector2i = FixedPoint.px_to_raw_v(b.position + b.size - body)
		var clamped: Vector2i = Vector2i(
			clampi(pos_raw.x, lo.x, hi.x), clampi(pos_raw.y, lo.y, hi.y)
		)
		if clamped != pos_raw:
			_clamped_last_tick = true
			pos_raw = clamped

	if applied != Vector2i.ZERO:
		_acc_moved_ticks += 1
		_update_facing(applied)
		EventLog.emit_move(t, pos_raw, pos_raw - before)


## TEMP (temp_player_facing_mode = LAST_INPUT): the last nonzero desired
## direction, mapped through the P-003 direction encoding purely so placeholder
## art points somewhere. Facing does NOT feed the melee contact test.
func _update_facing(d: Vector2i) -> void:
	# The P-003 formula this encoding comes from resolves a VICTIM's direction:
	# there `dy = playerCy - targetCy` points from the target BACK toward the
	# attacker, so `dy < 1` means the attacker is above and the victim faces UP.
	# Self-movement is the opposite sense. In Godot +Y is DOWN, so holding Down
	# gives `d.y = +1` and must select DIR_DOWN. Applying the victim formula
	# verbatim here inverted the vertical axis: walking down faced the player up.
	# Horizontal needs no flip because +X is right in both conventions.
	if absi(d.y) < absi(d.x):
		facing = MeleeResolver.DIR_LEFT if d.x < 1 else MeleeResolver.DIR_RIGHT
	else:
		facing = MeleeResolver.DIR_UP if d.y < 1 else MeleeResolver.DIR_DOWN


## Acceptance is decided on the tick the button is pressed and is entirely
## separate from raw button state: holding and mashing produce identical accepted
## rates because the gate is on ACCEPTANCE, not on edges.
##
## 20 is not 16. The animation ends at t+16; the next attack may be accepted at
## _last_accept_tick + 20 (P-006C).
func _try_attack(t: int, attack_pressed: bool) -> void:
	if not attack_pressed:
		return
	var since: int = t - _last_accept_tick
	if since < config.attack_accept_interval_ticks:
		_acc_rejected += 1
		EventLog.emit_attack_rejected(t, config.attack_accept_interval_ticks - since)
		return

	_last_accept_tick = t
	# P-008: uniform over the three presentation variants. Clips 0x0851C680 /
	# 0x0851C6C0 / 0x0851C6A0 are VARIANTS, not combo steps - no combo counter, no
	# avoid-repeat filter, no progression between attacks.
	_attack_variant = rng.melee_variant(config.melee_variant_count)
	_attack_end_tick = t + config.melee_duration_ticks
	_attack_hit = false
	_acc_accepted += 1
	EventLog.emit_attack_accepted(t, _attack_variant)

	# ONE ACCEPTED SWING PRODUCES AT MOST ONE HIT. The reach test is evaluated
	# HERE, once, on the accepted-attack tick - never per-tick across the 16-tick
	# clip. Resolved by firsthand user evidence (the maintainer, 2026-08-29: "one swing =
	# one hit"), consistent with the confirmed four-hits-to-kill wolf.
	_resolve_contact(t)


func _resolve_contact(t: int) -> void:
	var mine: BodyRect = body_rect()
	for w: Wolf in targets:
		if w == null or not w.is_hittable():
			continue
		var theirs: BodyRect = w.body_rect()
		if not MeleeResolver.in_reach(mine, theirs, config):
			continue
		# Direction resolution runs only AFTER the reach test passes.
		var dir: int = MeleeResolver.hit_direction(mine, theirs)
		_attack_hit = true
		_acc_contacts += 1
		# CONTACT: damage is ROLLED here but NOT applied. The wolf schedules the
		# reaction entry and the +3 application itself - three distinct moments.
		EventLog.emit_contact(t, _attack_variant, BodyRect.center_dist_sq(mine, theirs))
		w.on_contact(t, dir)
		# At most one hit per accepted swing: the first target in reach consumes
		# the swing.
		return


## P-015: the player body is DIRECTION-DEPENDENT in width. The recovered table
## 0x086AD30C gives (0,-20)..(16,6) for dirs 0/1 and (5,-20)..(13,6) for dirs 2/3,
## i.e. 16 wide facing UP/DOWN and 8 wide in profile facing LEFT/RIGHT. Height is
## 26 in every direction. This is the one place `facing` reaches the SIMULATION —
## it still does not feed the reach test, which is direction-independent (P-003);
## it only sizes the body the reach test is run against.
func body_size_px() -> Vector2i:
	var w: int = config.player_body_w_facing_px
	if facing == MeleeResolver.DIR_LEFT or facing == MeleeResolver.DIR_RIGHT:
		w = config.player_body_w_profile_px
	return Vector2i(w, config.player_body_h_px)


func body_rect() -> BodyRect:
	return BodyRect.from_raw(pos_raw, body_size_px())


## True while the 16-tick presentation clip is playing. Presentation only.
func is_attacking() -> bool:
	return _attack_end_tick >= 0


func attack_variant() -> int:
	return _attack_variant


## Presentation only. True while the current swing is one that connected.
func attack_connected() -> bool:
	return _attack_hit


func ticks_since_accept(t: int) -> int:
	return t - _last_accept_tick


func gate_open(t: int) -> bool:
	return ticks_since_accept(t) >= config.attack_accept_interval_ticks


func was_clamped() -> bool:
	return _clamped_last_tick


## Rendering only. `pos_raw` stays authoritative; nothing reads this back.
func _sync_render() -> void:
	position = FixedPoint.raw_to_render_px(pos_raw)


## Once per second, never per tick. A stuck input ring, a jammed acceptance gate,
## or swings that never connect all show up here without reading the trace.
func _log_aggregate(t: int) -> void:
	if t % Clock.TICKS_PER_SECOND != 0:
		return
	print("[Player] t=%d pos_raw=%s px=%s moved_ticks=%d accepted=%d rejected=%d contacts=%d clamped=%s" % [
		t, pos_raw, FixedPoint.raw_to_px_v(pos_raw), _acc_moved_ticks,
		_acc_accepted, _acc_rejected, _acc_contacts, _clamped_last_tick,
	])
	_acc_moved_ticks = 0
	_acc_accepted = 0
	_acc_rejected = 0
	_acc_contacts = 0


# ---------------------------------------------------------------------------
# Placeholder art. Drawing only: _draw runs on the render thread's schedule but
# reads nothing it does not own and writes no simulation state. queue_redraw is
# called from _on_tick, so every visual change lands on a gameplay tick.
#
# Colourblind-safe by construction: every distinction is carried by BRIGHTNESS
# and by SHAPE. No red-vs-green anywhere. The three swing variants differ in
# glyph (bar / fork / wedge), in reach, and in brightness, so they stay
# separable in greyscale.
# ---------------------------------------------------------------------------

## Unit vector for each P-003 direction, in screen space (y grows downward).
const _DIR_VEC: Array[Vector2] = [
	Vector2(0, -1),  # DIR_UP
	Vector2(0, 1),  # DIR_DOWN
	Vector2(-1, 0),  # DIR_LEFT
	Vector2(1, 0),  # DIR_RIGHT
]

## Per-variant reach in px, half-width in px, and base brightness.
const _VARIANT_REACH: Array[float] = [14.0, 9.0, 22.0]
const _VARIANT_HALF: Array[float] = [9.0, 13.0, 4.0]
const _VARIANT_TONE: Array[float] = [0.62, 0.80, 0.98]


## Set true to force the facing wedge and swing glyphs back on even while real
## sprites are showing, for checking the exact facing and reach the SIMULATION
## believes in when the art and the hitbox disagree. Toggled by F6.
var debug_visuals_forced: bool = false


## True when a real sprite frame is on screen for this actor. Read from the
## Sprite2D itself rather than from a config flag, so it cannot drift out of
## sync with what is actually rendered.
func sprite_is_showing() -> bool:
	var sprite: Sprite2D = get_node_or_null(^"Sprite") as Sprite2D
	return sprite != null and sprite.visible and sprite.texture != null


func _draw() -> void:
	# The sprites carry facing and the punch animation natively, so the debug
	# wedge and glyphs are redundant clutter on top of them. They are SUPPRESSED
	# rather than deleted: sprite PNGs are git-ignored, so a fresh clone has no
	# art at all and these are the only thing making facing and attacks legible.
	if sprite_is_showing() and not debug_visuals_forced:
		return
	# The LIVE directional size, so the wedge sits on the edge of the box the
	# simulation is actually testing - the debug draw exists precisely to show
	# what the sim believes, including the P-015 narrowing in profile.
	var half: Vector2 = Vector2(body_size_px()) * 0.5
	var fwd: Vector2 = _DIR_VEC[facing]
	var side: Vector2 = Vector2(-fwd.y, fwd.x)
	# The body is a ColorRect anchored at the node origin, so its centre is +half.
	_draw_facing(half, fwd, side)
	if is_attacking():
		_draw_swing(half, fwd, side)


## Always visible. A bright wedge sitting on the faced edge of the body plus a
## short stem back to the centre: the wedge alone reads as direction even at a
## glance, and the stem disambiguates it from the body outline.
func _draw_facing(half: Vector2, fwd: Vector2, side: Vector2) -> void:
	# Sit the wedge just outside the body edge along the faced axis, so it reads
	# against the rect rather than swamping it.
	var edge: float = absf(fwd.x) * half.x + absf(fwd.y) * half.y
	var base: Vector2 = half + fwd * (edge + 1.0)
	var tip: Vector2 = half + fwd * (edge + 7.0)
	var col: Color = Color(1.0, 0.98, 0.90)
	draw_line(half, base, col, 2.0)
	draw_colored_polygon(
		PackedVector2Array([tip, base + side * 4.0, base - side * 4.0]),
		col
	)


## Only while the 16-tick clip runs. The swing sweeps OUT over the first half of
## the clip and holds, so a start and an end are both obvious; `_attack_end_tick`
## is the sim's own deadline, so the animation cannot drift from the simulation.
func _draw_swing(half: Vector2, fwd: Vector2, side: Vector2) -> void:
	var v: int = clampi(_attack_variant, 0, 2)
	var remaining: int = maxi(_attack_end_tick - Clock.current_tick, 0)
	var elapsed: int = config.melee_duration_ticks - remaining
	# Integer-fraction extension over the first third of the clip, then held.
	var grow: int = mini(elapsed * 3, config.melee_duration_ticks)
	var reach: float = _VARIANT_REACH[v] * float(grow) / float(config.melee_duration_ticks)
	var hw: float = _VARIANT_HALF[v]

	var tone: float = _VARIANT_TONE[v]
	var width: float = 3.0
	if _attack_hit:
		tone = 1.0
		width = 6.0
	var col: Color = Color(tone, tone * 0.96, tone * 0.86)

	var edge: float = absf(fwd.x) * half.x + absf(fwd.y) * half.y
	var origin: Vector2 = half + fwd * edge
	var far: Vector2 = origin + fwd * (reach + 6.0)

	# Variant glyph: 0 = single bar, 1 = two-pronged fork, 2 = long thin spike.
	match v:
		0:
			draw_line(far - side * hw, far + side * hw, col, width)
			draw_line(origin, far, col, width)
		1:
			# Two splayed prongs off a short stub. Widest and dimmest of the three.
			var mid: Vector2 = origin + fwd * (reach * 0.4 + 3.0)
			draw_line(origin, mid, col, width)
			draw_line(mid, far + side * hw, col, width)
			draw_line(mid, far - side * hw, col, width)
		_:
			draw_line(origin, far, col, width)
			draw_line(far - fwd * 8.0 - side * hw, far, col, width * 0.6)
			draw_line(far - fwd * 8.0 + side * hw, far, col, width * 0.6)

	if _attack_hit:
		# Contact reads on three channels at once: a FILLED burst (whiffs draw no
		# fill at all), maximum brightness, and four spokes radiating outward.
		var burst: PackedVector2Array = PackedVector2Array()
		for i: int in 8:
			var a: float = TAU * float(i) / 8.0
			var r: float = 7.0 if i % 2 == 0 else 3.0
			burst.push_back(far + Vector2(cos(a), sin(a)) * r)
		draw_colored_polygon(burst, Color(1.0, 1.0, 0.95))
		for i: int in 4:
			var a2: float = TAU * float(i) / 4.0 + PI * 0.25
			draw_line(far, far + Vector2(cos(a2), sin(a2)) * 12.0, Color(1.0, 1.0, 0.95), 2.0)
