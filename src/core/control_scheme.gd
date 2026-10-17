class_name ControlScheme
extends RefCounted
## Keyboard layout of one human player. Physical keys, so ZQSD on AZERTY and WASD on QWERTY.

enum Action { LEFT, RIGHT, UP, DOWN, ATTACK, SPECIAL }

const PLAYER_KEYS := {
	1: {
		Action.LEFT: KEY_A,
		Action.RIGHT: KEY_D,
		Action.UP: KEY_W,
		Action.DOWN: KEY_S,
		Action.ATTACK: KEY_F,
		Action.SPECIAL: KEY_G,
	},
	2: {
		Action.LEFT: KEY_LEFT,
		Action.RIGHT: KEY_RIGHT,
		Action.UP: KEY_UP,
		Action.DOWN: KEY_DOWN,
		Action.ATTACK: KEY_K,
		Action.SPECIAL: KEY_L,
	},
}

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


func action(which: Action) -> StringName:
	return StringName("p%d_%s" % [player, Action.keys()[which].to_lower()])


func compute_key_label(which: Action) -> String:
	var physical: Key = PLAYER_KEYS[player][which]
	if ARROW_GLYPHS.has(physical):
		return ARROW_GLYPHS[physical]
	var localized := DisplayServer.keyboard_get_label_from_physical(physical)
	return OS.get_keycode_string(localized if localized != KEY_NONE else physical).to_upper()


func _register_action(which: Action) -> void:
	var name := action(which)
	if InputMap.has_action(name):
		return
	InputMap.add_action(name)
	var event := InputEventKey.new()
	event.physical_keycode = PLAYER_KEYS[player][which]
	InputMap.action_add_event(name, event)
