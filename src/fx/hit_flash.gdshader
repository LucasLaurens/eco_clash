shader_type canvas_item;
// Fighting-game hit flash: the struck sprite turns to a warm white for a few frames.

uniform float flash_amount : hint_range(0.0, 1.0) = 0.0;
uniform vec3 flash_color : source_color = vec3(1.0, 0.97, 0.9);

void fragment() {
	vec4 texel = texture(TEXTURE, UV) * COLOR;
	COLOR = vec4(mix(texel.rgb, flash_color, flash_amount), texel.a);
}
