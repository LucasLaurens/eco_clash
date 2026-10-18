extends TestCase


func _create_config(mode: MatchConfig.Mode) -> MatchConfig:
	return MatchConfig.create(mode, FighterRoster.find_at(0), FighterRoster.find_at(1))


func test_vs_bot_puts_the_bot_in_slot_two() -> void:
	# Arrange
	var config := _create_config(MatchConfig.Mode.VS_BOT)
	# Act & Assert
	assert_true(not config.is_bot_slot(0) and config.is_bot_slot(1), "human then bot")
	assert_equal(config.compute_scheme_number(1), 1, "player 1 also picks the bot")


func test_versus_gives_each_player_a_keyboard_half() -> void:
	# Arrange
	var config := _create_config(MatchConfig.Mode.VERSUS)
	# Act & Assert
	assert_true(not config.is_bot_slot(0) and not config.is_bot_slot(1), "two humans")
	assert_equal(config.compute_scheme_number(1), 2, "second player on scheme 2")


func test_demo_is_bot_against_bot() -> void:
	# Arrange
	var config := _create_config(MatchConfig.Mode.DEMO)
	# Act & Assert
	assert_true(config.is_bot_slot(0) and config.is_bot_slot(1), "two bots")


func test_two_schemes_never_share_a_key() -> void:
	# Arrange
	var seen_keys: Dictionary[Key, bool] = {}
	# Act
	for player: int in ControlScheme.PLAYER_KEYS:
		for action: int in ControlScheme.PLAYER_KEYS[player]:
			var key: Key = ControlScheme.PLAYER_KEYS[player][action]
			assert_true(not seen_keys.has(key), "key %s is bound twice" % OS.get_keycode_string(key))
			seen_keys[key] = true
	# Assert
	assert_equal(seen_keys.size(), 12, "6 actions x 2 players")
