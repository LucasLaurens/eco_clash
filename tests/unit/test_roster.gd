extends TestCase


func test_four_unique_fighters() -> void:
	# Arrange
	var ids: Dictionary[StringName, bool] = {}
	# Act
	for definition in FighterRoster.list_all():
		ids[definition.id] = true
	# Assert
	assert_equal(ids.size(), 4, "four distinct ids")


func test_sheets_match_the_generated_layout() -> void:
	# Arrange
	var layout := FighterSpriteFrames.read_layout()
	var expected_width := int(layout["frame_count"]) * int(layout["frame_size"])
	# Act & Assert
	for definition in FighterRoster.list_all():
		assert_equal(definition.sprite_sheet.get_width(), expected_width, "%s sheet width" % definition.id)
		assert_equal(definition.sprite_sheet.get_height(), int(layout["frame_size"]), "%s sheet height" % definition.id)


func test_every_move_is_complete() -> void:
	# Act & Assert
	for definition in FighterRoster.list_all():
		for move: FighterMove in [definition.light_attack, definition.special]:
			assert_true(move != null and move.attack != null, "%s has both moves" % definition.id)
			assert_true(move.attack.compute_total_duration() > 0.0, "%s move has a timeline" % definition.id)
			assert_true(FighterSpriteFrames.read_layout()["animations"].has(String(move.animation)), "%s animation exists" % definition.id)


func test_ratings_stay_on_the_five_pip_scale() -> void:
	# Act & Assert
	for definition in FighterRoster.list_all():
		for rating in [definition.compute_speed_rating(), definition.compute_power_rating(), definition.compute_weight_rating()]:
			assert_true(rating >= 1 and rating <= FighterDefinition.MAX_RATING, "%s rating %d in range" % [definition.id, rating])
