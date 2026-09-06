class_name DeterministicRng
extends RefCounted
## Seeded RNG, INJECTED and never global. Player, Wolf, Damage and the drop roll
## each take an instance; test_room.gd creates one seeded instance and passes it
## in. Nothing in this project calls the global randi()/randf().
##
## Exactly five named call sites, so every roll is nameable in a trace.

var _rng: RandomNumberGenerator = RandomNumberGenerator.new()
var _seed: int = 0
var _calls: int = 0


func _init(p_seed: int = 0) -> void:
	_seed = p_seed
	_rng.seed = p_seed


func seed_value() -> int:
	return _seed


## Number of rolls drawn so far. A divergence in this count between two runs of
## the same seed is the first symptom of a determinism break.
func call_count() -> int:
	return _calls


func reset() -> void:
	_rng.seed = _seed
	_calls = 0


## P-008: uniform over the `n` presentation variants. No combo counter, no
## avoid-repeat filter, no progression — immediate repeats are correct.
func melee_variant(n: int) -> int:
	return next_int(0, n - 1)


## Critical decision. `permille` is TEMP (temp_crit_chance_permille): the rate was
## never established, only a raw count of 2 crits in 59 hits (P-009).
func crit_roll(permille: int) -> bool:
	return next_int(1, 1000) <= permille


## P-010: base damage, inclusive of both bounds (47956..52250 confirmed).
func damage_raw(lo: int, hi: int) -> int:
	return next_int(lo, hi)


## Index into the zeni denomination table. The drop roll producer is UNKNOWN
## (P-010); this roll is invented and the overlay labels it TEMP.
func drop_index(n: int) -> int:
	return next_int(0, n - 1)


## P-012: the reference engine's chance gate, reproduced in its own arithmetic.
## `threshold` is the behavior node's param field verbatim; the game rolls its
## PRNG, truncates to 16 bits, and passes when `value < threshold` - so the
## probability is threshold/65536 and the raw ROM constant can be carried into
## this project unconverted. Confirmed live: every threshold observed was an
## exact round percent (1310=2%, 2621=4%, 3932=6%, 5242=8%, 7864=12%).
##
## Upper bound is 65535, not 65536, because the reference comparison is strictly
## `<` against a 16-bit value: threshold 65536 would always pass, and matching
## that here keeps the two implementations identical at the boundary.
func gate_roll(threshold: int) -> bool:
	return next_int(0, 65535) < threshold


## Inclusive integer range. The single primitive every named call site above
## routes through, so ScriptedRng only has to override one method.
##
## Deliberately NOT named `randi_range`: that is a GDScript BUILT-IN GLOBAL, so an
## unqualified call to it binds to the global generator and silently bypasses both
## this class and any subclass override. Verified in 4.7-beta5. Keep this name.
func next_int(lo: int, hi: int) -> int:
	_calls += 1
	return _rng.randi_range(lo, hi)


class ScriptedRng extends DeterministicRng:
	## Test double: returns queued values in order and fails LOUDLY on underflow.
	## Tests use this to force a variant sequence or a critical; distribution
	## tests use a seeded DeterministicRng instead.

	var _queue: Array[int] = []
	var _popped: int = 0

	func _init(values: Array[int] = []) -> void:
		super(0)
		_queue = values.duplicate()

	## Append more values to the back of the queue.
	func push_values(values: Array[int]) -> void:
		for v: int in values:
			_queue.append(v)

	func remaining() -> int:
		return _queue.size()

	func popped_count() -> int:
		return _popped

	## Pops the next queued value, IGNORING the range — the point is to force an
	## exact outcome. Underflow is a hard failure, never a silent fallback to a
	## real roll, because a silently-random test is worse than a failing one.
	func next_int(_lo: int, _hi: int) -> int:
		_calls += 1
		if _queue.is_empty():
			var msg: String = "ScriptedRng underflow after %d values" % _popped
			push_error("[ScriptedRng] " + msg)
			assert(false, msg)
			return 0
		_popped += 1
		return _queue.pop_front()

	## True when the queue drained exactly — a test that queued more values than
	## the engine consumed did not test what it thought it did.
	func is_drained() -> bool:
		return _queue.is_empty()
