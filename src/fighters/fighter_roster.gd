class_name FighterRoster
extends RefCounted
## The selectable fighters, in menu order.

const DEFINITIONS := [
	preload("res://data/fighters/kael.tres"),
	preload("res://data/fighters/pip.tres"),
	preload("res://data/fighters/grondak.tres"),
	preload("res://data/fighters/ormos.tres"),
	preload("res://data/fighters/vargo.tres"),
	preload("res://data/fighters/kragg.tres"),
]


static func list_all() -> Array[FighterDefinition]:
	var definitions: Array[FighterDefinition] = []
	definitions.assign(DEFINITIONS)
	return definitions


static func find_at(index: int) -> FighterDefinition:
	return DEFINITIONS[posmod(index, DEFINITIONS.size())]


static func count() -> int:
	return DEFINITIONS.size()
