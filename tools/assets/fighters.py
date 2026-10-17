"""Fighter sprite sheets, drawn by a tiny pose-driven puppet.

Template Method: FighterArtist fixes the skeleton and the drawing order;
each character subclass only paints its own torso, head and extras.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum

from PIL import Image

import palette
from pixel import Canvas, Color, Point, Ramp

FRAME_SIZE = 48
FEET_Y = 44
CENTER_X = 24


class Effect(Enum):
    NONE = "none"
    SMEAR = "smear"
    CHARGE = "charge"
    RELEASE = "release"
    FOLLOW = "follow"


@dataclass(frozen=True)
class Pose:
    """Offsets of one frame. Feet are relative to the hip on x and lifted from the ground on y."""

    bob: int = 0
    lean: int = 0
    front_foot: Point = (3, 0)
    back_foot: Point = (-3, 0)
    front_hand: Point = (3, 9)
    back_hand: Point = (-3, 9)
    hurt: bool = False
    effect: Effect = Effect.NONE


@dataclass(frozen=True)
class Animation:
    name: str
    fps: float
    loop: bool
    poses: list[Pose]


@dataclass(frozen=True)
class Anatomy:
    leg_length: int
    torso_height: int
    torso_width: int
    head_radius: int
    limb_radius: int
    hand_radius: int
    reach: float = 1.0
    legs_behind_torso: bool = False


@dataclass(frozen=True)
class Skeleton:
    hip: Point
    shoulder: Point
    head: Point
    front_foot: Point
    back_foot: Point
    front_hand: Point
    back_hand: Point


IDLE = [Pose(), Pose(bob=1, front_hand=(3, 8), back_hand=(-3, 8))]
RUN = [
    Pose(lean=2, front_foot=(6, 0), back_foot=(-5, 3), front_hand=(-3, 7), back_hand=(5, 6)),
    Pose(lean=2, bob=-1, front_foot=(2, 3), back_foot=(-1, 0), front_hand=(0, 9), back_hand=(1, 8)),
    Pose(lean=2, front_foot=(-5, 3), back_foot=(6, 0), front_hand=(6, 6), back_hand=(-4, 7)),
    Pose(lean=2, bob=-1, front_foot=(-1, 0), back_foot=(2, 3), front_hand=(1, 8), back_hand=(0, 9)),
]
JUMP = [Pose(front_foot=(4, 5), back_foot=(-3, 3), front_hand=(5, -3), back_hand=(-5, -2))]
FALL = [Pose(front_foot=(4, 1), back_foot=(-3, 2), front_hand=(7, 1), back_hand=(-7, 0))]
ATTACK = [
    Pose(lean=-1, front_hand=(-5, 4), back_hand=(3, 6), front_foot=(4, 0), back_foot=(-4, 0)),
    Pose(lean=3, front_hand=(11, 2), back_hand=(-5, 6), front_foot=(7, 0), back_foot=(-5, 0), effect=Effect.SMEAR),
    Pose(lean=2, front_hand=(8, 5), back_hand=(-4, 7), front_foot=(6, 0), back_foot=(-5, 0)),
]
GENERIC_SPECIAL = [
    Pose(bob=2, front_hand=(3, 6), back_hand=(2, 7), effect=Effect.CHARGE),
    Pose(lean=2, front_hand=(10, 1), back_hand=(-6, 3), front_foot=(6, 0), effect=Effect.RELEASE),
    Pose(lean=1, front_hand=(8, 4), back_hand=(-5, 6), front_foot=(5, 0), effect=Effect.FOLLOW),
]
HURT = [Pose(lean=-3, front_hand=(-6, -3), back_hand=(-3, -5), front_foot=(5, 3), back_foot=(-2, 1), hurt=True)]


def build_animations(special_poses: list[Pose]) -> list[Animation]:
    """Order matters: frames are laid out left to right in this exact sequence."""
    return [
        Animation("idle", 3, True, IDLE),
        Animation("run", 10, True, RUN),
        Animation("jump", 1, False, JUMP),
        Animation("fall", 1, False, FALL),
        Animation("attack", 1, False, ATTACK),
        Animation("special", 1, False, special_poses),
        Animation("hurt", 1, False, HURT),
    ]


def build_layout() -> dict:
    """Frame indices per animation. Exported to JSON so Godot reads the same truth (DRY)."""
    layout: dict = {"frame_size": FRAME_SIZE, "feet_y": FEET_Y, "animations": {}}
    index = 0
    for animation in build_animations(GENERIC_SPECIAL):
        frames = list(range(index, index + len(animation.poses)))
        layout["animations"][animation.name] = {"frames": frames, "fps": animation.fps, "loop": animation.loop}
        index += len(animation.poses)
    layout["frame_count"] = index
    return layout


@dataclass
class FighterArtist:
    """Base painter. Subclasses override the paint_* hooks, never the order."""

    anatomy: Anatomy
    skin: Ramp
    limb: Ramp
    sleeve: Ramp
    boot: Ramp
    eco: Ramp
    special_poses: list[Pose] = field(default_factory=lambda: GENERIC_SPECIAL)

    def render_sheet(self) -> Image.Image:
        animations = build_animations(self.special_poses)
        poses = [pose for animation in animations for pose in animation.poses]
        sheet = Image.new("RGBA", (FRAME_SIZE * len(poses), FRAME_SIZE), (0, 0, 0, 0))
        for index, pose in enumerate(poses):
            sheet.alpha_composite(self.render_frame(pose).image, dest=(index * FRAME_SIZE, 0))
        return sheet

    def render_frame(self, pose: Pose) -> Canvas:
        canvas = Canvas(FRAME_SIZE, FRAME_SIZE)
        skeleton = self.build_skeleton(pose)
        self.paint_back_extras(canvas, skeleton, pose)
        self.paint_leg(canvas, skeleton.hip, skeleton.back_foot, front=False)
        self.paint_arm(canvas, skeleton.shoulder, skeleton.back_hand, front=False)
        if self.anatomy.legs_behind_torso:
            self.paint_leg(canvas, skeleton.hip, skeleton.front_foot, front=True)
        self.paint_torso(canvas, skeleton, pose)
        if not self.anatomy.legs_behind_torso:
            self.paint_leg(canvas, skeleton.hip, skeleton.front_foot, front=True)
        self.paint_head(canvas, skeleton, pose)
        self.paint_arm(canvas, skeleton.shoulder, skeleton.front_hand, front=True)
        self.paint_front_extras(canvas, skeleton, pose)
        canvas.add_outline(palette.OUTLINE)
        # Effects live on their own layer: PIL replaces pixels instead of blending them.
        effects = Canvas(FRAME_SIZE, FRAME_SIZE)
        self.paint_effect(effects, skeleton, pose)
        canvas.paste(effects.image, (0, 0))
        return canvas

    def build_skeleton(self, pose: Pose) -> Skeleton:
        a = self.anatomy
        hip = (CENTER_X + pose.lean // 2, FEET_Y - a.leg_length + pose.bob)
        shoulder = (hip[0] + pose.lean - pose.lean // 2, hip[1] - a.torso_height)
        head = (shoulder[0] + 1, shoulder[1] - a.head_radius + 1)
        return Skeleton(
            hip=hip,
            shoulder=shoulder,
            head=head,
            front_foot=(hip[0] + self._scale(pose.front_foot[0]), FEET_Y - self._scale(pose.front_foot[1])),
            back_foot=(hip[0] + self._scale(pose.back_foot[0]), FEET_Y - self._scale(pose.back_foot[1])),
            front_hand=(shoulder[0] + self._scale(pose.front_hand[0]), shoulder[1] + self._scale(pose.front_hand[1])),
            back_hand=(shoulder[0] + self._scale(pose.back_hand[0]), shoulder[1] + self._scale(pose.back_hand[1])),
        )

    def _scale(self, value: int) -> int:
        return round(value * self.anatomy.reach)

    def paint_leg(self, canvas: Canvas, hip: Point, foot: Point, front: bool) -> None:
        color = self.limb.base if front else self.limb.shade
        start = (hip[0] + (1 if front else -1), hip[1])
        canvas.draw_capsule(start, (foot[0], foot[1] - 2), self.anatomy.limb_radius, color)
        boot = self.boot.base if front else self.boot.shade
        canvas.fill_ellipse((foot[0] - 2, foot[1] - 3, foot[0] + 3, foot[1]), boot)
        if front:
            canvas.put_pixel(foot[0] + 1, foot[1] - 2, self.boot.light)

    def paint_arm(self, canvas: Canvas, shoulder: Point, hand: Point, front: bool) -> None:
        color = self.sleeve.base if front else self.sleeve.shade
        canvas.draw_capsule(shoulder, hand, self.anatomy.limb_radius, color)
        r = self.anatomy.hand_radius
        canvas.fill_ellipse((hand[0] - r, hand[1] - r, hand[0] + r, hand[1] + r), self.skin.base if front else self.skin.shade)

    def paint_eye(self, canvas: Canvas, x: int, y: int, pose: Pose, height: int = 3) -> None:
        if pose.hurt:
            canvas.draw_line((x, y), (x + 2, y + 2), palette.PUPIL)
            canvas.draw_line((x, y + 2), (x + 2, y), palette.PUPIL)
            return
        canvas.fill_rect((x, y, x + 1, y + height - 1), palette.EYE_WHITE)
        canvas.fill_rect((x + 1, y + 1, x + 1, y + height - 1), palette.PUPIL)

    def paint_back_extras(self, canvas: Canvas, s: Skeleton, pose: Pose) -> None:
        pass

    def paint_front_extras(self, canvas: Canvas, s: Skeleton, pose: Pose) -> None:
        pass

    def paint_torso(self, canvas: Canvas, s: Skeleton, pose: Pose) -> None:
        raise NotImplementedError

    def paint_head(self, canvas: Canvas, s: Skeleton, pose: Pose) -> None:
        raise NotImplementedError

    def paint_effect(self, canvas: Canvas, s: Skeleton, pose: Pose) -> None:
        hx, hy = s.front_hand
        eco = self.eco
        if pose.effect is Effect.SMEAR:
            radius = abs(hx - s.shoulder[0]) + 3
            box = (s.shoulder[0] - radius, s.shoulder[1] - radius, s.shoulder[0] + radius, s.shoulder[1] + radius)
            canvas.draw_arc(box, -70, 40, (*palette.WHITE, 220), 2)
            canvas.draw_arc((box[0] + 2, box[1] + 2, box[2] - 2, box[3] - 2), -50, 30, (*eco.base, 200), 1)
        elif pose.effect is Effect.CHARGE:
            for dx, dy in ((-4, -3), (4, -4), (5, 3), (-3, 4)):
                canvas.put_pixel(hx + dx, hy + dy, eco.light)
                canvas.put_pixel(hx + dx + 1, hy + dy, eco.base)
            canvas.fill_ellipse((hx - 2, hy - 2, hx + 2, hy + 2), (*eco.base, 170))
        elif pose.effect is Effect.RELEASE:
            canvas.fill_ellipse((hx - 4, hy - 4, hx + 4, hy + 4), (*eco.base, 150))
            canvas.fill_ellipse((hx - 2, hy - 2, hx + 2, hy + 2), eco.light)
            for dx, dy in ((-6, 0), (6, 0), (0, -6), (0, 6)):
                canvas.put_pixel(hx + dx, hy + dy, eco.light)
        elif pose.effect is Effect.FOLLOW:
            for dx, dy in ((-3, -2), (-6, 1), (-2, 3)):
                canvas.put_pixel(hx + dx, hy + dy, eco.base)


class KaelArtist(FighterArtist):
    """Balanced hero: spiky blond hair with green tips, goggles, elf ears, blue tunic."""

    HAIR = Ramp(shade=(212, 156, 40), base=(250, 212, 92), light=(255, 240, 170))
    HAIR_TIP: Color = (106, 190, 70)
    TUNIC = Ramp(shade=(30, 78, 150), base=(52, 128, 200), light=(116, 182, 240))
    BELT = Ramp(shade=(84, 48, 28), base=(120, 72, 40), light=(160, 104, 60))
    SCARF = Ramp(shade=(180, 60, 30), base=(236, 104, 44), light=(255, 170, 90))
    LENS: Color = (90, 220, 230)

    def paint_torso(self, canvas: Canvas, s: Skeleton, pose: Pose) -> None:
        (sx, sy), (hx, hy) = s.shoulder, s.hip
        canvas.fill_polygon([(sx - 4, sy), (sx + 4, sy), (hx + 5, hy + 2), (hx - 5, hy + 2)], self.TUNIC.base)
        canvas.fill_polygon([(sx - 4, sy), (sx - 1, sy), (hx - 1, hy + 2), (hx - 5, hy + 2)], self.TUNIC.shade)
        canvas.put_pixel(sx + 2, sy + 2, self.TUNIC.light)
        canvas.fill_rect((hx - 4, hy - 1, hx + 4, hy), self.BELT.base)
        canvas.put_pixel(hx + 2, hy - 1, self.BELT.light)
        flutter = 1 if pose.bob else 0
        canvas.fill_rect((sx - 3, sy - 1, sx + 3, sy + 1), self.SCARF.base)
        canvas.fill_polygon([(sx - 3, sy), (sx - 8, sy + 2 + flutter), (sx - 7, sy + 4 + flutter), (sx - 2, sy + 2)], self.SCARF.shade)

    def paint_head(self, canvas: Canvas, s: Skeleton, pose: Pose) -> None:
        x, y = s.head
        r = self.anatomy.head_radius
        canvas.fill_polygon([(x - r + 2, y), (x - r - 4, y - 5), (x - r + 3, y - 2)], self.skin.base)
        canvas.fill_shaded_ellipse((x - r, y - r, x + r, y + r), self.skin)
        hair = [
            (x + r, y - 3), (x + 4, y - r - 3), (x + 2, y - r), (x - 1, y - r - 6), (x - 3, y - r),
            (x - 7, y - r - 3), (x - r - 1, y - 3), (x - r - 2, y + 2), (x - r + 2, y + 4), (x - 1, y - 1), (x + 2, y - 3),
        ]
        canvas.fill_polygon(hair, self.HAIR.base)
        canvas.fill_polygon([(x - r - 1, y - 3), (x - r - 2, y + 2), (x - r + 2, y + 4), (x - 2, y)], self.HAIR.shade)
        for tip in ((x + 4, y - r - 3), (x - 1, y - r - 6), (x - 7, y - r - 3)):
            canvas.put_pixel(tip[0], tip[1], self.HAIR_TIP)
            canvas.put_pixel(tip[0], tip[1] + 1, self.HAIR_TIP)
        canvas.put_pixel(x, y - r - 2, self.HAIR.light)
        canvas.draw_line((x - r + 1, y - 3), (x + r - 1, y - 4), self.BELT.base)
        canvas.fill_ellipse((x + 1, y - 7, x + 4, y - 4), self.LENS)
        canvas.put_pixel(x + 2, y - 6, palette.WHITE)
        self.paint_eye(canvas, x + 3, y - 1, pose)
        canvas.put_pixel(x + r, y + 1, self.skin.shade)
        canvas.draw_line((x + 3, y + 4), (x + 5, y + 3), self.skin.shade)


class PipArtist(FighterArtist):
    """Fast critter: orange fur, cream muzzle, huge ears, bushy tail, goggles."""

    CREAM = Ramp(shade=(220, 190, 140), base=(255, 236, 200), light=(255, 250, 235))
    INNER_EAR: Color = (240, 140, 140)
    NOSE: Color = (60, 30, 30)
    STRAP: Color = (90, 60, 40)
    LENS: Color = (90, 200, 255)

    def paint_back_extras(self, canvas: Canvas, s: Skeleton, pose: Pose) -> None:
        hx, hy = s.hip
        sway = pose.bob
        canvas.fill_ellipse((hx - 9, hy - 6 + sway, hx - 2, hy + 1), self.skin.shade)
        canvas.fill_ellipse((hx - 12, hy - 12 + sway, hx - 5, hy - 4 + sway), self.skin.base)
        canvas.fill_ellipse((hx - 13, hy - 16 + sway, hx - 8, hy - 10 + sway), self.CREAM.base)

    def paint_torso(self, canvas: Canvas, s: Skeleton, pose: Pose) -> None:
        (sx, sy), (hx, hy) = s.shoulder, s.hip
        canvas.fill_shaded_ellipse((hx - 5, sy - 1, hx + 5, hy + 2), self.skin)
        canvas.fill_ellipse((hx, sy + 1, hx + 4, hy + 1), self.CREAM.base)

    def paint_head(self, canvas: Canvas, s: Skeleton, pose: Pose) -> None:
        x, y = s.head
        r = self.anatomy.head_radius
        canvas.fill_polygon([(x - 5, y - r + 2), (x - 5, y - r - 6), (x, y - r + 1)], self.skin.shade)
        canvas.fill_polygon([(x, y - r + 2), (x + 3, y - r - 7), (x + 6, y - r + 3)], self.skin.base)
        canvas.draw_line((x + 2, y - r), (x + 3, y - r - 4), self.INNER_EAR)
        canvas.fill_shaded_ellipse((x - r, y - r, x + r, y + r), self.skin)
        canvas.fill_ellipse((x + 1, y, x + r + 3, y + 5), self.CREAM.base)
        canvas.put_pixel(x + r + 3, y + 1, self.NOSE)
        canvas.put_pixel(x + r + 2, y + 1, self.NOSE)
        canvas.draw_line((x - r + 1, y - 4), (x + r - 1, y - 5), self.STRAP)
        canvas.fill_ellipse((x, y - 7, x + 3, y - 4), self.LENS)
        canvas.put_pixel(x + 1, y - 6, palette.WHITE)
        self.paint_eye(canvas, x + 3, y - 2, pose, height=3)
        canvas.put_pixel(x + 6, y + 4, self.CREAM.shade)


class GrondakArtist(FighterArtist):
    """Heavy lurker brute: purple hide, tusks, spiked shoulder pad, huge fists."""

    BELLY = Ramp(shade=(140, 116, 180), base=(186, 160, 220), light=(220, 204, 240))
    TUSK: Color = (250, 244, 220)
    EYE: Color = (255, 220, 60)
    CLOTH = Ramp(shade=(96, 56, 30), base=(140, 86, 48), light=(180, 120, 70))
    BONE: Color = (230, 220, 190)

    def build_skeleton(self, pose: Pose) -> Skeleton:
        skeleton = super().build_skeleton(pose)
        # Hunched: the head sits forward and low, between the shoulders.
        hunched = (skeleton.shoulder[0] + 5, skeleton.shoulder[1] - 1)
        return replace(skeleton, head=hunched)

    def paint_torso(self, canvas: Canvas, s: Skeleton, pose: Pose) -> None:
        (sx, sy), (hx, hy) = s.shoulder, s.hip
        canvas.fill_shaded_ellipse((sx - 9, sy - 3, sx + 8, hy + 3), self.skin)
        canvas.fill_ellipse((sx - 1, sy + 3, sx + 7, hy + 1), self.BELLY.base)
        canvas.fill_polygon([(hx - 6, hy), (hx + 6, hy), (hx + 4, hy + 6), (hx - 4, hy + 6)], self.CLOTH.base)
        canvas.fill_rect((hx - 6, hy - 1, hx + 6, hy), self.CLOTH.shade)
        metal = palette.PRECURSOR_METAL
        canvas.fill_shaded_ellipse((sx - 10, sy - 5, sx - 2, sy + 2), metal)
        for spike_x in (sx - 8, sx - 5):
            canvas.fill_polygon([(spike_x - 1, sy - 4), (spike_x + 1, sy - 4), (spike_x, sy - 8)], self.BONE)

    def paint_head(self, canvas: Canvas, s: Skeleton, pose: Pose) -> None:
        x, y = s.head
        r = self.anatomy.head_radius
        canvas.fill_polygon([(x - 3, y - r + 1), (x - 6, y - r - 4), (x - 1, y - r + 2)], self.BONE)
        canvas.fill_shaded_ellipse((x - r, y - r, x + r, y + r - 1), self.skin)
        canvas.fill_ellipse((x - 2, y + 1, x + r + 2, y + r + 2), self.skin.shade)
        canvas.fill_rect((x - 1, y - 3, x + r, y - 3), self.skin.shade)
        if pose.hurt:
            self.paint_eye(canvas, x + 2, y - 2, pose)
        else:
            canvas.fill_rect((x + 2, y - 2, x + 3, y - 1), self.EYE)
        canvas.fill_rect((x + 1, y + 1, x + 1, y + 2), self.TUSK)
        canvas.fill_rect((x + r, y - 1, x + r, y + 2), self.TUSK)

    def paint_arm(self, canvas: Canvas, shoulder: Point, hand: Point, front: bool) -> None:
        super().paint_arm(canvas, shoulder, hand, front)
        if front:
            canvas.fill_rect((hand[0] - 1, hand[1] - 3, hand[0] + 1, hand[1] - 3), palette.PRECURSOR_METAL.light)

    def paint_effect(self, canvas: Canvas, s: Skeleton, pose: Pose) -> None:
        if pose.effect is not Effect.RELEASE:
            super().paint_effect(canvas, s, pose)
            return
        for offset in (6, 11, 16):
            canvas.draw_line((CENTER_X - offset, FEET_Y - 1), (CENTER_X - offset - 3, FEET_Y - 5), self.eco.base)
            canvas.draw_line((CENTER_X + offset, FEET_Y - 1), (CENTER_X + offset + 3, FEET_Y - 5), self.eco.base)
        canvas.fill_rect((CENTER_X - 18, FEET_Y, CENTER_X + 18, FEET_Y), self.eco.light)


class NyraArtist(FighterArtist):
    """Eco sage: purple hooded robe, teal trim, staff topped with yellow eco."""

    CLOAK = Ramp(shade=(40, 30, 84), base=(70, 52, 128), light=(110, 88, 176))
    TRIM: Color = (60, 210, 196)
    HAIR: Color = (40, 200, 180)
    STAFF = Ramp(shade=(96, 58, 34), base=(150, 100, 58), light=(190, 140, 90))

    def paint_back_extras(self, canvas: Canvas, s: Skeleton, pose: Pose) -> None:
        (sx, sy), (hx, hy) = s.shoulder, s.hip
        canvas.fill_polygon([(sx - 2, sy), (sx - 8, hy + 6), (hx - 2, hy + 8)], self.CLOAK.shade)
        bx, by = s.back_hand
        canvas.draw_line((bx - 2, by + 7), (bx - 2, by - 20), self.STAFF.base)
        canvas.fill_ellipse((bx - 4, by - 24, bx, by - 20), self.eco.base)
        canvas.put_pixel(bx - 3, by - 23, self.eco.light)

    def paint_torso(self, canvas: Canvas, s: Skeleton, pose: Pose) -> None:
        (sx, sy), (hx, hy) = s.shoulder, s.hip
        hem = FEET_Y - 3
        canvas.fill_polygon([(sx - 4, sy), (sx + 4, sy), (hx + 6, hem), (hx - 6, hem)], self.CLOAK.base)
        canvas.fill_polygon([(sx - 4, sy), (sx - 1, sy), (hx - 2, hem), (hx - 6, hem)], self.CLOAK.shade)
        canvas.fill_rect((hx - 6, hem - 1, hx + 6, hem), self.TRIM)
        canvas.draw_line((sx + 3, sy + 1), (hx + 5, hem - 2), self.TRIM)
        canvas.fill_rect((sx + 1, sy + 2, sx + 2, sy + 3), self.eco.base)

    def paint_head(self, canvas: Canvas, s: Skeleton, pose: Pose) -> None:
        x, y = s.head
        r = self.anatomy.head_radius
        canvas.fill_polygon([(x - r, y - 2), (x - r - 5, y + 3), (x - r + 1, y + 4)], self.CLOAK.shade)
        canvas.fill_shaded_ellipse((x - r - 1, y - r - 1, x + r + 1, y + r), self.CLOAK)
        canvas.fill_ellipse((x - 1, y - r + 2, x + r, y + r - 1), self.skin.base)
        canvas.fill_rect((x - 1, y - r + 2, x + r - 1, y - r + 3), self.HAIR)
        canvas.draw_line((x - 2, y - r + 1), (x + r, y - r + 1), self.TRIM)
        self.paint_eye(canvas, x + 2, y - 1, pose)
        canvas.put_pixel(x + 4, y + 3, self.skin.shade)

    def paint_effect(self, canvas: Canvas, s: Skeleton, pose: Pose) -> None:
        super().paint_effect(canvas, s, pose)
        if pose.effect is Effect.CHARGE:
            bx, by = s.back_hand
            canvas.fill_ellipse((bx - 6, by - 26, bx + 2, by - 18), (*self.eco.light, 140))


SKIN_LIGHT = Ramp(shade=(201, 140, 98), base=(241, 190, 140), light=(255, 222, 184))
SKIN_TAN = Ramp(shade=(150, 96, 66), base=(200, 140, 100), light=(232, 180, 140))


def build_artists() -> dict[str, FighterArtist]:
    return {
        "kael": KaelArtist(
            anatomy=Anatomy(leg_length=10, torso_height=9, torso_width=8, head_radius=7, limb_radius=1, hand_radius=2),
            skin=SKIN_LIGHT,
            limb=Ramp(shade=(180, 160, 120), base=(226, 214, 180), light=(244, 236, 210)),
            sleeve=KaelArtist.TUNIC,
            boot=Ramp(shade=(84, 48, 28), base=(120, 72, 40), light=(170, 110, 64)),
            eco=palette.ECO_GREEN,
            special_poses=[
                Pose(bob=3, front_hand=(3, 6), back_hand=(-2, 7), effect=Effect.CHARGE),
                Pose(front_foot=(3, 4), back_foot=(-2, 6), front_hand=(3, -10), back_hand=(-5, 4), effect=Effect.RELEASE),
                Pose(front_foot=(3, 3), back_foot=(-3, 4), front_hand=(2, -8), back_hand=(-5, 5), effect=Effect.FOLLOW),
            ],
        ),
        "pip": PipArtist(
            anatomy=Anatomy(leg_length=6, torso_height=7, torso_width=9, head_radius=7, limb_radius=1, hand_radius=1, reach=0.75),
            skin=Ramp(shade=(190, 96, 24), base=(240, 140, 40), light=(255, 196, 100)),
            limb=Ramp(shade=(190, 96, 24), base=(240, 140, 40), light=(255, 196, 100)),
            sleeve=Ramp(shade=(190, 96, 24), base=(240, 140, 40), light=(255, 196, 100)),
            boot=PipArtist.CREAM,
            eco=palette.ECO_BLUE,
            special_poses=[
                Pose(bob=2, lean=-2, front_hand=(2, 6), back_hand=(-2, 6), effect=Effect.CHARGE),
                Pose(lean=5, front_foot=(7, 3), back_foot=(-8, 4), front_hand=(11, 3), back_hand=(-8, 2), effect=Effect.RELEASE),
                Pose(lean=3, front_foot=(5, 1), back_foot=(-6, 2), front_hand=(8, 5), back_hand=(-6, 4), effect=Effect.FOLLOW),
            ],
        ),
        "grondak": GrondakArtist(
            anatomy=Anatomy(leg_length=9, torso_height=13, torso_width=16, head_radius=6, limb_radius=2, hand_radius=3, reach=1.15),
            skin=Ramp(shade=(84, 62, 130), base=(122, 96, 178), light=(166, 142, 218)),
            limb=Ramp(shade=(84, 62, 130), base=(122, 96, 178), light=(166, 142, 218)),
            sleeve=Ramp(shade=(84, 62, 130), base=(122, 96, 178), light=(166, 142, 218)),
            boot=Ramp(shade=(70, 50, 100), base=(96, 74, 140), light=(140, 116, 190)),
            eco=palette.ECO_RED,
            special_poses=[
                Pose(front_hand=(2, -9), back_hand=(-1, -9), effect=Effect.CHARGE),
                Pose(bob=3, front_hand=(7, 14), back_hand=(-4, 14), front_foot=(5, 0), back_foot=(-5, 0), effect=Effect.RELEASE),
                Pose(bob=2, front_hand=(6, 12), back_hand=(-4, 12), front_foot=(5, 0), back_foot=(-5, 0)),
            ],
        ),
        "nyra": NyraArtist(
            anatomy=Anatomy(
                leg_length=9, torso_height=9, torso_width=8, head_radius=6, limb_radius=1, hand_radius=2, legs_behind_torso=True,
            ),
            skin=SKIN_TAN,
            limb=Ramp(shade=(30, 24, 50), base=(50, 40, 80), light=(80, 70, 120)),
            sleeve=NyraArtist.CLOAK,
            boot=Ramp(shade=(30, 24, 50), base=(54, 44, 86), light=(90, 80, 130)),
            eco=palette.ECO_YELLOW,
        ),
    }
