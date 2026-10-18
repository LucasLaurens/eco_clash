extends TestCase
## Feature scenarios: real scenes, real physics frames, checked from the player's point of view.

const FIGHT_SCENE := preload("res://scenes/fight.tscn")
const FIGHTER_SCENE := preload("res://scenes/fighter.tscn")
const SIMULATED_TICKS := 2400
const UNLIMITED_STOCKS := 99
const KO_TEST_STOCKS := 2
const OUTSIDE_BLAST_ZONE := Vector2(-500, 0)
const PROJECTILE_FLIGHT_TICKS := 40
const FLOOR_LAYER := 2
const FLOOR_SIZE := Vector2(400, 20)
const COOLDOWN_PROBE_TICKS := 75
const PARALYSIS_PROBE_TICKS := 60
const POISON_PROBE_TICKS := 100
const STRIKE_TICKS := 30
const HASTE_RAMP_TICKS := 30
const HASTE_RUN_TICKS := 60
const SCENARIOS: Array[String] = [
	"melee_hit_lands_exactly_once",
	"projectile_hits_once_and_vanishes",
	"knock_out_costs_a_stock_and_respawns",
	"two_bots_fight_without_errors",
	"special_waits_for_its_cooldown",
	"dark_surge_empowers_the_next_attack",
	"haste_speeds_up_and_hits_on_contact_once",
	"mend_heals_a_share_of_the_damage",
	"poison_keeps_hurting_after_the_hit",
	"detonation_paralyzes_until_the_next_hit",
]


## Holds the same intent every tick: a stand-in pad for scenarios.
class HeldInputSource:
	extends InputSource

	var frame := InputFrame.new()

	func read_frame() -> InputFrame:
		return frame


func run_scenarios(host: Node) -> void:
	set_meta(&"scenario_names", SCENARIOS)
	await _test_melee_hit_lands_exactly_once(host)
	await _test_projectile_hits_once_and_vanishes(host)
	await _test_knock_out_costs_a_stock_and_respawns(host)
	await _test_two_bots_fight_without_errors(host)
	await _test_special_waits_for_its_cooldown(host)
	await _test_dark_surge_empowers_the_next_attack(host)
	await _test_haste_speeds_up_and_hits_on_contact_once(host)
	await _test_mend_heals_a_share_of_the_damage(host)
	await _test_poison_keeps_hurting_after_the_hit(host)
	await _test_detonation_paralyzes_until_the_next_hit(host)


func _test_melee_hit_lands_exactly_once(host: Node) -> void:
	var scenario_name := "melee_hit_lands_exactly_once"
	# Arrange
	var world := Node2D.new()
	host.add_child(world)
	var resolver := CombatResolver.new()
	world.add_child(resolver)
	var attacker := _spawn_fighter(world, resolver, FighterRoster.find_at(0), Vector2(100, 100))
	var target := _spawn_fighter(world, resolver, FighterRoster.find_at(2), Vector2(114, 100))
	var attack: AttackData = FighterRoster.find_at(0).light_attack.attack
	# Act
	attacker.spawn_melee_volume(attack, attack.active)
	for _tick in 4:
		await host.get_tree().physics_frame
	# Assert
	assert_true(
		is_equal_approx(target.damage_percent, attack.damage),
		"%s: damage %.1f once" % [scenario_name, target.damage_percent]
	)
	assert_true(target.velocity.x > 0.0, "%s: target pushed away from attacker" % scenario_name)
	_dispose(host, world)


