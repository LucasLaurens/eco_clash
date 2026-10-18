class_name UiKit
extends RefCounted
## Small factory for the recurring widgets. The pixel font is drawn at integer multiples only.

const FONT_SMALL := 12
const FONT_MEDIUM := 24
const FONT_LARGE := 36
const FONT_HUGE := 48
const STAGE_SCENE := preload("res://scenes/stage.tscn")
const TEXT_LIGHT := Color(0.92, 0.96, 1.0)
const TEXT_MUTED := Color(0.62, 0.72, 0.84)
const TEXT_GOLD := Color(1.0, 0.86, 0.36)
## Night-blue veil laid over the arena so menu text reads; only its alpha varies per screen.
const VEIL_COLOR := Color(0.04, 0.05, 0.12)


static func create_label(text: String, size := FONT_SMALL, color := TEXT_LIGHT) -> Label:
	var label := Label.new()
	label.text = text
	label.add_theme_font_size_override(&"font_size", size)
	label.add_theme_color_override(&"font_color", color)
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return label


static func create_button(text: String, on_pressed: Callable) -> Button:
	var button := Button.new()
	button.text = text
	button.custom_minimum_size = Vector2(170, 0)
	button.pressed.connect(on_pressed)
	return button


## The arena itself, alive behind the menus (clouds, waterfall, sea), then a dark veil for readability.
## Platforms are hidden: floating slabs would cut through the logo, the buttons and the winner.
static func add_backdrop(parent: Control, veil_alpha: float) -> void:
	var stage := STAGE_SCENE.instantiate()
	stage.get_node("Platforms").hide()
	parent.add_child(stage)
	parent.add_child(create_veil(veil_alpha))


## Same veil as a panel background, for bands and cards that size to their content.
static func create_veil_style(alpha: float, padding: int) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = Color(VEIL_COLOR, alpha)
	style.set_content_margin_all(padding)
	return style


static func create_veil(alpha: float) -> ColorRect:
	var veil := ColorRect.new()
	veil.color = Color(VEIL_COLOR, alpha)
	veil.mouse_filter = Control.MOUSE_FILTER_IGNORE
	veil.set_anchors_preset(Control.PRESET_FULL_RECT)
	return veil


static func create_centered_column(parent: Control, separation: int) -> VBoxContainer:
	var center_container := CenterContainer.new()
	center_container.set_anchors_preset(Control.PRESET_FULL_RECT)
	center_container.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(center_container)
	var column := VBoxContainer.new()
	column.alignment = BoxContainer.ALIGNMENT_CENTER
	column.add_theme_constant_override(&"separation", separation)
	center_container.add_child(column)
	return column


## Pad buttons for a player who has a pad, keys otherwise.
static func format_controls(player_number: int, prefix: String) -> String:
	var scheme := ControlScheme.new(player_number)
	return (
		UiText.CONTROLS_LINE
		% [
			prefix,
			scheme.format_control_label(ControlScheme.Action.LEFT),
			scheme.format_control_label(ControlScheme.Action.UP),
			scheme.format_control_label(ControlScheme.Action.DOWN),
			scheme.format_control_label(ControlScheme.Action.RIGHT),
			scheme.format_control_label(ControlScheme.Action.ATTACK),
			scheme.format_control_label(ControlScheme.Action.SPECIAL),
		]
	)
