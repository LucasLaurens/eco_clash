class_name DarkSurge
extends FighterMove
## The fighter turns dark: its next light attack, thrown within the window, is replaced by a stronger strike.

@export var empowered_strike: FighterMove
@export var window := 4.0


func trigger_effect(user: Fighter) -> void:
	user.empower(empowered_strike, window)


func compute_rated_damage() -> float:
	return empowered_strike.compute_rated_damage()
