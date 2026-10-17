class_name SelectionCursor
extends RefCounted
## One player's pointer on the roster grid. Locked once confirmed.

var index: int
var confirmed := false
var _count: int


func _init(count: int, start_index: int) -> void:
	_count = count
	index = posmod(start_index, count)


func move_by(step: int) -> void:
	if not confirmed:
		index = posmod(index + step, _count)


func confirm() -> void:
	confirmed = true


func cancel() -> void:
	confirmed = false
