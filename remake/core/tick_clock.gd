extends Node
## Autoload "Clock". The single gameplay clock. 60 Hz integer ticks.
##
## Provenance: GBA hardware is ~59.7275 Hz; 60 is the deliberate approximation
## (VCOUNT rollovers measured 59.727/s armed, PROJECT_<local-state-name> ROM-011).
##
## This is the ONE gameplay constant that does not live in CombatConfig, because
## the clock owns it. Everything else belongs in config/combat_config.gd.
##
## Rendering runs at whatever _process rate the machine gives; the slice does not
## interpolate at all — placeholder rects snap to the integer position each tick,
## which is exactly what the GBA did.

const TICKS_PER_SECOND: int = 60

signal tick(t: int)

var current_tick: int = 0
var paused: bool = false

## Once-per-second heartbeat so a stalled or double-stepping clock is visible in
## the log. Never per-tick — that would be 60 lines a second of noise.
var verbose: bool = false

var _listener_count: int = 0


func _ready() -> void:
	Engine.physics_ticks_per_second = TICKS_PER_SECOND
	Engine.max_physics_steps_per_frame = 8
	print("[Clock] ready hz=%d" % TICKS_PER_SECOND)


## The only _physics_process in the simulation. `_delta` is named `_delta` and is
## never read: no float ever enters simulation code.
func _physics_process(_delta: float) -> void:
	if paused:
		return
	_advance()


## Manual advance. Used when paused (debug single-step, F5) and from a headless
## SceneTree in tests.
func step(n: int = 1) -> void:
	for _i: int in n:
		_advance()


func _advance() -> void:
	current_tick += 1
	tick.emit(current_tick)
	if verbose and current_tick % TICKS_PER_SECOND == 0:
		_listener_count = tick.get_connections().size()
		print("[Clock] t=%d second=%d listeners=%d paused=%s" % [
			current_tick, current_tick / TICKS_PER_SECOND, _listener_count, paused,
		])
