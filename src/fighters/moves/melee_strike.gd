class_name MeleeStrike
extends FighterMove
## Close-range hit, optionally with a lunge (a step in, a dash).

## x is relative to facing. A zero component leaves that velocity axis untouched.
@export var lunge := Vector2.ZERO


func trigger_effect(user: Fighter) -> void:
	user.apply_lunge(lunge)
	user.spawn_melee_volume(attack, attack.active)
