class_name Stage
extends Node2D
## The arena: solid ground, pass-through platforms, spawn points and the blast zone.

## Leaving this rectangle costs a stock.
@export var blast_zone := Rect2(-110, -150, 700, 500)

@onready var _ground_shape: CollisionShape2D = $Ground/Shape
@onready var _spawn_markers: Array[Node] = $Spawns.get_children()


func is_inside_blast_zone(point: Vector2) -> bool:
	return blast_zone.has_point(point)


func get_spawn_position(slot: int) -> Vector2:
	return (_spawn_markers[slot] as Marker2D).global_position


## Read from the collision shape itself, so there is one source of truth for the floor.
func compute_ground_surface() -> Rect2:
	var size := (_ground_shape.shape as RectangleShape2D).size
	return Rect2(_ground_shape.global_position - size / 2.0, size)
