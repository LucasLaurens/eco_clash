class_name HitVolume
extends Node2D
## A live, damaging rectangle: a melee swing (child of its fighter) or a projectile (child of the world).
## Strikes each target at most once.

const GROUP := &"hit_volumes"

var attack: AttackData
var attacker: Fighter
var velocity := Vector2.ZERO

var _lifetime_left := 0.0
var _vanishes_on_strike := false
var _struck_targets: Dictionary[Fighter, bool] = {}


static func create(attack_data: AttackData, attacker_fighter: Fighter, lifetime: float) -> HitVolume:
	var volume := HitVolume.new()
	volume.attack = attack_data
	volume.attacker = attacker_fighter
	volume._lifetime_left = lifetime
	volume.add_to_group(GROUP)
	return volume


func convert_to_projectile(projectile_velocity: Vector2, frames: SpriteFrames) -> void:
	velocity = projectile_velocity
	_vanishes_on_strike = true
	var sprite := AnimatedSprite2D.new()
	sprite.sprite_frames = frames
	sprite.flip_h = projectile_velocity.x < 0.0
	add_child(sprite)
	sprite.play()


func _physics_process(delta: float) -> void:
	position += velocity * delta
	_lifetime_left -= delta
	if _lifetime_left <= 0.0:
		queue_free()


func compute_hit_rect() -> Rect2:
	return Rect2(global_position - attack.hitbox_size / 2.0, attack.hitbox_size)


func can_strike(target: Fighter) -> bool:
	return target != attacker and not _struck_targets.has(target) and not is_queued_for_deletion()


## Melee pushes away from the attacker's body; projectiles push along their flight.
func compute_direction_to(target: Fighter) -> int:
	if not velocity.is_zero_approx():
		return 1 if velocity.x > 0.0 else -1
	var horizontal_offset := target.global_position.x - attacker.global_position.x
	if is_zero_approx(horizontal_offset):
		return attacker.facing
	return 1 if horizontal_offset > 0.0 else -1


func register_strike(target: Fighter) -> void:
	_struck_targets[target] = true
	if _vanishes_on_strike:
		queue_free()
