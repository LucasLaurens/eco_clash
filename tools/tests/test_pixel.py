"""Pixel primitives: colour mixing and haze keep what they promise."""

import random

from pixel import Canvas, mix_colors


def test_mix_colors_hits_both_ends() -> None:
    # Arrange
    rng = random.Random()
    start = tuple(rng.randrange(256) for _ in range(3))
    end = tuple(rng.randrange(256) for _ in range(3))
    # Act & Assert
    assert mix_colors(start, end, 0.0) == (*start, 255)
    assert mix_colors(start, end, 1.0) == (*end, 255)


def test_tint_toward_keeps_alpha_and_skips_transparent_pixels() -> None:
    # Arrange
    canvas = Canvas(4, 1)
    alpha = random.Random().randrange(1, 255)
    canvas.put_pixel(0, 0, (10, 20, 30, alpha))
    # Act
    canvas.tint_toward((250, 250, 250), 0.5)
    # Assert
    assert canvas.image.getpixel((0, 0))[3] == alpha
    assert canvas.image.getpixel((0, 0))[0] > 10
    assert canvas.image.getpixel((1, 0)) == (0, 0, 0, 0)
