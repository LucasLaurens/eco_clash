class_name InputSourceFactory
extends RefCounted
## Picks the controller of each slot: keyboard or bot. The fight scene never branches on it.


static func create(config: MatchConfig, slot: int, fighters: Array[Fighter], stage: Stage) -> InputSource:
	if not config.is_bot_slot(slot):
		return KeyboardInputSource.new(ControlScheme.new(config.compute_scheme_number(slot)))
	var rng := RandomNumberGenerator.new()
	rng.randomize()
	var opponent := fighters[MatchConfig.SLOT_COUNT - 1 - slot]
	return BotInputSource.new(BotBrain.new(rng), fighters[slot], opponent, stage)
