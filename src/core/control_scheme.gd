class_name ControlScheme
extends RefCounted
## Keyboard layout of one human player. Physical keys, so ZQSD on AZERTY and WASD on QWERTY.

enum Action { LEFT, RIGHT, UP, DOWN, ATTACK, SPECIAL }

const PLAYER_KEYS := {
	1:
	{
		Action.LEFT: KEY_A,
		Action.RIGHT: KEY_D,
		Action.UP: KEY_W,
		Action.DOWN: KEY_S,
		Action.ATTACK: KEY_F,
		Action.SPECIAL: KEY_G,
	},
	2:
	{
		Action.LEFT: KEY_LEFT,
		Action.RIGHT: KEY_RIGHT,
		Action.UP: KEY_UP,
		Action.DOWN: KEY_DOWN,
		Action.ATTACK: KEY_K,
		Action.SPECIAL: KEY_L,
	},
}

const HEADLESS_DISPLAY_SERVER := "headless"
const ARROW_GLYPHS := {
	KEY_LEFT: "←",
	KEY_RIGHT: "→",
	KEY_UP: "↑",
	KEY_DOWN: "↓",
}

var player: int


func _init(player_number: int) -> void:
	assert(PLAYER_KEYS.has(player_number), "No keyboard layout for player %d" % player_number)
	player = player_number


static func register_all_actions() -> void:
	for player_number: int in PLAYER_KEYS:
		var scheme := ControlScheme.new(player_number)
		for action: Action in PLAYER_KEYS[player_number]:
			scheme._register_action(action)


func resolve_action_name(action: Action) -> StringName:
	return StringName("p%d_%s" % [player, Action.keys()[action].to_lower()])


func format_key_label(action: Action) -> String:
	var physical_key: Key = PLAYER_KEYS[player][action]
	if ARROW_GLYPHS.has(physical_key):
		return ARROW_GLYPHS[physical_key]
	return OS.get_keycode_string(_resolve_layout_key(physical_key)).to_upper()


## The key this physical position types on the user's layout (ZQSD on AZERTY). A headless display server
## (tests, CI) has no keyboard layout, so it keeps the physical key instead of logging an error per call.
func _resolve_layout_key(physical_key: Key) -> Key:
	if DisplayServer.get_name() == HEADLESS_DISPLAY_SERVER:
		return physical_key
	var localized_key := DisplayServer.keyboard_get_label_from_physical(physical_key)
	return localized_key if localized_key != KEY_NONE else physical_key


func _register_action(action: Action) -> void:
	var action_name := resolve_action_name(action)
	if InputMap.has_action(action_name):
		return
	InputMap.add_action(action_name)
	var event := InputEventKey.new()
	event.physical_keycode = PLAYER_KEYS[player][action]
	InputMap.action_add_event(action_name, event)
