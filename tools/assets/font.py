"""EcoPixel: a 5x7 uppercase pixel font with a baked 1px outline, exported as AngelCode BMFont.

The fill is white so Godot's font_color tints it; the black outline stays black under tinting.
"""
from __future__ import annotations

from PIL import Image

import palette
from pixel import Canvas

ACCENT_ROWS = 2
BODY_ROWS = 7
DESCENDER_ROWS = 1
GLYPH_ROWS = ACCENT_ROWS + BODY_ROWS + DESCENDER_ROWS
CELL_HEIGHT = GLYPH_ROWS + 2
FONT_SIZE = CELL_HEIGHT
LINE_HEIGHT = CELL_HEIGHT + 1
COLUMNS = 16
CELL_WIDTH = 8

GLYPHS: dict[str, tuple[str, ...]] = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ".": (".", ".", ".", ".", ".", ".", "#"),
    ",": (".", ".", ".", ".", ".", "#", "#"),
    "!": ("#", "#", "#", "#", "#", ".", "#"),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    ":": (".", "#", ".", ".", ".", "#", "."),
    "-": ("...", "...", "...", "###", "...", "...", "..."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "%": ("##..#", "##..#", "...#.", "..#..", ".#...", "#..##", "#..##"),
    "'": ("#", "#", ".", ".", ".", ".", "."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": (".#", "#.", "#.", "#.", "#.", "#.", ".#"),
    ")": ("#.", ".#", ".#", ".#", ".#", ".#", "#."),
    "<": ("...#", "..#.", ".#..", "#...", ".#..", "..#.", "...#"),
    ">": ("#...", ".#..", "..#.", "...#", "..#.", ".#..", "#..."),
    "·": (".", ".", ".", "#", ".", ".", "."),
    "←": (".....", "..#..", ".#...", "#####", ".#...", "..#..", "....."),
    "→": (".....", "..#..", "...#.", "#####", "...#.", "..#..", "....."),
    "↑": ("..#..", ".###.", "#.#.#", "..#..", "..#..", "..#..", "..#.."),
    "↓": ("..#..", "..#..", "..#..", "..#..", "#.#.#", ".###.", "..#.."),
}

ACCENTS: dict[str, tuple[str, str]] = {
    "acute": ("...#.", "..#.."),
    "grave": (".#...", "..#.."),
    "circumflex": ("..#..", ".#.#."),
    "diaeresis": (".....", ".#.#."),
}

ACCENTED: dict[str, tuple[str, str]] = {
    "É": ("E", "acute"), "È": ("E", "grave"), "Ê": ("E", "circumflex"), "Ë": ("E", "diaeresis"),
    "À": ("A", "grave"), "Â": ("A", "circumflex"), "Ô": ("O", "circumflex"), "Ù": ("U", "grave"),
    "Û": ("U", "circumflex"), "Î": ("I", "circumflex"), "Ï": ("I", "diaeresis"),
}

SPACE_ADVANCE = 4


def build_glyph_rows() -> dict[str, list[str]]:
    """Every glyph as GLYPH_ROWS strings, accents on top, descender at the bottom."""
    empty_accent = lambda width: ["." * width] * ACCENT_ROWS  # noqa: E731
    rows: dict[str, list[str]] = {}
    for char, body in GLYPHS.items():
        width = len(body[0])
        rows[char] = empty_accent(width) + list(body) + ["." * width]
    for char, (base, accent) in ACCENTED.items():
        body = list(GLYPHS[base])
        width = len(body[0])
        accent_rows = [row[(5 - width) // 2:(5 - width) // 2 + width] for row in ACCENTS[accent]]
        rows[char] = accent_rows + body + ["." * width]
    cedilla = list(GLYPHS["C"])
    rows["Ç"] = empty_accent(5) + cedilla + ["..#.."]
    for char in list(rows):
        lower = char.lower()
        if lower != char and lower not in rows:
            rows[lower] = rows[char]
    return rows


def render_glyph(rows: list[str]) -> Canvas:
    width = len(rows[0])
    canvas = Canvas(width + 2, CELL_HEIGHT)
    for y, row in enumerate(rows):
        for x, cell in enumerate(row):
            if cell == "#":
                canvas.put_pixel(x + 1, y + 1, palette.WHITE)
    canvas.add_outline((0, 0, 0))
    return canvas


def render_font(page_name: str) -> tuple[Image.Image, str]:
    """Returns the atlas image and the BMFont text descriptor.

    O(g) glyphs, each O(1) since glyphs are fixed size.
    """
    rows = build_glyph_rows()
    chars = sorted(rows)
    sheet_rows = (len(chars) + COLUMNS) // COLUMNS
    atlas = Image.new("RGBA", (COLUMNS * CELL_WIDTH, sheet_rows * CELL_HEIGHT), (0, 0, 0, 0))
    lines = []
    for index, char in enumerate(chars):
        glyph = render_glyph(rows[char])
        x, y = (index % COLUMNS) * CELL_WIDTH, (index // COLUMNS) * CELL_HEIGHT
        atlas.alpha_composite(glyph.image, dest=(x, y))
        advance = glyph.width - 1
        lines.append(
            f"char id={ord(char)} x={x} y={y} width={glyph.width} height={CELL_HEIGHT} "
            f"xoffset=0 yoffset=0 xadvance={advance} page=0 chnl=15"
        )
    lines.append(f"char id=32 x=0 y=0 width=0 height=0 xoffset=0 yoffset=0 xadvance={SPACE_ADVANCE} page=0 chnl=15")
    header = [
        f'info face="EcoPixel" size={FONT_SIZE} bold=0 italic=0 charset="" unicode=1 stretchH=100 smooth=0 aa=1 padding=0,0,0,0 spacing=0,0 outline=0',
        f"common lineHeight={LINE_HEIGHT} base={1 + ACCENT_ROWS + BODY_ROWS} scaleW={atlas.width} scaleH={atlas.height} pages=1 packed=0",
        f'page id=0 file="{page_name}"',
        f"chars count={len(lines)}",
    ]
    return atlas, "\n".join(header + lines) + "\n"


def render_text(text: str, scale: int) -> Image.Image:
    """Rasterise a word with the same glyphs, for logos baked into images."""
    rows = build_glyph_rows()
    glyphs = [render_glyph(rows[char]) if char != " " else Canvas(SPACE_ADVANCE + 1, CELL_HEIGHT) for char in text]
    width = sum(glyph.width - 1 for glyph in glyphs) + 1
    image = Image.new("RGBA", (width, CELL_HEIGHT), (0, 0, 0, 0))
    x = 0
    for glyph in glyphs:
        image.alpha_composite(glyph.image, dest=(x, 0))
        x += glyph.width - 1
    return image.resize((image.width * scale, image.height * scale), Image.NEAREST)
