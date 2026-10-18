extends Control
## Victory screen: the winner, the match length, and three ways to continue.

const PREVIEW_SCALE := 2.0


func _ready() -> void:
	var result: MatchResult = MatchSettings.last_result
	UiKit.add_backdrop(self, 0.55)
	var column := UiKit.create_centered_column(self, 5)
	column.add_child(UiKit.create_label(UiText.RESULT_VICTORY, UiKit.FONT_HUGE, UiKit.TEXT_GOLD))
	column.add_child(_build_winner_preview(result.winner_definition))
	column.add_child(UiKit.create_label(
		UiText.RESULT_WINNER % [result.winner_label, result.winner_definition.display_name], UiKit.FONT_SMALL, result.winner_definition.accent_color
	))
	column.add_child(UiKit.create_label(result.format_duration(), UiKit.FONT_SMALL, UiKit.TEXT_MUTED))
	var rematch_button := UiKit.create_button(UiText.RESULT_REMATCH, _change_scene_to.bind(ScenePaths.FIGHT))
	column.add_child(rematch_button)
	column.add_child(UiKit.create_button(UiText.RESULT_RESELECT, _change_scene_to.bind(ScenePaths.CHARACTER_SELECT)))
	column.add_child(UiKit.create_button(UiText.RESULT_MENU, _change_scene_to.bind(ScenePaths.MAIN_MENU)))
	rematch_button.grab_focus()


func _build_winner_preview(winner: FighterDefinition) -> Control:
	var preview_box := Control.new()
	preview_box.custom_minimum_size = Vector2(0, 84)
	var sprite := AnimatedSprite2D.new()
	sprite.sprite_frames = FighterSpriteFrames.create(winner.sprite_sheet)
	sprite.scale = Vector2.ONE * PREVIEW_SCALE
	sprite.position = Vector2(0, 40)
	sprite.play(&"idle")
	preview_box.add_child(sprite)
	preview_box.resized.connect(func() -> void: sprite.position.x = preview_box.size.x / 2.0)
	return preview_box


func _change_scene_to(scene_path: String) -> void:
	get_tree().change_scene_to_file(scene_path)
