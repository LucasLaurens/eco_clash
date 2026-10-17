class_name PauseMenu
extends CanvasLayer
## Escape toggles a pause overlay. Runs while the tree is paused (process_mode = ALWAYS).

var _root: Control
var _resume: Button


func _ready() -> void:
	_root = Control.new()
	_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_root)
	var veil := ColorRect.new()
	veil.color = Color(0.03, 0.04, 0.1, 0.6)
	veil.set_anchors_preset(Control.PRESET_FULL_RECT)
	_root.add_child(veil)
	var column := UiKit.create_centered_column(_root, 8)
	column.add_child(UiKit.create_label(UiText.PAUSE_TITLE, UiKit.FONT_LARGE, UiKit.TEXT_GOLD))
	_resume = UiKit.create_button(UiText.PAUSE_RESUME, _close)
	column.add_child(_resume)
	column.add_child(UiKit.create_button(UiText.PAUSE_QUIT, _quit_to_menu))
	_root.hide()


func _unhandled_input(event: InputEvent) -> void:
	if not event.is_action_pressed(&"ui_cancel"):
		return
	get_viewport().set_input_as_handled()
	if _root.visible:
		_close()
	else:
		_open()


func _open() -> void:
	get_tree().paused = true
	_root.show()
	_resume.grab_focus()


func _close() -> void:
	get_tree().paused = false
	_root.hide()


func _quit_to_menu() -> void:
	get_tree().paused = false
	get_tree().change_scene_to_file(ScenePaths.MAIN_MENU)
