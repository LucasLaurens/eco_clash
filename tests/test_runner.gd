extends Node
## Headless runner: godot --headless --path . --fixed-fps 60 res://tests/test_runner.tscn
## Exit code 1 on any failure. Every test name is printed, so a silent suite cannot pass unseen.

const SUITES: Array[Script] = [
	preload("res://tests/unit/test_knockback_formula.gd"),
	preload("res://tests/unit/test_attack_data.gd"),
	preload("res://tests/unit/test_bot_brain.gd"),
	preload("res://tests/unit/test_selection_cursor.gd"),
	preload("res://tests/unit/test_match_config.gd"),
	preload("res://tests/unit/test_roster.gd"),
	preload("res://tests/unit/test_ui_text.gd"),
	preload("res://tests/unit/test_stage_layers.gd"),
	preload("res://tests/unit/test_fighter_visuals.gd"),
	preload("res://tests/unit/test_match_simulation.gd"),
]

var _total := 0
var _failed := 0


func _ready() -> void:
	for suite_script in SUITES:
		await _run_suite(suite_script.new())
	print("\n%d tests, %d failed" % [_total, _failed])
	get_tree().quit(1 if _failed > 0 else 0)


func _run_suite(suite: TestCase) -> void:
	print("\n# %s" % suite.get_script().resource_path.get_file())
	for method in suite.get_method_list():
		var test_name: String = method["name"]
		if test_name.begins_with("test_"):
			suite.failures.clear()
			suite.call(test_name)
			_print_report(test_name, suite.failures)
	suite.failures.clear()
	await suite.run_scenarios(self)
	if suite.has_meta(&"scenario_names"):
		for test_name: String in suite.get_meta(&"scenario_names"):
			_print_report(test_name, suite.failures.filter(func(failure: String) -> bool: return failure.begins_with(test_name)))


func _print_report(test_name: String, failures: Array) -> void:
	_total += 1
	if failures.is_empty():
		print("  ok   %s" % test_name)
		return
	_failed += 1
	print("  FAIL %s" % test_name)
	for failure: String in failures:
		print("       - %s" % failure)
