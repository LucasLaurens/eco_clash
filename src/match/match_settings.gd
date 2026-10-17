extends Node
## Autoload: carries the match setup and the last result across scene changes.

const DEMO_FLAG := "--demo"

var pending_mode := MatchConfig.Mode.VS_BOT
var current := MatchConfig.create(MatchConfig.Mode.VS_BOT, FighterRoster.find_at(0), FighterRoster.find_at(3))
var last_result := MatchResult.create(0, FighterRoster.find_at(0), UiText.SLOT_PLAYER % 1, 0.0)


## `godot --path . res://scenes/fight.tscn -- --demo` watches two bots fight.
func resolve_config() -> MatchConfig:
	if DEMO_FLAG in OS.get_cmdline_user_args():
		return MatchConfig.create(MatchConfig.Mode.DEMO, FighterRoster.find_at(0), FighterRoster.find_at(2))
	return current
