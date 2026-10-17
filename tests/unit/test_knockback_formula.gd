extends TestCase


func _create_attack(rng: RandomNumberGenerator) -> AttackData:
	var attack := AttackData.new()
	attack.base_knockback = rng.randf_range(60.0, 160.0)
	attack.knockback_growth = rng.randf_range(1.0, 5.0)
	attack.launch_angle_deg = rng.randf_range(10.0, 80.0)
	return attack


func test_force_grows_with_damage() -> void:
	# Arrange
	var rng := RandomNumberGenerator.new()
	var attack := _create_attack(rng)
	var weight := rng.randf_range(70.0, 140.0)
	# Act
	var fresh := KnockbackFormula.compute_force(attack, 0.0, weight)
	var battered := KnockbackFormula.compute_force(attack, rng.randf_range(50.0, 200.0), weight)
	# Assert
	assert_true(battered > fresh, "a damaged fighter flies further")
	assert_equal(fresh, attack.base_knockback, "at 0% only base knockback applies")


func test_heavier_fighters_fly_less() -> void:
	# Arrange
	var rng := RandomNumberGenerator.new()
	var attack := _create_attack(rng)
	var percent := rng.randf_range(20.0, 150.0)
	# Act
	var light := KnockbackFormula.compute_force(attack, percent, 75.0)
	var heavy := KnockbackFormula.compute_force(attack, percent, 135.0)
	# Assert
	assert_true(heavy < light, "weight resists knockback")


func test_launch_mirrors_with_direction_and_goes_up() -> void:
	# Arrange
	var rng := RandomNumberGenerator.new()
	var attack := _create_attack(rng)
	var force := rng.randf_range(100.0, 500.0)
	# Act
	var right := KnockbackFormula.compute_launch_velocity(attack, 1, force)
	var left := KnockbackFormula.compute_launch_velocity(attack, -1, force)
	# Assert
	assert_true(right.x > 0.0 and left.x < 0.0, "direction picks the side")
	assert_true(is_equal_approx(right.y, left.y) and right.y < 0.0, "vertical part is the same and upward")
	assert_true(is_equal_approx(right.length(), force), "speed equals force")


func test_hitstun_is_proportional_to_force() -> void:
	# Arrange
	var force := RandomNumberGenerator.new().randf_range(100.0, 500.0)
	# Act & Assert
	assert_true(is_equal_approx(KnockbackFormula.compute_hitstun(force * 2.0), KnockbackFormula.compute_hitstun(force) * 2.0), "linear hitstun")
