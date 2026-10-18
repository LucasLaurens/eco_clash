extends Node
## Headless runner: godot --headless --path . --fixed-fps 60 res://tests/test_runner.tscn [-- --only=unit|features]
## Exit code 1 on any failure. Every test name is printed, so a silent suite cannot pass unseen.
## Suites are discovered by folder: a new test_*.gd file runs without being registered anywhere.

const SUITE_FOLDERS := {
	"unit": "res://tests/unit",
	"features": "res://tests/features",
}
const ONLY_FLAG := "--only="
const SUITE_PREFIX := "test_"
const SUITE_EXTENSION := ".gd"

var _total := 0
var _failed := 0


func _ready() -> void:
	for folder in _resolve_folders():
		for suite_path in _list_suites(folder):
			await _run_suite(load(suite_path).new())
	print("\n%d tests, %d failed" % [_total, _failed])
	get_tree().quit(1 if _failed > 0 or _total == 0 else 0)


## All folders by default; `-- --only=unit` or `-- --only=features` narrows the run (CI runs them as two steps).
func _resolve_folders() -> Array[String]:
	var folders: Array[String] = []
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with(ONLY_FLAG):
			var kind := argument.trim_prefix(ONLY_FLAG)
			assert(SUITE_FOLDERS.has(kind), "Unknown test kind '%s'" % kind)
			folders.append(SUITE_FOLDERS[kind])
	if folders.is_empty():
		folders.assign(SUITE_FOLDERS.values())
	return folders


func _list_suites(folder: String) -> Array[String]:
	var suites: Array[String] = []
	for file_name in DirAccess.get_files_at(folder):
		if file_name.begins_with(SUITE_PREFIX) and file_name.ends_with(SUITE_EXTENSION):
			suites.append(folder.path_join(file_name))
	suites.sort()
	return suites


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
			_print_report(
				test_name, suite.failures.filter(func(failure: String) -> bool: return failure.begins_with(test_name))
			)


func _print_report(test_name: String, failures: Array) -> void:
	_total += 1
	if failures.is_empty():
		print("  ok   %s" % test_name)
		return
	_failed += 1
	print("  FAIL %s" % test_name)
	for failure: String in failures:
		print("       - %s" % failure)
