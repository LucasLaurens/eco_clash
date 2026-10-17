class_name BotInputSource
extends InputSource
## Drives a fighter with a BotBrain. Thinks every few ticks, like a human reaction time.

const DECISION_INTERVAL_TICKS := 6

var _brain: BotBrain
var _body: Fighter
var _target: Fighter
var _stage: Stage
var _held_move_x := 0.0
var _held_down := false
var _ticks_until_decision := 0


func _init(brain: BotBrain, body: Fighter, target: Fighter, stage: Stage) -> void:
	_brain = brain
	_body = body
	_target = target
	_stage = stage


func read_frame() -> InputFrame:
	_ticks_until_decision -= 1
	if _ticks_until_decision > 0:
		return _repeat_held_movement()
	_ticks_until_decision = DECISION_INTERVAL_TICKS
	var decision := _brain.decide(_perceive())
	_held_move_x = decision.move_x
	_held_down = decision.down
	return decision


## Between decisions, directions stay held; buttons fire only once.
func _repeat_held_movement() -> InputFrame:
	var frame := InputFrame.new()
	frame.move_x = _held_move_x
	frame.down = _held_down
	return frame


func _perceive() -> BotPerception:
	var perception := BotPerception.new()
	perception.self_position = _body.global_position
	perception.self_velocity = _body.velocity
	perception.self_on_floor = _body.is_on_floor()
	perception.self_has_air_jump = _body.has_air_jump()
	perception.target_position = _target.global_position
	perception.target_in_play = _target.is_in_play()
	perception.ground = _stage.compute_ground_surface()
	return perception
