extends TestCase
## The keyboard source turns held actions of one player's scheme into an InputFrame.


func test_held_right_and_down_become_movement() -> void:
	# Arrange
	var scheme := ControlScheme.new(RandomNumberGenerator.new().randi_range(1, 2))
	var source := KeyboardInputSource.new(scheme)
	Input.action_press(scheme.resolve_action_name(ControlScheme.Action.RIGHT))
	Input.action_press(scheme.resolve_action_name(ControlScheme.Action.DOWN))
	# Act
	var frame := source.read_frame()
	# Assert
	assert_equal(frame.move_x, 1.0, "right held moves right")
	assert_true(frame.down, "down held")
	Input.action_release(scheme.resolve_action_name(ControlScheme.Action.RIGHT))
	Input.action_release(scheme.resolve_action_name(ControlScheme.Action.DOWN))


func test_key_labels_name_a_real_key() -> void:
	# Arrange
	var scheme := ControlScheme.new(1)
	# Act & Assert
	for action: ControlScheme.Action in ControlScheme.Action.values():
		assert_true(not scheme.format_key_label(action).is_empty(), "label for action %d" % action)
