extends TestCase

const GROUND := Rect2(84, 186, 312, 40)


func _create_perception(rng: RandomNumberGenerator) -> BotPerception:
	var perception := BotPerception.new()
	perception.ground = GROUND
	perception.self_on_floor = true
	perception.self_has_air_jump = true
	perception.self_position = Vector2(rng.randf_range(150.0, 230.0), GROUND.position.y)
	perception.target_position = perception.self_position
	return perception


func test_chases_a_distant_target() -> void:
	# Arrange
	var rng := RandomNumberGenerator.new()
	var perception := _create_perception(rng)
	perception.target_position.x += rng.randf_range(60.0, 140.0)
	# Act
	var frame := BotBrain.new(rng).decide_input(perception)
	# Assert
	assert_true(frame.move_x > 0.0, "walks toward a target on its right")


func test_attacks_a_target_in_reach() -> void:
	# Arrange
	var rng := RandomNumberGenerator.new()
	var perception := _create_perception(rng)
	perception.target_position.x -= BotBrain.ATTACK_RANGE * 0.5
	# Act
	var frame := BotBrain.new(rng, 1.0).decide_input(perception)
	# Assert
	assert_true(frame.attack_pressed, "always attacks with full aggression")
	assert_true(frame.move_x < 0.0, "turns to face the target")


func test_recovers_toward_the_stage_when_off_it() -> void:
	# Arrange
	var rng := RandomNumberGenerator.new()
	var perception := _create_perception(rng)
	perception.self_on_floor = false
	perception.self_position = Vector2(GROUND.position.x - rng.randf_range(20.0, 60.0), GROUND.position.y + 30.0)
	perception.self_velocity = Vector2(0.0, rng.randf_range(50.0, 300.0))
	# Act
	var frame := BotBrain.new(rng).decide_input(perception)
	# Assert
	assert_true(frame.move_x > 0.0, "drifts back toward the centre")
	assert_true(frame.jump_pressed, "spends its air jump while falling")


func test_refuses_to_walk_off_the_edge() -> void:
	# Arrange
	var rng := RandomNumberGenerator.new()
	var perception := _create_perception(rng)
	perception.self_position.x = GROUND.end.x - 2.0
	perception.target_position = Vector2(GROUND.end.x + 80.0, GROUND.position.y + 40.0)
	# Act
	var frame := BotBrain.new(rng).decide_input(perception)
	# Assert
	assert_equal(frame.move_x, 0.0, "stays on the ledge")
