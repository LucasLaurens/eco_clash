class_name MatchResult
extends RefCounted

var winner_slot: int
var winner_definition: FighterDefinition
var winner_label: String
var duration_seconds: float


static func create(slot: int, definition: FighterDefinition, label: String, duration: float) -> MatchResult:
	var result := MatchResult.new()
	result.winner_slot = slot
	result.winner_definition = definition
	result.winner_label = label
	result.duration_seconds = duration
	return result


func format_duration() -> String:
	var total_seconds := int(duration_seconds)
	return UiText.RESULT_DURATION % [total_seconds / 60, total_seconds % 60]
