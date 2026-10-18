"""Ancient arena at dusk: sky, sea of clouds, distant spires, floating pylons, the arena and its platforms.

Few shapes, few tones. The only light in the decor is flux (cyan), and it lives inside objects:
spire tips, pylon conduits, the arena's seam and core.
"""

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

SUN_CENTER = (366, 156)
SUN_RADIUS = 22
# (center_x, base_y, height, half_width): rising out of the sea of clouds.
SPIRES = ((62, HORIZON_Y + 6, 104, 7), (418, HORIZON_Y + 6, 78, 6), (300, HORIZON_Y + 4, 40, 4))
# (center_x, top_y, height, half_width): hovering monoliths framing the arena.
PYLONS = ((34, 96, 112, 14), (448, 112, 96, 12))
PYLON_GLOW_FRAMES = 3
PYLON_GLOW_FPS = 3
FLUX_MOTE_FRAMES = 3
FLUX_MOTE_FPS = 4
FLUX_MOTE_COUNT = 26


def render_sky() -> Canvas:
    canvas = Canvas(WIDTH, HEIGHT)
    canvas.fill_vertical_gradient((0, 0, WIDTH - 1, HORIZON_Y + 10), palette.SKY_BANDS)
    _paint_far_ring(canvas)
    sun_x, sun_y = SUN_CENTER
    canvas.fill_ellipse(
        (sun_x - SUN_RADIUS, sun_y - SUN_RADIUS, sun_x + SUN_RADIUS, sun_y + SUN_RADIUS), palette.SUN.shade
    )
    canvas.fill_ellipse(
        (sun_x - SUN_RADIUS + 3, sun_y - SUN_RADIUS + 2, sun_x + SUN_RADIUS - 3, sun_y + SUN_RADIUS - 4),
        palette.SUN.base,
    )
    canvas.fill_ellipse((sun_x - 8, sun_y - 14, sun_x + 4, sun_y - 6), palette.SUN.light)
    return canvas


def _paint_far_ring(canvas: Canvas) -> None:
    """A colossal ancient arch rising out of the clouds, so far away it barely darkens the sky."""
    ring = mix_colors(palette.SKY_BANDS[2], palette.SILHOUETTE_FAR, 0.5)
    edge = mix_colors(palette.SKY_BANDS[2], palette.SUN.base, 0.25)
    box = (150, HORIZON_Y - 120, 450, HORIZON_Y + 120)
    canvas.draw_arc(box, 180, 360, ring, 6)
    canvas.draw_arc((box[0] + 6, box[1] + 6, box[2] - 6, box[3] - 6), 200, 340, edge, 1)


def render_clouds() -> Canvas:
    """Horizontally tileable band of thin dusk clouds, scrolled slowly in game."""
    canvas = Canvas(WIDTH, 110)
    rng = random.Random(7)
    shade: Color = (112, 102, 156)
    light: Color = (176, 140, 172)
    for _ in range(6):
        x = rng.randrange(0, WIDTH)
        y = rng.randrange(30, 96)
        length = rng.randrange(40, 90)
        for shift in (-WIDTH, 0, WIDTH):
            _paint_cloud_streak(canvas, x + shift, y, length, shade, light)
    return canvas


