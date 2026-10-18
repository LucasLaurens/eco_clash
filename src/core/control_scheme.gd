class_name ControlScheme
extends RefCounted
## Controls of one human player: a keyboard half (physical keys, so ZQSD on AZERTY and WASD on QWERTY)
## and a gamepad. Every binding of the game lives here, menus and fights read the same actions.

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
## Same pad layout for both players, only the device differs. Xbox names: A is the bottom face button
## (Cross on DualSense), B the right one (Circle), X the left one (Square). The first button is the one shown.
const PAD_BUTTONS := {
	Action.LEFT: [JOY_BUTTON_DPAD_LEFT],
	Action.RIGHT: [JOY_BUTTON_DPAD_RIGHT],
	Action.UP: [JOY_BUTTON_DPAD_UP, JOY_BUTTON_X],
	Action.DOWN: [JOY_BUTTON_DPAD_DOWN],
	Action.ATTACK: [JOY_BUTTON_A],
	Action.SPECIAL: [JOY_BUTTON_B],
}
const PAD_STICK := {
	Action.LEFT: [JOY_AXIS_LEFT_X, -1.0],
	Action.RIGHT: [JOY_AXIS_LEFT_X, 1.0],
	Action.UP: [JOY_AXIS_LEFT_Y, -1.0],
	Action.DOWN: [JOY_AXIS_LEFT_Y, 1.0],
}
## Half a tilt: a resting or worn stick never walks, and a slightly bent one never drops through a platform.
const STICK_DEADZONE := 0.5
const PAD_GLYPHS := {
	JOY_BUTTON_DPAD_LEFT: "←",
	JOY_BUTTON_DPAD_RIGHT: "→",
	JOY_BUTTON_DPAD_UP: "↑",
	JOY_BUTTON_DPAD_DOWN: "↓",
	JOY_BUTTON_A: "A",
	JOY_BUTTON_B: "B",
}
## Shared by every player: Escape or any pad's Start/Options opens the pause, and leaves the character select.
const PAUSE_ACTION := &"pause"
const PAUSE_KEY := KEY_ESCAPE
const PAUSE_PAD_BUTTON := JOY_BUTTON_START
## Godot's ui_accept knows no pad button: A validates the focused menu button, on any pad.
const MENU_ACCEPT_ACTION := &"ui_accept"
const MENU_ACCEPT_PAD_BUTTON := JOY_BUTTON_A
## Device id the InputMap reads as "any pad", as in Godot's own ui_up.
const ALL_PADS := -1
## Base of the device ids given to a player without a pad. Real pads get 0-15, the keyboard 16, the mouse 32,
## and Input drops negative ids below -1, so ids from here on are never sent by real hardware.
const PADLESS_DEVICE_BASE := 1000

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


## Idempotent: called at startup, then again on every pad plug or unplug so each player follows his pad.
static func register_all_actions() -> void:
	for player_number: int in PLAYER_KEYS:
		var scheme := ControlScheme.new(player_number)
		for action: Action in Action.values():
			scheme._register_action(action)
	_register_shared_actions()


func resolve_action_name(action: Action) -> StringName:
	return StringName("p%d_%s" % [player, Action.keys()[action].to_lower()])


## Player N owns the N-th connected pad. Without one, a device id no hardware ever sends: a lone pad must
## not drive both players.
func resolve_pad_device() -> int:
	var pads := Input.get_connected_joypads()
	pads.sort()
	return pads[player - 1] if pads.size() >= player else PADLESS_DEVICE_BASE + player


func has_pad() -> bool:
	return Input.get_connected_joypads().size() >= player


## What the on-screen hints show: the pad button when this player has a pad, the key otherwise.
func format_control_label(action: Action) -> String:
	return format_pad_label(action) if has_pad() else format_key_label(action)


func format_key_label(action: Action) -> String:
	var physical_key: Key = PLAYER_KEYS[player][action]
	if ARROW_GLYPHS.has(physical_key):
		return ARROW_GLYPHS[physical_key]
	return OS.get_keycode_string(_resolve_layout_key(physical_key)).to_upper()


func format_pad_label(action: Action) -> String:
	return PAD_GLYPHS[PAD_BUTTONS[action][0]]


## The key this physical position types on the user's layout (ZQSD on AZERTY). A headless display server
## (tests, CI) has no keyboard layout, so it keeps the physical key instead of logging an error per call.
func _resolve_layout_key(physical_key: Key) -> Key:
	if DisplayServer.get_name() == HEADLESS_DISPLAY_SERVER:
		return physical_key
	var localized_key := DisplayServer.keyboard_get_label_from_physical(physical_key)
	return localized_key if localized_key != KEY_NONE else physical_key


func _register_action(action: Action) -> void:
	var action_name := resolve_action_name(action)
	if not InputMap.has_action(action_name):
		InputMap.add_action(action_name, STICK_DEADZONE)
	InputMap.action_erase_events(action_name)
	var key_event := InputEventKey.new()
	key_event.physical_keycode = PLAYER_KEYS[player][action]
	InputMap.action_add_event(action_name, key_event)
	var device := resolve_pad_device()
	for button: JoyButton in PAD_BUTTONS[action]:
		InputMap.action_add_event(action_name, _create_pad_button_event(button, device))
	if PAD_STICK.has(action):
		var stick_event := InputEventJoypadMotion.new()
		stick_event.device = device
		stick_event.axis = PAD_STICK[action][0]
		stick_event.axis_value = PAD_STICK[action][1]
		InputMap.action_add_event(action_name, stick_event)


static func _register_shared_actions() -> void:
	if not InputMap.has_action(PAUSE_ACTION):
		InputMap.add_action(PAUSE_ACTION)
		var key_event := InputEventKey.new()
		key_event.physical_keycode = PAUSE_KEY
		InputMap.action_add_event(PAUSE_ACTION, key_event)
		InputMap.action_add_event(PAUSE_ACTION, _create_pad_button_event(PAUSE_PAD_BUTTON, ALL_PADS))
	var accept_event := _create_pad_button_event(MENU_ACCEPT_PAD_BUTTON, ALL_PADS)
	if not InputMap.action_has_event(MENU_ACCEPT_ACTION, accept_event):
		InputMap.action_add_event(MENU_ACCEPT_ACTION, accept_event)


static func _create_pad_button_event(button: JoyButton, device: int) -> InputEventJoypadButton:
	var event := InputEventJoypadButton.new()
	event.device = device
	event.button_index = button
	return event
