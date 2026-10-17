extends TestCase
## Scenarios running real physics frames inside the scene tree.

const FIGHT_SCENE := preload("res://scenes/fight.tscn")
const FIGHTER_SCENE := preload("res://scenes/fighter.tscn")
const SIMULATED_TICKS := 2400
const UNLIMITED_STOCKS := 99


func run_scenarios(host: Node) -> void:
	set_meta(&"scenario_names", ["melee_hit_lands_exactly_once", "two_bots_fight_without_errors"])
	await _melee_hit_lands_exactly_once(host)
	await _two_bots_fight_without_errors(host)


func _melee_hit_lands_exactly_once(host: Node) -> void:
	var name := "melee_hit_lands_exactly_once"
	# Arrange
	var world := Node2D.new()
	host.add_child(world)
	var resolver := CombatResolver.new()
	world.add_child(resolver)
	var attacker := _spawn(world, resolver, FighterRoster.find_at(0), Vector2(100, 100))
	var target := _spawn(world, resolver, FighterRoster.find_at(2), Vector2(114, 100))
	var attack: AttackData = FighterRoster.find_at(0).light_attack.attack
	# Act
	attacker.spawn_melee_volume(attack)
	for _tick in 4:
		await host.get_tree().physics_frame
	# Assert
	assert_true(is_equal_approx(target.damage_percent, attack.damage), "%s: damage %.1f once" % [name, target.damage_percent])
	assert_true(target.velocity.x > 0.0, "%s: target pushed away from attacker" % name)
	world.queue_free()


func _two_bots_fight_without_errors(host: Node) -> void:
	var name := "two_bots_fight_without_errors"
	# Arrange
	var config := MatchConfig.create(MatchConfig.Mode.DEMO, FighterRoster.find_at(1), FighterRoster.find_at(3))
	config.stocks = UNLIMITED_STOCKS
	MatchSettings.current = config
	var fight := FIGHT_SCENE.instantiate()
	host.add_child(fight)
	# Act
	for _tick in SIMULATED_TICKS:
		await host.get_tree().physics_frame
	# Assert
	var fighters: Array[Fighter] = []
	fighters.assign(fight.get_node("World").get_children().filter(func(n: Node) -> bool: return n is Fighter))
	assert_equal(fighters.size(), 2, "%s: two fighters" % name)
	var action_happened := fighters.any(
		func(f: Fighter) -> bool: return f.damage_percent > 0.0 or f.stocks < UNLIMITED_STOCKS
	)
	assert_true(action_happened, "%s: bots actually hit each other" % name)
	for fighter in fighters:
		assert_true(fighter.global_position.is_finite(), "%s: finite position" % name)
	fight.queue_free()
	Engine.time_scale = 1.0


func _spawn(world: Node2D, resolver: CombatResolver, definition: FighterDefinition, at: Vector2) -> Fighter:
	var fighter: Fighter = FIGHTER_SCENE.instantiate()
	world.add_child(fighter)
	fighter.setup(definition, world, 1)
	fighter.global_position = at
	resolver.register_fighter(fighter)
	return fighter
