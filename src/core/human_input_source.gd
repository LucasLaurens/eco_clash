class_name HumanInputSource
extends InputSource
## A human player: keyboard and pad both feed the actions of his ControlScheme, so this source reads only actions.

var _scheme: ControlScheme


func _init(scheme: ControlScheme) -> void:
	_scheme = scheme


func read_frame() -> InputFrame:
	var frame := InputFrame.new()
	frame.move_x = Input.get_axis(
		_scheme.resolve_action_name(ControlScheme.Action.LEFT), _scheme.resolve_action_name(ControlScheme.Action.RIGHT)
	)
	frame.down = Input.is_action_pressed(_scheme.resolve_action_name(ControlScheme.Action.DOWN))
	frame.jump_pressed = Input.is_action_just_pressed(_scheme.resolve_action_name(ControlScheme.Action.UP))
	frame.attack_pressed = Input.is_action_just_pressed(_scheme.resolve_action_name(ControlScheme.Action.ATTACK))
	frame.special_pressed = Input.is_action_just_pressed(_scheme.resolve_action_name(ControlScheme.Action.SPECIAL))
	return frame
