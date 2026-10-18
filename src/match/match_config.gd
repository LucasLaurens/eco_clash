class_name MatchConfig
extends RefCounted
## Who fights whom and how. Built by the menus, read by the fight scene.

enum Mode { VS_BOT, VERSUS, DEMO }

const DEFAULT_STOCKS := 3
const SLOT_COUNT := 2

var mode: Mode
var definitions: Array[FighterDefinition]
var stocks := DEFAULT_STOCKS


static func create(match_mode: Mode, first_definition: FighterDefinition, second_definition: FighterDefinition) -> MatchConfig:
	var config := MatchConfig.new()
	config.mode = match_mode
	config.definitions = [first_definition, second_definition]
	return config


func is_bot_slot(slot: int) -> bool:
	match mode:
		Mode.DEMO:
			return true
		Mode.VS_BOT:
			return slot == 1
	return false


func format_slot_label(slot: int) -> String:
	return UiText.SLOT_BOT if is_bot_slot(slot) else UiText.SLOT_PLAYER % (slot + 1)


## Human slot index -> keyboard layout number. In VS_BOT player 1 drives both menu cursors.
func compute_scheme_number(slot: int) -> int:
	return 1 if mode == Mode.VS_BOT else slot + 1
