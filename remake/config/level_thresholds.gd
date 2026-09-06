class_name LevelThresholds
extends RefCounted
## EXP required to reach each level. A table, not a tuning value — which is why it
## lives here and not in CombatConfig, and why it is never edited per-test.

# TODO(P-010): table decoded from 0x086B7084; only the first 15 entries are
# transcribed. Levels beyond 15 are not exercised by the slice. Entries 16..200
# were not supplied by any source document and inventing them would fabricate
# reference data — the level-up loop is bounded by TABLE.size() instead.
const TABLE: PackedInt32Array = [
	0, 10, 40, 100, 200, 350, 560, 840, 1200, 1650, 2200, 2875, 3700, 4700, 5900,
]
