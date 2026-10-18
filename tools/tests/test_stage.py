"""Stage layers: animated sheets cut into whole frames, every layer has its timing."""

import stage


def test_animated_layers_cut_into_whole_frames() -> None:
    # Arrange
    renderers = {"FluxMotes": stage.render_flux_motes, "PylonGlow": stage.render_pylon_glow}
    # Act
    layers = stage.build_animated_layers()
    # Assert
    assert set(layers) == set(renderers)
    for name, spec in layers.items():
        sheet = renderers[name]()
        assert sheet.width % spec["frame_width"] == 0, name
        assert spec["fps"] > 0, name


def test_ko_burst_rays_never_bleed_into_the_next_frame() -> None:
    # Arrange
    burst = stage.render_ko_burst()
    size = burst.height
    alpha = burst.image.getchannel("A")
    # Act & Assert
    for frame in range(burst.width // size):
        left_edge = alpha.crop((frame * size, 0, frame * size + 1, size)).getextrema()[1]
        right_edge = alpha.crop((frame * size + size - 1, 0, frame * size + size, size)).getextrema()[1]
        assert left_edge == 0 and right_edge == 0, f"frame {frame}"
