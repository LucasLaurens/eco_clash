class_name FighterStatus
extends RefCounted
## Timed conditions on one fighter: special cooldown, dark empowerment, haste, poison, paralysis.
## Pure data and timers, no scene: the fighter asks it questions and forwards the hits it takes.

const POISON_TICK := 0.5
const DARK_TINT := Color(0.42, 0.28, 0.58)
const HASTE_TINT := Color(0.7, 0.95, 1.0)
const POISON_TINT := Color(0.62, 1.0, 0.42)
const PARALYSIS_TINT := Color(0.78, 0.56, 1.0)

var _cooldown_left := 0.0
var _cooldown_total := 0.0
var _empowered_move: FighterMove
var _empowered_left := 0.0
var _is_empowerment_spent := false
var _haste_left := 0.0
var _haste_multiplier := 1.0
var _poison_ticks_left := 0
var _poison_per_tick := 0.0
var _poison_tick_left := 0.0
var _paralysis_left := 0.0


## O(1) per call: poison ticks at most a few times per second. Returns the poison damage due this step.
func tick_timers(delta: float) -> float:
	_cooldown_left = maxf(_cooldown_left - delta, 0.0)
	_empowered_left = maxf(_empowered_left - delta, 0.0)
	_haste_left = maxf(_haste_left - delta, 0.0)
	_paralysis_left = maxf(_paralysis_left - delta, 0.0)
	var poison_damage := 0.0
	_poison_tick_left -= delta
	while _poison_ticks_left > 0 and _poison_tick_left <= 0.0:
		poison_damage += _poison_per_tick
		_poison_ticks_left -= 1
		_poison_tick_left += POISON_TICK
	return poison_damage


func start_special_cooldown(duration: float) -> void:
	_cooldown_left = duration
	_cooldown_total = duration


func is_special_ready() -> bool:
	return _cooldown_left <= 0.0


## 0 right after a special, 1 once it can be used again.
func compute_special_readiness() -> float:
	if _cooldown_total <= 0.0:
		return 1.0
	return 1.0 - _cooldown_left / _cooldown_total


func empower(move: FighterMove, window: float) -> void:
	_empowered_move = move
	_empowered_left = window
	_is_empowerment_spent = false


func is_empowered() -> bool:
	return _empowered_left > 0.0 and not _is_empowerment_spent


func select_light_attack(default_move: FighterMove) -> FighterMove:
	return _empowered_move if is_empowered() else default_move


## The dark aura stays on for the strike itself, then fades.
func spend_empowerment(strike_duration: float) -> void:
	if not is_empowered():
		return
	_is_empowerment_spent = true
	_empowered_left = minf(_empowered_left, strike_duration)


func hasten(duration: float, multiplier: float) -> void:
	_haste_left = duration
	_haste_multiplier = multiplier


func compute_speed_multiplier() -> float:
	return _haste_multiplier if _haste_left > 0.0 else 1.0


## Every hit replaces the paralysis: a plain hit wakes a paralysed fighter up.
func apply_hit(attack: AttackData) -> void:
	_paralysis_left = attack.paralysis
	if attack.poison_damage <= 0.0:
		return
	_poison_ticks_left = maxi(roundi(attack.poison_duration / POISON_TICK), 1)
	_poison_per_tick = attack.poison_damage / _poison_ticks_left
	_poison_tick_left = POISON_TICK


func is_paralyzed() -> bool:
	return _paralysis_left > 0.0


## Strongest condition wins: paralysis, poison, dark aura, haste.
func resolve_tint() -> Color:
	if is_paralyzed():
		return PARALYSIS_TINT
	if _poison_ticks_left > 0:
		return POISON_TINT
	if _empowered_left > 0.0:
		return DARK_TINT
	if _haste_left > 0.0:
		return HASTE_TINT
	return Color.WHITE
