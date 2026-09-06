class_name WolfState
extends RefCounted
## The wolf state enum. The ENUM is the mechanism.
##
## Reference selector ids appear here for provenance only and NOWHERE else - not
## in a table, a dispatch, or a comparison:
##   IDLE 434, HUB 435, ATTACK 437, PURSUIT 438 (near) / 439 (far).
##   RETREAT 436 (P-014: 590 moving rows, 99.8% directed AWAY from the player).
##
## P-014 also found selector 439 to be a SEPARATE, rarer, ~35% faster retreat
## (9 occurrences, median 9 ticks at 217 raw/tick against 436's 12 ticks at 163).
## It is deliberately NOT modelled: n=9 is too few, and its gating differs from
## 436's. RETREAT here means 436 and only 436.
##
## This file declares no runtime behavior beyond a name lookup; the state
## TRANSITIONS - the thing worth diagnosing - are logged by actors/wolf.gd and by
## the WOLF_STATE_CHANGE trace record. `name_of` is what makes those lines
## readable, and it warns loudly on an out-of-range state rather than returning a
## silent placeholder.

enum { IDLE, HUB, PURSUIT, ATTACK, REACTION, RETREAT, DEAD }

const NAMES: PackedStringArray = [
	"IDLE", "HUB", "PURSUIT", "ATTACK", "REACTION", "RETREAT", "DEAD",
]


static func name_of(s: int) -> String:
	if s < 0 or s >= NAMES.size():
		push_warning("[WolfState] out-of-range state %d" % s)
		return "?%d" % s
	return NAMES[s]
