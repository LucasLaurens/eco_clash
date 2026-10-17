class_name TestCase
extends RefCounted
## Minimal xUnit base: methods named test_* are run by tests/test_runner.gd.

var failures: Array[String] = []


func assert_true(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)


func assert_equal(actual: Variant, expected: Variant, message: String) -> void:
	if actual != expected:
		failures.append("%s (expected %s, got %s)" % [message, expected, actual])


## Scene-tree scenarios (async). Override when a suite needs real frames.
func run_scenarios(_host: Node) -> void:
	pass
