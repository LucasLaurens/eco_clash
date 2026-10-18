extends Control
## Roster screen. VERSUS: each player moves his own cursor. VS_BOT: player 1 picks himself, then the bot.

const CARD_SIZE := 48
const CARD_GAP := 12
const ROW_Y := 28.0
## Right under the selector tags: the panels need every pixel for the 64px preview.
const PANEL_Y := 90.0
const SELECTOR_INSET := 2.0
const SELECTOR_SHARED_OFFSET := Vector2(3, 3)
const START_DELAY := 0.7
const SELECTORS := {
	"p1": preload("res://assets/ui/selector_p1.png"),
	"p2": preload("res://assets/ui/selector_p2.png"),
	"bot": preload("res://assets/ui/selector_bot.png"),
}

var _mode: MatchConfig.Mode
var _slot_rules: MatchConfig
var _cursors: Array[SelectionCursor] = []
var _schemes: Array[ControlScheme] = []
var _selectors: Array[TextureRect] = []
var _info_panels: Array[FighterInfoPanel] = []
var _card_origins: Array[Vector2] = []
var _is_starting_match := false


func _ready() -> void:
	_mode = MatchSettings.pending_mode
	# Same rules as the coming match: bot slots and keyboard layouts are decided in one place.
	_slot_rules = MatchConfig.create(_mode, FighterRoster.find_at(0), FighterRoster.find_at(0))
	UiKit.add_backdrop(self, 0.6)
	var title := UiKit.create_label(UiText.SELECT_TITLE, UiKit.FONT_MEDIUM, UiKit.TEXT_GOLD)
	title.set_anchors_preset(Control.PRESET_TOP_WIDE)
	title.offset_top = 4
	add_child(title)
	_build_cards()
	for slot in MatchConfig.SLOT_COUNT:
		_cursors.append(SelectionCursor.new(FighterRoster.count(), slot * (FighterRoster.count() - 1)))
		_schemes.append(ControlScheme.new(_slot_rules.compute_scheme_number(slot)))
		_selectors.append(_build_selector(slot))
		_info_panels.append(_build_info_panel(slot))
	_add_controls_hint()
	_refresh_display()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"ui_cancel"):
		get_tree().change_scene_to_file(ScenePaths.MAIN_MENU)
		return
	for slot in MatchConfig.SLOT_COUNT:
		if _is_slot_active(slot) and _apply_slot_input(slot, event):
			get_viewport().set_input_as_handled()
			_refresh_display()
			return


func _is_slot_active(slot: int) -> bool:
	if _mode == MatchConfig.Mode.VERSUS:
		return true
	return _cursors[0].confirmed == (slot == 1)


## Returns true when the event was consumed, so one key press never drives two cursors.
func _apply_slot_input(slot: int, event: InputEvent) -> bool:
	var scheme := _schemes[slot]
	var cursor := _cursors[slot]
	if event.is_action_pressed(scheme.resolve_action_name(ControlScheme.Action.LEFT)):
		cursor.move_by(-1)
	elif event.is_action_pressed(scheme.resolve_action_name(ControlScheme.Action.RIGHT)):
		cursor.move_by(1)
	elif event.is_action_pressed(scheme.resolve_action_name(ControlScheme.Action.ATTACK)):
		cursor.confirm()
		_try_start_match()
	elif event.is_action_pressed(scheme.resolve_action_name(ControlScheme.Action.SPECIAL)):
		_step_back(slot)
	else:
		return false
	return true


func _step_back(slot: int) -> void:
	if _cursors[slot].confirmed:
		_cursors[slot].cancel()
	elif _mode == MatchConfig.Mode.VS_BOT and slot == 1:
		_cursors[0].cancel()
	elif _mode == MatchConfig.Mode.VS_BOT:
		get_tree().change_scene_to_file(ScenePaths.MAIN_MENU)


func _try_start_match() -> void:
	if _is_starting_match or not _cursors.all(func(cursor: SelectionCursor) -> bool: return cursor.confirmed):
		return
	_is_starting_match = true
	await get_tree().create_timer(START_DELAY).timeout
	_is_starting_match = false
	if not _cursors.all(func(cursor: SelectionCursor) -> bool: return cursor.confirmed):
		return
	MatchSettings.current_config = MatchConfig.create(
		_mode, FighterRoster.find_at(_cursors[0].index), FighterRoster.find_at(_cursors[1].index)
	)
	get_tree().change_scene_to_file(ScenePaths.FIGHT)


func _refresh_display() -> void:
	for slot in MatchConfig.SLOT_COUNT:
		var cursor := _cursors[slot]
		var is_shared_card := slot == 1 and cursor.index == _cursors[0].index
		_selectors[slot].position = _card_origins[cursor.index] - Vector2.ONE * SELECTOR_INSET
		_selectors[slot].position += SELECTOR_SHARED_OFFSET if is_shared_card else Vector2.ZERO
		_selectors[slot].visible = _is_slot_active(slot) or cursor.confirmed
		_info_panels[slot].show_definition(FighterRoster.find_at(cursor.index))
		_info_panels[slot].show_status(_compute_status_text(slot), cursor.confirmed)


func _compute_status_text(slot: int) -> String:
	if _cursors[slot].confirmed:
		return UiText.SELECT_READY
	if _is_slot_active(slot):
		return UiText.SELECT_CHOOSING
	return UiText.SELECT_BOT_TURN if _slot_rules.is_bot_slot(slot) else UiText.SELECT_WAITING


func _build_cards() -> void:
	var count := FighterRoster.count()
	var row_width := count * CARD_SIZE + (count - 1) * CARD_GAP
	var row_left_x := (get_viewport_rect().size.x - row_width) / 2.0
	for index in count:
		var card := TextureRect.new()
		card.texture = FighterRoster.find_at(index).portrait
		card.position = Vector2(row_left_x + index * (CARD_SIZE + CARD_GAP), ROW_Y)
		add_child(card)
		_card_origins.append(card.position)


func _build_selector(slot: int) -> TextureRect:
	var selector := TextureRect.new()
	selector.texture = SELECTORS[_slot_rules.resolve_slot_tag(slot)]
	add_child(selector)
	return selector


func _build_info_panel(slot: int) -> FighterInfoPanel:
	var panel := FighterInfoPanel.new()
	panel.position = Vector2(16.0 + slot * 236.0, PANEL_Y)
	panel.set_slot_text(_slot_rules.format_slot_label(slot))
	add_child(panel)
	return panel


func _add_controls_hint() -> void:
	var scheme := _schemes[0]
	var hint_text := (
		UiText.SELECT_HINT
		% [
			scheme.format_key_label(ControlScheme.Action.LEFT),
			scheme.format_key_label(ControlScheme.Action.RIGHT),
			scheme.format_key_label(ControlScheme.Action.ATTACK),
			scheme.format_key_label(ControlScheme.Action.SPECIAL),
		]
	)
	if _mode == MatchConfig.Mode.VERSUS:
		var second_scheme := _schemes[1]
		hint_text += (
			"   ·   %s%s %s %s"
			% [
				second_scheme.format_key_label(ControlScheme.Action.LEFT),
				second_scheme.format_key_label(ControlScheme.Action.RIGHT),
				second_scheme.format_key_label(ControlScheme.Action.ATTACK),
				second_scheme.format_key_label(ControlScheme.Action.SPECIAL),
			]
		)
	var label := UiKit.create_label(hint_text, UiKit.FONT_SMALL, UiKit.TEXT_MUTED)
	label.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	label.grow_vertical = Control.GROW_DIRECTION_BEGIN
	label.offset_bottom = -4
	add_child(label)
