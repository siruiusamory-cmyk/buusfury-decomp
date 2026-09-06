extends MarginContainer
## The section-26 debug overlay. Redrawn on Clock.tick, reads only, never mutates
## simulation state.
##
## CONFIRMED vs TEMP is signalled on THREE simultaneous channels, so no single one
## carries the whole load:
##   1. Brightness - CONFIRMED bright (#F2F2F2), TEMP dim amber (#B8862B). A
##      BRIGHTNESS split, never red-vs-green.
##   2. Glyph - every TEMP line is prefixed [T], every confirmed line [C].
##      Legible in a screenshot, a grayscale capture, and a log paste.
##   3. Section - two headed blocks separated by a rule.
##
## The TEMP list is NOT hardcoded here: the config block iterates
## get_property_list() and asks config.is_temp(name), so a new guess can never be
## silently displayed as a fact.

const CONFIRMED_COLOR: String = "f2f2f2"
const TEMP_COLOR: String = "b8862b"
const HEAD_COLOR: String = "8fb8d8"

## Injected by scenes/test_room.gd.
@export var config: CombatConfig

var player: Player = null
## The room, injected by scenes/test_room.gd. Replaces the former single `wolf`
## reference: the overlay now reads whichever wolves are live rather than holding
## one node that F7/F8 or a death could leave stale.
var room: Node2D = null
var gizmos: Node2D = null

@onready var _live: RichTextLabel = $Panel/Rows/Live
@onready var _confirmed: RichTextLabel = $Panel/Rows/ConfirmedConfig
@onready var _temp: RichTextLabel = $Panel/Rows/TempConfig

var _last_damage_raw: int = 0
var _last_damage_displayed: int = 0
var _last_damage_crit: bool = false


func _ready() -> void:
	Clock.tick.connect(_on_tick)
	_render_config_sections()
	print("[DebugOverlay] ready F1 overlay F2 gizmos F3 switch-character F4 pause F5 step F6 force-debug-visuals F7 respawn-all F8 spawn-wolf")


## Moves this overlay's tick listener to the BACK of Clock.tick's connection list,
## so a wolf spawned after the overlay still ticks before presentation reads. See
## the tick-order note in scenes/test_room.gd. Read-only either way - re-seating
## cannot change what the simulation computes, only when the overlay samples it.
func reseat_tick_listener() -> void:
	Clock.tick.disconnect(_on_tick)
	Clock.tick.connect(_on_tick)


## Input is a presentation concern and lives in _unhandled_input, not in the
## simulation. The overlay is not a TickNode.
func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey) or not event.is_pressed() or event.is_echo():
		return
	var k: InputEventKey = event
	match k.keycode:
		KEY_F1:
			visible = not visible
			print("[DebugOverlay] overlay visible=%s" % visible)
		KEY_F2:
			if gizmos != null:
				gizmos.visible = not gizmos.visible
				print("[DebugOverlay] gizmos visible=%s" % gizmos.visible)
		KEY_F3:
			Party.active_index = (Party.active_index + 1) % Party.characters.size()
			print("[DebugOverlay] active_index=%d" % Party.active_index)
		KEY_F4:
			Clock.paused = not Clock.paused
			print("[DebugOverlay] clock paused=%s" % Clock.paused)
		KEY_F5:
			if Clock.paused:
				Clock.step(1)
		KEY_F6:
			# The player suppresses its own facing wedge and swing glyphs once a
			# real sprite is showing, because the two never agree: what is drawn is
			# the SIMULATION's reach, and the P-003 melee box is asymmetric
			# (x0-4, x1+3, y0+0, y1-6), so no sprite will ever line up with it
			# exactly. F6 forces the glyphs back on - it is how to see what the sim
			# believes when the art disagrees.
			if player != null:
				player.debug_visuals_forced = not player.debug_visuals_forced
				player.queue_redraw()
				print("[DebugOverlay] forced debug visuals=%s" % player.debug_visuals_forced)
		KEY_F7:
			# Playtest tooling: put every wolf back to full HP at its own start
			# position so the same approach can be watched again. Alive wolves are
			# reset too - the point is a repeatable observation, not a revive.
			if room != null:
				room.respawn_all()
				print("[DebugOverlay] respawned all wolves live=%d" % room.live_wolf_count())
		KEY_F8:
			# Playtest tooling: one more wolf, at a fixed deterministic offset so
			# bodies never stack. No randomness in placement.
			if room != null:
				var w: Wolf = room.spawn_wolf()
				print("[DebugOverlay] spawned wolf at start_px=%s live=%d" % [
					w.start_px, room.live_wolf_count(),
				])


