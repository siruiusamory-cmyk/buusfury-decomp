class_name MeleeResolver
extends RefCounted
## The P-003 contact test. Four STRICT `<` integer comparisons against the
## EXPANDED TARGET BODY. There is no separate hitbox, no radius, no distance
## check and no Rect2i.intersects anywhere in this file - Rect2i's inclusivity
## semantics do not match and the expansion is asymmetric per edge.
##
## Diagnostics: `trace_reach` prints the four edge comparisons individually, so a
## near-miss is diagnosable ("which edge failed?") instead of guessed. It is OFF
## by default and driven from the debug overlay - a per-swing print is fine, a
## per-tick one would be spam, and this only runs on an ACCEPTED attack.

## P-003 direction encoding, written into the victim's hit-direction byte.
const DIR_UP: int = 0
const DIR_DOWN: int = 1
const DIR_LEFT: int = 2
const DIR_RIGHT: int = 3

## Print the per-edge breakdown of every reach evaluation.
static var trace_reach: bool = false


## P-003 m5 (0x08029ED8) initial reach test. ALL comparisons STRICT `<`.
## Body-vs-EXPANDED-TARGET-BODY. Asymmetric on purpose: x0 pushed OUT 4,
## x1 pushed OUT 3, y0 unchanged, y1 pulled IN 6.
static func in_reach(player: BodyRect, target: BodyRect, c: CombatConfig) -> bool:
	var e_left: bool = (target.x0 - c.melee_expand_x0) < player.x1
	var e_right: bool = player.x0 < (target.x1 + c.melee_expand_x1)
	var e_top: bool = (target.y0 + c.melee_expand_y0) < player.y1
	var e_bottom: bool = player.y0 < (target.y1 - c.melee_shrink_y1)
	if trace_reach:
		print("[MeleeResolver] reach p=%s t=%s left=%s right=%s top=%s bottom=%s" % [
			player, target, e_left, e_right, e_top, e_bottom,
		])
	return e_left and e_right and e_top and e_bottom


## The EXPANDED target rect, for the gizmo outline only. in_reach above does NOT
## call this - it spells the four edges out so it reads as the recovered code.
static func expanded(target: BodyRect, c: CombatConfig) -> BodyRect:
	return BodyRect.new(
		target.x0 - c.melee_expand_x0,
		target.y0 + c.melee_expand_y0,
		target.x1 + c.melee_expand_x1,
		target.y1 - c.melee_shrink_y1,
	)


## Direction resolution runs ONLY AFTER the reach test passes - P-003's reach test
## is direction-independent, and the direction merely decides the victim's
## hit-direction byte. Keep that order.
static func hit_direction(player: BodyRect, target: BodyRect) -> int:
	var dx: int = player.center_x() - target.center_x()
	var dy: int = player.center_y() - target.center_y()
	if absi(dy) < absi(dx):
		return DIR_LEFT if dx < 1 else DIR_RIGHT
	return DIR_DOWN if dy < 1 else DIR_UP
