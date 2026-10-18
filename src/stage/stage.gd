class_name Stage
extends Node2D
## The arena: solid ground, pass-through platforms, spawn points and the blast zone.

## Written by the asset generator next to the sheets, so placement and timing have one source.
const ANIMATED_LAYERS_PATH := "res://assets/stage/animated_layers.json"
const STAGE_ASSETS_DIR := "res://assets/stage/"

## Leaving this rectangle costs a stock.
@export var blast_zone := Rect2(-110, -150, 700, 500)

@onready var _ground_shape: CollisionShape2D = $Ground/Shape
@onready var _spawn_markers: Array[Node] = $Spawns.get_children()


func _ready() -> void:
	_start_animated_layers()


func is_inside_blast_zone(point: Vector2) -> bool:
	return blast_zone.has_point(point)


func get_spawn_position(slot: int) -> Vector2:
	return (_spawn_markers[slot] as Marker2D).global_position


## Read from the collision shape itself, so there is one source of truth for the floor.
func compute_ground_surface() -> Rect2:
	var size := (_ground_shape.shape as RectangleShape2D).size
	return Rect2(_ground_shape.global_position - size / 2.0, size)


static func read_animated_layers() -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string(ANIMATED_LAYERS_PATH))


## O(n) time, n = animated layers (waterfall, sea glints).
func _start_animated_layers() -> void:
	var layers := read_animated_layers()
	for node_name: String in layers:
		var spec: Dictionary = layers[node_name]
		var sheet: Texture2D = load(STAGE_ASSETS_DIR + String(spec["sheet"]))
		var layer := get_node(node_name) as AnimatedSprite2D
		layer.sprite_frames = SpriteStrip.create_frames_of_width(
			sheet, int(spec["frame_width"]), float(spec["fps"]), true
		)
		layer.centered = false
		layer.position = Vector2(spec["offset"][0], spec["offset"][1])
		layer.play()
