extends RefCounted
## R14-R15: the EXP payout lands one tick after the lethal hit, its AMOUNT is
## fixed at the kill and its RECIPIENT is resolved at the payout; and the
## equipment bonus is ADDITIVE.
##
## Plus the contract guard on LevelThresholds.TABLE.
##
## Roll order on a killing blow (actors/wolf.gd):
##   1. rng.damage_raw(...)               -- the base damage
##   2. rng.crit_roll(temp_crit_chance)   -- crit decision
##   3. rng.crit_roll(temp_drop_chance)   -- the drop roll, inside _die
##   4. rng.drop_index(...)               -- only when 3 succeeded
## Every test below sets temp_drop_chance_permille = 0 so roll 4 never happens and
## the queue stays [damage, NO_CRIT, NO_DROP].

const NO_CRIT: int = 1001
const NO_DROP: int = 1001
## Enough to kill the 179200-raw wolf in one application, forced by the script.
const LETHAL_RAW: int = 200000


func run(h: TestHarness) -> void:
	h.begin_suite("test_progression (R14-R15 + level table guard)")
	_r14_late_resolved_recipient(h)
	_r15_additive_equipment_bonus(h)
	_guard_level_table(h)
	h.end_suite()


## Fresh party state. Party is an autoload, so every test resets it explicitly
## rather than inheriting whatever the previous one left behind.
func _reset_party(c: CombatConfig, bonus_a: int, bonus_b: int) -> void:
	Party.config = c
	Party.characters = [
		Character.new("A", 1, bonus_a),
		Character.new("B", 1, bonus_b),
	]
	Party.active_index = 0
	Party.item_count = 0


## Kill the wolf on a scheduled tick and return the tick the lethal damage landed.
func _kill_wolf(h: TestHarness, c: CombatConfig) -> Array:
	var rng := DeterministicRng.ScriptedRng.new([LETHAL_RAW, NO_CRIT, NO_DROP])
	var w: Wolf = h.spawn_wolf(c, rng, Vector2i(200, 200))
	EventLog.clear()
	Clock.step(1)
	var entry: int = Clock.current_tick
	w.on_contact(entry, MeleeResolver.DIR_LEFT)
	# Damage lands at entry+3; that is the lethal tick.
	Clock.step(3)
	return [w, entry + 3, rng]


## R14: payout is exactly 1 tick after the lethal damage, the AMOUNT was fixed at
## the kill, and the RECIPIENT is whoever is active AT THE PAYOUT. Switching the
## active character inside the one-tick gap moves the whole award.
func _r14_late_resolved_recipient(h: TestHarness) -> void:
	var c: CombatConfig = TestHarness.make_config()
	c.temp_drop_chance_permille = 0
	h.assert_eq(c.exp_payout_delay_ticks, 1, "R14 configured payout delay")

	# Character A (active at the kill) has no bonus items, B has two — so if the
	# amount were resolved at PAYOUT rather than at the kill it would be 271, and
	# if the recipient were resolved at the KILL, A would be paid.
	_reset_party(c, 0, 2)

	var killed: Array = _kill_wolf(h, c)
	var w: Wolf = killed[0]
	var lethal_tick: int = killed[1]
	var rng: DeterministicRng.ScriptedRng = killed[2]

	h.assert_eq(w.state, WolfState.DEAD, "R14 the wolf died")
	h.assert_eq(Clock.current_tick, lethal_tick, "R14 clock is on the lethal tick")
	h.assert_true(rng.is_drained(), "R14 exactly the queued rolls were consumed")
	h.assert_eq(Party.pending_reward_count(), 1, "R14 one reward queued at the kill")

	var created: Array[Dictionary] = EventLog.records_of(EventLog.KIND_REWARD_CREATED)
	h.assert_eq(created.size(), 1, "R14 one REWARD_CREATED record")
	h.assert_eq(created[0]["tick"], lethal_tick, "R14 reward created ON the lethal tick")
	h.assert_eq(created[0]["data"]["amount"], 225,
		"R14 amount fixed at the kill from A's 0 bonus items")
	h.assert_eq(created[0]["data"]["payout_tick"], lethal_tick + 1, "R14 payout scheduled at +1")

	# Nothing paid yet.
	h.assert_eq(Party.characters[0].xp, 0, "R14 A has no xp on the lethal tick")
	h.assert_eq(Party.characters[1].xp, 0, "R14 B has no xp on the lethal tick")
	h.assert_eq(EventLog.records_of(EventLog.KIND_EXP_PAYOUT).size(), 0,
		"R14 no payout on the lethal tick")

	# THE ONE-TICK GAP: switch the active character before the payout lands.
	Party.active_index = 1
	Clock.step(1)

	h.assert_eq(Clock.current_tick, lethal_tick + 1, "R14 clock is at lethal+1")
	var payouts: Array[Dictionary] = EventLog.records_of(EventLog.KIND_EXP_PAYOUT)
	h.assert_eq(payouts.size(), 1, "R14 exactly one payout")
	h.assert_eq(payouts[0]["tick"], lethal_tick + 1, "R14 payout lands at lethal+1")
	h.assert_eq(payouts[0]["data"]["recipient"], 1, "R14 the traced recipient is B")
	h.assert_eq(Party.characters[1].xp, 225, "R14 the NEW active character receives 225")
	h.assert_eq(Party.characters[0].xp, 0, "R14 the original character receives 0")
	# The amount did NOT follow the switch: B has 2 bonus items but was paid A's 225.
	h.assert_eq(payouts[0]["data"]["amount"], 225,
		"R14 amount stayed fixed at the kill (not re-derived from B's 2 items)")
	h.assert_ne(payouts[0]["data"]["amount"], 271,
		"R14 the amount is NOT re-resolved from the payout recipient")
	h.assert_eq(Party.pending_reward_count(), 0, "R14 the queue drained")
	h.despawn([w])


