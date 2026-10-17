extends TestCase
## The pixel font is hand-made: any character it lacks would render as a blank. Encode that rule.

const FONT := preload("res://assets/fonts/eco_pixel.fnt")
const FORMAT_TOKEN := "%"


func test_font_draws_every_ui_string() -> void:
	# Arrange
	var texts: Array[String] = []
	for value: Variant in UiText.new().get_script().get_script_constant_map().values():
		if value is String:
			texts.append(value)
		elif value is Array:
			texts.append_array(value)
	for definition in FighterRoster.list_all():
		texts.append_array([definition.display_name, definition.title, definition.light_attack.display_name])
		texts.append_array([definition.compute_special_name(), definition.compute_special_description()])
	# Act & Assert
	for text in texts:
		for character in text.replace("%d", "").replace("%s", "").replace("%02d", "").replace("%%", FORMAT_TOKEN):
			assert_true(FONT.has_char(character.unicode_at(0)), "glyph '%s' missing (in \"%s\")" % [character, text])
