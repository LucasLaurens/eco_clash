class_name Mend
extends FighterMove
## Heals a share of the damage taken, capped. A long startup leaves the healer open to a hit that cancels it.

@export_range(0.0, 1.0) var heal_ratio := 0.3
@export var max_heal := 20.0


func trigger_effect(user: Fighter) -> void:
	user.heal(heal_ratio, max_heal)


func compute_rated_damage() -> float:
	return 0.0
