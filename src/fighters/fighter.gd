class_name Fighter
extends CharacterBody2D
## A playable character. It reads intent from an InputSource and never knows
## whether a human or a bot is behind it.

signal damage_changed(percent: float)
signal stocks_changed(stocks: int)

enum State { FREE, ACTING, HITSTUN, OUT }

const PLATFORM_LAYER := 3
const GRAVITY := 980.0
const MAX_FALL_SPEED := 380.0
const FAST_FALL_SPEED := 560.0
const GROUND_ACCELERATION := 1500.0
const GROUND_FRICTION := 1700.0
const AIR_ACCELERATION := 950.0
const ACTING_FRICTION := 420.0
const HITSTUN_DRAG := 150.0
const AIR_JUMP_RATIO := 0.9
const DROP_THROUGH_DURATION := 0.25
const RESPAWN_INVULNERABILITY := 2.0
const BLINK_PERIOD := 0.08
const BLINK_ALPHA := 0.35
const RUN_ANIMATION_THRESHOLD := 12.0

var definition: FighterDefinition
var damage_percent := 0.0
var stocks := 0
var facing := 1

var _input_source: InputSource = NullInputSource.new()
var _world: Node2D
var _state := State.FREE
var _move: FighterMove
var _move_elapsed := 0.0
var _move_effect_triggered := false
var _hitstun_left := 0.0
var _air_jumps_left := 0
var _air_special_used := false
var _drop_through_left := 0.0
var _invulnerable_left := 0.0

@onready var _sprite: AnimatedSprite2D = $Sprite
@onready var _body_shape: CollisionShape2D = $BodyShape
@onready var _melee_volumes: Node2D = $Volumes


## Call right after add_child: the fighter is inert until it knows who it is.
func configure(fighter_definition: FighterDefinition, world: Node2D, starting_stocks: int) -> void:
	definition = fighter_definition
	_world = world
	stocks = starting_stocks
	_air_jumps_left = definition.air_jumps
	var shape := RectangleShape2D.new()
	shape.size = definition.body_size
	_body_shape.shape = shape
	_body_shape.position = Vector2(0.0, -definition.body_size.y / 2.0)
	_sprite.sprite_frames = FighterSpriteFrames.create(definition.sprite_sheet)
	_sprite.position = FighterSpriteFrames.compute_sprite_offset()
	_sprite.play(&"idle")


func attach_input(input_source: InputSource) -> void:
	_input_source = input_source


func _physics_process(delta: float) -> void:
	if _state == State.OUT:
		return
	var frame := _input_source.read_frame()
	_tick_timers(delta)
	match _state:
		State.FREE:
			_update_free_state(frame, delta)
		State.ACTING:
			_update_acting_state(delta)
		State.HITSTUN:
			_update_hitstun_state(delta)
	_apply_gravity(frame, delta)
	move_and_slide()
	if is_on_floor():
		_air_jumps_left = definition.air_jumps
		_air_special_used = false
	_update_visuals()


func receive_hit(attack: AttackData, direction: int) -> void:
	damage_percent += attack.damage
	var force := KnockbackFormula.compute_force(attack, damage_percent, definition.weight)
	velocity = KnockbackFormula.compute_launch_velocity(attack, direction, force)
	_hitstun_left = KnockbackFormula.compute_hitstun(force)
	_state = State.HITSTUN
	facing = -direction
	_clear_melee_volumes()
	damage_changed.emit(damage_percent)


func can_be_struck() -> bool:
	return _state != State.OUT and _invulnerable_left <= 0.0


func is_in_play() -> bool:
	return _state != State.OUT


func has_stocks_left() -> bool:
	return stocks > 0


func has_air_jump() -> bool:
	return _air_jumps_left > 0


func compute_hurt_rect() -> Rect2:
	var size := definition.body_size
	return Rect2(global_position - Vector2(size.x / 2.0, size.y), size)


func lose_stock() -> void:
	stocks -= 1
	stocks_changed.emit(stocks)
	if stocks <= 0:
		_remove_from_play()


func respawn_at(spawn_position: Vector2) -> void:
	global_position = spawn_position
	velocity = Vector2.ZERO
	damage_percent = 0.0
	_state = State.FREE
	_invulnerable_left = RESPAWN_INVULNERABILITY
	_clear_melee_volumes()
	damage_changed.emit(damage_percent)


func apply_lunge(lunge: Vector2) -> void:
	if not is_zero_approx(lunge.x):
		velocity.x = lunge.x * facing
	if not is_zero_approx(lunge.y):
		velocity.y = lunge.y


