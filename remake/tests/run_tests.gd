extends Node
## VS-001 permanent headless test suite — entry point.
##
##   Godot_v4.7-beta5_win64_console.exe --headless --path remake res://tests/run_tests.tscn
##
## DEVIATION from the design (solution.md §11, which specifies a SceneTree script
## launched with `--script`): autoload globals are NOT bound under `--script`, so
## player.gd / wolf.gd fail to compile on `Identifier not found: EventLog`. The
## runner is therefore a SCENE, which is the only way to get Clock, EventLog and
## Party bound. Nothing else about the plan changed.
##
## Exit code is the failure count, capped at 125 — zero only when everything
## passes.

const SUITES: Array[Dictionary] = [
	{"name": "movement", "path": "res://tests/test_movement.gd"},
	{"name": "melee", "path": "res://tests/test_melee.gd"},
	{"name": "contact", "path": "res://tests/test_contact.gd"},
	{"name": "wolf_ai", "path": "res://tests/test_wolf_ai.gd"},
	{"name": "damage", "path": "res://tests/test_damage.gd"},
	{"name": "progression", "path": "res://tests/test_progression.gd"},
	{"name": "multi_wolf", "path": "res://tests/test_multi_wolf.gd"},
	{"name": "sprite_set", "path": "res://tests/test_sprite_set.gd"},
]


func _ready() -> void:
	# Determinism: the clock advances ONLY when a test says so. Nothing here waits
	# on a frame, a timer or wall-clock time.
	Clock.paused = true
	Clock.verbose = false
	# The suites assert against the TRACE, so records must be kept; echoing all of
	# them to stdout would bury the pass/fail lines.
	EventLog.echo = false
	EventLog.verbose = false
	# Per-event prints from the simulation classes: same reasoning.
	Combatant.log_lethal = false
	Damage.log_crit = false
	Reward.log_create = false
	MeleeResolver.trace_reach = false

	var h := TestHarness.new()
	h.root = self

	print("=== VS-001 test suite ===")
	for entry: Dictionary in SUITES:
		var script: GDScript = load(entry["path"]) as GDScript
		if script == null:
			h.begin_suite(entry["name"])
			h.fail("load", "could not load %s" % entry["path"])
			h.end_suite()
			continue
		var suite: RefCounted = script.new()
		suite.run(h)

	print("\n=== %s" % h.summary())
	if h.failed > 0:
		print("FAILURES:")
		for f: String in h.failures:
			print("  - %s" % f)
	print("RESULT: %s" % ("PASS" if h.failed == 0 else "FAIL"))

	get_tree().quit(mini(h.failed, 125))
