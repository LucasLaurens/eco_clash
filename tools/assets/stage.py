"""Precursor Isle: sky, sea, distant islands, the floating arena and its platforms."""
from __future__ import annotations

import math
import random

import palette
from pixel import Canvas, Color, Ramp, mix_colors

WIDTH, HEIGHT = 480, 270
HORIZON_Y = 168
ISLAND_SIZE = (320, 100)
ISLAND_SURFACE_Y = 6
PLATFORM_SIZE = (64, 14)
PLATFORM_SURFACE_Y = 2

WATERFALL_X, WATERFALL_TOP_Y, WATERFALL_BOTTOM_Y = 20, 150, 214
WATERFALL_FRAME_WIDTH = 20
WATERFALL_FRAMES = 4
WATERFALL_FPS = 8
WATERFALL_BAND = 4
SEA_GLINT_FRAMES = 3
SEA_GLINT_FPS = 4
SEA_GLINT_COUNT = 40


def render_sky() -> Canvas:
    canvas = Canvas(WIDTH, HEIGHT)
    canvas.fill_vertical_gradient((0, 0, WIDTH - 1, HORIZON_Y + 10), palette.SKY_BANDS)
    sun_x, sun_y = 368, 64
    for radius, alpha in ((34, 40), (27, 70), (21, 110)):
        halo = Canvas(WIDTH, HEIGHT)
        halo.fill_ellipse((sun_x - radius, sun_y - radius, sun_x + radius, sun_y + radius), (255, 244, 200, alpha))
        canvas.paste(halo.image, (0, 0))
    canvas.fill_ellipse((sun_x - 15, sun_y - 15, sun_x + 15, sun_y + 15), (255, 246, 210))
    canvas.fill_ellipse((sun_x - 12, sun_y - 13, sun_x + 10, sun_y + 9), (255, 252, 236))
    return canvas


def render_clouds() -> Canvas:
    """Horizontally tileable cloud band, scrolled slowly in game."""
    canvas = Canvas(WIDTH, 110)
    rng = random.Random(7)
    for _ in range(9):
        x = rng.randrange(0, WIDTH)
        y = rng.randrange(28, 92)
        size = rng.randrange(14, 30)
        for shift in (-WIDTH, 0, WIDTH):
            _paint_cloud(canvas, x + shift, y, size)
    return canvas


