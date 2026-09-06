class_name Character
extends RefCounted
## One party member. Level, xp, and the count of items that grant the EXP bonus.

var name_text: String = ""
var level: int = 1
var xp: int = 0
## P-010: each qualifying item adds +23 EXP to a reward, ADDITIVELY.
## 0 / 1 / 2 items produce awards of 225 / 248 / 271.
var equipment_bonus_items: int = 0


func _init(p_name: String = "", p_level: int = 1, p_bonus_items: int = 0) -> void:
	name_text = p_name
	level = p_level
	equipment_bonus_items = p_bonus_items


func _to_string() -> String:
	return "Character(%s lv=%d xp=%d bonus_items=%d)" % [
		name_text, level, xp, equipment_bonus_items,
	]
