"""Pixel-level drawing primitives shared by every asset generator.

PIL draws aliased shapes by default, which is exactly what pixel art needs:
every primitive here lands on whole pixels, no blending.
"""
from __future__ import annotations

from dataclasses import dataclass

from PIL import Image, ImageDraw

Color = tuple[int, ...]
Point = tuple[int, int]
Box = tuple[int, int, int, int]

TRANSPARENT: Color = (0, 0, 0, 0)

# 4x4 ordered-dither matrix, normalised to [0, 1).
BAYER_4X4: tuple[tuple[float, ...], ...] = tuple(
    tuple(value / 16 for value in row)
    for row in ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))
)


@dataclass(frozen=True)
class Ramp:
    """Three tones of one material: shadow, base and highlight."""

    shade: Color
    base: Color
    light: Color


def to_rgba(color: Color) -> Color:
    return color if len(color) == 4 else (*color, 255)


def mix_colors(start: Color, end: Color, ratio: float) -> Color:
    start, end = to_rgba(start), to_rgba(end)
    return tuple(round(a + (b - a) * ratio) for a, b in zip(start, end))


class Canvas:
    """A transparent RGBA image with pixel-art friendly drawing verbs."""

    def __init__(self, width: int, height: int) -> None:
        self.image = Image.new("RGBA", (width, height), TRANSPARENT)
        self._draw = ImageDraw.Draw(self.image)

    @property
    def width(self) -> int:
        return self.image.width

    @property
    def height(self) -> int:
        return self.image.height

    def put_pixel(self, x: int, y: int, color: Color) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.image.putpixel((x, y), to_rgba(color))

    def fill_rect(self, box: Box, color: Color) -> None:
        x0, y0, x1, y1 = box
        if x1 >= x0 and y1 >= y0:
            self._draw.rectangle(box, fill=to_rgba(color))

    def fill_ellipse(self, box: Box, color: Color) -> None:
        x0, y0, x1, y1 = box
        if x1 >= x0 and y1 >= y0:
            self._draw.ellipse(box, fill=to_rgba(color))

    def fill_polygon(self, points: list[Point], color: Color) -> None:
        self._draw.polygon(points, fill=to_rgba(color))

    def draw_line(self, start: Point, end: Point, color: Color, width: int = 1) -> None:
        self._draw.line((start, end), fill=to_rgba(color), width=width)

    def draw_arc(self, box: Box, start_deg: float, end_deg: float, color: Color, width: int = 1) -> None:
        self._draw.arc(box, start_deg, end_deg, fill=to_rgba(color), width=width)

    def fill_shaded_ellipse(self, box: Box, ramp: Ramp) -> None:
        """Ellipse lit from the top-left: shadow rim bottom-right, highlight top-left."""
        x0, y0, x1, y1 = box
        self.fill_ellipse(box, ramp.shade)
        self.fill_ellipse((x0, y0, x1 - 1, y1 - 1), ramp.base)
        if x1 - x0 >= 4 and y1 - y0 >= 4:
            self.put_pixel(x0 + 1 + (x1 - x0) // 5, y0 + 1 + (y1 - y0) // 5, ramp.light)
            self.put_pixel(x0 + 2 + (x1 - x0) // 5, y0 + 1 + (y1 - y0) // 5, ramp.light)

    def draw_capsule(self, start: Point, end: Point, radius: int, color: Color) -> None:
        """Thick limb: stamps a disc at every pixel step of the segment.

        O(L * r^2) time where L is the segment length, O(1) extra space.
        """
        steps = max(abs(end[0] - start[0]), abs(end[1] - start[1]), 1)
        for step in range(steps + 1):
            x = round(start[0] + (end[0] - start[0]) * step / steps)
            y = round(start[1] + (end[1] - start[1]) * step / steps)
            if radius <= 1:
                self.fill_rect((x - radius, y - radius, x + radius, y + radius), color)
            else:
                self.fill_ellipse((x - radius, y - radius, x + radius, y + radius), color)

    def add_outline(self, color: Color) -> None:
        """Surround every opaque shape with a 1px outline (4-neighbourhood).

        O(w * h) time, O(w * h) space for the snapshot of the source pixels.
        """
        source = self.image.copy().load()
        target = self.image.load()
        outline = to_rgba(color)
        for y in range(self.height):
            for x in range(self.width):
                if source[x, y][3] > 0:
                    continue
                if self._has_opaque_neighbour(source, x, y):
                    target[x, y] = outline

    def _has_opaque_neighbour(self, pixels, x: int, y: int) -> bool:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height and pixels[nx, ny][3] > 0:
                return True
        return False

    def fill_vertical_gradient(self, box: Box, colors: list[Color]) -> None:
        """Banded gradient with ordered dithering between bands (classic pixel-art sky).

        O(w * h) time, O(1) extra space.
        """
        x0, y0, x1, y1 = box
        height = max(y1 - y0, 1)
        bands = len(colors) - 1
        for y in range(y0, y1 + 1):
            position = (y - y0) / height * bands
            band = min(int(position), bands - 1)
            ratio = position - band
            for x in range(x0, x1 + 1):
                threshold = BAYER_4X4[y % 4][x % 4]
                self.put_pixel(x, y, colors[band + 1] if ratio > threshold else colors[band])

    def paste(self, other: Image.Image, position: Point) -> None:
        self.image.alpha_composite(other, dest=position)

    def save(self, path: str) -> None:
        self.image.save(path)
