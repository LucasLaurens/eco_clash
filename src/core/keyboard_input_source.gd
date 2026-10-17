class_name KeyboardInputSource
extends InputSource

var _scheme: ControlScheme


func _init(scheme: ControlScheme) -> void:
	_scheme = scheme


func read_frame() -> InputFrame:
	var frame := InputFrame.new()
	frame.move_x = Input.get_axis(_scheme.action(ControlScheme.Action.LEFT), _scheme.action(ControlScheme.Action.RIGHT))
	frame.down = Input.is_action_pressed(_scheme.action(ControlScheme.Action.DOWN))
	frame.jump_pressed = Input.is_action_just_pressed(_scheme.action(ControlScheme.Action.UP))
	frame.attack_pressed = Input.is_action_just_pressed(_scheme.action(ControlScheme.Action.ATTACK))
	frame.special_pressed = Input.is_action_just_pressed(_scheme.action(ControlScheme.Action.SPECIAL))
	return frame
