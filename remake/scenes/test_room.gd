extends Node2D
## Wires the slice together and owns the ONE CombatConfig instance.
##
## CombatConfig is a Resource, not an autoload: it is loaded here once and
## INJECTED into Player, Wolf, Party and the overlay, so a test can construct its
## own instance with a tweaked TEMP value without mutating global state.
##
## TICK ORDER IS A DESIGN DECISION, not an accident. Clock.tick fires listeners in
## connection order, and children are readied depth-first in tree order, so the
## scene tree lists Player before Wolf before Gizmos before the overlay. Within a
## tick that gives: player input and movement resolve, then player melee contact
## resolves, then wolf AI reacts to the POST-MOVE world, then presentation reads a
## settled state. The overlay reads only; it never mutates.
##
## A wolf spawned at RUNTIME connects to Clock.tick last, which would put it AFTER
## presentation. `spawn_wolf` therefore re-seats the presentation listeners at the
## back of the connection list (disconnect + reconnect), restoring the property.
##
## CAVEAT, recorded rather than hidden: Godot does not DOCUMENT that emit invokes
## connections in connection order - the docs guarantee only that emission is
## synchronous. The ordering is verified empirically on 4.7-beta5 (connect A,B
## fires A,B; a late C fires A,B,C; disconnecting and reconnecting B fires A,C,B)
## and is relied on by the authored scene order too, but it is an OBSERVED engine
## behaviour, not a contracted one. If a future engine build reorders listeners,
## the symptom is the overlay reading a one-tick-stale wolf - presentation only,
## since both re-seated listeners are read-only.

const CONFIG_PATH: String = "res://config/combat_config.tres"
## Fixed seed: the slice is reproducible run to run.
const RNG_SEED: int = 20260829

const WOLF_SCENE: String = "res://actors/wolf.tscn"
## F8 places each extra wolf one step further along a fixed diagonal. Deterministic
## by construction - no RNG in placement - and large enough that two 16x32 bodies
## never overlap.
const SPAWN_OFFSET_PX: Vector2i = Vector2i(40, -28)

@onready var player: Player = $Player
@onready var gizmos: Node2D = $Gizmos
@onready var overlay: MarginContainer = $CanvasLayer/DebugOverlay

## Every wolf in the room, authored one first. Freed entries are pruned by
## `_prune`, so nothing here is ever a dangling reference.
var wolves: Array[Wolf] = []

var config: CombatConfig = null
var rng: DeterministicRng = null
## Where the next F8 wolf goes: bumped one SPAWN_OFFSET_PX per spawn.
var _spawn_index: int = 0


## Injection happens in _enter_tree, BEFORE any child _ready runs, because Player
## and Wolf both read `config` in their own _ready.
func _enter_tree() -> void:
	config = load(CONFIG_PATH) as CombatConfig
	assert(config != null, "combat_config.tres failed to load")
	rng = DeterministicRng.new(RNG_SEED)

	Party.config = config
	_ensure_input_actions()

	var p: Player = $Player
	var w: Wolf = $Wolf
	p.config = config
	p.rng = rng
	w.config = config
	w.rng = rng
	($CanvasLayer/DebugOverlay as Node).set("config", config)


func _ready() -> void:
	wolves = [$Wolf as Wolf]
	($Wolf as Wolf).target = player
	overlay.player = player
	overlay.room = self
	overlay.gizmos = gizmos
	_refresh_targets()
	gizmos.draw.connect(_draw_gizmos)
	# Gizmos is a bare Node2D used as a visibility switch and a draw surface; it
	# needs no script of its own, so TestRoom draws into it. Redrawn on the clock
	# because the simulation only moves on a tick.
	Clock.tick.connect(_redraw_gizmos)

	# The second character exists so the P-010 recipient asymmetry is observable:
	# F3 switches active_index, including inside the one-tick payout gap.
	print("[TestRoom] ready seed=%d config=%s characters=%d" % [
		RNG_SEED, CONFIG_PATH, Party.characters.size(),
	])
	print("[TestRoom] controls: WASD/arrows move, J or Space attack, F1..F8 debug")


