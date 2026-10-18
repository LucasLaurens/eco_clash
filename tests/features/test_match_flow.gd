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
const SCENARIOS: Array[String] = [
	"melee_hit_lands_exactly_once",
	"projectile_hits_once_and_vanishes",
	"knock_out_costs_a_stock_and_respawns",
	"two_bots_fight_without_errors",
]


func run_scenarios(host: Node) -> void:
	set_meta(&"scenario_names", SCENARIOS)
	await _test_melee_hit_lands_exactly_once(host)
	await _test_projectile_hits_once_and_vanishes(host)
	await _test_knock_out_costs_a_stock_and_respawns(host)
	await _test_two_bots_fight_without_errors(host)


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
	attacker.spawn_melee_volume(attack)
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
	var shooter_definition := _find_projectile_user()
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


func _find_projectile_user() -> FighterDefinition:
	for definition in FighterRoster.list_all():
		if definition.special is ProjectileShot:
			return definition
	assert(false, "No fighter has a projectile special")
	return FighterRoster.find_at(0)


func _list_fighters(fight: Node) -> Array[Fighter]:
	var fighters: Array[Fighter] = []
	fighters.assign(fight.get_node("World").get_children().filter(func(node: Node) -> bool: return node is Fighter))
	return fighters
