class_name MeleeStrike
extends FighterMove
## Close-range hit, optionally with a lunge (uppercut, dash, ground slam).

## x is relative to facing. A zero component leaves that velocity axis untouched.
@export var lunge := Vector2.ZERO


func release(user: Fighter) -> void:
	user.apply_lunge(lunge)
	user.spawn_melee_volume(attack)
