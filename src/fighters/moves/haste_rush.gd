class_name HasteRush
extends FighterMove
## The fighter runs faster for a while; its body carries a light hit that lands once.

@export var duration := 2.0
@export var speed_multiplier := 1.6


func trigger_effect(user: Fighter) -> void:
	user.hasten(duration, speed_multiplier)
	user.spawn_melee_volume(attack, duration)
