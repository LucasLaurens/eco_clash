extends TestCase
## Bindings of a player: keyboard and pad on the same actions, each pad on its own player.

const FONT := preload("res://assets/fonts/eco_pixel.fnt")
const FACE_BUTTON_ACTIONS := {
	JOY_BUTTON_A: ControlScheme.Action.ATTACK,
	JOY_BUTTON_B: ControlScheme.Action.SPECIAL,
	JOY_BUTTON_X: ControlScheme.Action.UP,
}


func _choose_player() -> int:
	return RandomNumberGenerator.new().randi_range(1, ControlScheme.PLAYER_KEYS.size())


func _create_pad_button(device: int, button: JoyButton) -> InputEventJoypadButton:
	var event := InputEventJoypadButton.new()
	event.device = device
	event.button_index = button
	event.pressed = true
	return event


func _create_stick_tilt(device: int, axis: JoyAxis, value: float) -> InputEventJoypadMotion:
	var event := InputEventJoypadMotion.new()
	event.device = device
	event.axis = axis
	event.axis_value = value
	return event


func test_every_action_has_a_key_and_a_pad_binding() -> void:
	for player_number: int in ControlScheme.PLAYER_KEYS:
		# Arrange
		var scheme := ControlScheme.new(player_number)
		for action: ControlScheme.Action in ControlScheme.Action.values():
			# Act
			var events := InputMap.action_get_events(scheme.resolve_action_name(action))
			# Assert
			var label := "p%d %s" % [player_number, ControlScheme.Action.keys()[action]]
			assert_true(events.any(func(event: InputEvent) -> bool: return event is InputEventKey), "%s key" % label)
			assert_true(
				events.any(func(event: InputEvent) -> bool: return event is InputEventJoypadButton), "%s pad" % label
			)


func test_pad_face_buttons_attack_special_and_jump() -> void:
	# Arrange
	var scheme := ControlScheme.new(_choose_player())
	var device := scheme.resolve_pad_device()
	# Act & Assert
	for button: JoyButton in FACE_BUTTON_ACTIONS:
		var event := _create_pad_button(device, button)
		var action_name := scheme.resolve_action_name(FACE_BUTTON_ACTIONS[button])
		assert_true(event.is_action_pressed(action_name), "button %d" % button)


func test_a_pad_only_drives_its_own_player() -> void:
	# Arrange
	var first := ControlScheme.new(1)
	var second := ControlScheme.new(2)
	var event := _create_pad_button(second.resolve_pad_device(), JOY_BUTTON_A)
	# Act & Assert
	assert_true(first.resolve_pad_device() != second.resolve_pad_device(), "one device per player")
	assert_true(event.is_action_pressed(second.resolve_action_name(ControlScheme.Action.ATTACK)), "own pad")
	assert_true(not event.is_action_pressed(first.resolve_action_name(ControlScheme.Action.ATTACK)), "other pad")


func test_stick_moves_past_the_deadzone_only() -> void:
	# Arrange
	var scheme := ControlScheme.new(_choose_player())
	var right := scheme.resolve_action_name(ControlScheme.Action.RIGHT)
	var rng := RandomNumberGenerator.new()
	var resting := _create_stick_tilt(
		scheme.resolve_pad_device(), JOY_AXIS_LEFT_X, rng.randf_range(0.0, ControlScheme.STICK_DEADZONE - 0.01)
	)
	var tilted := _create_stick_tilt(
		scheme.resolve_pad_device(), JOY_AXIS_LEFT_X, rng.randf_range(ControlScheme.STICK_DEADZONE + 0.01, 1.0)
	)
	# Act & Assert
	assert_true(not resting.is_action_pressed(right), "inside the deadzone")
	assert_true(tilted.is_action_pressed(right), "past the deadzone")


func test_a_pad_plugged_mid_session_rebinds_without_duplicates() -> void:
	# Arrange
	var scheme := ControlScheme.new(_choose_player())
	var action_name := scheme.resolve_action_name(ControlScheme.Action.UP)
	var event_count := InputMap.action_get_events(action_name).size()
	# Act
	Input.joy_connection_changed.emit(scheme.player - 1, true)
	# Assert
	assert_equal(InputMap.action_get_events(action_name).size(), event_count, "no duplicate after a hot-plug")
	assert_equal(InputMap.action_get_events(ControlScheme.PAUSE_ACTION).size(), 2, "Escape and Start")


func test_menus_accept_and_pause_from_any_pad() -> void:
	# Arrange
	var device := RandomNumberGenerator.new().randi_range(0, 7)
	# Act & Assert
	assert_true(_create_pad_button(device, ControlScheme.MENU_ACCEPT_PAD_BUTTON).is_action_pressed(&"ui_accept"), "A")
	assert_true(
		_create_pad_button(device, ControlScheme.PAUSE_PAD_BUTTON).is_action_pressed(ControlScheme.PAUSE_ACTION),
		"Start"
	)


func test_hints_show_keys_without_a_pad() -> void:
	# Arrange
	var scheme := ControlScheme.new(_choose_player())
	# Act & Assert
	assert_true(not scheme.has_pad(), "headless runs have no pad")
	for action: ControlScheme.Action in ControlScheme.Action.values():
		assert_equal(scheme.format_control_label(action), scheme.format_key_label(action), "key label")


func test_pad_labels_are_drawable() -> void:
	# Arrange
	var scheme := ControlScheme.new(_choose_player())
	# Act & Assert
	for action: ControlScheme.Action in ControlScheme.Action.values():
		var label := scheme.format_pad_label(action)
		assert_true(not label.is_empty(), "pad label for action %d" % action)
		for character in label:
			assert_true(FONT.has_char(character.unicode_at(0)), "glyph '%s' missing" % character)
