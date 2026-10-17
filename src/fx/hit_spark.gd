class_name HitSpark
extends AnimatedSprite2D
## One-shot impact flash.

const SHEET := preload("res://assets/fx/hit_spark.png")
const FPS := 24.0

static var _frames: SpriteFrames


static func create(at: Vector2) -> HitSpark:
	if _frames == null:
		_frames = SpriteStrip.create_frames(SHEET, FPS, false)
	var spark := HitSpark.new()
	spark.sprite_frames = _frames
	spark.position = at
	return spark


func _ready() -> void:
	animation_finished.connect(queue_free)
	play()
