class_name ProjectileShot
extends FighterMove
## Fires a travelling hit volume: straight, or thrown in an arc when lift and gravity are set.

const FPS := 10.0

@export var speed := 240.0
## Initial upward speed. Zero flies straight.
@export var lift := 0.0
@export var gravity := 0.0
@export var lifetime := 1.4
@export var sprite_sheet: Texture2D

var _frames: SpriteFrames


func trigger_effect(user: Fighter) -> void:
	if _frames == null:
		_frames = SpriteStrip.create_frames(sprite_sheet, FPS, true)
	user.launch_projectile(attack, Vector2(speed, -lift), gravity, lifetime, _frames)