func spawn_melee_volume(attack: AttackData) -> void:
	var volume := HitVolume.create(attack, self, attack.active)
	volume.position = Vector2(attack.hitbox_offset.x * facing, attack.hitbox_offset.y)
	_melee_volumes.add_child(volume)


func launch_projectile(attack: AttackData, speed: float, lifetime: float, frames: SpriteFrames) -> void:
	var volume := HitVolume.create(attack, self, lifetime)
	volume.position = position + Vector2(attack.hitbox_offset.x * facing, attack.hitbox_offset.y)
	volume.convert_to_projectile(Vector2(speed * facing, 0.0), frames)
	_world.add_child(volume)


func _tick_timers(delta: float) -> void:
	_invulnerable_left = maxf(_invulnerable_left - delta, 0.0)
	if _drop_through_left <= 0.0:
		return
	_drop_through_left -= delta
	if _drop_through_left <= 0.0:
		set_collision_mask_value(PLATFORM_LAYER, true)


func _update_free_state(frame: InputFrame, delta: float) -> void:
	var is_grounded := is_on_floor()
	var acceleration := AIR_ACCELERATION
	if is_grounded:
		acceleration = GROUND_FRICTION if is_zero_approx(frame.move_x) else GROUND_ACCELERATION
	velocity.x = move_toward(velocity.x, frame.move_x * definition.run_speed, acceleration * delta)
	if not is_zero_approx(frame.move_x):
		facing = 1 if frame.move_x > 0.0 else -1
	if frame.jump_pressed and frame.down and is_grounded:
		_drop_through_platforms()
	elif frame.jump_pressed:
		_jump()
	if frame.attack_pressed:
		_start_move(definition.light_attack)
	elif frame.special_pressed and not _air_special_used:
		_air_special_used = not is_grounded
		_start_move(definition.special)


func _jump() -> void:
	if is_on_floor():
		velocity.y = -definition.jump_velocity
	elif _air_jumps_left > 0:
		_air_jumps_left -= 1
		velocity.y = -definition.jump_velocity * AIR_JUMP_RATIO


func _drop_through_platforms() -> void:
	set_collision_mask_value(PLATFORM_LAYER, false)
	_drop_through_left = DROP_THROUGH_DURATION


func _start_move(move: FighterMove) -> void:
	_move = move
	_move_elapsed = 0.0
	_move_effect_triggered = false
	_state = State.ACTING


func _update_acting_state(delta: float) -> void:
	_move_elapsed += delta
	velocity.x = move_toward(velocity.x, 0.0, ACTING_FRICTION * delta)
	var attack := _move.attack
	if not _move_effect_triggered and _move_elapsed >= attack.startup:
		_move_effect_triggered = true
		_move.trigger_effect(self)
	if _move_elapsed >= attack.compute_total_duration():
		_state = State.FREE


func _update_hitstun_state(delta: float) -> void:
	_hitstun_left -= delta
	velocity.x = move_toward(velocity.x, 0.0, HITSTUN_DRAG * delta)
	if _hitstun_left <= 0.0:
		_state = State.FREE


func _apply_gravity(frame: InputFrame, delta: float) -> void:
	var is_fast_falling := _state == State.FREE and frame.down and velocity.y > 0.0
	var fall_speed_cap := FAST_FALL_SPEED if is_fast_falling else MAX_FALL_SPEED
	# A spike can launch faster than terminal speed: gravity never slows it down.
	if velocity.y < fall_speed_cap:
		velocity.y = minf(velocity.y + GRAVITY * delta, fall_speed_cap)


func _remove_from_play() -> void:
	_state = State.OUT
	velocity = Vector2.ZERO
	_clear_melee_volumes()
	hide()


func _clear_melee_volumes() -> void:
	for volume in _melee_volumes.get_children():
		volume.queue_free()


func _update_visuals() -> void:
	_sprite.flip_h = facing < 0
	_sprite.modulate.a = BLINK_ALPHA if _is_blinking() else 1.0
	match _state:
		State.ACTING:
			_show_move_frame()
		State.HITSTUN:
			_sprite.play(&"hurt")
		_:
			_sprite.play(_select_motion_animation())


func _is_blinking() -> bool:
	return _invulnerable_left > 0.0 and fmod(_invulnerable_left, BLINK_PERIOD * 2.0) < BLINK_PERIOD


func _show_move_frame() -> void:
	if _sprite.animation != _move.animation:
		_sprite.animation = _move.animation
	_sprite.set_frame_and_progress(_move.attack.compute_phase(_move_elapsed), 0.0)


func _select_motion_animation() -> StringName:
	if not is_on_floor():
		return &"jump" if velocity.y < 0.0 else &"fall"
	return &"run" if absf(velocity.x) > RUN_ANIMATION_THRESHOLD else &"idle"
