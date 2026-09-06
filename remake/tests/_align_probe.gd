extends Node2D
func _ready() -> void:
	var cfg: CombatConfig = load("res://config/combat_config.tres")
	var p: Player = preload("res://actors/player.tscn").instantiate()
	var w: Wolf = preload("res://actors/wolf.tscn").instantiate()
	p.config = cfg; w.config = cfg
	p.rng = DeterministicRng.new(1); w.rng = DeterministicRng.new(2)
	add_child(p); add_child(w)
	for f in [MeleeResolver.DIR_DOWN, MeleeResolver.DIR_UP, MeleeResolver.DIR_LEFT, MeleeResolver.DIR_RIGHT]:
		p.facing = f
		p._sync_sprite(false)
		var spr: Sprite2D = p.get_node("Sprite")
		var b: BodyRect = p.body_rect()
		var t: Texture2D = spr.texture
		if t != null:
			print("PLAYER dir=", f, " box=(", b.x0, ",", b.y0, ")..(", b.x1, ",", b.y1,
				") sprite_pos=", spr.position, " tex=", t.get_size(),
				" -> art spans x ", spr.position.x, "..", spr.position.x + t.get_size().x,
				"  y ", spr.position.y, "..", spr.position.y + t.get_size().y)
	w._sync_sprite()
	var ws: Sprite2D = w.get_node("Sprite")
	var wb: BodyRect = w.body_rect()
	if ws.texture != null:
		print("WOLF box=(", wb.x0, ",", wb.y0, ")..(", wb.x1, ",", wb.y1,
			") sprite_pos=", ws.position, " tex=", ws.texture.get_size())
	get_tree().quit()
