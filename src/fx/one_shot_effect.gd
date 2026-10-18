class_name OneShotEffect
extends AnimatedSprite2D
## A strip played once then freed: impact spark, landing dust, KO burst.

const HIT_SPARK := preload("res://assets/fx/hit_spark.png")
const DUST := preload("res://assets/fx/dust.png")
const KO_BURST := preload("res://assets/fx/ko_burst.png")
const FPS := 24.0

static var _frames_by_sheet: Dictionary[Texture2D, SpriteFrames] = {}


static func create(sheet: Texture2D, impact_position: Vector2, tint := Color.WHITE) -> OneShotEffect:
	if not _frames_by_sheet.has(sheet):
		_frames_by_sheet[sheet] = SpriteStrip.create_frames(sheet, FPS, false)
	var effect := OneShotEffect.new()
	effect.sprite_frames = _frames_by_sheet[sheet]
	effect.position = impact_position
	effect.modulate = tint
	return effect


func _ready() -> void:
	animation_finished.connect(queue_free)
	play()
