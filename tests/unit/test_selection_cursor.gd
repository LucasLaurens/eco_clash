extends TestCase


func test_wraps_around_the_roster() -> void:
	# Arrange
	var count := RandomNumberGenerator.new().randi_range(2, 8)
	var cursor := SelectionCursor.new(count, 0)
	# Act
	cursor.move_by(-1)
	# Assert
	assert_equal(cursor.index, count - 1, "left of the first is the last")


func test_confirmed_cursor_is_locked_until_cancel() -> void:
	# Arrange
	var cursor := SelectionCursor.new(4, 1)
	cursor.confirm()
	# Act
	cursor.move_by(1)
	# Assert
	assert_equal(cursor.index, 1, "locked cursor ignores moves")
	cursor.cancel()
	cursor.move_by(1)
	assert_equal(cursor.index, 2, "cancel unlocks it")
