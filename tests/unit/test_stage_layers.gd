extends TestCase
## Fighters drop through platforms by toggling one mask bit: the stage must use that very layer.

const STAGE_SCENE := preload("res://scenes/stage.tscn")


func test_platforms_live_on_the_fighter_drop_layer() -> void:
	# Arrange
	var stage := STAGE_SCENE.instantiate()
	# Act
	var platforms := stage.get_node("Platforms").get_children()
	# Assert
	assert_equal(platforms.size(), 3, "three floating platforms")
	for platform: StaticBody2D in platforms:
		assert_true(platform.get_collision_layer_value(Fighter.PLATFORM_LAYER), "%s on platform layer" % platform.name)
		assert_true((platform.get_node("Shape") as CollisionShape2D).one_way_collision, "%s is one-way" % platform.name)
	stage.free()


func test_animated_layers_match_their_nodes_and_sheets() -> void:
	# Arrange
	var stage := STAGE_SCENE.instantiate()
	var layers := Stage.read_animated_layers()
	# Act & Assert
	assert_true(not layers.is_empty(), "generator wrote animated layers")
	for node_name: String in layers:
		var spec: Dictionary = layers[node_name]
		var sheet: Texture2D = load(Stage.STAGE_ASSETS_DIR + String(spec["sheet"]))
		assert_true(stage.get_node_or_null(node_name) is AnimatedSprite2D, "%s node exists in the stage" % node_name)
		assert_true(
			sheet != null and sheet.get_width() % int(spec["frame_width"]) == 0,
			"%s sheet splits into whole frames" % node_name
		)
	stage.free()
