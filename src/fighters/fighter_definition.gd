class_name FighterDefinition
extends Resource
## Everything that makes one character unique. Pure data, editable in the Godot inspector.

const SPEED_RANGE := Vector2(90.0, 170.0)
const POWER_RANGE := Vector2(10.0, 24.0)
const WEIGHT_RANGE := Vector2(70.0, 140.0)
const MAX_RATING := 5

@export var id: StringName
@export var display_name := ""
@export var title := ""
@export var accent_color := Color.WHITE
@export var sprite_sheet: Texture2D
@export var portrait: Texture2D
@export var stock_icon: Texture2D
@export var body_size := Vector2(14, 28)
@export var run_speed := 130.0
@export var jump_velocity := 340.0
@export var air_jumps := 1
@export var weight := 100.0
@export var light_attack: FighterMove
@export var special: FighterMove


func compute_speed_rating() -> int:
	return _compute_rating(run_speed, SPEED_RANGE)


func compute_power_rating() -> int:
	return _compute_rating(light_attack.compute_rated_damage() + special.compute_rated_damage(), POWER_RANGE)


func compute_weight_rating() -> int:
	return _compute_rating(weight, WEIGHT_RANGE)


func get_special_name() -> String:
	return special.display_name


func get_special_description() -> String:
	return special.description


func _compute_rating(value: float, value_range: Vector2) -> int:
	var ratio := inverse_lerp(value_range.x, value_range.y, value)
	return clampi(1 + roundi(ratio * (MAX_RATING - 1)), 1, MAX_RATING)
