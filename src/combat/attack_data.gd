class_name AttackData
extends Resource
## Numbers of one hit: damage, launch, lingering conditions and timeline (startup -> active -> recovery).

enum Phase { STARTUP, ACTIVE, RECOVERY }

@export var damage := 6.0
@export var base_knockback := 110.0
@export var knockback_growth := 3.0
## 0 = straight forward, 90 = straight up.
@export_range(-90.0, 90.0) var launch_angle_deg := 35.0
@export var hitbox_offset := Vector2(14, -16)
@export var hitbox_size := Vector2(18, 14)
@export var startup := 0.08
@export var active := 0.1
@export var recovery := 0.16
## Extra damage dealt in ticks after the hit, spread over poison_duration seconds.
@export var poison_damage := 0.0
@export var poison_duration := 0.0
## Seconds the target cannot act, even once the knockback is over. The next hit ends it.
@export var paralysis := 0.0


func compute_total_duration() -> float:
	return startup + active + recovery


func compute_total_damage() -> float:
	return damage + poison_damage


func compute_phase(elapsed: float) -> Phase:
	if elapsed < startup:
		return Phase.STARTUP
	if elapsed < startup + active:
		return Phase.ACTIVE
	return Phase.RECOVERY
