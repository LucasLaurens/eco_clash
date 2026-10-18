"""UI kit: logo, Precursor-metal panels, character portraits, stock icons, player selectors."""
from __future__ import annotations

from PIL import Image

import font
import palette
from fighters import FRAME_SIZE, IDLE, FighterArtist
from pixel import Canvas, Color, Ramp, mix_colors

PORTRAIT_SIZE = 48
STOCK_ICON_SIZE = 16
PANEL_SIZE = 24
SELECTOR_SIZE = 52


def render_logo() -> Image.Image:
    text = font.render_text("ECO CLASH", 4)
    canvas = Canvas(text.width + 8, text.height + 8)
    top, bottom = (255, 240, 120), (255, 132, 40)
    pixels = text.load()
    for y in range(text.height):
        for x in range(text.width):
            red, _green, _blue, alpha = pixels[x, y]
            if alpha and red > 128:
                pixels[x, y] = mix_colors(top, bottom, y / text.height)
            elif alpha:
                pixels[x, y] = (*palette.OUTLINE, 255)
    shadow = Image.new("RGBA", text.size, (*palette.ECO_BLUE.shade, 255))
    shadow.putalpha(text.getchannel("A"))
    canvas.paste(shadow, (6, 7))
    canvas.paste(text, (4, 4))
    canvas.add_outline(palette.OUTLINE)
    return canvas.image


def render_panel(border: Ramp, fill: Color) -> Canvas:
    """9-slice friendly: 6px border, rivets in the corners."""
    size = PANEL_SIZE
    canvas = Canvas(size, size)
    canvas.fill_rect((1, 1, size - 2, size - 2), border.base)
    canvas.fill_rect((1, 1, size - 2, 1), border.light)
    canvas.fill_rect((1, size - 2, size - 2, size - 2), border.shade)
    canvas.fill_rect((4, 4, size - 5, size - 5), fill)
    canvas.fill_rect((4, 4, size - 5, 4), mix_colors(fill, (0, 0, 0), 0.35))
    for x, y in ((2, 2), (size - 3, 2), (2, size - 3), (size - 3, size - 3)):
        canvas.put_pixel(x, y, border.light)
    canvas.add_outline(palette.OUTLINE)
    return canvas


def render_panels() -> dict[str, Canvas]:
    metal, glow = palette.PRECURSOR_METAL, palette.PRECURSOR_GLOW
    return {
        "panel": render_panel(metal, (28, 40, 60, 230)),
        "button": render_panel(metal, (40, 58, 84)),
        "button_focus": render_panel(glow, (40, 90, 120)),
        "button_pressed": render_panel(Ramp(metal.shade, metal.shade, metal.base), (24, 34, 50)),
    }


def crop_head(artist: FighterArtist) -> Image.Image:
    """Square crop around the idle head, shared by portrait and stock icon."""
    frame = artist.render_frame(IDLE[0]).image
    x, y = artist.build_skeleton(IDLE[0]).head
    half = 12
    left = max(min(x - half, FRAME_SIZE - half * 2), 0)
    top = max(y - half - 2, 0)
    return frame.crop((left, top, left + half * 2, top + half * 2))


def render_portrait(artist: FighterArtist) -> Image.Image:
    canvas = Canvas(PORTRAIT_SIZE, PORTRAIT_SIZE)
    eco = artist.eco
    canvas.fill_vertical_gradient((2, 2, PORTRAIT_SIZE - 3, PORTRAIT_SIZE - 3), [eco.light, eco.base, eco.shade])
    head = crop_head(artist).resize((PORTRAIT_SIZE - 4, PORTRAIT_SIZE - 4), Image.NEAREST)
    canvas.paste(head, (2, 4))
    frame = Canvas(PORTRAIT_SIZE, PORTRAIT_SIZE)
    frame.fill_rect((0, 0, PORTRAIT_SIZE - 1, 1), palette.OUTLINE)
    frame.fill_rect((0, PORTRAIT_SIZE - 2, PORTRAIT_SIZE - 1, PORTRAIT_SIZE - 1), palette.OUTLINE)
    frame.fill_rect((0, 0, 1, PORTRAIT_SIZE - 1), palette.OUTLINE)
    frame.fill_rect((PORTRAIT_SIZE - 2, 0, PORTRAIT_SIZE - 1, PORTRAIT_SIZE - 1), palette.OUTLINE)
    canvas.paste(frame.image, (0, 0))
    return canvas.image


def render_stock_icon(artist: FighterArtist) -> Image.Image:
    return crop_head(artist).resize((STOCK_ICON_SIZE, STOCK_ICON_SIZE), Image.NEAREST)


def render_selector(color: Color, label: str) -> Image.Image:
    """Corner brackets plus a tag, drawn around the hovered portrait."""
    size = SELECTOR_SIZE
    canvas = Canvas(size, size + 12)
    arm = 10
    for x, y, dx, dy in ((1, 1, 1, 1), (size - 2, 1, -1, 1), (1, size - 2, 1, -1), (size - 2, size - 2, -1, -1)):
        canvas.draw_line((x, y), (x + dx * arm, y), color, 2)
        canvas.draw_line((x, y), (x, y + dy * arm), color, 2)
    tag = font.render_text(label, 1)
    tag_x = (size - tag.width) // 2
    canvas.fill_rect((tag_x - 2, size + 1, tag_x + tag.width + 1, size + tag.height - 2), color)
    canvas.paste(tag, (tag_x, size - 1))
    canvas.add_outline(palette.OUTLINE)
    return canvas.image


def render_slot_marker(color: Color, label: str) -> Image.Image:
    """Tag floating above a fighter: the slot label on its colour, with a notch pointing down at the head."""
    tag = font.render_text(label, 1)
    width = tag.width + 4
    canvas = Canvas(width + 2, tag.height + 4)
    canvas.fill_rect((1, 2, width, tag.height - 3), color)
    center = (width + 2) // 2
    canvas.fill_polygon([(center - 3, tag.height - 3), (center + 3, tag.height - 3), (center, tag.height)], color)
    canvas.paste(tag, (3, 0))
    canvas.add_outline(palette.OUTLINE)
    return canvas.image