func _test_projectile_hits_once_and_vanishes(host: Node) -> void:
	var scenario_name := "projectile_hits_once_and_vanishes"
	# Arrange
	var world := Node2D.new()
	host.add_child(world)
	var resolver := CombatResolver.new()
	world.add_child(resolver)
	world.add_child(_create_floor(Vector2(150, 100)))
	var shooter_definition := _find_definition(
		func(definition: FighterDefinition) -> bool: return definition.special is ProjectileShot
	)
	var shooter := _spawn_fighter(world, resolver, shooter_definition, Vector2(80, 100))
	var target := _spawn_fighter(world, resolver, FighterRoster.find_at(2), Vector2(170, 100))
	var shot := shooter_definition.special as ProjectileShot
	# Act
	shot.trigger_effect(shooter)
	for _tick in PROJECTILE_FLIGHT_TICKS:
		await host.get_tree().physics_frame
	# Assert
	assert_true(
		is_equal_approx(target.damage_percent, shot.attack.damage),
		"%s: damage %.1f once" % [scenario_name, target.damage_percent]
	)
	assert_equal(
		host.get_tree().get_nodes_in_group(HitVolume.GROUP).size(),
		0,
		"%s: projectile gone after the hit" % scenario_name
	)
	_dispose(host, world)


func _test_knock_out_costs_a_stock_and_respawns(host: Node) -> void:
	var scenario_name := "knock_out_costs_a_stock_and_respawns"
	# Arrange
	var config := MatchConfig.create(MatchConfig.Mode.DEMO, FighterRoster.find_at(0), FighterRoster.find_at(1))
	config.stocks = KO_TEST_STOCKS
	MatchSettings.current_config = config
	var fight := FIGHT_SCENE.instantiate()
	host.add_child(fight)
	await host.get_tree().physics_frame
	var fighter := _list_fighters(fight)[0]
	fighter.receive_hit(FighterRoster.find_at(2).light_attack.attack, 1)
	# Act
	fighter.global_position = OUTSIDE_BLAST_ZONE
	for _tick in 3:
		await host.get_tree().physics_frame
	# Assert
	assert_equal(fighter.stocks, KO_TEST_STOCKS - 1, "%s: one stock lost" % scenario_name)
	assert_true(
		fight.get_node("Stage").is_inside_blast_zone(fighter.global_position),
		"%s: back inside the arena" % scenario_name
	)
	assert_equal(fighter.damage_percent, 0.0, "%s: damage reset" % scenario_name)
	assert_true(fighter.is_in_play(), "%s: still in play" % scenario_name)
	_dispose(host, fight)
	Engine.time_scale = 1.0


func _test_two_bots_fight_without_errors(host: Node) -> void:
	var scenario_name := "two_bots_fight_without_errors"
	# Arrange
	var config := MatchConfig.create(MatchConfig.Mode.DEMO, FighterRoster.find_at(1), FighterRoster.find_at(3))
	config.stocks = UNLIMITED_STOCKS
	MatchSettings.current_config = config
	var fight := FIGHT_SCENE.instantiate()
	host.add_child(fight)
	# Act
	for _tick in SIMULATED_TICKS:
		await host.get_tree().physics_frame
	# Assert
	var fighters := _list_fighters(fight)
	assert_equal(fighters.size(), 2, "%s: two fighters" % scenario_name)
	var action_happened := fighters.any(
		func(candidate: Fighter) -> bool: return candidate.damage_percent > 0.0 or candidate.stocks < UNLIMITED_STOCKS
	)
	assert_true(action_happened, "%s: bots actually hit each other" % scenario_name)
	for fighter in fighters:
		assert_true(fighter.global_position.is_finite(), "%s: finite position" % scenario_name)
	_dispose(host, fight)
	Engine.time_scale = 1.0


func _test_special_waits_for_its_cooldown(host: Node) -> void:
	var scenario_name := "special_waits_for_its_cooldown"
	# Arrange
	var world := _create_world(host)
	var shooter_definition := _find_definition(
		func(definition: FighterDefinition) -> bool:
			var special := definition.special
			return special is ProjectileShot and special.attack.compute_total_duration() < special.cooldown
	)
	var shooter := _spawn_fighter(world, world.get_node("Resolver"), shooter_definition, Vector2(100, 100))
	var input := HeldInputSource.new()
	input.frame.special_pressed = true
	shooter.attach_input(input)
	# Act
	for _tick in COOLDOWN_PROBE_TICKS:
		await host.get_tree().physics_frame
	# Assert
	assert_equal(
		host.get_tree().get_nodes_in_group(HitVolume.GROUP).size(),
		1,
		"%s: one shot despite the held button" % scenario_name
	)
	assert_true(shooter.compute_special_readiness() < 1.0, "%s: gauge still refilling" % scenario_name)
	_dispose(host, world)


