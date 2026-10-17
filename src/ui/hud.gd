class_name Hud
extends CanvasLayer
## In-fight overlay: one card per fighter, the countdown and the end banner.

const CARD_CENTERS_X := [150.0, 330.0]
const CARD_BOTTOM_MARGIN := 4.0
const COUNTDOWN_STEP := 0.6
const POP_SCALE := 2.0

var _banner: Label


func _ready() -> void:
	_banner = UiKit.create_label("", UiKit.FONT_HUGE, UiKit.TEXT_GOLD)
	_banner.set_anchors_preset(Control.PRESET_CENTER)
	_banner.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_banner.grow_vertical = Control.GROW_DIRECTION_BOTH
	add_child(_banner)


func bind_fighters(fighters: Array[Fighter], config: MatchConfig) -> void:
	for slot in fighters.size():
		var card := FighterCard.new()
		add_child(card)
		card.bind(fighters[slot], config.definitions[slot], config.compute_slot_label(slot))
		card.reset_size()
		card.position = Vector2(CARD_CENTERS_X[slot] - card.size.x / 2.0, _screen_size().y - card.size.y - CARD_BOTTOM_MARGIN)


func play_countdown() -> void:
	for step: String in UiText.COUNTDOWN_STEPS:
		_pop_banner(step)
		await get_tree().create_timer(COUNTDOWN_STEP).timeout
	_pop_banner(UiText.COUNTDOWN_GO)
	var fade := create_tween()
	fade.tween_interval(COUNTDOWN_STEP)
	fade.tween_property(_banner, "modulate:a", 0.0, COUNTDOWN_STEP)


func show_banner(text: String) -> void:
	_pop_banner(text)


func _pop_banner(text: String) -> void:
	_banner.text = text
	_banner.modulate.a = 1.0
	_banner.reset_size()
	_banner.position = (_screen_size() - _banner.size) / 2.0
	_banner.pivot_offset = _banner.size / 2.0
	_banner.scale = Vector2.ONE * POP_SCALE
	create_tween().tween_property(_banner, "scale", Vector2.ONE, 0.25).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


func _screen_size() -> Vector2:
	return get_viewport().get_visible_rect().size
