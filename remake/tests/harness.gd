class_name TestHarness
extends RefCounted
## Minimal assertion harness for the VS-001 suite. No GUT, no gdUnit4 — fifteen
## rules do not justify an addon.
##
## Each suite is a RefCounted exposing `run(h: TestHarness) -> void`. The harness
## tallies pass/fail; run_tests.gd turns the fail count into the process exit code.

var passed: int = 0
var failed: int = 0
var failures: Array[String] = []

var _suite: String = ""
var _suite_passed: int = 0
var _suite_failed: int = 0


func begin_suite(suite_name: String) -> void:
	_suite = suite_name
	_suite_passed = 0
	_suite_failed = 0
	print("\n--- %s" % suite_name)


func end_suite() -> void:
	print("--- %s: %d passed, %d failed" % [_suite, _suite_passed, _suite_failed])


func ok(label: String) -> void:
	passed += 1
	_suite_passed += 1
	print("  PASS  %s" % label)


func fail(label: String, detail: String) -> void:
	failed += 1
	_suite_failed += 1
	failures.append("%s / %s: %s" % [_suite, label, detail])
	print("  FAIL  %s  %s" % [label, detail])


func assert_eq(actual: Variant, expected: Variant, label: String) -> bool:
	if actual == expected:
		ok("%s == %s" % [label, expected])
		return true
	fail(label, "expected %s, got %s" % [expected, actual])
	return false


func assert_ne(actual: Variant, unexpected: Variant, label: String) -> bool:
	if actual != unexpected:
		ok("%s: %s != %s" % [label, actual, unexpected])
		return true
	fail(label, "expected anything but %s" % unexpected)
	return false


func assert_true(cond: bool, label: String) -> bool:
	if cond:
		ok(label)
		return true
	fail(label, "expected true, got false")
	return false


func assert_false(cond: bool, label: String) -> bool:
	if not cond:
		ok(label)
		return true
	fail(label, "expected false, got true")
	return false


## Inclusive bounds.
func assert_range(actual: int, lo: int, hi: int, label: String) -> bool:
	if actual >= lo and actual <= hi:
		ok("%s: %d in [%d,%d]" % [label, actual, lo, hi])
		return true
	fail(label, "expected %d in [%d,%d]" % [actual, lo, hi])
	return false


func summary() -> String:
	return "TOTAL: %d passed, %d failed" % [passed, failed]


# --- fixtures ----------------------------------------------------------------
# Shared spawn helpers. They live here rather than in a tenth file because every
# suite needs the same three lines and nothing else.

const CONFIG_PATH: String = "res://config/combat_config.tres"

## Scene-tree parent for spawned actors. Set once by run_tests.gd. Actors MUST be
## in the tree: TickNode._ready is what connects them to Clock.tick.
var root: Node = null


## A fresh CombatConfig per test, so a suite that tweaks a TEMP field cannot leak
## into the next one. `duplicate()` of the loaded Resource keeps every CONFIRMED
## value exactly as the .tres records it.
static func make_config() -> CombatConfig:
	var res: CombatConfig = load(CONFIG_PATH) as CombatConfig
	assert(res != null, "combat_config.tres failed to load")
	return res.duplicate() as CombatConfig


func spawn_player(c: CombatConfig, rng: DeterministicRng, start_px: Vector2i) -> Player:
	var p: Player = Player.new()
	p.config = c
	p.rng = rng
	p.start_px = start_px
	root.add_child(p)
	return p


func spawn_wolf(c: CombatConfig, rng: DeterministicRng, start_px: Vector2i) -> Wolf:
	var w: Wolf = Wolf.new()
	w.config = c
	w.rng = rng
	w.start_px = start_px
	root.add_child(w)
	return w


## Remove and free spawned actors so their Clock.tick connections die with them
## and cannot bleed into the next test.
func despawn(nodes: Array[Node]) -> void:
	for n: Node in nodes:
		if n == null:
			continue
		root.remove_child(n)
		n.free()
