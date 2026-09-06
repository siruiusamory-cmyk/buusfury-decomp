class_name SpriteSet
extends RefCounted
## OPTIONAL runtime sprite loader. Presentation only - nothing here is read by
## the simulation, and an empty sprite directory changes nothing about how the
## game runs or looks.
##
## Sprites extracted from the commercial ROM must NEVER be committed
## (docs/DEVELOPMENT.md:83/87). They live in `res://build/sprites/`, which is ignored by
## both remake/.gitignore and the repo-root .gitignore. See the README there.
##
## Loading uses Image.load_from_file + ImageTexture.create_from_image on
## purpose: load()/preload() would require Godot's import step and would bake
## the extracted art into .godot/, which is exactly what must not happen.
##
## Expected filenames, all optional:
##   player_idle_<dir>.png
##   player_walk_<dir>_0.png   player_walk_<dir>_1.png
##   player_punch_<dir>.png
##   wolf_idle_<dir>.png
##   wolf_walk_<dir>_0.png     wolf_walk_<dir>_1.png
##   wolf_hurt_<dir>.png       wolf_hurt.png
##   wolf_dead.png
## where <dir> is one of up / down / left / right.
##
## Every lookup degrades: a missing walk frame falls back to idle, a missing
## punch frame falls back to idle (so the drawn swing stays the hit cue), a
## missing directional flinch falls back to the non-directional `wolf_hurt.png`,
## and a missing idle returns null, which keeps the actor's ColorRect placeholder.

const DIR: String = "res://build/sprites/"

## TEMP: the original's walk cadence was never measured. Ticks each of the two
## walk frames is held for. Do not read this as a recovered constant.
const TEMP_WALK_FRAME_TICKS: int = 8

## Name per MeleeResolver.DIR_* index. Same order as the P-003 encoding.
const DIR_NAME: Array[String] = ["up", "down", "left", "right"]

## Absolute-path cache; a null value means "checked, not present", so a missing
## file is stat'd once rather than every tick.
static var _cache: Dictionary = {}


## Texture for `key`, or null when the PNG is absent or unreadable.
static func get_texture(key: String) -> Texture2D:
	if _cache.has(key):
		return _cache[key]
	var path: String = DIR + key + ".png"
	var tex: Texture2D = null
	if FileAccess.file_exists(path):
		var img: Image = Image.new()
		if img.load(ProjectSettings.globalize_path(path)) == OK:
			tex = ImageTexture.create_from_image(img)
		else:
			push_warning("[SpriteSet] failed to load %s" % path)
	_cache[key] = tex
	return tex


## Frame for one actor, resolving the fallbacks described in the header.
## `walk_phase` is 0 or 1 and is advanced by the caller on the gameplay tick.
static func frame(
	actor: String, dir: int, moving: bool, attacking: bool, walk_phase: int
) -> Texture2D:
	var d: String = DIR_NAME[clampi(dir, 0, 3)]
	var idle: Texture2D = get_texture("%s_idle_%s" % [actor, d])
	if attacking:
		var punch: Texture2D = get_texture("%s_punch_%s" % [actor, d])
		return punch if punch != null else idle
	if moving:
		var walk: Texture2D = get_texture("%s_walk_%s_%d" % [actor, d, walk_phase & 1])
		if walk != null:
			return walk
	return idle


## Hit-reaction frame for `actor` facing `dir`: the directional flinch first,
## then the non-directional one. Returns null when neither is present, which
## leaves the caller's own fallback (the normal `frame()` chain) in charge.
static func hurt(actor: String, dir: int) -> Texture2D:
	var d: String = DIR_NAME[clampi(dir, 0, 3)]
	var tex: Texture2D = get_texture("%s_hurt_%s" % [actor, d])
	return tex if tex != null else get_texture("%s_hurt" % actor)


## Advance and return the walk phase. Called once per gameplay tick.
static func step_phase(counter: int) -> int:
	return (counter / TEMP_WALK_FRAME_TICKS) & 1


## Where an actor's Sprite2D goes so the ART lines up with the BODY RECT.
##
## The actor's node origin is the body rect's TOP-LEFT (BodyRect.from_raw), and
## the Sprite2D is `centered = false`, so with no offset a frame would draw from
## that corner - which is why the art hung down-right of the box.
##
## Every frame the slicer emits is a whole 32x32 sheet cell, padding included, so
## they all share one origin: the character stands centred in the cell with its
## feet near the cell bottom. Centring the cell on the box and sitting the cell's
## bottom on the box's bottom therefore puts the feet at the box floor and the
## torso in the box's width, in every frame and every facing. The art is taller
## than the box, so hair overhangs the top - expected, not a fit to force.
##
## `body_size_px` is the LIVE directional size, so the 8px-wide profile box
## re-centres rather than shifting the character sideways when facing turns.
static func sprite_offset(tex: Texture2D, body_size_px: Vector2i) -> Vector2:
	if tex == null:
		return Vector2.ZERO
	var s: Vector2 = tex.get_size()
	return Vector2(floorf((body_size_px.x - s.x) * 0.5), body_size_px.y - s.y)
