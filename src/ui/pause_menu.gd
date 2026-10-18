class_name PauseMenu
extends CanvasLayer
## Escape toggles a pause overlay. Runs while the tree is paused (process_mode = ALWAYS).

const PAUSE_VEIL_ALPHA := 0.6

var _overlay: Control
var _resume_button: Button


func _ready() -> void:
	_overlay = Control.new()
	_overlay.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_overlay)
	_overlay.add_child(UiKit.create_veil(PAUSE_VEIL_ALPHA))
	var column := UiKit.create_centered_column(_overlay, 8)
	column.add_child(UiKit.create_label(UiText.PAUSE_TITLE, UiKit.FONT_LARGE, UiKit.TEXT_GOLD))
	_resume_button = UiKit.create_button(UiText.PAUSE_RESUME, _resume_game)
	column.add_child(_resume_button)
	column.add_child(UiKit.create_button(UiText.PAUSE_QUIT, _quit_to_menu))
	_overlay.hide()


func _unhandled_input(event: InputEvent) -> void:
	if not event.is_action_pressed(&"ui_cancel"):
		return
	get_viewport().set_input_as_handled()
	if _overlay.visible:
		_resume_game()
	else:
		_pause_game()


func _pause_game() -> void:
	get_tree().paused = true
	_overlay.show()
	_resume_button.grab_focus()


func _resume_game() -> void:
	get_tree().paused = false
	_overlay.hide()


func _quit_to_menu() -> void:
	get_tree().paused = false
	get_tree().change_scene_to_file(ScenePaths.MAIN_MENU)
