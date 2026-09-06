class_name BodyRect
extends RefCounted
## Integer AABB in PIXELS, matching the recovered body registry
## (`cand_body_bounds_0800FE78`). Built by converting `pos_raw` down to pixels
## FIRST — distances and the reach test are pixel-space, never raw 8.8.
##
## There is no Area2D, no CollisionShape2D and no Rect2i anywhere near this.
## Godot's physics would round-trip through floats and its own broadphase, and
## the P-003 reach test is a strict-inequality INTEGER comparison.

var x0: int
var y0: int
var x1: int
var y1: int


func _init(p_x0: int = 0, p_y0: int = 0, p_x1: int = 0, p_y1: int = 0) -> void:
	x0 = p_x0
	y0 = p_y0
	x1 = p_x1
	y1 = p_y1


## Body rect for an actor at raw 8.8 position `pos_raw` with pixel size `size_px`,
## anchored at its top-left. Converts to pixels before any geometry happens.
static func from_raw(pos_raw: Vector2i, size_px: Vector2i) -> BodyRect:
	var px: Vector2i = FixedPoint.raw_to_px_v(pos_raw)
	return BodyRect.new(px.x, px.y, px.x + size_px.x, px.y + size_px.y)


## P-007: centers are `(lo + hi) >> 1` on the BODY rect.
func center_x() -> int:
	return (x0 + x1) >> 1


func center_y() -> int:
	return (y0 + y1) >> 1


## P-007: squared center distance in pixel space, integer. One primitive for both
## thresholds — mirroring the recovered structure where 0x08029BE0 and 0x08029C90
## are instruction-for-instruction identical with only the threshold differing.
## Callers compare with `<=` (inclusive; the recovered branch is a signed bgt to
## failure).
static func center_dist_sq(a: BodyRect, b: BodyRect) -> int:
	var dx: int = a.center_x() - b.center_x()
	var dy: int = a.center_y() - b.center_y()
	return dx * dx + dy * dy


func _to_string() -> String:
	return "BodyRect(%d,%d..%d,%d)" % [x0, y0, x1, y1]
