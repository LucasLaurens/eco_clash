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
        anatomy = self.anatomy
        hip = (CENTER_X + pose.lean // 2, FEET_Y - anatomy.leg_length + pose.bob)
        shoulder = (hip[0] + pose.lean - pose.lean // 2, hip[1] - anatomy.torso_height)
        head = (shoulder[0] + 1, shoulder[1] - anatomy.head_radius + 1)
        return Skeleton(
            hip=hip,
            shoulder=shoulder,
            head=head,
            front_foot=(hip[0] + self._scale_by_reach(pose.front_foot[0]), FEET_Y - self._scale_by_reach(pose.front_foot[1])),
            back_foot=(hip[0] + self._scale_by_reach(pose.back_foot[0]), FEET_Y - self._scale_by_reach(pose.back_foot[1])),
            front_hand=(shoulder[0] + self._scale_by_reach(pose.front_hand[0]), shoulder[1] + self._scale_by_reach(pose.front_hand[1])),
            back_hand=(shoulder[0] + self._scale_by_reach(pose.back_hand[0]), shoulder[1] + self._scale_by_reach(pose.back_hand[1])),
        )

    def _scale_by_reach(self, value: int) -> int:
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
        radius = self.anatomy.hand_radius
        canvas.fill_ellipse((hand[0] - radius, hand[1] - radius, hand[0] + radius, hand[1] + radius), self.skin.base if front else self.skin.shade)

    def paint_eye(self, canvas: Canvas, x: int, y: int, pose: Pose, height: int = 3) -> None:
        if pose.hurt:
            canvas.draw_line((x, y), (x + 2, y + 2), palette.PUPIL)
            canvas.draw_line((x, y + 2), (x + 2, y), palette.PUPIL)
            return
        canvas.fill_rect((x, y, x + 1, y + height - 1), palette.EYE_WHITE)
        canvas.fill_rect((x + 1, y + 1, x + 1, y + height - 1), palette.PUPIL)

    def paint_back_extras(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        pass

    def paint_front_extras(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        pass

    def paint_torso(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        raise NotImplementedError

    def paint_head(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        raise NotImplementedError

    def paint_effect(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        hand_x, hand_y = skeleton.front_hand
        eco = self.eco
        if pose.effect is Effect.SMEAR:
            radius = abs(hand_x - skeleton.shoulder[0]) + 3
            box = (skeleton.shoulder[0] - radius, skeleton.shoulder[1] - radius, skeleton.shoulder[0] + radius, skeleton.shoulder[1] + radius)
            canvas.draw_arc(box, -70, 40, (*palette.WHITE, 220), 2)
            canvas.draw_arc((box[0] + 2, box[1] + 2, box[2] - 2, box[3] - 2), -50, 30, (*eco.base, 200), 1)
        elif pose.effect is Effect.CHARGE:
            for dx, dy in ((-4, -3), (4, -4), (5, 3), (-3, 4)):
                canvas.put_pixel(hand_x + dx, hand_y + dy, eco.light)
                canvas.put_pixel(hand_x + dx + 1, hand_y + dy, eco.base)
            canvas.fill_ellipse((hand_x - 2, hand_y - 2, hand_x + 2, hand_y + 2), (*eco.base, 170))
        elif pose.effect is Effect.RELEASE:
            canvas.fill_ellipse((hand_x - 4, hand_y - 4, hand_x + 4, hand_y + 4), (*eco.base, 150))
            canvas.fill_ellipse((hand_x - 2, hand_y - 2, hand_x + 2, hand_y + 2), eco.light)
            for dx, dy in ((-6, 0), (6, 0), (0, -6), (0, 6)):
                canvas.put_pixel(hand_x + dx, hand_y + dy, eco.light)
        elif pose.effect is Effect.FOLLOW:
            for dx, dy in ((-3, -2), (-6, 1), (-2, 3)):
                canvas.put_pixel(hand_x + dx, hand_y + dy, eco.base)


class KaelArtist(FighterArtist):
    """Balanced hero: spiky blond hair with green tips, goggles, elf ears, armoured blue vest, eco conduit."""

    HAIR = Ramp(shade=(212, 156, 40), base=(250, 212, 92), light=(255, 240, 170))
    HAIR_TIP: Color = (106, 190, 70)
    VEST = Ramp(shade=(28, 52, 104), base=(44, 82, 150), light=(96, 140, 206))
    BELT = Ramp(shade=(36, 40, 58), base=(58, 64, 88), light=(104, 112, 140))
    LENS: Color = (90, 220, 230)

    def paint_torso(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        (shoulder_x, shoulder_y), (hip_x, hip_y) = skeleton.shoulder, skeleton.hip
        canvas.fill_polygon([(shoulder_x - 4, shoulder_y), (shoulder_x + 4, shoulder_y), (hip_x + 5, hip_y + 2), (hip_x - 5, hip_y + 2)], self.VEST.base)
        canvas.fill_polygon([(shoulder_x - 4, shoulder_y), (shoulder_x - 1, shoulder_y), (hip_x - 1, hip_y + 2), (hip_x - 5, hip_y + 2)], self.VEST.shade)
        canvas.draw_line((shoulder_x + 2, shoulder_y + 2), (hip_x + 2, hip_y - 2), self.eco.base)
        canvas.put_pixel(shoulder_x + 2, shoulder_y + 2, self.eco.light)
        canvas.fill_rect((hip_x - 4, hip_y - 1, hip_x + 4, hip_y), self.BELT.base)
        canvas.put_pixel(hip_x + 2, hip_y - 1, self.eco.light)
        canvas.fill_shaded_ellipse((shoulder_x - 4, shoulder_y - 2, shoulder_x + 2, shoulder_y + 3), palette.PRECURSOR_METAL)

    def paint_head(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        x, y = skeleton.head
        radius = self.anatomy.head_radius
        canvas.fill_polygon([(x - radius + 2, y), (x - radius - 4, y - 5), (x - radius + 3, y - 2)], self.skin.base)
        canvas.fill_shaded_ellipse((x - radius, y - radius, x + radius, y + radius), self.skin)
        hair = [
            (x + radius, y - 3), (x + 4, y - radius - 3), (x + 2, y - radius), (x - 1, y - radius - 6), (x - 3, y - radius),
            (x - 7, y - radius - 3), (x - radius - 1, y - 3), (x - radius - 2, y + 2), (x - radius + 2, y + 4), (x - 1, y - 1), (x + 2, y - 3),
        ]
        canvas.fill_polygon(hair, self.HAIR.base)
        canvas.fill_polygon([(x - radius - 1, y - 3), (x - radius - 2, y + 2), (x - radius + 2, y + 4), (x - 2, y)], self.HAIR.shade)
        for tip in ((x + 4, y - radius - 3), (x - 1, y - radius - 6), (x - 7, y - radius - 3)):
            canvas.put_pixel(tip[0], tip[1], self.HAIR_TIP)
            canvas.put_pixel(tip[0], tip[1] + 1, self.HAIR_TIP)
        canvas.put_pixel(x, y - radius - 2, self.HAIR.light)
        canvas.draw_line((x - radius + 1, y - 3), (x + radius - 1, y - 4), self.BELT.base)
        canvas.fill_ellipse((x + 1, y - 7, x + 4, y - 4), self.LENS)
        canvas.put_pixel(x + 2, y - 6, palette.WHITE)
        self.paint_eye(canvas, x + 3, y - 1, pose)
        canvas.put_pixel(x + radius, y + 1, self.skin.shade)
        canvas.draw_line((x + 3, y + 4), (x + 5, y + 3), self.skin.shade)


class PipArtist(FighterArtist):
    """Fast critter: orange fur, cream muzzle, huge ears, bushy tail, goggles."""

    CREAM = Ramp(shade=(220, 190, 140), base=(255, 236, 200), light=(255, 250, 235))
    INNER_EAR: Color = (240, 140, 140)
    NOSE: Color = (60, 30, 30)
    STRAP: Color = (90, 60, 40)
    LENS: Color = (90, 200, 255)

    def paint_back_extras(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        hip_x, hip_y = skeleton.hip
        sway = pose.bob
        canvas.fill_ellipse((hip_x - 9, hip_y - 6 + sway, hip_x - 2, hip_y + 1), self.skin.shade)
        canvas.fill_ellipse((hip_x - 12, hip_y - 12 + sway, hip_x - 5, hip_y - 4 + sway), self.skin.base)
        canvas.fill_ellipse((hip_x - 13, hip_y - 16 + sway, hip_x - 8, hip_y - 10 + sway), self.CREAM.base)

    def paint_torso(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        (shoulder_x, shoulder_y), (hip_x, hip_y) = skeleton.shoulder, skeleton.hip
        canvas.fill_shaded_ellipse((hip_x - 5, shoulder_y - 1, hip_x + 5, hip_y + 2), self.skin)
        canvas.fill_ellipse((hip_x, shoulder_y + 1, hip_x + 4, hip_y + 1), self.CREAM.base)
        canvas.fill_rect((hip_x - 4, shoulder_y - 1, hip_x + 4, shoulder_y), palette.PRECURSOR_METAL.base)
        canvas.put_pixel(hip_x + 2, shoulder_y, self.eco.light)

    def paint_head(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        x, y = skeleton.head
        radius = self.anatomy.head_radius
        canvas.fill_polygon([(x - 5, y - radius + 2), (x - 5, y - radius - 6), (x, y - radius + 1)], self.skin.shade)
        canvas.fill_polygon([(x, y - radius + 2), (x + 3, y - radius - 7), (x + 6, y - radius + 3)], self.skin.base)
        canvas.draw_line((x + 2, y - radius), (x + 3, y - radius - 4), self.INNER_EAR)
        canvas.fill_shaded_ellipse((x - radius, y - radius, x + radius, y + radius), self.skin)
        canvas.fill_ellipse((x + 1, y, x + radius + 3, y + 5), self.CREAM.base)
        canvas.put_pixel(x + radius + 3, y + 1, self.NOSE)
        canvas.put_pixel(x + radius + 2, y + 1, self.NOSE)
        canvas.draw_line((x - radius + 1, y - 4), (x + radius - 1, y - 5), self.STRAP)
        canvas.fill_ellipse((x, y - 7, x + 3, y - 4), self.LENS)
        canvas.put_pixel(x + 1, y - 6, palette.WHITE)
        self.paint_eye(canvas, x + 3, y - 2, pose, height=3)
        canvas.put_pixel(x + 6, y + 4, self.CREAM.shade)


class GrondakArtist(FighterArtist):
    """Heavy lurker brute in Krimzon armour: purple hide, tusks, red chest plate, visored helmet, huge fists."""

    ARMOR = Ramp(shade=(110, 30, 42), base=(160, 46, 52), light=(214, 92, 84))
    TUSK: Color = (250, 244, 220)

    def build_skeleton(self, pose: Pose) -> Skeleton:
        skeleton = super().build_skeleton(pose)
        # Hunched: the head sits forward and low, between the shoulders.
        hunched = (skeleton.shoulder[0] + 5, skeleton.shoulder[1] - 1)
        return replace(skeleton, head=hunched)

    def paint_torso(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        (shoulder_x, shoulder_y), (hip_x, hip_y) = skeleton.shoulder, skeleton.hip
        canvas.fill_shaded_ellipse((shoulder_x - 9, shoulder_y - 3, shoulder_x + 8, hip_y + 3), self.skin)
        metal = palette.PRECURSOR_METAL
        # The plate sits left of the front arm, or the arm hides it in every pose.
        canvas.fill_polygon([(shoulder_x - 8, shoulder_y + 1), (shoulder_x + 2, shoulder_y + 1), (shoulder_x + 1, hip_y), (shoulder_x - 7, hip_y)], self.ARMOR.base)
        canvas.fill_rect((shoulder_x - 8, shoulder_y + 1, shoulder_x + 1, shoulder_y + 1), self.ARMOR.light)
        canvas.fill_rect((shoulder_x - 7, shoulder_y + 3, shoulder_x - 6, hip_y - 2), self.ARMOR.shade)
        canvas.fill_polygon([(hip_x - 6, hip_y), (hip_x + 6, hip_y), (hip_x + 4, hip_y + 6), (hip_x - 4, hip_y + 6)], metal.shade)
        canvas.fill_rect((hip_x - 6, hip_y - 1, hip_x + 6, hip_y), metal.base)
        canvas.put_pixel(hip_x + 3, hip_y - 1, self.eco.light)
        canvas.fill_shaded_ellipse((shoulder_x - 10, shoulder_y - 5, shoulder_x - 2, shoulder_y + 2), metal)
        for spike_x in (shoulder_x - 8, shoulder_x - 5):
            canvas.fill_polygon([(spike_x - 1, shoulder_y - 4), (spike_x + 1, shoulder_y - 4), (spike_x, shoulder_y - 7)], metal.light)

    def paint_head(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        x, y = skeleton.head
        radius = self.anatomy.head_radius
        canvas.fill_shaded_ellipse((x - radius, y - radius, x + radius, y + radius - 1), self.skin)
        canvas.fill_ellipse((x - 2, y + 1, x + radius + 2, y + radius + 2), self.skin.shade)
        canvas.fill_shaded_ellipse((x - radius - 1, y - radius - 2, x + radius, y - 1), palette.PRECURSOR_METAL)
        if pose.hurt:
            self.paint_eye(canvas, x + 2, y - 2, pose)
        else:
            canvas.fill_rect((x, y - 3, x + radius, y - 2), self.eco.base)
            canvas.put_pixel(x + radius - 1, y - 3, self.eco.light)
        canvas.fill_rect((x + 1, y + 1, x + 1, y + 2), self.TUSK)
        canvas.fill_rect((x + radius, y - 1, x + radius, y + 2), self.TUSK)

    def paint_arm(self, canvas: Canvas, shoulder: Point, hand: Point, front: bool) -> None:
        super().paint_arm(canvas, shoulder, hand, front)
        if front:
            canvas.fill_rect((hand[0] - 1, hand[1] - 3, hand[0] + 1, hand[1] - 3), palette.PRECURSOR_METAL.light)

    def paint_effect(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        if pose.effect is not Effect.RELEASE:
            super().paint_effect(canvas, skeleton, pose)
            return
        for offset in (6, 11, 16):
            canvas.draw_line((CENTER_X - offset, FEET_Y - 1), (CENTER_X - offset - 3, FEET_Y - 5), self.eco.base)
            canvas.draw_line((CENTER_X + offset, FEET_Y - 1), (CENTER_X + offset + 3, FEET_Y - 5), self.eco.base)
        canvas.fill_rect((CENTER_X - 18, FEET_Y, CENTER_X + 18, FEET_Y), self.eco.light)


class NyraArtist(FighterArtist):
    """Eco sage: hooded night-blue robe with Precursor trim, silver hair, metal staff topped with yellow eco."""

    CLOAK = Ramp(shade=(30, 30, 72), base=(52, 52, 116), light=(92, 92, 168))
    TRIM: Color = (196, 210, 228)
    HAIR: Color = (214, 222, 240)
    STAFF = palette.PRECURSOR_METAL

    def paint_back_extras(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        (shoulder_x, shoulder_y), (hip_x, hip_y) = skeleton.shoulder, skeleton.hip
        canvas.fill_polygon([(shoulder_x - 2, shoulder_y), (shoulder_x - 8, hip_y + 6), (hip_x - 2, hip_y + 8)], self.CLOAK.shade)
        back_hand_x, back_hand_y = skeleton.back_hand
        canvas.draw_line((back_hand_x - 2, back_hand_y + 7), (back_hand_x - 2, back_hand_y - 20), self.STAFF.base)
        canvas.fill_ellipse((back_hand_x - 4, back_hand_y - 24, back_hand_x, back_hand_y - 20), self.eco.base)
        canvas.put_pixel(back_hand_x - 3, back_hand_y - 23, self.eco.light)

    def paint_torso(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        (shoulder_x, shoulder_y), (hip_x, hip_y) = skeleton.shoulder, skeleton.hip
        hem = FEET_Y - 3
        canvas.fill_polygon([(shoulder_x - 4, shoulder_y), (shoulder_x + 4, shoulder_y), (hip_x + 6, hem), (hip_x - 6, hem)], self.CLOAK.base)
        canvas.fill_polygon([(shoulder_x - 4, shoulder_y), (shoulder_x - 1, shoulder_y), (hip_x - 2, hem), (hip_x - 6, hem)], self.CLOAK.shade)
        canvas.fill_rect((hip_x - 6, hem - 1, hip_x + 6, hem), self.TRIM)
        canvas.draw_line((shoulder_x + 3, shoulder_y + 1), (hip_x + 5, hem - 2), self.TRIM)
        canvas.fill_rect((shoulder_x + 1, shoulder_y + 2, shoulder_x + 2, shoulder_y + 3), self.eco.base)

    def paint_head(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        x, y = skeleton.head
        radius = self.anatomy.head_radius
        canvas.fill_polygon([(x - radius, y - 2), (x - radius - 5, y + 3), (x - radius + 1, y + 4)], self.CLOAK.shade)
        canvas.fill_shaded_ellipse((x - radius - 1, y - radius - 1, x + radius + 1, y + radius), self.CLOAK)
        canvas.fill_ellipse((x - 1, y - radius + 2, x + radius, y + radius - 1), self.skin.base)
        canvas.fill_rect((x - 1, y - radius + 2, x + radius - 1, y - radius + 3), self.HAIR)
        canvas.draw_line((x - 2, y - radius + 1), (x + radius, y - radius + 1), self.TRIM)
        self.paint_eye(canvas, x + 2, y - 1, pose)
        canvas.put_pixel(x + 4, y + 3, self.skin.shade)

    def paint_effect(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        super().paint_effect(canvas, skeleton, pose)
        if pose.effect is Effect.CHARGE:
            back_hand_x, back_hand_y = skeleton.back_hand
            canvas.fill_ellipse((back_hand_x - 6, back_hand_y - 26, back_hand_x + 2, back_hand_y - 18), (*self.eco.light, 140))


SKIN_LIGHT = Ramp(shade=(201, 140, 98), base=(241, 190, 140), light=(255, 222, 184))
SKIN_TAN = Ramp(shade=(150, 96, 66), base=(200, 140, 100), light=(232, 180, 140))


def build_artists() -> dict[str, FighterArtist]:
    return {
        "kael": KaelArtist(
            anatomy=Anatomy(leg_length=10, torso_height=9, torso_width=8, head_radius=7, limb_radius=1, hand_radius=2),
            skin=SKIN_LIGHT,
            limb=KaelArtist.BELT,
            sleeve=KaelArtist.VEST,
            boot=palette.PRECURSOR_METAL,
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