def _paint_cloud_streak(canvas: Canvas, x: int, y: int, length: int, shade: Color, light: Color) -> None:
    canvas.fill_ellipse((x - length // 2, y - 3, x + length // 2, y + 3), shade)
    canvas.fill_ellipse((x - length // 3, y - 4, x + length // 3, y + 1), light)


def render_far() -> Canvas:
    canvas = Canvas(WIDTH, HEIGHT)
    for spire in SPIRES:
        _paint_spire(canvas, *spire)
    canvas.fill_vertical_gradient((0, HORIZON_Y, WIDTH - 1, HEIGHT - 1), palette.CLOUD_SEA)
    crest = mix_colors(palette.CLOUD_SEA[0], palette.SUN.light, 0.4)
    for x in range(-12, WIDTH + 12, 38):
        canvas.fill_ellipse((x, HORIZON_Y - 3, x + 46, HORIZON_Y + 5), crest)
    rng = random.Random(3)
    for _ in range(14):
        x, y = rng.randrange(0, WIDTH), rng.randrange(HORIZON_Y + 16, HEIGHT - 8)
        length = 8 + (y - HORIZON_Y) // 4
        canvas.draw_line((x, y), (x + length, y), mix_colors(palette.CLOUD_SEA[1], palette.CLOUD_SEA[0], 0.5))
    return canvas


def _paint_spire(canvas: Canvas, center_x: int, base_y: int, height: int, half_width: int) -> None:
    top_y = base_y - height
    color = palette.SILHOUETTE_FAR
    canvas.fill_polygon(
        [
            (center_x - half_width, base_y),
            (center_x - 1, top_y),
            (center_x + 1, top_y),
            (center_x + half_width, base_y),
        ],
        color,
    )
    collar_y = top_y + height // 3
    canvas.fill_rect((center_x - half_width + 1, collar_y, center_x + half_width - 1, collar_y + 2), color)
    canvas.put_pixel(center_x, top_y - 2, palette.ANCIENT_GLOW.light)
    canvas.put_pixel(center_x, top_y - 1, palette.ANCIENT_GLOW.base)


def render_mid() -> Canvas:
    """Two hovering monoliths frame the arena. The centre stays empty so fighters read clearly."""
    canvas = Canvas(WIDTH, HEIGHT)
    for pylon in PYLONS:
        _paint_pylon(canvas, *pylon)
    canvas.add_outline(palette.OUTLINE)
    return canvas


def _compute_pylon_outline(center_x: int, top_y: int, height: int, half_width: int) -> list[tuple[int, int]]:
    return [
        (center_x - half_width, top_y + 8),
        (center_x, top_y),
        (center_x + half_width, top_y + 8),
        (center_x + half_width, top_y + height - 16),
        (center_x, top_y + height),
        (center_x - half_width, top_y + height - 16),
    ]


def _compute_pylon_seams(
    center_x: int, top_y: int, height: int, half_width: int
) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """Flux conduits carved in the lit face. Shared by the static pylon and its pulsing glow layer."""
    seam_x = center_x - half_width // 2
    return [((seam_x, top_y + 12), (seam_x, top_y + height - 22))]


def _paint_pylon(canvas: Canvas, center_x: int, top_y: int, height: int, half_width: int) -> None:
    mid = palette.SILHOUETTE_MID
    canvas.fill_polygon(_compute_pylon_outline(center_x, top_y, height, half_width), mid.shade)
    lit_face = [
        (center_x - half_width, top_y + 8),
        (center_x, top_y),
        (center_x, top_y + height),
        (center_x - half_width, top_y + height - 16),
    ]
    canvas.fill_polygon(lit_face, mid.base)
    canvas.draw_line((center_x, top_y + 1), (center_x, top_y + height - 1), mid.light)
    for start, end in _compute_pylon_seams(center_x, top_y, height, half_width):
        canvas.draw_line(start, end, mid.shade)
    for index, shard_x in enumerate((center_x - half_width + 2, center_x + half_width - 5)):
        shard_y = top_y + height + 8 + index * 6
        canvas.fill_polygon([(shard_x, shard_y), (shard_x + 4, shard_y), (shard_x + 2, shard_y + 6)], mid.base)


def render_pylon_glow() -> Canvas:
    """Full-frame overlay of the pylon conduits, pulsing bright, soft, dim.

    O(f * s) time, f frames and s seam segments.
    """
    glow = palette.ANCIENT_GLOW
    pulse = (glow.light, glow.base, mix_colors(glow.base, palette.SILHOUETTE_MID.shade, 0.5))
    canvas = Canvas(WIDTH * PYLON_GLOW_FRAMES, HEIGHT)
    for frame in range(PYLON_GLOW_FRAMES):
        left = frame * WIDTH
        for pylon in PYLONS:
            for (x0, y0), (x1, y1) in _compute_pylon_seams(*pylon):
                canvas.draw_line((left + x0, y0), (left + x1, y1), pulse[frame])
            center_x, top_y, height, half_width = pylon
            core_x, core_y = center_x - half_width // 2, top_y + height // 2
            canvas.fill_polygon(
                [
                    (left + core_x - 2, core_y),
                    (left + core_x, core_y - 4),
                    (left + core_x + 2, core_y),
                    (left + core_x, core_y + 4),
                ],
                pulse[frame],
            )
    return canvas


def render_flux_motes() -> Canvas:
    """Specks of flux drifting in the air, each twinkling on its own phase: bright cross, dim dot, gone."""
    canvas = Canvas(WIDTH * FLUX_MOTE_FRAMES, HEIGHT)
    rng = random.Random(5)
    motes = [
        (rng.randrange(4, WIDTH - 4), rng.randrange(20, HORIZON_Y + 60), rng.randrange(FLUX_MOTE_FRAMES))
        for _ in range(FLUX_MOTE_COUNT)
    ]
    glow = palette.ANCIENT_GLOW
    for frame in range(FLUX_MOTE_FRAMES):
        for x, y, phase in motes:
            step = (frame - phase) % FLUX_MOTE_FRAMES
            mote_x = frame * WIDTH + x
            if step == 0:
                canvas.put_pixel(mote_x, y, glow.light)
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    canvas.put_pixel(mote_x + dx, y + dy, (*glow.base, 150))
            elif step == 1:
                canvas.put_pixel(mote_x, y, (*glow.base, 190))
    return canvas


def build_animated_layers() -> dict:
    """Placement and timing of the animated stage layers, read by Godot (one source, like layout.json)."""
    return {
        "FluxMotes": {"sheet": "flux_motes.png", "frame_width": WIDTH, "fps": FLUX_MOTE_FPS, "offset": (0, 0)},
        "PylonGlow": {"sheet": "pylon_glow.png", "frame_width": WIDTH, "fps": PYLON_GLOW_FPS, "offset": (0, 0)},
    }


def render_island() -> Canvas:
    """Main arena: an ancient slab with one flux seam, over a tapering hull with a glowing core."""
    width, height = ISLAND_SIZE
    metal, glow = palette.ANCIENT_METAL, palette.ANCIENT_GLOW
    hull_shade = mix_colors(metal.shade, palette.OUTLINE, 0.35)
    canvas = Canvas(width, height)
    top = ISLAND_SURFACE_Y
    slab_bottom = top + 10
    hull = [
        (6, slab_bottom),
        (width - 7, slab_bottom),
        (width - 44, top + 40),
        (width // 2 + 26, height - 8),
        (width // 2 - 26, height - 8),
        (44, top + 40),
    ]
    canvas.fill_polygon(hull, hull_shade)
    canvas.fill_polygon(
        [
            (6, slab_bottom),
            (width // 2, slab_bottom),
            (width // 2, height - 8),
            (width // 2 - 26, height - 8),
            (44, top + 40),
        ],
        metal.shade,
    )
    for x in (70, 110, width - 111, width - 71):
        canvas.draw_line(
            (x, slab_bottom + 2), (x + (width // 2 - x) // 6, top + 38), hull_shade if x < width // 2 else metal.shade
        )
    canvas.fill_rect((0, top, width - 1, slab_bottom), metal.base)
    canvas.fill_rect((0, top, width - 1, top), metal.light)
    canvas.fill_rect((0, slab_bottom, width - 1, slab_bottom), metal.shade)
    for x in range(10, width - 30, 32):
        canvas.fill_rect((x, top + 5, x + 21, top + 5), glow.base)
    core_x, core_y = width // 2, height - 20
    canvas.fill_ellipse((core_x - 9, core_y - 7, core_x + 9, core_y + 7), metal.shade)
    canvas.fill_ellipse((core_x - 5, core_y - 4, core_x + 5, core_y + 4), glow.base)
    canvas.fill_ellipse((core_x - 2, core_y - 2, core_x + 1, core_y + 1), glow.light)
    canvas.add_outline(palette.OUTLINE)
    return canvas


def render_platform() -> Canvas:
    width, height = PLATFORM_SIZE
    metal, glow = palette.ANCIENT_METAL, palette.ANCIENT_GLOW
    canvas = Canvas(width, height)
    top = PLATFORM_SURFACE_Y
    canvas.fill_polygon([(0, top), (width - 1, top), (width - 6, top + 7), (5, top + 7)], metal.base)
    canvas.fill_rect((0, top, width - 1, top), metal.light)
    canvas.fill_polygon(
        [(width // 2, top + 2), (width - 1, top + 2), (width - 6, top + 7), (width // 2, top + 7)], metal.shade
    )
    canvas.fill_rect((12, top + 4, width - 13, top + 4), glow.base)
    canvas.add_outline(palette.OUTLINE)
    return canvas


def render_hit_spark() -> Canvas:
    """4 frames, 32px each: an expanding white star with an flux-warm core."""
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
        canvas.fill_ellipse(
            (center_x - core, center_y - core, center_x + core, center_y + core),
            mix_colors((255, 236, 120), (255, 140, 60), frame / 3),
        )
    return canvas


def render_flux_bolt(flux: Ramp) -> Canvas:
    """2 frames, 16px each: pulsing flux orb with a trailing tail (faces right)."""
    size = 16
    canvas = Canvas(size * 2, size)
    for frame in range(2):
        center_x, center_y = frame * size + 10, size // 2
        canvas.fill_ellipse((center_x - 9, center_y - 2, center_x - 1, center_y + 2), (*flux.shade, 140))
        radius = 4 + frame
        canvas.fill_ellipse(
            (center_x - radius, center_y - radius, center_x + radius, center_y + radius), (*flux.base, 200)
        )
        canvas.fill_ellipse((center_x - 2, center_y - 2, center_x + 2, center_y + 2), flux.light)
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
        canvas.fill_ellipse(
            (center_x - half_width, center_y - half_height, center_x + half_width, center_y + half_height),
            (*palette.OUTLINE, 70),
        )
        canvas.fill_ellipse(
            (
                center_x - half_width + 3,
                center_y - half_height + 1,
                center_x + half_width - 3,
                center_y + half_height - 1,
            ),
            (*palette.OUTLINE, 120),
        )
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
            canvas.fill_ellipse(
                (puff_x - radius, puff_y - radius, puff_x + radius, puff_y + radius), (*sand.shade, alpha)
            )
            canvas.fill_ellipse(
                (puff_x - radius + 1, puff_y - radius, puff_x + radius - 1, puff_y + radius - 1), (*sand.light, alpha)
            )
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
        canvas.draw_arc(
            (center_x - ring, center_y - ring, center_x + ring, center_y + ring), 0, 360, (255, 248, 230, fade), 2
        )
        core = max(7 - frame * 2, 0)
        if core:
            canvas.fill_ellipse(
                (center_x - core, center_y - core, center_x + core, center_y + core), (255, 252, 240, fade)
            )
    return canvas
