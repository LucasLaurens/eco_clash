"""Shared colours. Warm tropical tones and glowing eco, in the spirit of Jak and Daxter."""
from __future__ import annotations

from pixel import Color, Ramp

OUTLINE: Color = (34, 24, 40)
WHITE: Color = (255, 255, 255)
EYE_WHITE: Color = (250, 248, 240)
PUPIL: Color = (30, 22, 36)

# Eco colours follow the series' code: green, blue (speed), red (strength), yellow (projectile).
ECO_GREEN = Ramp(shade=(46, 160, 70), base=(120, 230, 90), light=(220, 255, 190))
ECO_BLUE = Ramp(shade=(30, 110, 200), base=(90, 200, 255), light=(210, 245, 255))
ECO_RED = Ramp(shade=(170, 30, 40), base=(255, 90, 70), light=(255, 210, 180))
ECO_YELLOW = Ramp(shade=(210, 140, 20), base=(255, 226, 70), light=(255, 252, 200))

PRECURSOR_METAL = Ramp(shade=(56, 72, 96), base=(104, 130, 158), light=(170, 196, 214))
PRECURSOR_GLOW = Ramp(shade=(40, 150, 200), base=(110, 230, 255), light=(230, 255, 255))

GRASS = Ramp(shade=(46, 120, 52), base=(86, 170, 64), light=(160, 216, 92))
DIRT = Ramp(shade=(120, 62, 40), base=(176, 98, 56), light=(214, 146, 88))
ROCK = Ramp(shade=(88, 60, 64), base=(132, 92, 84), light=(178, 132, 110))
SAND = Ramp(shade=(206, 168, 110), base=(238, 210, 150), light=(252, 236, 196))
WOOD = Ramp(shade=(96, 58, 34), base=(140, 92, 54), light=(184, 132, 80))

SKY_BANDS: list[Color] = [
    (58, 128, 214),
    (84, 152, 228),
    (118, 178, 236),
    (156, 202, 240),
    (196, 222, 236),
    (240, 226, 196),
    (255, 206, 150),
]
