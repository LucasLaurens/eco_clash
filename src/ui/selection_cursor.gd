class_name SelectionCursor
extends RefCounted
## One player's pointer on the roster grid. Locked once confirmed.

var index: int
var confirmed := false
var _option_count: int


func _init(option_count: int, start_index: int) -> void:
	_option_count = option_count
	index = posmod(start_index, option_count)


func move_by(step: int) -> void:
	if not confirmed:
		index = posmod(index + step, _option_count)


func confirm() -> void:
	confirmed = true


func cancel() -> void:
	confirmed = false
