class_name BotBrain
extends RefCounted
## Decides one InputFrame from a BotPerception: recover first, then chase and hit.

const ATTACK_RANGE := 36.0
const VERTICAL_REACH := 32.0
const CHASE_STOP_RATIO := 0.7
const FACE_NUDGE := 0.1
const JUMP_CHASE_RANGE := 70.0
const SPECIAL_MIN_RANGE := 40.0
const SPECIAL_MAX_RANGE := 140.0
const EDGE_MARGIN := 14.0
const OFF_STAGE_DEPTH := 8.0
const PLATFORM_CLEARANCE := 4.0
const FALLING_SPEED := 30.0

var _rng: RandomNumberGenerator
var _aggression: float
var _special_chance: float


func _init(rng: RandomNumberGenerator, aggression := 0.55, special_chance := 0.1) -> void:
	_rng = rng
	_aggression = aggression
	_special_chance = special_chance


func decide_input(perception: BotPerception) -> InputFrame:
	if is_off_stage(perception):
		return _decide_recovery(perception)
	return _decide_offense(perception)


func is_off_stage(perception: BotPerception) -> bool:
	var self_x := perception.self_position.x
	return (
		self_x < perception.ground.position.x
		or self_x > perception.ground.end.x
		or perception.self_position.y > perception.ground.position.y + OFF_STAGE_DEPTH
	)


func _decide_recovery(perception: BotPerception) -> InputFrame:
	var frame := InputFrame.new()
	frame.move_x = signf(perception.ground.get_center().x - perception.self_position.x)
	frame.jump_pressed = perception.self_velocity.y > FALLING_SPEED and perception.self_has_air_jump
	return frame


func _decide_offense(perception: BotPerception) -> InputFrame:
	var frame := InputFrame.new()
	if not perception.target_in_play:
		return frame
	var offset_to_target := perception.target_position - perception.self_position
	var distance := absf(offset_to_target.x)
	var direction := signf(offset_to_target.x)
	frame.move_x = direction if distance > ATTACK_RANGE * CHASE_STOP_RATIO else direction * FACE_NUDGE
	if _would_walk_off(perception, frame.move_x):
		frame.move_x = 0.0
	var is_vertically_aligned := absf(offset_to_target.y) <= VERTICAL_REACH
	if is_vertically_aligned and distance <= ATTACK_RANGE:
		frame.attack_pressed = _rng.randf() < _aggression
	elif is_vertically_aligned and distance >= SPECIAL_MIN_RANGE and distance <= SPECIAL_MAX_RANGE:
		frame.special_pressed = _rng.randf() < _special_chance
	if perception.self_on_floor and offset_to_target.y < -VERTICAL_REACH and distance < JUMP_CHASE_RANGE:
		frame.jump_pressed = true
	elif perception.self_on_floor and offset_to_target.y > VERTICAL_REACH and _is_on_platform(perception):
		frame.down = true
		frame.jump_pressed = true
	return frame


func _would_walk_off(perception: BotPerception, move_x: float) -> bool:
	if not perception.self_on_floor or _is_on_platform(perception):
		return false
	var next_x := perception.self_position.x + move_x * EDGE_MARGIN
	return next_x < perception.ground.position.x or next_x > perception.ground.end.x


func _is_on_platform(perception: BotPerception) -> bool:
	return perception.self_position.y < perception.ground.position.y - PLATFORM_CLEARANCE
