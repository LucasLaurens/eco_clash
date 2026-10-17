class_name FighterInfoPanel
extends PanelContainer
## Character-select side panel: animated preview, name, stat pips, special move, ready state.

const PREVIEW_SIZE := Vector2(48, 48)
const PIP_SIZE := Vector2(8, 5)
const PIP_OFF := Color(0.16, 0.22, 0.32)
const READY_COLOR := Color(0.5, 1.0, 0.55)

var _slot_label: Label
var _name_label: Label
var _title_label: Label
var _preview: AnimatedSprite2D
var _pip_rows: Array[HBoxContainer] = []
var _special_label: Label
var _description_label: Label
var _slot_text := ""


func _init() -> void:
	custom_minimum_size = Vector2(212, 0)
	var column := VBoxContainer.new()
	column.add_theme_constant_override(&"separation", 2)
	add_child(column)
	column.add_child(_build_header())
	for stat_name: String in [UiText.STAT_SPEED, UiText.STAT_POWER, UiText.STAT_WEIGHT]:
		column.add_child(_build_stat_row(stat_name))
	_special_label = UiKit.create_label("", UiKit.FONT_SMALL, UiKit.TEXT_GOLD)
	_special_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	column.add_child(_special_label)
	_description_label = UiKit.create_label("", UiKit.FONT_SMALL, UiKit.TEXT_MUTED)
	_description_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	_description_label.autowrap_mode = TextServer.AUTOWRAP_WORD
	_description_label.custom_minimum_size = Vector2(200, 26)
	column.add_child(_description_label)


func show_definition(definition: FighterDefinition) -> void:
	_name_label.text = definition.display_name
	_name_label.add_theme_color_override(&"font_color", definition.accent_color)
	_title_label.text = definition.title
	_preview.sprite_frames = FighterSpriteFrames.create(definition.sprite_sheet)
	_preview.play(&"idle")
	var ratings := [definition.compute_speed_rating(), definition.compute_power_rating(), definition.compute_weight_rating()]
	for row_index in _pip_rows.size():
		_paint_pips(_pip_rows[row_index], ratings[row_index], definition.accent_color)
	_special_label.text = UiText.SPECIAL_PREFIX % definition.compute_special_name()
	_description_label.text = definition.compute_special_description()


func show_slot(label: String) -> void:
	_slot_text = label


## Slot and status share one line: "JOUEUR 1 · PRÊT !".
func show_status(text: String, is_ready: bool) -> void:
	_slot_label.text = "%s · %s" % [_slot_text, text]
	_slot_label.add_theme_color_override(&"font_color", READY_COLOR if is_ready else UiKit.TEXT_MUTED)


func _build_header() -> HBoxContainer:
	var header := HBoxContainer.new()
	var preview_box := Control.new()
	preview_box.custom_minimum_size = PREVIEW_SIZE
	_preview = AnimatedSprite2D.new()
	_preview.position = PREVIEW_SIZE / 2.0
	preview_box.add_child(_preview)
	header.add_child(preview_box)
	var names := VBoxContainer.new()
	names.alignment = BoxContainer.ALIGNMENT_CENTER
	names.add_theme_constant_override(&"separation", 0)
	_slot_label = _create_left_label(UiKit.FONT_SMALL, UiKit.TEXT_MUTED)
	_name_label = _create_left_label(UiKit.FONT_MEDIUM, UiKit.TEXT_LIGHT)
	_title_label = _create_left_label(UiKit.FONT_SMALL, UiKit.TEXT_GOLD)
	for label in [_slot_label, _name_label, _title_label]:
		names.add_child(label)
	header.add_child(names)
	return header


func _build_stat_row(stat_name: String) -> HBoxContainer:
	var row := HBoxContainer.new()
	var label := _create_left_label(UiKit.FONT_SMALL, UiKit.TEXT_LIGHT)
	label.text = stat_name
	label.custom_minimum_size = Vector2(70, 0)
	row.add_child(label)
	var pips := HBoxContainer.new()
	pips.alignment = BoxContainer.ALIGNMENT_CENTER
	pips.add_theme_constant_override(&"separation", 2)
	for _pip in FighterDefinition.MAX_RATING:
		var pip := ColorRect.new()
		pip.custom_minimum_size = PIP_SIZE
		pip.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		pips.add_child(pip)
	row.add_child(pips)
	_pip_rows.append(pips)
	return row


func _paint_pips(row: HBoxContainer, rating: int, color: Color) -> void:
	for index in row.get_child_count():
		(row.get_child(index) as ColorRect).color = color if index < rating else PIP_OFF


func _create_left_label(size: int, color: Color) -> Label:
	var label := UiKit.create_label("", size, color)
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	return label
