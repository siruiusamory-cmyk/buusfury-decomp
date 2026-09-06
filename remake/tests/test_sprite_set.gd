extends RefCounted
## SpriteSet.hurt: the directional flinch wins, the non-directional one catches
## a missing file, and neither present returns null so the caller's own fallback
## still runs.
##
## Sprite PNGs are git-ignored extracted art, so a test that reads the disk would
## pass or fail depending on whether the slicer had been run. Instead the static
## path cache is primed with sentinel textures - a cached entry is exactly what
## `get_texture` returns for a file it has already resolved, and a cached `null`
## is exactly how it records "checked, not present".

const KEYS: Array[String] = [
	"wolf_hurt", "wolf_hurt_up", "wolf_hurt_down", "wolf_hurt_left", "wolf_hurt_right",
]


static func _sentinel() -> Texture2D:
	return ImageTexture.create_from_image(Image.create(1, 1, false, Image.FORMAT_RGBA8))


## Overwrite every wolf_hurt key: present ones get their own sentinel, the rest
## get a cached null. Returns the sentinel map so the test can compare identity.
static func _prime(present: Array[String]) -> Dictionary:
	var made: Dictionary = {}
	for k: String in KEYS:
		var tex: Texture2D = _sentinel() if present.has(k) else null
		SpriteSet._cache[k] = tex
		made[k] = tex
	return made


func run(h: TestHarness) -> void:
	h.begin_suite("test_sprite_set (directional flinch)")
	_directional_wins(h)
	_falls_back_to_non_directional(h)
	_null_when_absent(h)
	_offset_sits_art_on_the_box(h)
	for k: String in KEYS:
		SpriteSet._cache.erase(k)
	h.end_suite()


## Each direction index resolves to ITS OWN file, using SpriteSet.DIR_NAME rather
## than a second mapping - the bug this suite exists for was every direction
## getting the one DOWN frame.
func _directional_wins(h: TestHarness) -> void:
	var made: Dictionary = _prime(KEYS)
	for dir: int in range(4):
		var want: Texture2D = made["wolf_hurt_%s" % SpriteSet.DIR_NAME[dir]]
		h.assert_true(
			SpriteSet.hurt("wolf", dir) == want,
			"dir %d (%s) resolves to its own flinch" % [dir, SpriteSet.DIR_NAME[dir]]
		)
	h.assert_true(
		SpriteSet.hurt("wolf", MeleeResolver.DIR_LEFT)
			!= SpriteSet.hurt("wolf", MeleeResolver.DIR_RIGHT),
		"left and right flinches differ"
	)


func _falls_back_to_non_directional(h: TestHarness) -> void:
	var made: Dictionary = _prime(["wolf_hurt"])
	for dir: int in range(4):
		h.assert_true(
			SpriteSet.hurt("wolf", dir) == made["wolf_hurt"],
			"dir %d falls back to wolf_hurt when the directional file is missing" % dir
		)


func _null_when_absent(h: TestHarness) -> void:
	_prime([])
	h.assert_true(
		SpriteSet.hurt("wolf", MeleeResolver.DIR_DOWN) == null,
		"null when no flinch art exists at all"
	)
	# Out-of-range indices clamp instead of crashing, same as SpriteSet.frame.
	h.assert_true(SpriteSet.hurt("wolf", -1) == null, "dir -1 clamps")
	h.assert_true(SpriteSet.hurt("wolf", 99) == null, "dir 99 clamps")


## The actor origin is the body rect's TOP-LEFT, so an unoffset `centered = false`
## sprite hung down-right of the box - the misalignment this offset exists to fix.
## Every emitted frame is a whole 32x32 sheet cell, so the offset must centre that
## cell on the box and sit its BOTTOM on the box bottom.
func _offset_sits_art_on_the_box(h: TestHarness) -> void:
	var cell: Texture2D = ImageTexture.create_from_image(
		Image.create(32, 32, false, Image.FORMAT_RGBA8)
	)
	# Player facing UP/DOWN: 16x26 box. Wolf: 16x32, where the cell is exactly the
	# box height, so the offset must not shift it vertically at all.
	var facing: Vector2 = SpriteSet.sprite_offset(cell, Vector2i(16, 26))
	h.assert_true(facing == Vector2(-8, -6), "16x26 box centres the cell, bottom on bottom")
	var profile: Vector2 = SpriteSet.sprite_offset(cell, Vector2i(8, 26))
	h.assert_true(profile == Vector2(-12, -6), "8x26 profile box re-centres rather than shifting")
	h.assert_true(
		SpriteSet.sprite_offset(cell, Vector2i(16, 32)) == Vector2(-8, 0),
		"16x32 box matches the cell height exactly, so no vertical shift"
	)
	# Bottom edges coincide: off.y + 32 == box height, in every case above.
	h.assert_true(facing.y + 32 == 26, "cell bottom lands on the 26px box bottom")
	# A missing frame must not crash or move the node - the ColorRect placeholder
	# is what shows, and it is anchored at the origin.
	h.assert_true(
		SpriteSet.sprite_offset(null, Vector2i(16, 26)) == Vector2.ZERO,
		"null texture yields a zero offset, leaving the placeholder in place"
	)
