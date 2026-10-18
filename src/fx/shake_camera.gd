class_name ShakeCamera
extends Camera2D
## Trauma-based screen shake: shake strength is trauma squared, trauma decays over time.

const DECAY_PER_SECOND := 2.5
const MAX_OFFSET := 6.0

var _trauma := 0.0
var _rng := RandomNumberGenerator.new()


func add_trauma(amount: float) -> void:
	_trauma = minf(_trauma + amount, 1.0)


func _process(delta: float) -> void:
	_trauma = maxf(_trauma - DECAY_PER_SECOND * delta, 0.0)
	var shake_amplitude := _trauma * _trauma * MAX_OFFSET
	offset = Vector2(roundf(_rng.randf_range(-shake_amplitude, shake_amplitude)), roundf(_rng.randf_range(-shake_amplitude, shake_amplitude)))
