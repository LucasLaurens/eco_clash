class_name MatchConfig
extends RefCounted
## Who fights whom and how. Built by the menus, read by the fight scene.

enum Mode { VS_BOT, VERSUS, DEMO }

const DEFAULT_STOCKS := 3
const SLOT_COUNT := 2

var mode: Mode
var definitions: Array[FighterDefinition]
var stocks := DEFAULT_STOCKS


static func create(
	match_mode: Mode, first_definition: FighterDefinition, second_definition: FighterDefinition
) -> MatchConfig:
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


## Key of the slot's identity assets (selector, in-fight marker): "p1", "p2" or "bot".
func resolve_slot_tag(slot: int) -> String:
	return "bot" if is_bot_slot(slot) else "p%d" % (slot + 1)


## Short form for tight spots (HUD card), same words as the floating marker: "1P", "2P", "BOT".
func format_short_slot_label(slot: int) -> String:
	return UiText.SLOT_BOT if is_bot_slot(slot) else UiText.SLOT_TAG_PLAYER % (slot + 1)


func format_slot_label(slot: int) -> String:
	return UiText.SLOT_BOT if is_bot_slot(slot) else UiText.SLOT_PLAYER % (slot + 1)


## Human slot index -> control scheme number. In VS_BOT player 1 drives both menu cursors.
func compute_scheme_number(slot: int) -> int:
	return 1 if mode == Mode.VS_BOT else slot + 1
