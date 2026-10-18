extends Node2D
## Fight scene controller: spawns fighters, runs the countdown, watches the blast zone, ends the match.

const FIGHTER_SCENE := preload("res://scenes/fighter.tscn")
const SPAWN_HEIGHT := 16.0
const KO_TRAUMA := 0.7
const TRAUMA_PER_DAMAGE := 0.03
const HITSTOP_BASE := 0.03
const HITSTOP_PER_DAMAGE := 0.004
const HITSTOP_TIME_SCALE := 0.05
const FINISH_TIME_SCALE := 0.35
const FINISH_DELAY := 2.0

var _config: MatchConfig
var _fighters: Array[Fighter] = []
var _elapsed_seconds := 0.0
var _match_over := false

@onready var _stage: Stage = $Stage
@onready var _world: Node2D = $World
@onready var _resolver: CombatResolver = $CombatResolver
@onready var _camera: ShakeCamera = $Camera
@onready var _hud: Hud = $Hud


func _ready() -> void:
	_config = MatchSettings.resolve_config()
	for slot in MatchConfig.SLOT_COUNT:
		_fighters.append(_spawn_fighter(slot))
	_resolver.hit_landed.connect(_on_hit_landed)
	_hud.bind_fighters(_fighters, _config)
	await _hud.play_countdown()
	_attach_controllers()


func _exit_tree() -> void:
	Engine.time_scale = 1.0


func _physics_process(delta: float) -> void:
	if _match_over:
		return
	_elapsed_seconds += delta
	for fighter in _fighters:
		if fighter.is_in_play() and not _stage.is_inside_blast_zone(fighter.global_position):
			_knock_out(fighter)


func _spawn_fighter(slot: int) -> Fighter:
	var fighter: Fighter = FIGHTER_SCENE.instantiate()
	_world.add_child(fighter)
	fighter.configure(_config.definitions[slot], _world, _config.stocks)
	fighter.global_position = _stage.get_spawn_position(slot) - Vector2(0.0, SPAWN_HEIGHT)
	fighter.facing = 1 if slot == 0 else -1
	_resolver.register_fighter(fighter)
	return fighter


func _attach_controllers() -> void:
	for slot in _fighters.size():
		_fighters[slot].attach_input(InputSourceFactory.create(_config, slot, _fighters, _stage))


func _knock_out(fighter: Fighter) -> void:
	_camera.add_trauma(KO_TRAUMA)
	fighter.lose_stock()
	if fighter.has_stocks_left():
		fighter.respawn_at(_stage.get_spawn_position(_fighters.find(fighter)) - Vector2(0.0, SPAWN_HEIGHT * 3.0))
		return
	_finish_match(_fighters.find(fighter))


func _finish_match(loser_slot: int) -> void:
	_match_over = true
	var winner_slot := MatchConfig.SLOT_COUNT - 1 - loser_slot
	MatchSettings.last_result = MatchResult.create(
		winner_slot, _config.definitions[winner_slot], _config.format_slot_label(winner_slot), _elapsed_seconds
	)
	for fighter in _fighters:
		fighter.attach_input(NullInputSource.new())
	_hud.show_banner(UiText.GAME_SET)
	Engine.time_scale = FINISH_TIME_SCALE
	await get_tree().create_timer(FINISH_DELAY, true, false, true).timeout
	Engine.time_scale = 1.0
	get_tree().change_scene_to_file(ScenePaths.RESULTS)


func _on_hit_landed(impact_position: Vector2, attack: AttackData) -> void:
	_world.add_child(HitSpark.create(impact_position))
	_camera.add_trauma(attack.damage * TRAUMA_PER_DAMAGE)
	if not _match_over:
		_freeze_frames(HITSTOP_BASE + attack.damage * HITSTOP_PER_DAMAGE)


## Hit-stop: a few frames of near-freeze sell the impact.
func _freeze_frames(duration: float) -> void:
	Engine.time_scale = HITSTOP_TIME_SCALE
	await get_tree().create_timer(duration, true, false, true).timeout
	if not _match_over:
		Engine.time_scale = 1.0
