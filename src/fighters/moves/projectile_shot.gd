class_name ProjectileShot
extends FighterMove
## Fires a travelling hit volume.

const FPS := 10.0

@export var speed := 240.0
@export var lifetime := 1.4
@export var sprite_sheet: Texture2D

var _frames: SpriteFrames


func trigger_effect(user: Fighter) -> void:
	if _frames == null:
		_frames = SpriteStrip.create_frames(sprite_sheet, FPS, true)
	user.launch_projectile(attack, speed, lifetime, _frames)