# --- wolves ------------------------------------------------------------------

## Drops freed and dead-and-hidden wolves, then re-points `player.targets` at
## what is left. Called after every spawn, respawn and draw.
func _prune() -> void:
	var live: Array[Wolf] = []
	for w: Wolf in wolves:
		if is_instance_valid(w):
			live.append(w)
	wolves = live


func _refresh_targets() -> void:
	_prune()
	player.targets = wolves.duplicate()


func live_wolf_count() -> int:
	_prune()
	var n: int = 0
	for w: Wolf in wolves:
		if w.is_hittable():
			n += 1
	return n


## F8. A wolf instanced from the same scene the room authors, sharing the ONE
## seeded rng, placed on a fixed diagonal from the authored wolf's start.
func spawn_wolf() -> Wolf:
	_spawn_index += 1
	var w: Wolf = (load(WOLF_SCENE) as PackedScene).instantiate() as Wolf
	w.config = config
	w.rng = rng
	w.start_px = ($Wolf as Wolf).start_px + SPAWN_OFFSET_PX * _spawn_index
	w.target = player
	add_child(w)
	wolves.append(w)
	# The new wolf connected to Clock.tick in its _ready, i.e. AFTER the overlay
	# and the gizmo redraw. Re-seating both presentation listeners at the back of
	# the connection list puts the wolf ahead of them again, preserving the header's
	# ordering property. Simulation listeners are never re-seated.
	overlay.reseat_tick_listener()
	Clock.tick.disconnect(_redraw_gizmos)
	Clock.tick.connect(_redraw_gizmos)
	_refresh_targets()
	return w


## F7. Every wolf back to full HP at its own start position, in its initial state.
## Alive wolves are reset too - the point is a repeatable observation, not a revive.
func respawn_all() -> void:
	_prune()
	for w: Wolf in wolves:
		w.reset_to_start()
	_refresh_targets()


## F2 gizmos: both body rects plus the MELEE-EXPANDED target rect, in outline.
## Colours are distinguished by brightness and by an explicit legend order, never
## by red-vs-green.
func _draw_gizmos() -> void:
	_prune()
	_outline(player.body_rect(), Color(0.95, 0.95, 0.95), 1.0)
	for w: Wolf in wolves:
		_outline(w.body_rect(), Color(0.55, 0.60, 0.70), 1.0)
		_outline(MeleeResolver.expanded(w.body_rect(), config), Color(0.72, 0.53, 0.17), 1.0)


## A named method rather than the former inline lambda, so `spawn_wolf` can
## disconnect and reconnect it to move it back behind the new wolf.
func _redraw_gizmos(_t: int) -> void:
	gizmos.queue_redraw()


func _outline(r: BodyRect, col: Color, w: float) -> void:
	gizmos.draw_rect(
		Rect2(Vector2(r.x0, r.y0), Vector2(r.x1 - r.x0, r.y1 - r.y0)), col, false, w
	)


## The project ships no InputMap entries, so they are created here rather than in
## project.godot - keeping the slice's key bindings next to the code that reads
## them, and making a headless test that never touches input still parse.
func _ensure_input_actions() -> void:
	_bind(&"move_up", [KEY_W, KEY_UP])
	_bind(&"move_down", [KEY_S, KEY_DOWN])
	_bind(&"move_left", [KEY_A, KEY_LEFT])
	_bind(&"move_right", [KEY_D, KEY_RIGHT])
	_bind(&"attack", [KEY_J, KEY_SPACE])


func _bind(action: StringName, keys: Array) -> void:
	if not InputMap.has_action(action):
		InputMap.add_action(action)
	for k: Key in keys:
		var ev: InputEventKey = InputEventKey.new()
		ev.physical_keycode = k
		InputMap.action_add_event(action, ev)
