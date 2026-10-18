"""Shared colours: a dusk sky, ancient metal, and glowing flux in six colours."""

from __future__ import annotations

from pixel import Color, Ramp

OUTLINE: Color = (34, 24, 40)
WHITE: Color = (255, 255, 255)
EYE_WHITE: Color = (250, 248, 240)
PUPIL: Color = (30, 22, 36)

# Flux colours follow the series' code: green, blue (speed), red (strength), yellow (projectile).
FLUX_GREEN = Ramp(shade=(46, 160, 70), base=(120, 230, 90), light=(220, 255, 190))
FLUX_BLUE = Ramp(shade=(30, 110, 200), base=(90, 200, 255), light=(210, 245, 255))
FLUX_RED = Ramp(shade=(170, 30, 40), base=(255, 90, 70), light=(255, 210, 180))
FLUX_YELLOW = Ramp(shade=(210, 140, 20), base=(255, 226, 70), light=(255, 252, 200))
FLUX_DARK = Ramp(shade=(90, 40, 140), base=(160, 90, 230), light=(226, 190, 255))
FLUX_ORANGE = Ramp(shade=(200, 90, 20), base=(255, 150, 40), light=(255, 220, 150))

ANCIENT_METAL = Ramp(shade=(56, 72, 96), base=(104, 130, 158), light=(170, 196, 214))
ANCIENT_GLOW = Ramp(shade=(40, 150, 200), base=(110, 230, 255), light=(230, 255, 255))

SAND = Ramp(shade=(206, 168, 110), base=(238, 210, 150), light=(252, 236, 196))

# Player identity: selectors, in-fight markers. Distinct in luminance, not only in hue.
SLOT_P1: Color = (236, 70, 70)
SLOT_P2: Color = (70, 140, 240)
SLOT_BOT: Color = (150, 150, 160)

# Dusk over a sea of clouds. The decor keeps to these few tones plus one flux accent (cyan);
# saturated colour is left to the fighters so they read first.
SKY_BANDS: list[Color] = [
    (30, 40, 82),
    (58, 74, 128),
    (124, 108, 158),
    (222, 148, 132),
    (250, 202, 152),
]
CLOUD_SEA: list[Color] = [(244, 190, 156), (196, 140, 152), (128, 104, 150), (78, 76, 128)]
SILHOUETTE_FAR: Color = (104, 96, 150)
SILHOUETTE_MID = Ramp(shade=(40, 42, 78), base=(58, 60, 102), light=(96, 102, 148))
SUN = Ramp(shade=(246, 180, 130), base=(252, 214, 164), light=(255, 238, 206))
