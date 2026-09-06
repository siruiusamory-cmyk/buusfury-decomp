extends Node
## Autoload "Party". The characters, the active index, and the pending-reward
## queue that makes the P-010 recipient asymmetry observable.
##
## The slice creates two characters deliberately: the debug overlay offers F3 to
## switch `active_index` at runtime, and the test suite switches it inside the
## one-tick gap between the lethal hit and the payout.

var characters: Array[Character] = []
var active_index: int = 0
## Item count for the P-010 capacity check. Adding past the cap is a silent no-op.
var item_count: int = 0
## Injected by test_room.gd (and by tests). CombatConfig is a Resource, not an
## autoload, so no gameplay constant is duplicated here: `level_cap` and
## `item_inventory_cap` are read from it. Until it is set, the level-up loop is
## still bounded by the transcribed threshold table.
var config: CombatConfig = null

## Rewards awaiting payout. Elements are `Reward` (combat/reward.gd, owned by
## another module) — read structurally via `amount` and `payout_tick` so this
## autoload does not depend on a class it does not own.
var _pending: Array[RefCounted] = []


func _ready() -> void:
	Clock.tick.connect(_on_tick)
	if characters.is_empty():
		characters = [Character.new("A"), Character.new("B")]
	print("[Party] ready characters=%d active=%d" % [characters.size(), active_index])


func active_character() -> Character:
	if active_index < 0 or active_index >= characters.size():
		return null
	return characters[active_index]


## Queue a reward whose AMOUNT is already fixed. The recipient is deliberately not
## recorded here.
func queue_reward(reward: RefCounted) -> void:
	_pending.append(reward)


func pending_reward_count() -> int:
	return _pending.size()


func _on_tick(t: int) -> void:
	for r: RefCounted in _pending.duplicate():
		if t >= r.get("payout_tick"):
			# P-010: RECIPIENT is resolved HERE, at payout, not at kill.
			# This asymmetry is the confirmed mechanism behind the documented
			# save-point character-switch glitch. Do not simplify to
			# killer-ownership: `Reward` carries no recipient field precisely so
			# that "simplification" is structurally impossible.
			var recipient: Character = active_character()
			var amount: int = r.get("amount")
			_pending.erase(r)
			if recipient == null:
				push_warning("[Party] reward of %d dropped: no active character" % amount)
				continue
			recipient.xp += amount
			EventLog.emit_exp_payout(t, amount, active_index)
			_check_level_up(recipient)


## A `while`, not an `if` — one large award may cross several thresholds.
## Cap 200 (P-010) is the first clause; the second bounds the loop to the fifteen
## transcribed entries, because levels 16..200 were never supplied by any source.
func _check_level_up(ch: Character) -> void:
	var cap: int = LevelThresholds.TABLE.size()
	if config != null:
		cap = config.level_cap
	while ch.level < cap \
	  and ch.level < LevelThresholds.TABLE.size() \
	  and ch.xp >= LevelThresholds.TABLE[ch.level]:
		ch.level += 1
		EventLog.emit_level_up(Clock.current_tick, ch.level)


## P-010: silent no-op when the inventory is full. Encoded once — in CombatConfig
## as `item_inventory_cap` — rather than rediscovered later. Pass the cap
## explicitly when no config has been injected.
func try_add_item(_id: StringName, cap: int = -1) -> bool:
	var limit: int = cap
	if limit < 0:
		if config == null:
			push_error("[Party] try_add_item needs a config or an explicit cap")
			return false
		limit = config.item_inventory_cap
	if item_count >= limit:
		return false
	item_count += 1
	return true