func _on_tick(t: int) -> void:
	if not visible:
		return
	_pull_last_damage()
	_live.text = _live_text(t)


func _pull_last_damage() -> void:
	var recs: Array[Dictionary] = EventLog.records_of(EventLog.KIND_DAMAGE_APPLIED)
	if recs.is_empty():
		return
	var d: Dictionary = recs[recs.size() - 1]["data"]
	_last_damage_raw = d["raw"]
	_last_damage_displayed = d["displayed"]
	_last_damage_crit = d["crit"]


func _live_text(t: int) -> String:
	var ch: Character = Party.active_character()
	var lines: PackedStringArray = PackedStringArray()
	lines.append(_head("LIVE  [C] confirmed   [T] temp"))
	lines.append(_c("tick %d  clock %s" % [t, "PAUSED" if Clock.paused else "running"]))

	if player != null:
		var px: Vector2i = FixedPoint.raw_to_px_v(player.pos_raw)
		lines.append(_c("player pos_raw %s  px %s" % [player.pos_raw, px]))
		var since: int = player.ticks_since_accept(t)
		lines.append(_c("attack gate %s  since_accept %d / %d  variant %d" % [
			"OPEN" if player.gate_open(t) else "closed", since,
			config.attack_accept_interval_ticks, player.attack_variant(),
		]))
		lines.append(_t("wall clamp firing: %s" % player.was_clamped()))

	# Per-wolf detail for ALL of them, not just wolf #1: the whole point of F8 is
	# comparing how several react at once, which one tracked wolf cannot show. The
	# four lines the single-wolf overlay printed are compressed to one line each so
	# the block stays readable at four or five wolves.
	if room != null:
		var wolves: Array = room.wolves
		lines.append(_c("wolves %d live  (acquire <= %d, attack <= %d)" % [
			room.live_wolf_count(), config.wolf_acquire_dist_sq, config.wolf_attack_dist_sq,
		]))
		for i: int in wolves.size():
			var w: Wolf = wolves[i]
			if not is_instance_valid(w):
				continue
			lines.append(_c("  #%d %s  dist_sq %d  ticks_left %d  acq %s  hp %d  dmg_tick %d" % [
				i, WolfState.name_of(w.state), w.dist_sq(), w.ticks_remaining(t),
				w.is_acquired(), Damage.to_displayed_hp(w.combatant.hp_raw, config),
				w.damage_tick(),
			]))

	lines.append(_c("last damage raw %d  displayed %d  crit %s" % [
		_last_damage_raw, _last_damage_displayed, _last_damage_crit,
	]))
	if ch != null:
		lines.append(_c("active char %d (%s)  xp %d  level %d  pending rewards %d" % [
			Party.active_index, ch.name_text, ch.xp, ch.level, Party.pending_reward_count(),
		]))
	return "\n".join(lines)


## Both config sections are built ONCE from get_property_list(); their values do
## not change at runtime and re-rendering them per tick would be pure waste.
func _render_config_sections() -> void:
	var conf: PackedStringArray = PackedStringArray()
	var temp: PackedStringArray = PackedStringArray()
	conf.append(_head("CONFIRMED"))
	temp.append(_head("TEMP - NOT REFERENCE ACCURATE"))

	for p: Dictionary in config.get_property_list():
		var n: String = p["name"]
		if int(p["usage"]) & PROPERTY_USAGE_SCRIPT_VARIABLE == 0:
			continue
		if n.begins_with("_"):
			continue
		var line: String = "%s = %s" % [n, config.get(n)]
		if config.is_temp(n):
			temp.append(_t(line))
		else:
			conf.append(_c(line))

	_confirmed.text = "\n".join(conf)
	_temp.text = "\n".join(temp)


func _head(s: String) -> String:
	return "[color=#%s][b]%s[/b][/color]" % [HEAD_COLOR, s]


## CONFIRMED: bright, glyph [C].
func _c(s: String) -> String:
	return "[color=#%s][C] %s[/color]" % [CONFIRMED_COLOR, s]


## TEMP: dim amber, glyph [T]. Brightness split, never red-vs-green.
func _t(s: String) -> String:
	return "[color=#%s][T] %s[/color]" % [TEMP_COLOR, s]
