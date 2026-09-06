class_name FixedPoint
extends RefCounted
## The two fixed-point scales, and the ONLY conversions between them.
##
## They must NEVER be conflated (P-009):
##   POSITION uses  8 fractional bits — 256 raw = 1 pixel      (P-002)
##   HP       uses 10 fractional bits — 1024 raw = 1 displayed HP (P-009)
##
## Position truncates (a sub-pixel is not a pixel yet). HP CEILING-divides: the
## display path adds 0x3FF then asrs #0xA, so 1 raw of HP still shows as 1.
## The ceiling divide lives here and nowhere else.

## P-002: 8 fractional bits.
const RAW_UNITS_PER_PIXEL: int = 256
## P-009: 10 fractional bits.
const HP_RAW_PER_POINT: int = 1024


## Raw 8.8 world position -> integer pixels. Truncating (arithmetic shift).
static func raw_to_px(raw: int) -> int:
	return raw >> 8


## Integer pixels -> raw 8.8 world position.
static func px_to_raw(px: int) -> int:
	return px * RAW_UNITS_PER_PIXEL


## Raw 8.8 world position -> integer pixel vector.
static func raw_to_px_v(raw: Vector2i) -> Vector2i:
	return Vector2i(raw.x >> 8, raw.y >> 8)


## Integer pixel vector -> raw 8.8 world position.
static func px_to_raw_v(px: Vector2i) -> Vector2i:
	return px * RAW_UNITS_PER_PIXEL


## Raw 8.8 world position -> float pixels, for RENDERING ONLY. Never feed the
## result back into simulation; `pos_raw` stays authoritative.
static func raw_to_render_px(raw: Vector2i) -> Vector2:
	return Vector2(raw) / float(RAW_UNITS_PER_PIXEL)


## Raw HP -> displayed HP. P-009 CEILING divide: `(raw + 0x3FF) >> 10`.
## This is the only raw->HP conversion in the project; HP bars and damage numbers
## both route through it. `divisor` exists so a test can vary the scale; the
## confirmed value is 1024.
static func to_displayed_hp(raw: int, divisor: int = HP_RAW_PER_POINT) -> int:
	if raw <= 0:
		return 0
	return (raw + divisor - 1) / divisor
