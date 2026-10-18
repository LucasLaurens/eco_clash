class_name InputFrame
extends RefCounted
## One physics tick of fighter intent. Same shape whether it comes from a keyboard, a pad or a bot.

var move_x := 0.0
var down := false
var jump_pressed := false
var attack_pressed := false
var special_pressed := false
