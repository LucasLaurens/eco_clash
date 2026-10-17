class_name FighterCard
extends PanelContainer
## HUD card of one fighter: portrait, name, damage percent (white to red), remaining stocks.

const PORTRAIT_SIZE := Vector2(32, 32)
const DANGER_PERCENT := 150.0
const WARM := Color(1.0, 0.72, 0.24)
const DANGER := Color(0.92, 0.18, 0.16)
const POP_SCALE := 1.35
const POP_TIME := 0.15

var _percent: Label
var _stocks_row: HBoxContainer
var _stock_icon: Texture2D


func bind(fighter: Fighter, definition: FighterDefinition, slot_label: String) -> void:
	_stock_icon = definition.stock_icon
	var row := HBoxContainer.new()
	row.add_theme_constant_override(&"separation", 4)
	add_child(row)
	var portrait := TextureRect.new()
	portrait.texture = definition.portrait
	portrait.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	portrait.custom_minimum_size = PORTRAIT_SIZE
	row.add_child(portrait)
	var column := VBoxContainer.new()
	column.add_theme_constant_override(&"separation", 0)
	row.add_child(column)
	var name_label := UiKit.create_label("%s · %s" % [slot_label, definition.display_name], UiKit.FONT_SMALL, definition.accent_color)
	name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	column.add_child(name_label)
	_percent = UiKit.create_label("", UiKit.FONT_MEDIUM)
	_percent.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	column.add_child(_percent)
	_stocks_row = HBoxContainer.new()
	_stocks_row.add_theme_constant_override(&"separation", 1)
	row.add_child(_stocks_row)
	fighter.damage_changed.connect(_on_damage_changed)
	fighter.stocks_changed.connect(_on_stocks_changed)
	_show_percent(fighter.damage_percent)
	_on_stocks_changed(fighter.stocks)


func _on_damage_changed(percent: float) -> void:
	_show_percent(percent)
	_percent.pivot_offset = _percent.size / 2.0
	_percent.scale = Vector2.ONE * POP_SCALE
	create_tween().tween_property(_percent, "scale", Vector2.ONE, POP_TIME)


func _show_percent(percent: float) -> void:
	_percent.text = UiText.PERCENT % roundi(percent)
	var heat := clampf(percent / DANGER_PERCENT, 0.0, 1.0)
	var color := Color.WHITE.lerp(WARM, heat * 2.0) if heat < 0.5 else WARM.lerp(DANGER, (heat - 0.5) * 2.0)
	_percent.add_theme_color_override(&"font_color", color)


func _on_stocks_changed(stocks: int) -> void:
	for child in _stocks_row.get_children():
		child.queue_free()
	for _stock in stocks:
		var icon := TextureRect.new()
		icon.texture = _stock_icon
		icon.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		_stocks_row.add_child(icon)
