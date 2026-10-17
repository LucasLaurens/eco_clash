class_name BotPerception
extends RefCounted
## Snapshot of what the bot can see this tick. Plain data, so the brain is testable without a scene.

var self_position := Vector2.ZERO
var self_velocity := Vector2.ZERO
var self_on_floor := false
var self_has_air_jump := false
var target_position := Vector2.ZERO
var target_in_play := true
var ground := Rect2()
