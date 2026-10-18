"""Preview helper: nearest-neighbour upscale keeps pixels square."""

import random

from PIL import Image

import preview


def test_save_upscaled_multiplies_size_without_blending(tmp_path) -> None:
    # Arrange
    factor = random.Random().randint(2, 6)
    source = tmp_path / "source.png"
    image = Image.new("RGBA", (2, 1), (0, 0, 0, 0))
    image.putpixel((0, 0), (255, 0, 0, 255))
    image.save(source)
    target = tmp_path / "target.png"
    # Act
    preview.save_upscaled(str(source), str(target), factor, (0, 0, 255))
    # Assert
    with Image.open(target) as result:
        assert result.size == (2 * factor, factor)
        assert result.convert("RGB").getpixel((factor - 1, 0)) == (255, 0, 0)
        assert result.convert("RGB").getpixel((factor, 0)) == (0, 0, 255)
