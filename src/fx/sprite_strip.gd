class_name SpriteStrip
extends RefCounted
## Cuts a horizontal strip of frames into AtlasTextures.


static func create_frame(sheet: Texture2D, index: int, frame_size: Vector2i) -> AtlasTexture:
	var frame := AtlasTexture.new()
	frame.atlas = sheet
	frame.region = Rect2(index * frame_size.x, 0, frame_size.x, frame_size.y)
	return frame


## Square frames: the strip height is the frame size.
static func create_frames(sheet: Texture2D, fps: float, loop: bool) -> SpriteFrames:
	return create_frames_of_width(sheet, sheet.get_height(), fps, loop)


## O(n) time and space, n = frames in the strip.
static func create_frames_of_width(sheet: Texture2D, frame_width: int, fps: float, loop: bool) -> SpriteFrames:
	var frame_size := Vector2i(frame_width, sheet.get_height())
	var frames := SpriteFrames.new()
	frames.set_animation_speed(&"default", fps)
	frames.set_animation_loop(&"default", loop)
	for index in sheet.get_width() / frame_width:
		frames.add_frame(&"default", create_frame(sheet, index, frame_size))
	return frames