## R15: the equipment bonus is ADDITIVE, +23 per qualifying item: 0/1/2 items give
## exactly 225 / 248 / 271.
func _r15_additive_equipment_bonus(h: TestHarness) -> void:
	var c: CombatConfig = TestHarness.make_config()
	c.temp_drop_chance_permille = 0
	h.assert_eq(c.wolf_base_exp, 225, "R15 configured base EXP")
	h.assert_eq(c.equipment_exp_bonus_per_item, 23, "R15 configured per-item bonus")

	var expected: Array[int] = [225, 248, 271]
	for items: int in 3:
		_reset_party(c, items, 0)
		var killed: Array = _kill_wolf(h, c)
		var w: Wolf = killed[0]
		var lethal_tick: int = killed[1]
		Clock.step(1)

		var payouts: Array[Dictionary] = EventLog.records_of(EventLog.KIND_EXP_PAYOUT)
		h.assert_eq(payouts.size(), 1, "R15 one payout with %d bonus items" % items)
		h.assert_eq(payouts[0]["tick"], lethal_tick + 1,
			"R15 payout at lethal+1 with %d bonus items" % items)
		h.assert_eq(payouts[0]["data"]["amount"], expected[items],
			"R15 award with %d bonus items" % items)
		h.assert_eq(Party.characters[0].xp, expected[items],
			"R15 xp credited with %d bonus items" % items)
		h.despawn([w])

	# Additive, not multiplicative: the steps are equal and 225*2 is not 271.
	h.assert_eq(expected[1] - expected[0], 23, "R15 first item adds exactly 23")
	h.assert_eq(expected[2] - expected[1], 23, "R15 second item adds exactly 23")
	h.assert_ne(225 * 2, 271, "R15 guard: a multiplicative regression would give 450, not 271")
	h.assert_ne(expected[2], 225 * 2, "R15 two items is 271, not double")
	# Straight from the Reward factory too, independent of the wolf path.
	h.assert_eq(Reward.create(c.wolf_base_exp, 0, c, 0).amount, 225, "R15 Reward.create 0 items")
	h.assert_eq(Reward.create(c.wolf_base_exp, 1, c, 0).amount, 248, "R15 Reward.create 1 item")
	h.assert_eq(Reward.create(c.wolf_base_exp, 2, c, 0).amount, 271, "R15 Reward.create 2 items")


## Contract guard: the first fifteen EXP thresholds, transcribed from the table at
## 0x086B7084. A cross-threshold award levels up more than once.
func _guard_level_table(h: TestHarness) -> void:
	var expected: Array[int] = [
		0, 10, 40, 100, 200, 350, 560, 840, 1200, 1650, 2200, 2875, 3700, 4700, 5900,
	]
	h.assert_eq(LevelThresholds.TABLE.size(), 15, "GUARD level table has 15 entries")
	var actual: Array[int] = []
	for v: int in LevelThresholds.TABLE:
		actual.append(v)
	h.assert_eq(actual, expected, "GUARD level table entries 1..15")

	# One award crossing several thresholds levels up several times.
	var c: CombatConfig = TestHarness.make_config()
	_reset_party(c, 0, 0)
	EventLog.clear()
	var ch: Character = Party.characters[0]
	h.assert_eq(ch.level, 1, "GUARD character starts at level 1")
	Party.queue_reward(Reward.create(225, 0, c, Clock.current_tick))
	Clock.step(2)
	# 225 xp clears the thresholds for levels 2 (10), 3 (40), 4 (100) and 5 (200).
	h.assert_eq(ch.xp, 225, "GUARD xp after the award")
	h.assert_eq(ch.level, 5, "GUARD one 225 award crosses four thresholds")
	h.assert_eq(EventLog.records_of(EventLog.KIND_LEVEL_UP).size(), 4,
		"GUARD four LEVEL_UP records from one award")
