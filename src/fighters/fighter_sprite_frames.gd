class_name FighterSpriteFrames
extends RefCounted
## Builds SpriteFrames from a fighter sheet using layout.json, written by the asset generator.
## One layout file for Python and Godot: frame indices are never duplicated by hand.

const LAYOUT_PATH := "res://assets/fighters/layout.json"

static var _layout: Dictionary = {}
static var _cache: Dictionary[Texture2D, SpriteFrames] = {}


static func create(sheet: Texture2D) -> SpriteFrames:
	if _cache.has(sheet):
		return _cache[sheet]
	var layout := read_layout()
	var size := Vector2i(int(layout["frame_size"]), int(layout["frame_size"]))
	var frames := SpriteFrames.new()
	frames.remove_animation(&"default")
	for animation_name: String in layout["animations"]:
		var spec: Dictionary = layout["animations"][animation_name]
		frames.add_animation(animation_name)
		frames.set_animation_speed(animation_name, float(spec["fps"]))
		frames.set_animation_loop(animation_name, bool(spec["loop"]))
		for index in spec["frames"]:
			frames.add_frame(animation_name, SpriteStrip.create_frame(sheet, int(index), size))
	_cache[sheet] = frames
	return frames


## Sprite offset that puts the drawn feet exactly on the body origin.
static func compute_sprite_offset() -> Vector2:
	var layout := read_layout()
	return Vector2(0.0, float(layout["frame_size"]) / 2.0 - float(layout["feet_y"]) - 1.0)


static func read_layout() -> Dictionary:
	if _layout.is_empty():
		_layout = JSON.parse_string(FileAccess.get_file_as_string(LAYOUT_PATH))
	return _layout
