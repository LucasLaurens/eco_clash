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
