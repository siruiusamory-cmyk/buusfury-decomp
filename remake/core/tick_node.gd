class_name TickNode
extends Node2D
## Base for every simulation node. Subclasses override `_on_tick(t: int)` and
## MUST NOT define `_process` or `_physics_process`.
##
## Four reinforcing layers make delta-time misuse structurally hard rather than
## merely discouraged:
##
##   1. set_process(false) / set_physics_process(false) here in _ready() — even a
##      subclass that declares _process does not run it unless it deliberately
##      re-enables the callback.
##   2. The debug-build assertion below fails loudly at scene entry if a subclass
##      declares either callback.
##   3. _on_tick receives an INT. No float enters simulation code, so there is no
##      `delta` in scope to accidentally multiply by.
##   4. Every duration in CombatConfig is typed `int` and named `*_ticks`; a
##      duration compared against a float is a type error under static typing.
##
## All simulation code is written as "at tick T, do X" with integer deadline
## comparisons (`if Clock.current_tick >= _state_end_tick`), never as
## "accumulate time until".

const _FORBIDDEN_CALLBACKS: PackedStringArray = ["_process", "_physics_process"]


func _ready() -> void:
	Clock.tick.connect(_on_tick)
	set_process(false)
	set_physics_process(false)
	if OS.is_debug_build():
		_assert_no_frame_callbacks()


## Override this. `t` is the absolute gameplay tick.
func _on_tick(_t: int) -> void:
	pass


## `has_method("_process")` is useless for this check — it is true for every Node,
## because the callback is declared on Node itself. The script's own method list
## reports only what the script chain DECLARES, which is the thing we forbid.
func _assert_no_frame_callbacks() -> void:
	var s: Script = get_script()
	if s == null:
		return
	for m: Dictionary in s.get_script_method_list():
		var n: String = m["name"]
		if _FORBIDDEN_CALLBACKS.has(n):
			var msg: String = "%s defines %s; simulation must be tick-driven" % [name, n]
			push_error("[TickNode] " + msg)
			assert(false, msg)
