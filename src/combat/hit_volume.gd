class_name HitVolume
extends Node2D
## A live, damaging rectangle: a melee swing (child of its fighter) or a projectile (child of the world).
## Strikes each target at most once.

const GROUP := &"hit_volumes"

var attack: AttackData
var source: Fighter
var velocity := Vector2.ZERO

var _lifetime_left := 0.0
var _vanishes_on_strike := false
var _struck: Dictionary[Fighter, bool] = {}


static func create(hit: AttackData, owner_fighter: Fighter, lifetime: float) -> HitVolume:
	var volume := HitVolume.new()
	volume.attack = hit
	volume.source = owner_fighter
	volume._lifetime_left = lifetime
	volume.add_to_group(GROUP)
	return volume


func make_projectile(projectile_velocity: Vector2, frames: SpriteFrames) -> void:
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


func compute_rect() -> Rect2:
	return Rect2(global_position - attack.hitbox_size / 2.0, attack.hitbox_size)


func can_strike(target: Fighter) -> bool:
	return target != source and not _struck.has(target) and not is_queued_for_deletion()


## Melee pushes away from the attacker's body; projectiles push along their flight.
func compute_direction_to(target: Fighter) -> int:
	if not velocity.is_zero_approx():
		return 1 if velocity.x > 0.0 else -1
	var dx := target.global_position.x - source.global_position.x
	if is_zero_approx(dx):
		return source.facing
	return 1 if dx > 0.0 else -1


func register_strike(target: Fighter) -> void:
	_struck[target] = true
	if _vanishes_on_strike:
		queue_free()
