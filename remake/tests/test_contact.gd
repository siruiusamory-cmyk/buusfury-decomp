extends RefCounted
## R7: the P-003 contact test — four STRICT `<` integer comparisons against an
## ASYMMETRICALLY expanded target body. Pure function: no clock, no RNG, no tree.
##
## The geometry is the LIVE geometry, read from combat_config.tres, not a
## placeholder: the player is 26 tall and direction-dependent in WIDTH — 16 wide
## facing UP/DOWN, 8 wide in LEFT/RIGHT profile — and the wolf is a uniform
## 16x32. Testing the reach math against sizes the game does not use makes a
## green suite that cannot detect a constants-vs-rects mismatch, which is exactly
## what this file used to do (16x24 player, 20x16 target).
##
## Every case below places the player at a computed boundary and then one PIXEL
## either side of it, so the flip is pinned to the exact inequality rather than
## to a region. One pixel is the finest resolution the test operates at: BodyRect
## is built in pixel space (BodyRect.from_raw shifts raw down by 8 first), so a
## sub-pixel raw nudge cannot change the comparison at all — which the last case
## asserts directly.

## Player size per ATTACK FACING. The player is the one that narrows, so the
## boundary for a left/right swing is NOT the boundary for an up/down one, and a
## single fixed player size cannot express both.
const P_FACING := Vector2i(16, 26)  # dirs 0/1, attacking UP or DOWN
const P_PROFILE := Vector2i(8, 26)  # dirs 2/3, attacking LEFT or RIGHT
const T_SIZE := Vector2i(16, 32)  # wolf, uniform in all four directions


func run(h: TestHarness) -> void:
	h.begin_suite("test_contact (R7)")
	var c: CombatConfig = TestHarness.make_config()
	_r7_config_asymmetry(h, c)
	_r7_edges(h, c)
	_r7_subpixel(h, c)
	h.end_suite()


func _player_at(px: Vector2i, size: Vector2i = P_FACING) -> BodyRect:
	return BodyRect.new(px.x, px.y, px.x + size.x, px.y + size.y)


func _target_at(px: Vector2i) -> BodyRect:
	return BodyRect.new(px.x, px.y, px.x + T_SIZE.x, px.y + T_SIZE.y)


## The asymmetry itself, before any geometry: x0 expands OUT 4, x1 expands OUT 3,
## y0 unchanged, y1 shrinks IN 6. A symmetric "inflate by N" regression fails here.
func _r7_config_asymmetry(h: TestHarness, c: CombatConfig) -> void:
	h.assert_eq(c.melee_expand_x0, 4, "R7 left edge expands OUT by")
	h.assert_eq(c.melee_expand_x1, 3, "R7 right edge expands OUT by")
	h.assert_eq(c.melee_expand_y0, 0, "R7 top edge unchanged")
	h.assert_eq(c.melee_shrink_y1, 6, "R7 bottom edge shrinks IN by")
	h.assert_ne(c.melee_expand_x0, c.melee_expand_x1, "R7 x expansion is asymmetric")
	h.assert_ne(c.melee_expand_y0, c.melee_shrink_y1, "R7 y adjustment is asymmetric")

	# The same asymmetry as the expanded rect actually produced.
	var t: BodyRect = _target_at(Vector2i(100, 100))
	var e: BodyRect = MeleeResolver.expanded(t, c)
	h.assert_eq(e.x0, t.x0 - 4, "R7 expanded x0")
	h.assert_eq(e.x1, t.x1 + 3, "R7 expanded x1")
	h.assert_eq(e.y0, t.y0, "R7 expanded y0")
	h.assert_eq(e.y1, t.y1 - 6, "R7 expanded y1")
	h.assert_true(e.y1 < t.y1, "R7 the bottom edge is pulled IN, not out")


