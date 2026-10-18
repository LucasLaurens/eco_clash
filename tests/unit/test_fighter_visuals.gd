extends TestCase
## Readability helpers of a fighter: the contact shadow shrinks as it rises, in whole frames.

const SHADOW_SHEET := preload("res://assets/fx/shadow.png")


func test_shadow_is_full_on_the_ground_and_smallest_at_max_height() -> void:
	# Arrange
	var frame_count := SHADOW_SHEET.get_width() / SHADOW_SHEET.get_height()
	# Act & Assert
	assert_equal(Fighter.compute_shadow_frame(0.0, frame_count), 0, "standing: full shadow")
	assert_equal(
		Fighter.compute_shadow_frame(Fighter.SHADOW_MAX_DISTANCE, frame_count),
		frame_count - 1,
		"at max height: smallest"
	)
	assert_equal(
		Fighter.compute_shadow_frame(Fighter.SHADOW_MAX_DISTANCE * 4.0, frame_count), frame_count - 1, "clamped above"
	)


func test_shadow_never_grows_while_rising() -> void:
	# Arrange
	var rng := RandomNumberGenerator.new()
	var frame_count := SHADOW_SHEET.get_width() / SHADOW_SHEET.get_height()
	var low := rng.randf_range(0.0, Fighter.SHADOW_MAX_DISTANCE)
	var high := low + rng.randf_range(1.0, Fighter.SHADOW_MAX_DISTANCE)
	# Act & Assert
	assert_true(
		Fighter.compute_shadow_frame(high, frame_count) >= Fighter.compute_shadow_frame(low, frame_count),
		"higher means same or smaller"
	)
