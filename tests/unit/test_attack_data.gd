extends TestCase


func test_phases_follow_the_timeline() -> void:
	# Arrange
	var rng := RandomNumberGenerator.new()
	var attack := AttackData.new()
	attack.startup = rng.randf_range(0.05, 0.3)
	attack.active = rng.randf_range(0.05, 0.3)
	attack.recovery = rng.randf_range(0.05, 0.3)
	# Act & Assert
	assert_equal(attack.compute_phase(attack.startup * 0.5), AttackData.Phase.STARTUP, "before startup ends")
	assert_equal(
		attack.compute_phase(attack.startup + attack.active * 0.5), AttackData.Phase.ACTIVE, "inside active window"
	)
	assert_equal(
		attack.compute_phase(attack.compute_total_duration()), AttackData.Phase.RECOVERY, "after active window"
	)
	assert_true(
		is_equal_approx(attack.compute_total_duration(), attack.startup + attack.active + attack.recovery),
		"total sums phases"
	)
