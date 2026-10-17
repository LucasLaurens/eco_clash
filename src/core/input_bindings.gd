extends Node
## Autoload: registers every player action in the InputMap before any scene reads input.


func _enter_tree() -> void:
	ControlScheme.register_all_actions()
