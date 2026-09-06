class_name Reward
extends RefCounted
## An EXP award whose AMOUNT is fixed at kill time and whose RECIPIENT is not
## recorded at all.
##
## P-010: the recipient is resolved LATER, at payout, from whoever is the active
## character at that moment (progression/party.gd). This class holds no killer
## reference and no recipient index precisely so that "simplifying" the asymmetry
## into killer-ownership is structurally impossible.
##
## Party._pending is typed Array[RefCounted] and reads `amount` and `payout_tick`
## structurally, so these two member names are load-bearing.
##
## Diagnostics: one line per creation, naming the amount and the payout deadline
## but deliberately NOT a recipient - the log then shows the asymmetry directly
## (creation names no one; the EXP_PAYOUT record names the recipient). Creation is
## once per kill, so this is never spam.

## Set false to silence the creation line.
static var log_create: bool = true

var amount: int = 0
var payout_tick: int = 0


static func create(base_exp: int, bonus_items: int, c: CombatConfig, t: int) -> Reward:
	var r: Reward = Reward.new()
	# P-010: the bonus is ADDITIVE, +23 per qualifying item. Multiplicative was
	# REFUTED - the reward object at +0x08 read 225 / 248 / 271. Baked in HERE,
	# at creation, from the character active at the kill.
	r.amount = base_exp + c.equipment_exp_bonus_per_item * bonus_items
	r.payout_tick = t + c.exp_payout_delay_ticks
	if log_create:
		print("[Reward] created t=%d base=%d bonus_items=%d amount=%d payout_tick=%d recipient=UNRESOLVED" % [
			t, base_exp, bonus_items, r.amount, r.payout_tick,
		])
	return r
