extends Control
## Title screen: logo over the live arena, three choices, controls reminder.

const LOGO := preload("res://assets/ui/logo.png")
const FOOTER_PADDING := 4
const FOOTER_VEIL_ALPHA := 0.7


func _ready() -> void:
	UiKit.add_backdrop(self, 0.35)
	var column := UiKit.create_centered_column(self, 6)
	var logo := TextureRect.new()
	logo.texture = LOGO
	logo.stretch_mode = TextureRect.STRETCH_KEEP_CENTERED
	column.add_child(logo)
	column.add_child(UiKit.create_label(UiText.MENU_TAGLINE, UiKit.FONT_SMALL, UiKit.TEXT_GOLD))
	column.add_child(Control.new())
	var vs_bot_button := UiKit.create_button(UiText.MENU_VS_BOT, _open_character_select.bind(MatchConfig.Mode.VS_BOT))
	column.add_child(vs_bot_button)
	column.add_child(UiKit.create_button(UiText.MENU_VERSUS, _open_character_select.bind(MatchConfig.Mode.VERSUS)))
	column.add_child(UiKit.create_button(UiText.MENU_QUIT, get_tree().quit))
	_add_footer()
	vs_bot_button.grab_focus()


## A dark band lifts the controls off the island: two player lines first, the shared tip quieter below.
func _add_footer() -> void:
	var band := PanelContainer.new()
	band.add_theme_stylebox_override(&"panel", UiKit.create_veil_style(FOOTER_VEIL_ALPHA, FOOTER_PADDING))
	band.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	band.grow_vertical = Control.GROW_DIRECTION_BEGIN
	band.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var lines := VBoxContainer.new()
	lines.add_theme_constant_override(&"separation", 0)
	band.add_child(lines)
	lines.add_child(
		UiKit.create_label(UiKit.format_controls(1, UiText.CONTROLS_P1), UiKit.FONT_SMALL, UiKit.TEXT_LIGHT)
	)
	lines.add_child(
		UiKit.create_label(UiKit.format_controls(2, UiText.CONTROLS_P2), UiKit.FONT_SMALL, UiKit.TEXT_LIGHT)
	)
	lines.add_child(UiKit.create_label(UiText.CONTROLS_EXTRA, UiKit.FONT_SMALL, UiKit.TEXT_MUTED))
	add_child(band)


func _open_character_select(mode: MatchConfig.Mode) -> void:
	MatchSettings.pending_mode = mode
	get_tree().change_scene_to_file(ScenePaths.CHARACTER_SELECT)