func _test_dark_surge_empowers_the_next_attack(host: Node) -> void:
	var scenario_name := "dark_surge_empowers_the_next_attack"
	# Arrange
	var world := _create_world(host)
	var resolver: CombatResolver = world.get_node("Resolver")
	var definition := _find_definition(
		func(candidate: FighterDefinition) -> bool: return candidate.special is DarkSurge
	)
	var surge := definition.special as DarkSurge
	var user := _spawn_fighter(world, resolver, definition, Vector2(100, 100))
	var target := _spawn_fighter(world, resolver, FighterRoster.find_at(2), Vector2(118, 100))
	var input := HeldInputSource.new()
	user.attach_input(input)
	surge.trigger_effect(user)
	# Act
	input.frame.attack_pressed = true
	await host.get_tree().physics_frame
	input.frame.attack_pressed = false
	for _tick in STRIKE_TICKS:
		await host.get_tree().physics_frame
	# Assert
	assert_true(
		is_equal_approx(target.damage_percent, surge.empowered_strike.attack.damage),
		"%s: dark strike damage %.1f" % [scenario_name, target.damage_percent]
	)
	_dispose(host, world)


func _test_haste_speeds_up_and_hits_on_contact_once(host: Node) -> void:
	var scenario_name := "haste_speeds_up_and_hits_on_contact_once"
	# Arrange
	var world := _create_world(host)
	var resolver: CombatResolver = world.get_node("Resolver")
	var definition := _find_definition(
		func(candidate: FighterDefinition) -> bool: return candidate.special is HasteRush
	)
	var runner := _spawn_fighter(world, resolver, definition, Vector2(40, 100))
	var target := _spawn_fighter(world, resolver, FighterRoster.find_at(2), Vector2(130, 100))
	var input := HeldInputSource.new()
	input.frame.move_x = 1.0
	runner.attach_input(input)
	# Act
	definition.special.trigger_effect(runner)
	for _tick in HASTE_RAMP_TICKS:
		await host.get_tree().physics_frame
	var hasted_speed := runner.velocity.x
	for _tick in HASTE_RUN_TICKS:
		await host.get_tree().physics_frame
	# Assert
	assert_true(hasted_speed > definition.run_speed, "%s: faster than the normal run" % scenario_name)
	assert_true(
		is_equal_approx(target.damage_percent, definition.special.attack.damage),
		"%s: contact damage %.1f once" % [scenario_name, target.damage_percent]
	)
	_dispose(host, world)


func _test_mend_heals_a_share_of_the_damage(host: Node) -> void:
	var scenario_name := "mend_heals_a_share_of_the_damage"
	# Arrange
	var world := _create_world(host)
	var definition := _find_definition(func(candidate: FighterDefinition) -> bool: return candidate.special is Mend)
	var mend := definition.special as Mend
	var healer := _spawn_fighter(world, world.get_node("Resolver"), definition, Vector2(100, 100))
	var damage_before := RandomNumberGenerator.new().randf_range(10.0, 120.0)
	healer.damage_percent = damage_before
	# Act
	mend.trigger_effect(healer)
	# Assert
	var expected := damage_before - minf(damage_before * mend.heal_ratio, mend.max_heal)
	assert_true(
		is_equal_approx(healer.damage_percent, expected),
		"%s: %.1f -> %.1f, expected %.1f" % [scenario_name, damage_before, healer.damage_percent, expected]
	)
	_dispose(host, world)


func _test_poison_keeps_hurting_after_the_hit(host: Node) -> void:
	var scenario_name := "poison_keeps_hurting_after_the_hit"
	# Arrange
	var world := _create_world(host)
	var definition := _find_definition(
		func(candidate: FighterDefinition) -> bool: return candidate.special.attack.poison_damage > 0.0
	)
	var attack := definition.special.attack
	var target := _spawn_fighter(world, world.get_node("Resolver"), FighterRoster.find_at(2), Vector2(100, 100))
	# Act
	target.receive_hit(attack, 1)
	var damage_on_impact := target.damage_percent
	for _tick in POISON_PROBE_TICKS:
		await host.get_tree().physics_frame
	# Assert
	assert_true(is_equal_approx(damage_on_impact, attack.damage), "%s: impact damage first" % scenario_name)
	assert_true(
		is_equal_approx(target.damage_percent, attack.compute_total_damage()),
		"%s: poison added %.1f" % [scenario_name, target.damage_percent - damage_on_impact]
	)
	_dispose(host, world)