def _paint_cloud(canvas: Canvas, x: int, y: int, size: int) -> None:
    shade: Color = (210, 224, 240)
    light: Color = (255, 255, 255)
    puffs = [(-size, 0, size // 2), (-size // 3, -size // 3, size // 2 + 3), (size // 3, -size // 5, size // 2), (size, 2, size // 3)]
    for dx, dy, radius in puffs:
        canvas.fill_ellipse((x + dx - radius, y + dy - radius + 2, x + dx + radius, y + dy + radius + 2), shade)
    for dx, dy, radius in puffs:
        canvas.fill_ellipse((x + dx - radius, y + dy - radius, x + dx + radius, y + dy + radius - 2), light)
    canvas.fill_rect((x - size - size // 2, y + size // 3, x + size + size // 3, y + size // 2 + 2), (0, 0, 0, 0))


def render_far() -> Canvas:
    canvas = Canvas(WIDTH, HEIGHT)
    haze: Color = (150, 186, 214)
    haze_dark: Color = (122, 160, 196)
    _paint_hills(canvas, HORIZON_Y, [(30, 26, 70), (150, 14, 50), (420, 30, 90)], haze)
    _paint_precursor_tower(canvas, 64, HORIZON_Y - 24, haze_dark)
    _paint_volcano(canvas, 430, HORIZON_Y - 6, haze_dark)
    sea = [(56, 176, 196), (40, 150, 186), (28, 120, 168), (22, 96, 150)]
    canvas.fill_vertical_gradient((0, HORIZON_Y, WIDTH - 1, HEIGHT - 1), sea)
    rng = random.Random(3)
    for _ in range(70):
        x, y = rng.randrange(0, WIDTH), rng.randrange(HORIZON_Y + 3, HEIGHT)
        length = 2 + (y - HORIZON_Y) // 20
        canvas.draw_line((x, y), (x + length, y), (190, 240, 245))
    return canvas


def _paint_hills(canvas: Canvas, base_y: int, hills: list[tuple[int, int, int]], color: Color) -> None:
    for center, height, half_width in hills:
        canvas.fill_ellipse((center - half_width, base_y - height, center + half_width, base_y + height), color)


def _paint_precursor_tower(canvas: Canvas, x: int, base_y: int, color: Color) -> None:
    canvas.fill_polygon([(x - 9, base_y + 24), (x - 4, base_y - 70), (x + 4, base_y - 70), (x + 9, base_y + 24)], color)
    canvas.fill_rect((x - 12, base_y - 40, x + 12, base_y - 36), color)
    canvas.fill_polygon([(x - 6, base_y - 70), (x, base_y - 84), (x + 6, base_y - 70)], color)
    glow = palette.PRECURSOR_GLOW
    canvas.fill_ellipse((x - 2, base_y - 80, x + 2, base_y - 76), glow.base)
    for y in range(base_y - 60, base_y + 20, 14):
        canvas.put_pixel(x, y, glow.light)


def _paint_volcano(canvas: Canvas, x: int, base_y: int, color: Color) -> None:
    canvas.fill_polygon([(x - 50, base_y + 6), (x - 10, base_y - 46), (x + 8, base_y - 46), (x + 50, base_y + 6)], color)
    canvas.fill_ellipse((x - 14, base_y - 64, x + 4, base_y - 50), (196, 214, 228))
    canvas.fill_ellipse((x - 4, base_y - 76, x + 14, base_y - 60), (206, 222, 234))


def render_mid() -> Canvas:
    """Closer islets on both edges. The centre stays empty so fighters read clearly."""
    canvas = Canvas(WIDTH, HEIGHT)
    _paint_islet(canvas, 34, 214, 72, with_hut=True)
    _paint_islet(canvas, 452, 224, 64, with_hut=False)
    canvas.tint_toward(palette.HAZE, palette.MID_HAZE_RATIO)
    return canvas


def _paint_islet(canvas: Canvas, x: int, y: int, half_width: int, with_hut: bool) -> None:
    rock = Ramp(shade=(96, 92, 120), base=(124, 118, 146), light=(150, 146, 170))
    canvas.fill_polygon([(x - half_width, y), (x + half_width, y), (x + half_width // 3, y + 50), (x - half_width // 2, y + 46)], rock.base)
    canvas.fill_polygon([(x, y), (x + half_width, y), (x + half_width // 3, y + 50)], rock.shade)
    canvas.fill_ellipse((x - half_width - 4, y - 10, x + half_width + 4, y + 8), (70, 140, 92))
    canvas.fill_ellipse((x - half_width, y - 12, x + half_width, y + 2), (92, 166, 100))
    for palm_x in (x - half_width // 2, x + half_width // 3):
        _paint_palm(canvas, palm_x, y - 8, 30 + (palm_x % 9))
    if with_hut:
        _paint_hut(canvas, x + 6, y - 10)


def _paint_palm(canvas: Canvas, x: int, base_y: int, height: int) -> None:
    trunk: Color = (150, 116, 90)
    leaf: Color = (64, 140, 90)
    leaf_light: Color = (100, 176, 110)
    top_x, top_y = x + 5, base_y - height
    canvas.draw_line((x, base_y), (top_x, top_y), trunk, 2)
    for angle in (200, 235, 270, 305, 340, 20):
        angle_radians = math.radians(angle)
        end = (round(top_x + math.cos(angle_radians) * 14), round(top_y + math.sin(angle_radians) * 6 + 6))
        canvas.draw_line((top_x, top_y), end, leaf, 3)
        canvas.draw_line((top_x, top_y - 1), end, leaf_light, 1)


def _paint_hut(canvas: Canvas, x: int, base_y: int) -> None:
    wood = Ramp(shade=(120, 96, 90), base=(156, 124, 108), light=(184, 156, 130))
    thatch: Color = (196, 170, 110)
    canvas.fill_rect((x - 10, base_y - 14, x + 10, base_y), wood.base)
    canvas.fill_rect((x - 3, base_y - 8, x + 2, base_y), wood.shade)
    canvas.fill_polygon([(x - 15, base_y - 13), (x, base_y - 27), (x + 15, base_y - 13)], thatch)
    canvas.fill_ellipse((x - 2, base_y - 12, x + 1, base_y - 10), palette.PRECURSOR_GLOW.base)


def render_waterfall() -> Canvas:
    """Falling streaks scrolled down one band per frame, so the loop is seamless.

    O(f * w * h) time over the frames, O(1) extra space. Hazed like the middle layer it sits on.
    """
    height = WATERFALL_BOTTOM_Y - WATERFALL_TOP_Y + 6
    canvas = Canvas(WATERFALL_FRAME_WIDTH * WATERFALL_FRAMES, height)
    center = WATERFALL_FRAME_WIDTH // 2
    period = WATERFALL_BAND * 3
    for frame in range(WATERFALL_FRAMES):
        left = frame * WATERFALL_FRAME_WIDTH
        shift = frame * period // WATERFALL_FRAMES
        for column in range(center - 4, center + 5):
            for y in range(height - 4):
                band = ((y - shift + column * 5) // WATERFALL_BAND) % 3
                canvas.put_pixel(left + column, y, (150, 210, 236) if band == 0 else (200, 236, 250))
        splash = 9 + frame % 2
        canvas.fill_ellipse((left + center - splash, height - 7, left + center + splash - 1, height - 1), (230, 248, 255))
    canvas.tint_toward(palette.HAZE, palette.MID_HAZE_RATIO)
    return canvas


def compute_waterfall_offset() -> tuple[int, int]:
    return WATERFALL_X - WATERFALL_FRAME_WIDTH // 2, WATERFALL_TOP_Y


def render_sea_glints() -> Canvas:
    """Sparkles on the sea, each twinkling on its own phase: bright cross, dim dot, gone."""
    height = HEIGHT - HORIZON_Y
    canvas = Canvas(WIDTH * SEA_GLINT_FRAMES, height)
    rng = random.Random(5)
    glints = [(rng.randrange(2, WIDTH - 2), rng.randrange(4, height - 2), rng.randrange(SEA_GLINT_FRAMES)) for _ in range(SEA_GLINT_COUNT)]
    bright: Color = (250, 254, 255)
    dim: Color = (200, 240, 248)
    for frame in range(SEA_GLINT_FRAMES):
        for x, y, phase in glints:
            step = (frame - phase) % SEA_GLINT_FRAMES
            gx = frame * WIDTH + x
            if step == 0:
                canvas.put_pixel(gx, y, bright)
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    canvas.put_pixel(gx + dx, y + dy, dim)
            elif step == 1:
                canvas.put_pixel(gx, y, dim)
    return canvas


def build_animated_layers() -> dict:
    """Placement and timing of the animated stage layers, read by Godot (one source, like layout.json)."""
    return {
        "Waterfall": {"sheet": "waterfall.png", "frame_width": WATERFALL_FRAME_WIDTH, "fps": WATERFALL_FPS, "offset": compute_waterfall_offset()},
        "SeaGlints": {"sheet": "sea_glints.png", "frame_width": WIDTH, "fps": SEA_GLINT_FPS, "offset": (0, HORIZON_Y)},
    }


def render_island() -> Canvas:
    """Main arena: grass top, warm cliff, a band of Precursor metal with glowing eco lights."""
    width, height = ISLAND_SIZE
    canvas = Canvas(width, height)
    top = ISLAND_SURFACE_Y
    body = [(0, top + 2), (width - 1, top + 2), (width - 18, top + 38), (width - 70, top + 66), (width // 2 + 6, height - 2), (70, top + 64), (16, top + 36)]
    canvas.fill_polygon(body, palette.DIRT.base)
    canvas.fill_polygon([(width // 2, top + 2), (width - 1, top + 2), (width - 18, top + 38), (width - 70, top + 66), (width // 2 + 6, height - 2)], palette.DIRT.shade)
    rng = random.Random(11)
    for _ in range(90):
        x, y = rng.randrange(10, width - 10), rng.randrange(top + 14, height - 10)
        end_x = x + rng.randrange(3, 9)
        if canvas.image.getpixel((x, y))[3] and canvas.image.getpixel((min(end_x, width - 1), y))[3]:
            canvas.draw_line((x, y), (end_x, y), palette.ROCK.shade if rng.random() < 0.6 else palette.DIRT.light)
    _paint_precursor_band(canvas, top + 16, width)
    canvas.fill_rect((0, top, width - 1, top + 5), palette.GRASS.base)
    canvas.fill_rect((0, top + 5, width - 1, top + 7), palette.GRASS.shade)
    canvas.fill_rect((0, top, width - 1, top), palette.GRASS.light)
    for x in range(2, width - 2, 3):
        tuft = rng.randrange(1, 5)
        canvas.draw_line((x, top), (x + rng.choice((-1, 0, 1)), top - tuft), palette.GRASS.base if tuft > 2 else palette.GRASS.light)
    for x in range(10, width - 10, 37):
        canvas.put_pixel(x, top - 2, (255, 120, 150))
        canvas.put_pixel(x + 17, top - 1, (255, 230, 90))
    for x in range(30, width - 30, 23):
        length = rng.randrange(8, 24)
        canvas.draw_line((x, top + 8), (x + rng.choice((-2, 2)), top + 8 + length), palette.GRASS.shade)
    canvas.add_outline(palette.OUTLINE)
    return canvas


def _paint_precursor_band(canvas: Canvas, y: int, width: int) -> None:
    metal, glow = palette.PRECURSOR_METAL, palette.PRECURSOR_GLOW
    canvas.fill_rect((14, y, width - 15, y + 8), metal.base)
    canvas.fill_rect((14, y, width - 15, y), metal.light)
    canvas.fill_rect((14, y + 8, width - 15, y + 8), metal.shade)
    for x in range(26, width - 20, 24):
        canvas.fill_ellipse((x - 2, y + 2, x + 2, y + 6), glow.base)
        canvas.put_pixel(x - 1, y + 3, glow.light)
        canvas.draw_line((x + 8, y + 2), (x + 8, y + 6), metal.shade)


def render_platform() -> Canvas:
    width, height = PLATFORM_SIZE
    metal, glow = palette.PRECURSOR_METAL, palette.PRECURSOR_GLOW
    canvas = Canvas(width, height)
    top = PLATFORM_SURFACE_Y
    canvas.fill_polygon([(0, top), (width - 1, top), (width - 6, top + 7), (5, top + 7)], metal.base)
    canvas.fill_rect((0, top, width - 1, top + 1), metal.light)
    canvas.fill_polygon([(width // 2, top + 2), (width - 1, top + 2), (width - 6, top + 7), (width // 2, top + 7)], metal.shade)
    for x in range(8, width - 6, 12):
        canvas.fill_rect((x, top + 4, x + 3, top + 5), glow.base)
    canvas.add_outline(palette.OUTLINE)
    under = Canvas(width, height)
    for x in range(10, width - 10, 6):
        under.fill_rect((x, top + 10, x + 2, top + 10), (*glow.light, 160))
        under.put_pixel(x + 1, top + 11, (*glow.base, 110))
    canvas.paste(under.image, (0, 0))
    return canvas


def render_hit_spark() -> Canvas:
    """4 frames, 32px each: an expanding white star with an eco-warm core."""
    size, frames = 32, 4
    canvas = Canvas(size * frames, size)
    for frame in range(frames):
        center_x, center_y = frame * size + size // 2, size // 2
        reach = 5 + frame * 4
        fade = 255 - frame * 55
        for index in range(8):
            angle = math.radians(index * 45 + frame * 10)
            inner = (round(center_x + math.cos(angle) * reach * 0.4), round(center_y + math.sin(angle) * reach * 0.4))
            outer = (round(center_x + math.cos(angle) * reach), round(center_y + math.sin(angle) * reach))
            canvas.draw_line(inner, outer, (255, 255, 255, fade), 2 if index % 2 == 0 else 1)
        core = max(4 - frame, 1)
        canvas.fill_ellipse((center_x - core, center_y - core, center_x + core, center_y + core), mix_colors((255, 236, 120), (255, 140, 60), frame / 3))
    return canvas


def render_eco_bolt(eco: Ramp) -> Canvas:
    """2 frames, 16px each: pulsing eco orb with a trailing tail (faces right)."""
    size = 16
    canvas = Canvas(size * 2, size)
    for frame in range(2):
        center_x, center_y = frame * size + 10, size // 2
        canvas.fill_ellipse((center_x - 9, center_y - 2, center_x - 1, center_y + 2), (*eco.shade, 140))
        radius = 4 + frame
        canvas.fill_ellipse((center_x - radius, center_y - radius, center_x + radius, center_y + radius), (*eco.base, 200))
        canvas.fill_ellipse((center_x - 2, center_y - 2, center_x + 2, center_y + 2), eco.light)
    return canvas


def render_shadow() -> Canvas:
    """3 frames, 18px each: contact shadow shrinking as the fighter rises. Outline-tinted, never pure black.

    Discrete sizes instead of a runtime scale, so the shadow stays on the pixel grid.
    """
    size = 18
    half_sizes = ((8, 2), (6, 2), (4, 1))
    canvas = Canvas(size * len(half_sizes), size)
    for frame, (half_width, half_height) in enumerate(half_sizes):
        center_x, center_y = frame * size + size // 2, size // 2
        canvas.fill_ellipse((center_x - half_width, center_y - half_height, center_x + half_width, center_y + half_height), (*palette.OUTLINE, 70))
        canvas.fill_ellipse((center_x - half_width + 3, center_y - half_height + 1, center_x + half_width - 3, center_y + half_height - 1), (*palette.OUTLINE, 120))
    return canvas


def render_dust() -> Canvas:
    """4 frames, 16px each: two sand puffs drifting apart from the feet and thinning out."""
    size, frames = 16, 4
    canvas = Canvas(size * frames, size)
    sand = palette.SAND
    for frame in range(frames):
        center_x, ground_y = frame * size + size // 2, size - 2
        spread = 2 + frame * 2
        radius = 4 - frame
        alpha = 240 - frame * 45
        for side in (-1, 1):
            puff_x = center_x + side * spread
            puff_y = ground_y - radius - frame // 2
            canvas.fill_ellipse((puff_x - radius, puff_y - radius, puff_x + radius, puff_y + radius), (*sand.shade, alpha))
            canvas.fill_ellipse((puff_x - radius + 1, puff_y - radius, puff_x + radius - 1, puff_y + radius - 1), (*sand.light, alpha))
    return canvas


def render_ko_burst() -> Canvas:
    """6 frames, 64px each: a ring and long rays flaring out. Drawn light, tinted by the fighter colour in game."""
    size, frames = 64, 6
    canvas = Canvas(size * frames, size)
    for frame in range(frames):
        center_x, center_y = frame * size + size // 2, size // 2
        fade = 255 - frame * 40
        # Longest ray stays inside its own frame, or it bleeds into the next one.
        reach = min(10 + frame * 4, size // 2 - 2)
        for index in range(12):
            angle = math.radians(index * 30 + 15)
            inner = (round(center_x + math.cos(angle) * reach * 0.5), round(center_y + math.sin(angle) * reach * 0.5))
            outer = (round(center_x + math.cos(angle) * reach), round(center_y + math.sin(angle) * reach))
            canvas.draw_line(inner, outer, (255, 252, 240, fade), 3 if index % 3 == 0 else 1)
        ring = 4 + frame * 4
        canvas.draw_arc((center_x - ring, center_y - ring, center_x + ring, center_y + ring), 0, 360, (255, 248, 230, fade), 2)
        core = max(7 - frame * 2, 0)
        if core:
            canvas.fill_ellipse((center_x - core, center_y - core, center_x + core, center_y + core), (255, 252, 240, fade))
    return canvas
