extends Node
## Autoload "EventLog". The §27 event trace: a ring buffer of typed records,
## each `{tick: int, kind: StringName, data: Dictionary}`.
##
## Three consumers:
##   - print() to stdout while `echo` is true (default in debug builds);
##   - dump(path) writes the buffer to user://trace.log;
##   - tests call records_of(&"DAMAGE_APPLIED") and assert against the TRACE
##     rather than against internal state — that is what makes the three-moment
##     separation (contact / reaction entry / damage application) testable rather
##     than merely documented.

const KIND_TICK_START: StringName = &"TICK_START"
const KIND_INPUT: StringName = &"INPUT"
const KIND_MOVE: StringName = &"MOVE"
const KIND_ATTACK_ACCEPTED: StringName = &"ATTACK_ACCEPTED"
const KIND_ATTACK_REJECTED: StringName = &"ATTACK_REJECTED"
const KIND_CONTACT: StringName = &"CONTACT"
const KIND_REACTION_ENTER: StringName = &"REACTION_ENTER"
const KIND_DAMAGE_APPLIED: StringName = &"DAMAGE_APPLIED"
const KIND_REACTION_EXIT: StringName = &"REACTION_EXIT"
const KIND_WOLF_STATE_CHANGE: StringName = &"WOLF_STATE_CHANGE"
const KIND_DEATH: StringName = &"DEATH"
const KIND_REWARD_CREATED: StringName = &"REWARD_CREATED"
const KIND_EXP_PAYOUT: StringName = &"EXP_PAYOUT"
const KIND_LEVEL_UP: StringName = &"LEVEL_UP"
const KIND_DROP: StringName = &"DROP"

const CAPACITY: int = 4096

## Mirror every record to stdout. Default on in debug builds.
var echo: bool = true
## TICK_START is only recorded when this is true; it is one record per tick.
var verbose: bool = false

var _records: Array[Dictionary] = []


func _ready() -> void:
	echo = OS.is_debug_build()
	print("[EventLog] ready capacity=%d echo=%s" % [CAPACITY, echo])


## Record one event. `data` is copied so a caller reusing a scratch dictionary
## cannot retroactively rewrite history.
func emit_event(t: int, kind: StringName, data: Dictionary = {}) -> void:
	var rec: Dictionary = {"tick": t, "kind": kind, "data": data.duplicate()}
	_records.append(rec)
	if _records.size() > CAPACITY:
		_records.pop_front()
	if echo:
		print(format_record(rec))


func emit_tick_start(t: int) -> void:
	if verbose:
		emit_event(t, KIND_TICK_START)


func emit_input(t: int, dir: Vector2i, attack: bool) -> void:
	emit_event(t, KIND_INPUT, {"dir": dir, "attack": attack})


func emit_move(t: int, pos_raw: Vector2i, delta_raw: Vector2i) -> void:
	emit_event(t, KIND_MOVE, {"pos_raw": pos_raw, "delta_raw": delta_raw})


func emit_attack_accepted(t: int, variant: int) -> void:
	emit_event(t, KIND_ATTACK_ACCEPTED, {"variant": variant})


func emit_attack_rejected(t: int, ticks_until_open: int) -> void:
	emit_event(t, KIND_ATTACK_REJECTED, {"ticks_until_open": ticks_until_open})


func emit_contact(t: int, variant: int, dist_sq: int) -> void:
	emit_event(t, KIND_CONTACT, {"variant": variant, "dist_sq": dist_sq})


func emit_reaction_enter(t: int, end_tick: int, damage_tick: int) -> void:
	emit_event(t, KIND_REACTION_ENTER, {"end_tick": end_tick, "damage_tick": damage_tick})


func emit_damage_applied(t: int, raw: int, displayed: int, crit: bool, hp_after: int) -> void:
	emit_event(t, KIND_DAMAGE_APPLIED, {
		"raw": raw, "displayed": displayed, "crit": crit, "hp_after": hp_after,
	})


func emit_reaction_exit(t: int) -> void:
	emit_event(t, KIND_REACTION_EXIT)


func emit_wolf_state_change(t: int, from_state: int, to_state: int) -> void:
	emit_event(t, KIND_WOLF_STATE_CHANGE, {"from": from_state, "to": to_state})


func emit_death(t: int) -> void:
	emit_event(t, KIND_DEATH)


func emit_reward_created(t: int, amount: int, payout_tick: int) -> void:
	emit_event(t, KIND_REWARD_CREATED, {"amount": amount, "payout_tick": payout_tick})


func emit_exp_payout(t: int, amount: int, recipient: int) -> void:
	emit_event(t, KIND_EXP_PAYOUT, {"amount": amount, "recipient": recipient})


func emit_level_up(t: int, level: int) -> void:
	emit_event(t, KIND_LEVEL_UP, {"level": level})


func emit_drop(t: int, kind_name: String, amount: int) -> void:
	emit_event(t, KIND_DROP, {"drop": kind_name, "amount": amount})


## All records of one kind, in order. The test-facing read path.
func records_of(kind: StringName) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for r: Dictionary in _records:
		if r["kind"] == kind:
			out.append(r)
	return out


func records() -> Array[Dictionary]:
	return _records.duplicate()


func clear() -> void:
	_records.clear()


## One line per record: `[  142] DAMAGE_APPLIED  raw=51338 displayed=51 ...`
func format_record(rec: Dictionary) -> String:
	var line: String = "[%5d] %s" % [rec["tick"], rec["kind"]]
	var data: Dictionary = rec["data"]
	if data.is_empty():
		return line
	var parts: PackedStringArray = PackedStringArray()
	for k: Variant in data:
		parts.append("%s=%s" % [k, data[k]])
	return line + "  " + " ".join(parts)


func dump(path: String = "user://trace.log") -> Error:
	var f: FileAccess = FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		push_error("[EventLog] cannot open %s: %d" % [path, FileAccess.get_open_error()])
		return FileAccess.get_open_error()
	for r: Dictionary in _records:
		f.store_line(format_record(r))
	f.close()
	print("[EventLog] dumped %d records to %s" % [_records.size(), path])
	return OK
