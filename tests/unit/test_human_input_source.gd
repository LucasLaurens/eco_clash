extends TestCase
## The human source turns held actions of one player's scheme, keys or pad, into an InputFrame.


func test_held_right_and_down_become_movement() -> void:
	# Arrange
	var scheme := ControlScheme.new(RandomNumberGenerator.new().randi_range(1, 2))
	var source := HumanInputSource.new(scheme)
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


func test_pad_stick_and_button_become_movement_and_attack() -> void:
	# Arrange
	var scheme := ControlScheme.new(RandomNumberGenerator.new().randi_range(1, 2))
	var source := HumanInputSource.new(scheme)
	var stick := InputEventJoypadMotion.new()
	stick.device = scheme.resolve_pad_device()
	stick.axis = JOY_AXIS_LEFT_X
	stick.axis_value = -1.0
	var button := InputEventJoypadButton.new()
	button.device = scheme.resolve_pad_device()
	button.button_index = JOY_BUTTON_A
	button.pressed = true
	Input.parse_input_event(stick)
	Input.parse_input_event(button)
	Input.flush_buffered_events()
	# Act
	var frame := source.read_frame()
	# Assert
	assert_equal(frame.move_x, -1.0, "stick left moves left")
	assert_true(frame.attack_pressed, "A attacks")
	var centered_stick: InputEventJoypadMotion = stick.duplicate()
	centered_stick.axis_value = 0.0
	var released_button: InputEventJoypadButton = button.duplicate()
	released_button.pressed = false
	Input.parse_input_event(centered_stick)
	Input.parse_input_event(released_button)
	Input.flush_buffered_events()
