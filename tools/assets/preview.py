"""Dev helper: upscale a PNG with nearest-neighbour so pixel art can be inspected."""
from __future__ import annotations

import sys

from PIL import Image


def save_upscaled(source: str, target: str, factor: int, background: tuple[int, int, int]) -> None:
    image = Image.open(source).convert("RGBA")
    backdrop = Image.new("RGBA", image.size, (*background, 255))
    backdrop.alpha_composite(image)
    backdrop.resize((image.width * factor, image.height * factor), Image.NEAREST).save(target)


if __name__ == "__main__":
    save_upscaled(sys.argv[1], sys.argv[2], int(sys.argv[3]), (120, 170, 200))
