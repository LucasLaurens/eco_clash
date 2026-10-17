class_name FighterRoster
extends RefCounted
## The four selectable fighters, in menu order.

const DEFINITIONS := [
	preload("res://data/fighters/kael.tres"),
	preload("res://data/fighters/pip.tres"),
	preload("res://data/fighters/grondak.tres"),
	preload("res://data/fighters/nyra.tres"),
]


static func list_all() -> Array[FighterDefinition]:
	var all: Array[FighterDefinition] = []
	all.assign(DEFINITIONS)
	return all


static func find_at(index: int) -> FighterDefinition:
	return DEFINITIONS[posmod(index, DEFINITIONS.size())]


static func count() -> int:
	return DEFINITIONS.size()
