class_name CombatResolver
extends Node
## Single owner of "who hits whom". Fighters only spawn volumes and receive hits (SRP).

signal hit_landed(impact_position: Vector2, attack: AttackData)

var _fighters: Array[Fighter] = []


func _ready() -> void:
	# Run after fighters and projectiles have moved this tick.
	process_physics_priority = 100


func register_fighter(fighter: Fighter) -> void:
	_fighters.append(fighter)


## O(V * F) time per tick (V live volumes, F = 2 fighters), O(1) extra space.
func _physics_process(_delta: float) -> void:
	for node in get_tree().get_nodes_in_group(HitVolume.GROUP):
		var volume := node as HitVolume
		for fighter in _fighters:
			_resolve_hit(volume, fighter)


func _resolve_hit(volume: HitVolume, fighter: Fighter) -> void:
	if not volume.can_strike(fighter) or not fighter.can_be_struck():
		return
	var overlap := volume.compute_hit_rect().intersection(fighter.compute_hurt_rect())
	if not overlap.has_area():
		return
	fighter.receive_hit(volume.attack, volume.compute_direction_to(fighter))
	volume.register_strike(fighter)
	hit_landed.emit(overlap.get_center(), volume.attack)
