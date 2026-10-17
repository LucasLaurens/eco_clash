class_name BotBrain
extends RefCounted
## Decides one InputFrame from a BotPerception: recover first, then chase and hit.

const ATTACK_RANGE := 26.0
const VERTICAL_REACH := 22.0
const CHASE_STOP_RATIO := 0.7
const FACE_NUDGE := 0.1
const JUMP_CHASE_RANGE := 50.0
const SPECIAL_MIN_RANGE := 40.0
const SPECIAL_MAX_RANGE := 140.0
const EDGE_MARGIN := 10.0
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


func decide(perception: BotPerception) -> InputFrame:
	if is_off_stage(perception):
		return _decide_recovery(perception)
	return _decide_offense(perception)


func is_off_stage(p: BotPerception) -> bool:
	var x := p.self_position.x
	return x < p.ground.position.x or x > p.ground.end.x or p.self_position.y > p.ground.position.y + OFF_STAGE_DEPTH


func _decide_recovery(p: BotPerception) -> InputFrame:
	var frame := InputFrame.new()
	frame.move_x = signf(p.ground.get_center().x - p.self_position.x)
	frame.jump_pressed = p.self_velocity.y > FALLING_SPEED and p.self_has_air_jump
	return frame


func _decide_offense(p: BotPerception) -> InputFrame:
	var frame := InputFrame.new()
	if not p.target_in_play:
		return frame
	var gap := p.target_position - p.self_position
	var distance := absf(gap.x)
	var direction := signf(gap.x)
	frame.move_x = direction if distance > ATTACK_RANGE * CHASE_STOP_RATIO else direction * FACE_NUDGE
	if _would_walk_off(p, frame.move_x):
		frame.move_x = 0.0
	var aligned := absf(gap.y) <= VERTICAL_REACH
	if aligned and distance <= ATTACK_RANGE:
		frame.attack_pressed = _rng.randf() < _aggression
	elif aligned and distance >= SPECIAL_MIN_RANGE and distance <= SPECIAL_MAX_RANGE:
		frame.special_pressed = _rng.randf() < _special_chance
	if p.self_on_floor and gap.y < -VERTICAL_REACH and distance < JUMP_CHASE_RANGE:
		frame.jump_pressed = true
	elif p.self_on_floor and gap.y > VERTICAL_REACH and _is_on_platform(p):
		frame.down = true
		frame.jump_pressed = true
	return frame


func _would_walk_off(p: BotPerception, move_x: float) -> bool:
	if not p.self_on_floor or _is_on_platform(p):
		return false
	var next_x := p.self_position.x + move_x * EDGE_MARGIN
	return next_x < p.ground.position.x or next_x > p.ground.end.x


func _is_on_platform(p: BotPerception) -> bool:
	return p.self_position.y < p.ground.position.y - PLATFORM_CLEARANCE