## One case per ATTACK FACING, at the live geometry. Each is stated as the AIR
## GAP between the two bodies — the reachable distance a player actually feels —
## rather than as a bare coordinate, and the player uses the width it really has
## in that facing. A positive gap means the bodies are apart and the swing still
## lands; a negative gap means they must OVERLAP by that much before it does.
##
## Wolf at (200,200), so 200,200 .. 216,232.
##
##   RIGHT  p 8 wide, left of wolf:  (t.x0-4) < p.x1 -> 196 < p.x+8  -> p.x >= 189
##          gap = t.x0 - p.x1 = 200 - 197 =  +3
##   LEFT   p 8 wide, right of wolf: p.x0 < (t.x1+3) -> p.x < 219    -> p.x <= 218
##          gap = p.x0 - t.x1 = 218 - 216 =  +2
##   DOWN   p 16 wide, above wolf:   (t.y0+0) < p.y1 -> 200 < p.y+26 -> p.y >= 175
##          gap = t.y0 - p.y1 = 200 - 201 =  -1
##   UP     p 16 wide, below wolf:   p.y0 < (t.y1-6) -> p.y < 226    -> p.y <= 225
##          gap = p.y0 - t.y1 = 225 - 232 =  -7
##
## The two vertical gaps being NEGATIVE is the whole point of the y asymmetry:
## a swing up or down needs real overlap, and needs seven pixels of it upward.
func _r7_edges(h: TestHarness, c: CombatConfig) -> void:
	var t: BodyRect = _target_at(Vector2i(200, 200))  # 200,200 .. 216,232

	# RIGHT-facing swing: player LEFT of the wolf, in 8-wide profile.
	_gap_case(h, c, t, "R7 right-facing", P_PROFILE, 3, Vector2i(189, 200), Vector2i(188, 200))

	# LEFT-facing swing: player RIGHT of the wolf, in 8-wide profile.
	_gap_case(h, c, t, "R7 left-facing", P_PROFILE, 2, Vector2i(218, 200), Vector2i(219, 200))

	# DOWN-facing swing: player ABOVE the wolf, 16 wide.
	_gap_case(h, c, t, "R7 down-facing", P_FACING, -1, Vector2i(205, 175), Vector2i(205, 174))

	# UP-facing swing: player BELOW the wolf, 16 wide.
	_gap_case(h, c, t, "R7 up-facing", P_FACING, -7, Vector2i(205, 225), Vector2i(205, 226))

	# The width itself changes the answer. At p.x=188 an 8-wide profile player is
	# OUT of reach, but a 16-wide body reaches — so a suite fixed to one player
	# size cannot pin the horizontal boundary at all.
	h.assert_false(MeleeResolver.in_reach(_player_at(Vector2i(188, 200), P_PROFILE), t, c),
		"R7 p.x=188 is OUT of reach at the 8-wide profile width")
	h.assert_true(MeleeResolver.in_reach(_player_at(Vector2i(188, 200), P_FACING), t, c),
		"R7 but the same p.x=188 IS in reach at the 16-wide facing width")

	# The asymmetry as BEHAVIOUR, not as config. The P-003 test differs from a
	# plain AABB overlap in BOTH directions, which a symmetric inflate cannot do.
	#
	# RIGHT-facing: a naive AABB needs p.x + 8 > 200, i.e. p.x >= 193, to touch.
	# The expanded rect connects at 189 — four pixels further out.
	h.assert_false(_naive_overlap(Vector2i(189, 205), t, P_PROFILE),
		"R7 p.x=189 is NOT an overlap under a naive AABB")
	h.assert_true(MeleeResolver.in_reach(_player_at(Vector2i(189, 205), P_PROFILE), t, c),
		"R7 but it IS in reach — the left edge expands 4 px OUT")

	# UP-facing, the mirror image: p.y=226 IS an overlap under a naive AABB and is
	# a MISS here, because y1 is pulled six pixels IN.
	h.assert_true(_naive_overlap(Vector2i(205, 226), t, P_FACING),
		"R7 p.y=226 IS an overlap under a naive AABB")
	h.assert_false(MeleeResolver.in_reach(_player_at(Vector2i(205, 226), P_FACING), t, c),
		"R7 but it is NOT in reach — the bottom edge shrinks 6 px IN")


## Plain half-open AABB overlap with no expansion at all, purely as the contrast
## case above. Nothing in the project uses this — the reach test is the four
## strict comparisons in MeleeResolver.in_reach.
func _naive_overlap(px: Vector2i, t: BodyRect, size: Vector2i) -> bool:
	var p: BodyRect = _player_at(px, size)
	return p.x0 < t.x1 and p.x1 > t.x0 and p.y0 < t.y1 and p.y1 > t.y0


## `inside_px` is the LAST player position that still lands; `outside_px` is one
## pixel past it and must miss. `gap` is the air gap between the two bodies at
## `inside_px`, asserted independently so the boundary is pinned to a measured
## distance and not merely to whichever coordinate happens to pass today.
func _gap_case(h: TestHarness, c: CombatConfig, t: BodyRect, label: String,
		size: Vector2i, gap: int, inside_px: Vector2i, outside_px: Vector2i) -> void:
	var p: BodyRect = _player_at(inside_px, size)
	var horizontal: bool = inside_px.y == outside_px.y
	var actual_gap: int = 0
	if horizontal:
		actual_gap = (t.x0 - p.x1) if inside_px.x < t.x0 else (p.x0 - t.x1)
	else:
		actual_gap = (t.y0 - p.y1) if inside_px.y < t.y0 else (p.y0 - t.y1)
	h.assert_eq(actual_gap, gap, "%s: max air gap between bodies" % label)
	h.assert_true(MeleeResolver.in_reach(p, t, c),
		"%s: %s is IN reach" % [label, inside_px])
	h.assert_false(MeleeResolver.in_reach(_player_at(outside_px, size), t, c),
		"%s: %s (one px over) is OUT of reach" % [label, outside_px])


## The test is integer PIXEL space. A raw 8.8 nudge below one pixel cannot move
## the boundary — that is what makes the four comparisons exact rather than
## approximate.
func _r7_subpixel(h: TestHarness, c: CombatConfig) -> void:
	var t: BodyRect = _target_at(Vector2i(200, 200))
	# p.x = 188 fails the right-facing boundary at the 8-wide profile width.
	# 188 px = 48128 raw; +255 raw is still 188 px.
	var fail_raw := Vector2i(FixedPoint.px_to_raw(188) + 255, FixedPoint.px_to_raw(200))
	var pass_raw := Vector2i(FixedPoint.px_to_raw(188) + 256, FixedPoint.px_to_raw(200))
	h.assert_eq(BodyRect.from_raw(fail_raw, P_PROFILE).x0, 188, "R7 raw+255 truncates to the same pixel")
	h.assert_false(MeleeResolver.in_reach(BodyRect.from_raw(fail_raw, P_PROFILE), t, c),
		"R7 a sub-pixel nudge (+255 raw) does NOT flip the strict comparison")
	h.assert_true(MeleeResolver.in_reach(BodyRect.from_raw(pass_raw, P_PROFILE), t, c),
		"R7 one whole pixel (+256 raw) does flip it")
