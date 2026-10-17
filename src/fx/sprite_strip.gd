class_name SpriteStrip
extends RefCounted
## Cuts a horizontal strip of square frames into AtlasTextures.


static func create_frame(sheet: Texture2D, index: int, size: Vector2i) -> AtlasTexture:
	var frame := AtlasTexture.new()
	frame.atlas = sheet
	frame.region = Rect2(index * size.x, 0, size.x, size.y)
	return frame


## Square frames: the strip height is the frame size.
static func create_frames(sheet: Texture2D, fps: float, loop: bool) -> SpriteFrames:
	var size := Vector2i(sheet.get_height(), sheet.get_height())
	var frames := SpriteFrames.new()
	frames.set_animation_speed(&"default", fps)
	frames.set_animation_loop(&"default", loop)
	for index in sheet.get_width() / size.x:
		frames.add_frame(&"default", create_frame(sheet, index, size))
	return frames
