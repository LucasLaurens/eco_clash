extends Node
## Autoload: registers every player action in the InputMap before any scene reads input, and again when a pad
## is plugged or unplugged, so a pad works mid-session without a restart.


func _enter_tree() -> void:
	ControlScheme.register_all_actions()
	Input.joy_connection_changed.connect(_refresh_bindings)


func _refresh_bindings(_device: int, _connected: bool) -> void:
	ControlScheme.register_all_actions()
