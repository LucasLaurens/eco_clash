extends TestCase
## Feature scenarios on the menus: real scenes, real input events. No scenario ever confirms a choice that
## would change scene, since change_scene_to_file would replace the test runner itself.

const MAIN_MENU_SCENE := preload("res://scenes/ui/main_menu.tscn")
const CHARACTER_SELECT_SCENE := preload("res://scenes/ui/character_select.tscn")
const RESULTS_SCENE := preload("res://scenes/ui/results.tscn")
const MENU_CHOICES := 3
const SCENARIOS: Array[String] = [
	"main_menu_offers_three_choices",
	"character_select_moves_and_confirms",
	"results_show_winner_and_duration",
	"escape_toggles_the_pause",
]


func run_scenarios(host: Node) -> void:
	set_meta(&"scenario_names", SCENARIOS)
	await _test_main_menu_offers_three_choices(host)
	await _test_character_select_moves_and_confirms(host)
	await _test_results_show_winner_and_duration(host)
	await _test_escape_toggles_the_pause(host)


func _test_main_menu_offers_three_choices(host: Node) -> void:
	var scenario_name := "main_menu_offers_three_choices"
	# Arrange
	var menu := MAIN_MENU_SCENE.instantiate()
	# Act
	host.add_child(menu)
	await host.get_tree().process_frame
	# Assert
	var buttons := menu.find_children("*", "Button", true, false)
	assert_equal(buttons.size(), MENU_CHOICES, "%s: three buttons" % scenario_name)
	assert_true((buttons[0] as Button).has_focus(), "%s: first choice focused" % scenario_name)
	assert_true(_has_label_containing(menu, UiText.CONTROLS_P1), "%s: controls reminder" % scenario_name)
	_dispose(host, menu)


func _test_character_select_moves_and_confirms(host: Node) -> void:
	var scenario_name := "character_select_moves_and_confirms"
	# Arrange
	MatchSettings.pending_mode = MatchConfig.Mode.VS_BOT
	var select := CHARACTER_SELECT_SCENE.instantiate()
	host.add_child(select)
	await host.get_tree().process_frame
	var scheme := ControlScheme.new(1)
	# Act
	await _press(host, scheme.resolve_action_name(ControlScheme.Action.RIGHT))
	await _press(host, scheme.resolve_action_name(ControlScheme.Action.ATTACK))
	# Assert
	assert_true(
		_has_label_containing(select, FighterRoster.find_at(1).display_name),
		"%s: cursor moved to the 2nd fighter" % scenario_name
	)
	assert_true(_has_label_containing(select, UiText.SELECT_READY), "%s: player 1 is ready" % scenario_name)
	_dispose(host, select)


func _test_results_show_winner_and_duration(host: Node) -> void:
	var scenario_name := "results_show_winner_and_duration"
	# Arrange
	var winner := FighterRoster.find_at(1)
	var seconds := RandomNumberGenerator.new().randi_range(60, 599)
	MatchSettings.last_result = MatchResult.create(0, winner, UiText.SLOT_PLAYER % 1, seconds)
	# Act
	var results := RESULTS_SCENE.instantiate()
	host.add_child(results)
	await host.get_tree().process_frame
	# Assert
	assert_true(_has_label_containing(results, winner.display_name), "%s: winner named" % scenario_name)
	var duration := UiText.RESULT_DURATION % [seconds / 60, seconds % 60]
	assert_true(_has_label_containing(results, duration), "%s: duration shown" % scenario_name)
	_dispose(host, results)


func _test_escape_toggles_the_pause(host: Node) -> void:
	var scenario_name := "escape_toggles_the_pause"
	# Arrange
	var pause_menu := PauseMenu.new()
	host.add_child(pause_menu)
	await host.get_tree().process_frame
	# Act
	await _press(host, &"ui_cancel")
	var paused_after_first := host.get_tree().paused
	await _press(host, &"ui_cancel")
	# Assert
	assert_true(paused_after_first, "%s: escape pauses" % scenario_name)
	assert_true(not host.get_tree().paused, "%s: escape again resumes" % scenario_name)
	host.get_tree().paused = false
	_dispose(host, pause_menu)


## A full press: the action goes down, a frame passes, it comes back up.
func _press(host: Node, action: StringName) -> void:
	for pressed in [true, false]:
		var event := InputEventAction.new()
		event.action = action
		event.pressed = pressed
		Input.parse_input_event(event)
		await host.get_tree().process_frame


func _has_label_containing(root: Node, text: String) -> bool:
	return root.find_children("*", "Label", true, false).any(
		func(label: Label) -> bool: return label.text.contains(text)
	)


func _dispose(host: Node, scene: Node) -> void:
	host.remove_child(scene)
	scene.queue_free()
