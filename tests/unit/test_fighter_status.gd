extends TestCase

const FRAME := 1.0 / 60.0


func test_special_is_ready_again_after_its_cooldown() -> void:
	# Arrange
	var rng := RandomNumberGenerator.new()
	var cooldown := rng.randf_range(2.0, 10.0)
	var status := FighterStatus.new()
	# Act
	status.start_special_cooldown(cooldown)
	status.tick_timers(cooldown * 0.5)
	var is_ready_halfway := status.is_special_ready()
	var halfway_readiness := status.compute_special_readiness()
	status.tick_timers(cooldown * 0.5)
	# Assert
	assert_true(not is_ready_halfway, "locked during the cooldown")
	assert_true(is_equal_approx(halfway_readiness, 0.5), "gauge half full halfway")
	assert_true(status.is_special_ready(), "ready once the cooldown is over")
	assert_equal(status.compute_special_readiness(), 1.0, "gauge full")


func test_fresh_fighter_has_its_special_ready() -> void:
	# Act & Assert
	assert_equal(FighterStatus.new().compute_special_readiness(), 1.0, "no cooldown before the first special")


func test_empowered_strike_replaces_one_light_attack_only() -> void:
	# Arrange
	var light_attack := MeleeStrike.new()
	var dark_strike := MeleeStrike.new()
	var status := FighterStatus.new()
	status.empower(dark_strike, RandomNumberGenerator.new().randf_range(2.0, 6.0))
	# Act
	var first := status.select_light_attack(light_attack)
	status.spend_empowerment(FRAME)
	var second := status.select_light_attack(light_attack)
	var tint_during_strike := status.resolve_tint()
	status.tick_timers(FRAME)
	# Assert
	assert_equal(first, dark_strike, "first attack is the dark strike")
	assert_equal(second, light_attack, "second attack is back to normal")
	assert_equal(tint_during_strike, FighterStatus.DARK_TINT, "still dark during the strike")
	assert_equal(status.resolve_tint(), Color.WHITE, "dark aura gone after the strike")


func test_empowerment_fades_after_its_window() -> void:
	# Arrange
	var window := RandomNumberGenerator.new().randf_range(2.0, 6.0)
	var light_attack := MeleeStrike.new()
	var status := FighterStatus.new()
	status.empower(MeleeStrike.new(), window)
	# Act
	status.tick_timers(window)
	# Assert
	assert_true(not status.is_empowered(), "window over")
	assert_equal(status.select_light_attack(light_attack), light_attack, "normal attack after the window")


func test_haste_multiplies_speed_until_it_ends() -> void:
	# Arrange
	var rng := RandomNumberGenerator.new()
	var duration := rng.randf_range(1.0, 3.0)
	var multiplier := rng.randf_range(1.2, 2.0)
	var status := FighterStatus.new()
	# Act
	status.hasten(duration, multiplier)
	var hasted_multiplier := status.compute_speed_multiplier()
	status.tick_timers(duration)
	# Assert
	assert_equal(hasted_multiplier, multiplier, "faster while hasted")
	assert_equal(status.compute_speed_multiplier(), 1.0, "normal speed afterwards")


func test_poison_deals_its_damage_over_its_duration() -> void:
	# Arrange
	var rng := RandomNumberGenerator.new()
	var attack := AttackData.new()
	attack.poison_damage = rng.randf_range(2.0, 10.0)
	attack.poison_duration = rng.randf_range(1.0, 2.0)
	var status := FighterStatus.new()
	status.apply_hit(attack)
	var dealt := 0.0
	# Act
	for _frame in roundi((attack.poison_duration + FighterStatus.POISON_TICK) / FRAME):
		dealt += status.tick_timers(FRAME)
	# Assert
	assert_true(is_equal_approx(dealt, attack.poison_damage), "all the poison, no more (%.2f)" % dealt)


func test_poison_hurts_over_time_not_at_once() -> void:
	# Arrange
	var attack := AttackData.new()
	attack.poison_damage = RandomNumberGenerator.new().randf_range(2.0, 10.0)
	attack.poison_duration = 1.5
	var status := FighterStatus.new()
	# Act
	status.apply_hit(attack)
	var first_tick := status.tick_timers(FighterStatus.POISON_TICK)
	# Assert
	assert_true(first_tick > 0.0 and first_tick < attack.poison_damage, "one tick is a slice of the poison")
	assert_equal(status.resolve_tint(), FighterStatus.POISON_TINT, "poisoned fighter turns green")


func test_a_plain_hit_ends_paralysis() -> void:
	# Arrange
	var paralysing := AttackData.new()
	paralysing.paralysis = RandomNumberGenerator.new().randf_range(1.0, 2.0)
	var status := FighterStatus.new()
	status.apply_hit(paralysing)
	var was_paralyzed := status.is_paralyzed()
	# Act
	status.apply_hit(AttackData.new())
	# Assert
	assert_true(was_paralyzed, "paralysed by the detonation")
	assert_true(not status.is_paralyzed(), "woken up by the next hit")


func test_tint_shows_the_strongest_condition() -> void:
	# Arrange
	var paralysing := AttackData.new()
	paralysing.paralysis = 1.5
	var status := FighterStatus.new()
	status.hasten(2.0, 1.5)
	var hasted_tint := status.resolve_tint()
	# Act
	status.apply_hit(paralysing)
	# Assert
	assert_equal(hasted_tint, FighterStatus.HASTE_TINT, "haste alone tints blue")
	assert_equal(status.resolve_tint(), FighterStatus.PARALYSIS_TINT, "paralysis outranks haste")
