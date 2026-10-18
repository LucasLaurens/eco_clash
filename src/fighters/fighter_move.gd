@abstract class_name FighterMove
extends Resource
## Strategy for one button: what happens when the move's active window opens.
## The fighter runs the timeline; the move only decides the effect (Open/Closed).

@export var display_name := ""
@export_multiline var description := ""
@export var animation: StringName = &"attack"
@export var attack: AttackData
## Seconds before the special can be used again, counted from the moment it is launched.
@export var cooldown := 0.0

@abstract func trigger_effect(user: Fighter) -> void


## What the move adds to the power gauge of the selection screen.
func compute_rated_damage() -> float:
	return attack.compute_total_damage()
