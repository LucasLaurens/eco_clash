class_name FighterCard
extends PanelContainer
## HUD card of one fighter: head icon, "1P · KAEL", damage percent (white to red), one pip per stock,
## and a thin special gauge that refills during the cooldown.
## Kept small and frameless: the arena is the show, the card only answers "how hurt, how many lives, special ready?".

const DANGER_PERCENT := 150.0
const WARM_COLOR := Color(1.0, 0.72, 0.24)
const DANGER_COLOR := Color(0.92, 0.18, 0.16)
const POP_SCALE := 1.35
const POP_TIME := 0.15
const CARD_VEIL_ALPHA := 0.55
const CARD_PADDING := 3
const STOCK_PIP_SIZE := Vector2(4, 4)
const SPECIAL_GAUGE_SIZE := Vector2(30, 2)
const SPECIAL_CHARGING_ALPHA := 0.35

var _fighter: Fighter
var _special_fill: ColorRect

var _percent_label: Label
var _stock_pips: HBoxContainer
var _accent_color: Color


func bind_fighter(fighter: Fighter, definition: FighterDefinition, slot_label: String) -> void:
	_accent_color = definition.accent_color
	add_theme_stylebox_override(&"panel", UiKit.create_veil_style(CARD_VEIL_ALPHA, CARD_PADDING))
	var row := HBoxContainer.new()
	row.add_theme_constant_override(&"separation", 4)
	add_child(row)
	var head := TextureRect.new()
	head.texture = definition.stock_icon
	head.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(head)
	var column := VBoxContainer.new()
	column.add_theme_constant_override(&"separation", 0)
	row.add_child(column)
	var header := HBoxContainer.new()
	header.add_theme_constant_override(&"separation", 4)
	column.add_child(header)
	var name_label := UiKit.create_label(
		"%s · %s" % [slot_label, definition.display_name], UiKit.FONT_SMALL, _accent_color
	)
	name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	header.add_child(name_label)
	_stock_pips = HBoxContainer.new()
	_stock_pips.add_theme_constant_override(&"separation", 2)
	_stock_pips.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	header.add_child(_stock_pips)
	_percent_label = UiKit.create_label("", UiKit.FONT_MEDIUM)
	_percent_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	column.add_child(_percent_label)
	column.add_child(_create_special_gauge())
	_fighter = fighter
	fighter.damage_changed.connect(_on_damage_changed)
	fighter.stocks_changed.connect(_on_stocks_changed)
	_show_percent(fighter.damage_percent)
	_on_stocks_changed(fighter.stocks)


func _process(_delta: float) -> void:
	var readiness := _fighter.compute_special_readiness()
	_special_fill.size.x = SPECIAL_GAUGE_SIZE.x * readiness
	_special_fill.modulate.a = 1.0 if readiness >= 1.0 else SPECIAL_CHARGING_ALPHA


func _create_special_gauge() -> Control:
	var gauge := ColorRect.new()
	gauge.color = Color(UiKit.TEXT_MUTED, SPECIAL_CHARGING_ALPHA)
	gauge.custom_minimum_size = SPECIAL_GAUGE_SIZE
	gauge.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	_special_fill = ColorRect.new()
	_special_fill.color = _accent_color
	_special_fill.size = SPECIAL_GAUGE_SIZE
	gauge.add_child(_special_fill)
	return gauge


func _on_damage_changed(percent: float) -> void:
	_show_percent(percent)
	_percent_label.pivot_offset = _percent_label.size / 2.0
	_percent_label.scale = Vector2.ONE * POP_SCALE
	create_tween().tween_property(_percent_label, "scale", Vector2.ONE, POP_TIME)


func _show_percent(percent: float) -> void:
	_percent_label.text = UiText.PERCENT % roundi(percent)
	var danger_ratio := clampf(percent / DANGER_PERCENT, 0.0, 1.0)
	var color := (
		Color.WHITE.lerp(WARM_COLOR, danger_ratio * 2.0)
		if danger_ratio < 0.5
		else WARM_COLOR.lerp(DANGER_COLOR, (danger_ratio - 0.5) * 2.0)
	)
	_percent_label.add_theme_color_override(&"font_color", color)


func _on_stocks_changed(stocks: int) -> void:
	for child in _stock_pips.get_children():
		child.queue_free()
	for _stock in stocks:
		var pip := ColorRect.new()
		pip.color = _accent_color
		pip.custom_minimum_size = STOCK_PIP_SIZE
		_stock_pips.add_child(pip)
