class_name KnockbackFormula
extends RefCounted
## Smash-like launch: the more damage a fighter holds, the further it flies. Pure functions.

const REFERENCE_WEIGHT := 100.0
const HITSTUN_PER_FORCE := 0.0018


static func compute_force(attack: AttackData, percent_after_hit: float, weight: float) -> float:
	return attack.base_knockback + attack.knockback_growth * percent_after_hit * REFERENCE_WEIGHT / weight


static func compute_launch_velocity(attack: AttackData, direction: int, force: float) -> Vector2:
	var angle := deg_to_rad(attack.launch_angle_deg)
	return Vector2(cos(angle) * direction, -sin(angle)) * force


static func compute_hitstun(force: float) -> float:
	return force * HITSTUN_PER_FORCE
