extends Control
## Title screen: logo over the live arena, three choices, controls reminder.

const LOGO := preload("res://assets/ui/logo.png")
const FOOTER_MARGIN := 6.0


func _ready() -> void:
	UiKit.add_backdrop(self, 0.35)
	var column := UiKit.create_centered_column(self, 6)
	var logo := TextureRect.new()
	logo.texture = LOGO
	logo.stretch_mode = TextureRect.STRETCH_KEEP_CENTERED
	column.add_child(logo)
	column.add_child(UiKit.create_label(UiText.MENU_TAGLINE, UiKit.FONT_SMALL, UiKit.TEXT_GOLD))
	column.add_child(Control.new())
	var vs_bot := UiKit.create_button(UiText.MENU_VS_BOT, _open_select.bind(MatchConfig.Mode.VS_BOT))
	column.add_child(vs_bot)
	column.add_child(UiKit.create_button(UiText.MENU_VERSUS, _open_select.bind(MatchConfig.Mode.VERSUS)))
	column.add_child(UiKit.create_button(UiText.MENU_QUIT, get_tree().quit))
	_add_footer()
	vs_bot.grab_focus()


func _add_footer() -> void:
	var footer := VBoxContainer.new()
	footer.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	footer.grow_vertical = Control.GROW_DIRECTION_BEGIN
	footer.offset_bottom = -FOOTER_MARGIN
	footer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	footer.add_child(UiKit.create_label(UiKit.format_controls(1, UiText.CONTROLS_P1), UiKit.FONT_SMALL, UiKit.TEXT_MUTED))
	footer.add_child(UiKit.create_label(UiKit.format_controls(2, UiText.CONTROLS_P2), UiKit.FONT_SMALL, UiKit.TEXT_MUTED))
	footer.add_child(UiKit.create_label(UiText.CONTROLS_EXTRA, UiKit.FONT_SMALL, UiKit.TEXT_MUTED))
	add_child(footer)


func _open_select(mode: MatchConfig.Mode) -> void:
	MatchSettings.pending_mode = mode
	get_tree().change_scene_to_file(ScenePaths.CHARACTER_SELECT)