func _test_detonation_paralyzes_until_the_next_hit(host: Node) -> void:
	var scenario_name := "detonation_paralyzes_until_the_next_hit"
	# Arrange
	var world := _create_world(host)
	var definition := _find_definition(
		func(candidate: FighterDefinition) -> bool: return candidate.special.attack.paralysis > 0.0
	)
	var target := _spawn_fighter(world, world.get_node("Resolver"), FighterRoster.find_at(0), Vector2(100, 100))
	var input := HeldInputSource.new()
	input.frame.attack_pressed = true
	target.attach_input(input)
	var target_volumes := target.get_node("Volumes")
	# Act
	target.receive_hit(definition.special.attack, 1)
	var attacked_while_paralyzed := false
	for _tick in PARALYSIS_PROBE_TICKS:
		await host.get_tree().physics_frame
		attacked_while_paralyzed = attacked_while_paralyzed or target_volumes.get_child_count() > 0
	target.receive_hit(FighterRoster.find_at(1).light_attack.attack, 1)
	var attacked_after_wake_up := false
	for _tick in PARALYSIS_PROBE_TICKS:
		await host.get_tree().physics_frame
		attacked_after_wake_up = attacked_after_wake_up or target_volumes.get_child_count() > 0
	# Assert
	assert_true(not attacked_while_paralyzed, "%s: no attack while paralysed" % scenario_name)
	assert_true(attacked_after_wake_up, "%s: a plain hit wakes the target up" % scenario_name)
	_dispose(host, world)


## A bare arena: resolver and floor, no stage, no blast zone.
func _create_world(host: Node) -> Node2D:
	var world := Node2D.new()
	host.add_child(world)
	var resolver := CombatResolver.new()
	resolver.name = "Resolver"
	world.add_child(resolver)
	world.add_child(_create_floor(Vector2(150, 100)))
	return world


## Detach first: a queued node stays in the tree until the frame ends, and its resolver would still
## read the global hit_volumes group and let the next scenario's projectile strike a stale fighter.
func _dispose(host: Node, scene: Node) -> void:
	host.remove_child(scene)
	scene.queue_free()


func _spawn_fighter(
	world: Node2D, resolver: CombatResolver, definition: FighterDefinition, spawn_position: Vector2
) -> Fighter:
	var fighter: Fighter = FIGHTER_SCENE.instantiate()
	world.add_child(fighter)
	fighter.configure(definition, world, 1)
	fighter.global_position = spawn_position
	resolver.register_fighter(fighter)
	return fighter


## A flat floor on the ground layer, top edge at surface_center.y, so fighters stand still instead of falling.
func _create_floor(surface_center: Vector2) -> StaticBody2D:
	var floor_body := StaticBody2D.new()
	floor_body.collision_layer = 0
	floor_body.set_collision_layer_value(FLOOR_LAYER, true)
	floor_body.position = surface_center + Vector2(0, FLOOR_SIZE.y / 2.0)
	var shape := CollisionShape2D.new()
	var rectangle := RectangleShape2D.new()
	rectangle.size = FLOOR_SIZE
	shape.shape = rectangle
	floor_body.add_child(shape)
	return floor_body


func _find_definition(predicate: Callable) -> FighterDefinition:
	for definition in FighterRoster.list_all():
		if predicate.call(definition):
			return definition
	assert(false, "No fighter matches the scenario")
	return FighterRoster.find_at(0)


func _list_fighters(fight: Node) -> Array[Fighter]:
	var fighters: Array[Fighter] = []
	fighters.assign(fight.get_node("World").get_children().filter(func(node: Node) -> bool: return node is Fighter))
	return fighters
