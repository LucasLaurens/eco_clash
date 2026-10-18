"""Fighter sprite sheets: heroic 64px puppets with jointed limbs.

Template Method: FighterArtist fixes the skeleton, the inverse kinematics and the drawing order;
each character subclass only paints its own torso, head, limbs' dress and extras.

Proportions follow Jak II: about five heads tall, long tapered limbs, a fighting guard at rest.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from enum import Enum

from PIL import Image

import palette
from pixel import Canvas, Color, Point, Ramp

FRAME_SIZE = 64
FEET_Y = 62
CENTER_X = 32
ANKLE_LIFT = 2
STAFF_REACH = 26
STAFF_TOP_MIN_Y = 8


class Effect(Enum):
    NONE = "none"
    SMEAR = "smear"
    CHARGE = "charge"
    RELEASE = "release"
    FOLLOW = "follow"


@dataclass(frozen=True)
class Pose:
    """Offsets of one frame, in Kael-sized pixels (scaled by Anatomy.reach).

    Feet are relative to the hip on x and lifted from the ground on y; hands are relative to the shoulder.
    """

    bob: int = 0
    lean: int = 2
    front_foot: Point = (7, 0)
    back_foot: Point = (-9, 0)
    front_hand: Point = (11, 3)
    back_hand: Point = (-2, 11)
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
    shoulder_half_width: int
    waist_half_width: int
    head_radius: int
    thigh_width: float
    shin_width: float
    upper_arm_width: float
    forearm_width: float
    hand_radius: int
    arm_length: int
    reach: float = 1.0
    legs_behind_torso: bool = False


@dataclass(frozen=True)
class Skeleton:
    hip: Point
    shoulder: Point
    head: Point
    front_knee: Point
    front_foot: Point
    back_knee: Point
    back_foot: Point
    front_elbow: Point
    front_hand: Point
    back_elbow: Point
    back_hand: Point


IDLE = [
    Pose(),
    Pose(bob=1, front_hand=(11, 4), back_hand=(-2, 12)),
]
RUN = [
    Pose(lean=4, front_foot=(11, 0), back_foot=(-9, 6), front_hand=(-4, 11), back_hand=(8, 7)),
    Pose(lean=4, bob=-1, front_foot=(3, 6), back_foot=(-2, 0), front_hand=(3, 12), back_hand=(1, 12)),
    Pose(lean=4, front_foot=(-9, 6), back_foot=(11, 0), front_hand=(10, 6), back_hand=(-5, 11)),
    Pose(lean=4, bob=-1, front_foot=(-2, 0), back_foot=(3, 6), front_hand=(1, 12), back_hand=(3, 12)),
]
JUMP = [Pose(lean=1, front_foot=(6, 9), back_foot=(-5, 6), front_hand=(9, -8), back_hand=(-8, -5))]
FALL = [Pose(lean=1, front_foot=(7, 4), back_foot=(-6, 5), front_hand=(13, -2), back_hand=(-12, -1))]
ATTACK = [
    Pose(lean=-1, front_foot=(8, 0), back_foot=(-9, 0), front_hand=(-6, 6), back_hand=(4, 8)),
    Pose(lean=5, front_foot=(11, 0), back_foot=(-9, 0), front_hand=(17, 2), back_hand=(-6, 9), effect=Effect.SMEAR),
    Pose(lean=4, front_foot=(10, 0), back_foot=(-9, 0), front_hand=(13, 5), back_hand=(-4, 10)),
]
GENERIC_SPECIAL = [
    Pose(bob=2, front_hand=(4, 8), back_hand=(2, 9), effect=Effect.CHARGE),
    Pose(lean=4, front_foot=(10, 0), front_hand=(16, 0), back_hand=(-9, 4), effect=Effect.RELEASE),
    Pose(lean=3, front_foot=(8, 0), front_hand=(13, 4), back_hand=(-7, 8), effect=Effect.FOLLOW),
]
HURT = [Pose(lean=-5, front_foot=(8, 6), back_foot=(-3, 2), front_hand=(-9, -5), back_hand=(-5, -8), hurt=True)]


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


def solve_joint(start: Point, end: Point, upper: float, lower: float, bend: int) -> tuple[Point, Point]:
    """Two-bone inverse kinematics: the middle joint (knee, elbow) and the end, pulled in if out of reach.

    bend = -1 puts the joint ahead of a limb pointing down (knees), +1 behind it (elbows). O(1).
    """
    dx, dy = end[0] - start[0], end[1] - start[1]
    distance = math.hypot(dx, dy) or 1.0
    reach = upper + lower - 0.01
    if distance > reach:
        end = (round(start[0] + dx / distance * reach), round(start[1] + dy / distance * reach))
        dx, dy, distance = dx / distance * reach, dy / distance * reach, reach
    along = (upper * upper - lower * lower + distance * distance) / (2 * distance)
    height = math.sqrt(max(upper * upper - along * along, 0.0))
    joint = (
        round(start[0] + dx / distance * along - dy / distance * height * bend),
        round(start[1] + dy / distance * along + dx / distance * height * bend),
    )
    return joint, end


def fill_limb(canvas: Canvas, start: Point, end: Point, start_width: float, end_width: float, color: Color) -> None:
    """Tapered segment: a quad from start to end, half-widths given at each joint."""
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy) or 1.0
    normal_x, normal_y = -dy / length, dx / length
    canvas.fill_polygon([
        (round(start[0] + normal_x * start_width), round(start[1] + normal_y * start_width)),
        (round(end[0] + normal_x * end_width), round(end[1] + normal_y * end_width)),
        (round(end[0] - normal_x * end_width), round(end[1] - normal_y * end_width)),
        (round(start[0] - normal_x * start_width), round(start[1] - normal_y * start_width)),
    ], color)
    canvas.fill_ellipse((round(end[0] - end_width), round(end[1] - end_width), round(end[0] + end_width), round(end[1] + end_width)), color)


def fill_v_torso(canvas: Canvas, shoulder: Point, hip: Point, anatomy: Anatomy, cloth: Ramp) -> None:
    """Broad shoulders narrowing to the waist, shaded on the back side, lit on the chest."""
    (shoulder_x, shoulder_y), (hip_x, hip_y) = shoulder, hip
    shoulder_half, waist_half = anatomy.shoulder_half_width, anatomy.waist_half_width
    canvas.fill_polygon([(shoulder_x - shoulder_half, shoulder_y), (shoulder_x + shoulder_half, shoulder_y),
                         (hip_x + waist_half, hip_y), (hip_x - waist_half, hip_y)], cloth.base)
    canvas.fill_polygon([(shoulder_x - shoulder_half, shoulder_y), (shoulder_x - shoulder_half + 4, shoulder_y),
                         (hip_x - waist_half + 2, hip_y), (hip_x - waist_half, hip_y)], cloth.shade)
    canvas.draw_line((shoulder_x + shoulder_half - 1, shoulder_y + 1), (hip_x + waist_half - 1, hip_y - 1), cloth.light)


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
        self.paint_arm(canvas, skeleton.shoulder, skeleton.back_elbow, skeleton.back_hand, front=False)
        self.paint_leg(canvas, skeleton.hip, skeleton.back_knee, skeleton.back_foot, front=False)
        if self.anatomy.legs_behind_torso:
            self.paint_leg(canvas, skeleton.hip, skeleton.front_knee, skeleton.front_foot, front=True)
        self.paint_torso(canvas, skeleton, pose)
        if not self.anatomy.legs_behind_torso:
            self.paint_leg(canvas, skeleton.hip, skeleton.front_knee, skeleton.front_foot, front=True)
        self.paint_head(canvas, skeleton, pose)
        self.paint_arm(canvas, skeleton.shoulder, skeleton.front_elbow, skeleton.front_hand, front=True)
        self.paint_front_extras(canvas, skeleton, pose)
        canvas.add_outline(palette.OUTLINE)
        effects = Canvas(FRAME_SIZE, FRAME_SIZE)
        self.paint_effect(effects, skeleton, pose)
        canvas.paste(effects.image, (0, 0))
        return canvas

    def build_skeleton(self, pose: Pose) -> Skeleton:
        anatomy = self.anatomy
        lean = self._scale_by_reach(pose.lean)
        hip = (CENTER_X + lean // 2, FEET_Y - anatomy.leg_length + pose.bob)
        shoulder = (hip[0] + lean - lean // 2, hip[1] - anatomy.torso_height)
        thigh = shin = anatomy.leg_length / 2 + 1
        upper_arm = forearm = anatomy.arm_length / 2
        front_knee, front_foot = solve_joint(hip, self._place_foot(hip, pose.front_foot), thigh, shin, bend=-1)
        back_knee, back_foot = solve_joint(hip, self._place_foot(hip, pose.back_foot), thigh, shin, bend=-1)
        front_elbow, front_hand = solve_joint(shoulder, self._place_hand(shoulder, pose.front_hand), upper_arm, forearm, bend=1)
        back_elbow, back_hand = solve_joint(shoulder, self._place_hand(shoulder, pose.back_hand), upper_arm, forearm, bend=1)
        return Skeleton(
            hip=hip, shoulder=shoulder, head=self.place_head(shoulder),
            front_knee=front_knee, front_foot=front_foot, back_knee=back_knee, back_foot=back_foot,
            front_elbow=front_elbow, front_hand=front_hand, back_elbow=back_elbow, back_hand=back_hand,
        )

    def place_head(self, shoulder: Point) -> Point:
        return shoulder[0] + 2, shoulder[1] - self.anatomy.head_radius - 3

    def _place_foot(self, hip: Point, offset: Point) -> Point:
        return hip[0] + self._scale_by_reach(offset[0]), FEET_Y - ANKLE_LIFT - self._scale_by_reach(offset[1])

    def _place_hand(self, shoulder: Point, offset: Point) -> Point:
        return shoulder[0] + self._scale_by_reach(offset[0]), shoulder[1] + self._scale_by_reach(offset[1])

    def _scale_by_reach(self, value: int) -> int:
        return round(value * self.anatomy.reach)

    def paint_leg(self, canvas: Canvas, hip: Point, knee: Point, ankle: Point, front: bool) -> None:
        anatomy = self.anatomy
        tone = self.limb.base if front else self.limb.shade
        fill_limb(canvas, hip, knee, anatomy.thigh_width, anatomy.shin_width, tone)
        fill_limb(canvas, knee, ankle, anatomy.shin_width, anatomy.shin_width - 0.4, tone)
        if front:
            canvas.draw_line((knee[0] + 1, knee[1] - 5), (knee[0] + 1, knee[1]), self.limb.light)
        self.paint_boot(canvas, ankle, front)

    def paint_boot(self, canvas: Canvas, ankle: Point, front: bool) -> None:
        """Shin guard plus a long toe: the silhouette of Jak's boots."""
        tone = self.boot.base if front else self.boot.shade
        x, y = ankle
        canvas.fill_polygon([(x - 2, y - 4), (x + 2, y - 4), (x + 6, y + 1), (x + 6, y + 2), (x - 3, y + 2)], tone)
        if front:
            canvas.draw_line((x - 1, y - 3), (x + 5, y + 1), self.boot.light)

    def paint_arm(self, canvas: Canvas, shoulder: Point, elbow: Point, hand: Point, front: bool) -> None:
        anatomy = self.anatomy
        fill_limb(canvas, shoulder, elbow, anatomy.upper_arm_width, anatomy.upper_arm_width - 0.3, self.sleeve.base if front else self.sleeve.shade)
        self.paint_forearm(canvas, elbow, hand, front)
        radius = anatomy.hand_radius
        canvas.fill_ellipse((hand[0] - radius, hand[1] - radius, hand[0] + radius, hand[1] + radius), self.skin.base if front else self.skin.shade)

    def paint_forearm(self, canvas: Canvas, elbow: Point, hand: Point, front: bool) -> None:
        fill_limb(canvas, elbow, hand, self.anatomy.forearm_width, self.anatomy.forearm_width - 0.2, self.skin.base if front else self.skin.shade)

    def paint_eye(self, canvas: Canvas, x: int, y: int, pose: Pose, height: int = 3) -> None:
        if pose.hurt:
            canvas.draw_line((x - 1, y), (x + 1, y + 2), palette.PUPIL)
            canvas.draw_line((x - 1, y + 2), (x + 1, y), palette.PUPIL)
            return
        canvas.fill_rect((x - 1, y, x + 1, y + height - 1), palette.EYE_WHITE)
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
        shoulder_x, shoulder_y = skeleton.shoulder
        eco = self.eco
        if pose.effect is Effect.SMEAR:
            radius = abs(hand_x - shoulder_x) + 4
            box = (shoulder_x - radius, shoulder_y - radius, shoulder_x + radius, shoulder_y + radius)
            canvas.draw_arc(box, -60, 40, (*palette.WHITE, 220), 2)
            canvas.draw_arc((box[0] + 3, box[1] + 3, box[2] - 3, box[3] - 3), -45, 30, (*eco.base, 200), 1)
        elif pose.effect is Effect.CHARGE:
            for dx, dy in ((-6, -4), (5, -6), (7, 4), (-4, 6)):
                canvas.put_pixel(hand_x + dx, hand_y + dy, eco.light)
                canvas.put_pixel(hand_x + dx + 1, hand_y + dy, eco.base)
            canvas.fill_ellipse((hand_x - 3, hand_y - 3, hand_x + 3, hand_y + 3), (*eco.base, 170))
        elif pose.effect is Effect.RELEASE:
            canvas.fill_ellipse((hand_x - 6, hand_y - 6, hand_x + 6, hand_y + 6), (*eco.base, 150))
            canvas.fill_ellipse((hand_x - 3, hand_y - 3, hand_x + 3, hand_y + 3), eco.light)
            for dx, dy in ((-9, 0), (9, 0), (0, -9), (0, 9)):
                canvas.put_pixel(hand_x + dx, hand_y + dy, eco.light)
        elif pose.effect is Effect.FOLLOW:
            for dx, dy in ((-4, -3), (-8, 1), (-3, 4), (-11, -1)):
                canvas.put_pixel(hand_x + dx, hand_y + dy, eco.base)


class KaelArtist(FighterArtist):
    """Eco ranger: military cut (shaved sides, long blond crest standing up and back, green tips), goatee,
    goggles strapped over the shaved side, long elf ears, blue vest, red scarf, metal gauntlets, leather boots."""

    HAIR = Ramp(shade=(200, 140, 40), base=(246, 206, 84), light=(255, 238, 160))
    HAIR_TIP: Color = (96, 196, 80)
    STUBBLE: Color = (206, 168, 100)
    VEST = Ramp(shade=(26, 58, 112), base=(44, 92, 160), light=(104, 154, 214))
    SCARF = Ramp(shade=(170, 56, 36), base=(222, 92, 50), light=(250, 150, 90))
    BELT: Color = (96, 64, 42)
    STRAP: Color = (60, 44, 34)
    LENS: Color = (90, 220, 230)
    BROW: Color = (150, 100, 30)

    def paint_back_extras(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        shoulder_x, shoulder_y = skeleton.shoulder
        # The scarf trails behind and flutters with the bob, longer when running or struck.
        flutter = pose.bob + (2 if pose.lean >= 4 or pose.hurt else 0)
        tail = [(shoulder_x - 4, shoulder_y - 1), (shoulder_x - 15, shoulder_y + 3 + flutter),
                (shoulder_x - 14, shoulder_y + 6 + flutter), (shoulder_x - 2, shoulder_y + 2)]
        canvas.fill_polygon(tail, self.SCARF.shade)
        canvas.fill_polygon([(shoulder_x - 15, shoulder_y + 3 + flutter), (shoulder_x - 19, shoulder_y + 2 + flutter * 2),
                             (shoulder_x - 18, shoulder_y + 6 + flutter)], self.SCARF.base)

    def paint_torso(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        (shoulder_x, shoulder_y), (hip_x, hip_y) = skeleton.shoulder, skeleton.hip
        fill_v_torso(canvas, skeleton.shoulder, skeleton.hip, self.anatomy, self.VEST)
        canvas.fill_rect((hip_x - 4, hip_y - 2, hip_x + 4, hip_y), self.BELT)
        canvas.put_pixel(hip_x + 1, hip_y - 1, self.eco.light)
        canvas.fill_rect((hip_x - 4, hip_y, hip_x + 4, hip_y + 2), self.limb.base)
        canvas.fill_shaded_ellipse((shoulder_x + 2, shoulder_y - 3, shoulder_x + 9, shoulder_y + 3), palette.PRECURSOR_METAL)
        canvas.fill_rect((shoulder_x - 4, shoulder_y - 3, shoulder_x + 4, shoulder_y - 1), self.SCARF.base)
        canvas.draw_line((shoulder_x - 3, shoulder_y - 3), (shoulder_x + 3, shoulder_y - 3), self.SCARF.light)

    def paint_head(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        x, y = skeleton.head
        skin = self.skin
        canvas.fill_rect((x - 2, y + 4, x, y + 7), skin.shade)
        # Long pointed ear sweeping back: the Precursor-elf signature.
        canvas.fill_polygon([(x - 2, y + 1), (x - 10, y - 4), (x - 1, y + 3)], skin.base)
        canvas.draw_line((x - 3, y + 1), (x - 8, y - 3), skin.shade)
        canvas.fill_ellipse((x - 4, y - 5, x + 5, y + 6), skin.base)
        canvas.fill_rect((x - 4, y + 2, x - 2, y + 5), skin.shade)
        # Jaw pushed forward: sharper and older than a round mascot head.
        canvas.fill_polygon([(x + 1, y + 5), (x + 6, y + 2), (x + 5, y + 6), (x + 2, y + 8)], skin.base)
        canvas.put_pixel(x + 6, y + 1, skin.shade)
        self.paint_eye(canvas, x + 3, y - 1, pose)
        canvas.draw_line((x + 2, y - 2), (x + 5, y - 3), self.BROW)
        canvas.draw_line((x + 3, y + 5), (x + 5, y + 4), skin.shade)
        # Shaved sides: a short stubble cap hugging the skull.
        canvas.fill_ellipse((x - 4, y - 5, x + 4, y - 1), self.STUBBLE)
        canvas.fill_rect((x - 4, y - 2, x - 3, y + 1), self.STUBBLE)
        # Long crest on top, swept up and back.
        crest = [(x + 4, y - 4), (x + 4, y - 9), (x + 1, y - 7), (x, y - 15), (x - 2, y - 9), (x - 5, y - 16),
                 (x - 6, y - 9), (x - 10, y - 14), (x - 9, y - 7), (x - 13, y - 9), (x - 8, y - 3), (x - 3, y - 5)]
        canvas.fill_polygon(crest, self.HAIR.base)
        canvas.fill_polygon([(x - 5, y - 16), (x - 6, y - 9), (x - 10, y - 14), (x - 9, y - 7), (x - 13, y - 9), (x - 8, y - 3), (x - 3, y - 5)], self.HAIR.shade)
        canvas.draw_line((x + 2, y - 8), (x - 1, y - 12), self.HAIR.light)
        for tip in ((x + 4, y - 9), (x, y - 15), (x - 5, y - 16), (x - 10, y - 14), (x - 13, y - 9)):
            canvas.put_pixel(*tip, self.HAIR_TIP)
        canvas.fill_polygon([(x + 3, y + 6), (x + 5, y + 6), (x + 3, y + 9)], self.HAIR.shade)
        canvas.draw_line((x - 5, y - 4), (x + 5, y - 5), self.STRAP)
        canvas.fill_ellipse((x + 1, y - 7, x + 4, y - 4), self.LENS)
        canvas.put_pixel(x + 2, y - 6, palette.WHITE)

    def paint_forearm(self, canvas: Canvas, elbow: Point, hand: Point, front: bool) -> None:
        metal = palette.PRECURSOR_METAL
        fill_limb(canvas, elbow, hand, self.anatomy.forearm_width, self.anatomy.forearm_width - 0.2, metal.base if front else metal.shade)
        if front:
            canvas.draw_line((elbow[0], elbow[1] - 1), ((elbow[0] + hand[0]) // 2, (elbow[1] + hand[1]) // 2 - 1), metal.light)
            canvas.put_pixel((elbow[0] + hand[0]) // 2, (elbow[1] + hand[1]) // 2, self.eco.light)


class PipArtist(FighterArtist):
    """Fast ottsel: orange fur, cream muzzle and belly, huge ears, bushy striped tail, goggles, tech collar."""

    CREAM = Ramp(shade=(220, 190, 140), base=(255, 236, 200), light=(255, 250, 235))
    INNER_EAR: Color = (240, 140, 140)
    NOSE: Color = (60, 30, 30)
    STRAP: Color = (90, 60, 40)
    LENS: Color = (90, 200, 255)
    STRIPE: Color = (176, 84, 24)

    def place_head(self, shoulder: Point) -> Point:
        return shoulder[0] + 2, shoulder[1] - self.anatomy.head_radius - 1

    def paint_back_extras(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        hip_x, hip_y = skeleton.hip
        sway = pose.bob + (2 if pose.lean >= 4 else 0)
        # Bushy tail streaming back at hip height, so it never reads as a raised arm.
        canvas.fill_polygon([(hip_x - 1, hip_y - 3), (hip_x - 9, hip_y - 4 + sway), (hip_x - 16, hip_y - 7 + sway),
                             (hip_x - 18, hip_y - 3 + sway), (hip_x - 10, hip_y + 1 + sway), (hip_x - 1, hip_y + 2)], self.skin.base)
        canvas.draw_line((hip_x - 7, hip_y - 3 + sway), (hip_x - 7, hip_y), self.STRIPE)
        canvas.draw_line((hip_x - 12, hip_y - 5 + sway), (hip_x - 12, hip_y - 1 + sway), self.STRIPE)
        canvas.fill_polygon([(hip_x - 16, hip_y - 7 + sway), (hip_x - 20, hip_y - 6 + sway), (hip_x - 18, hip_y - 3 + sway)], self.CREAM.base)

    def paint_torso(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        (shoulder_x, shoulder_y), (hip_x, hip_y) = skeleton.shoulder, skeleton.hip
        canvas.fill_shaded_ellipse((hip_x - 6, shoulder_y - 1, hip_x + 6, hip_y + 3), self.skin)
        canvas.fill_ellipse((hip_x, shoulder_y + 2, hip_x + 5, hip_y + 2), self.CREAM.base)
        canvas.fill_rect((shoulder_x - 4, shoulder_y - 1, shoulder_x + 4, shoulder_y), palette.PRECURSOR_METAL.base)
        canvas.put_pixel(shoulder_x + 2, shoulder_y, self.eco.light)

    def paint_boot(self, canvas: Canvas, ankle: Point, front: bool) -> None:
        x, y = ankle
        canvas.fill_ellipse((x - 2, y - 1, x + 4, y + 2), self.CREAM.base if front else self.CREAM.shade)

    def paint_head(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        x, y = skeleton.head
        radius = self.anatomy.head_radius
        canvas.fill_polygon([(x - 5, y - radius + 2), (x - 7, y - radius - 9), (x, y - radius + 1)], self.skin.shade)
        canvas.fill_polygon([(x - 1, y - radius + 2), (x + 3, y - radius - 10), (x + 6, y - radius + 3)], self.skin.base)
        canvas.draw_line((x + 2, y - radius - 1), (x + 3, y - radius - 6), self.INNER_EAR)
        canvas.fill_shaded_ellipse((x - radius, y - radius, x + radius, y + radius), self.skin)
        canvas.fill_ellipse((x + 1, y, x + radius + 4, y + 6), self.CREAM.base)
        canvas.fill_rect((x + radius + 3, y + 1, x + radius + 4, y + 2), self.NOSE)
        canvas.draw_line((x - radius + 1, y - 4), (x + radius - 1, y - 5), self.STRAP)
        canvas.fill_ellipse((x, y - 8, x + 4, y - 4), self.LENS)
        canvas.put_pixel(x + 1, y - 7, palette.WHITE)
        self.paint_eye(canvas, x + 4, y - 2, pose, height=4)
        canvas.draw_line((x + 4, y + 5), (x + 7, y + 5), self.CREAM.shade)


class GrondakArtist(FighterArtist):
    """Metal Head brute, like their leader: dark hide, bone carapace plates and dorsal spikes, a horned skull
    with a glowing gem in the forehead, red eye sockets, mandible tusks, huge metal fists."""

    BONE = Ramp(shade=(156, 122, 74), base=(210, 178, 112), light=(240, 222, 168))
    SOCKET: Color = (30, 20, 30)

    def place_head(self, shoulder: Point) -> Point:
        # Hunched forward, but the skull rides above the guard fist so its gem and sockets stay readable.
        return shoulder[0] + 5, shoulder[1] - 6

    def paint_back_extras(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        shoulder_x, shoulder_y = skeleton.shoulder
        for index, (dx, dy) in enumerate(((-12, -2), (-14, 5), (-13, 12))):
            base_x, base_y = shoulder_x + dx, shoulder_y + dy
            canvas.fill_polygon([(base_x + 2, base_y - 2), (base_x + 2, base_y + 3), (base_x - 6 + index, base_y - 4)], self.BONE.shade)

    def paint_torso(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        (shoulder_x, shoulder_y), (hip_x, hip_y) = skeleton.shoulder, skeleton.hip
        metal = palette.PRECURSOR_METAL
        canvas.fill_shaded_ellipse((shoulder_x - 12, shoulder_y - 4, shoulder_x + 10, hip_y + 4), self.skin)
        # Overlapping carapace plates down the chest, like an insect's armour.
        for row in range(3):
            top = shoulder_y + row * 6
            canvas.fill_ellipse((shoulder_x - 6 + row, top, shoulder_x + 7 - row, top + 7), self.BONE.shade)
            canvas.fill_ellipse((shoulder_x - 5 + row, top, shoulder_x + 6 - row, top + 5), self.BONE.base)
            canvas.draw_line((shoulder_x - 3 + row, top + 1), (shoulder_x + 3 - row, top + 1), self.BONE.light)
        canvas.fill_rect((hip_x - 8, hip_y - 2, hip_x + 7, hip_y + 1), metal.shade)
        canvas.fill_polygon([(hip_x - 7, hip_y + 1), (hip_x + 6, hip_y + 1), (hip_x + 4, hip_y + 7), (hip_x - 5, hip_y + 7)], self.skin.shade)
        canvas.fill_shaded_ellipse((shoulder_x - 14, shoulder_y - 6, shoulder_x - 3, shoulder_y + 3), self.BONE)
        for spike_x in (shoulder_x - 12, shoulder_x - 8):
            canvas.fill_polygon([(spike_x - 1, shoulder_y - 5), (spike_x + 1, shoulder_y - 5), (spike_x - 1, shoulder_y - 10)], self.BONE.light)

    def paint_head(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        x, y = skeleton.head
        radius = self.anatomy.head_radius
        # Horns sweeping up and back from the skull.
        canvas.fill_polygon([(x - 2, y - radius + 1), (x - 9, y - radius - 7), (x - 12, y - radius - 5), (x - 4, y - radius + 3)], self.BONE.shade)
        canvas.fill_polygon([(x + 1, y - radius), (x - 3, y - radius - 9), (x - 6, y - radius - 8), (x - 1, y - radius + 2)], self.BONE.base)
        canvas.fill_shaded_ellipse((x - radius, y - radius, x + radius + 2, y + radius), self.BONE)
        canvas.fill_ellipse((x - 1, y + 1, x + radius + 3, y + radius + 3), self.skin.shade)
        canvas.fill_polygon([(x + 1, y - radius - 1), (x + 3, y - radius + 1), (x + 1, y - radius + 3), (x - 1, y - radius + 1)], self.eco.light)
        canvas.put_pixel(x + 1, y - radius + 1, palette.WHITE)
        if pose.hurt:
            self.paint_eye(canvas, x + 3, y - 2, pose)
        else:
            canvas.fill_rect((x + 1, y - 2, x + radius + 1, y - 1), self.SOCKET)
            canvas.put_pixel(x + 2, y - 2, self.eco.base)
            canvas.put_pixel(x + radius, y - 2, self.eco.light)
        canvas.fill_polygon([(x + 1, y + 2), (x + 3, y + 2), (x + 1, y + 6)], self.BONE.light)
        canvas.fill_polygon([(x + radius, y + 1), (x + radius + 2, y + 1), (x + radius + 2, y + 5)], self.BONE.light)

    def paint_boot(self, canvas: Canvas, ankle: Point, front: bool) -> None:
        metal = palette.PRECURSOR_METAL
        x, y = ankle
        canvas.fill_polygon([(x - 3, y - 6), (x + 3, y - 6), (x + 6, y + 2), (x - 4, y + 2)], metal.base if front else metal.shade)
        if front:
            canvas.draw_line((x - 2, y - 5), (x + 4, y + 1), metal.light)

    def paint_arm(self, canvas: Canvas, shoulder: Point, elbow: Point, hand: Point, front: bool) -> None:
        super().paint_arm(canvas, shoulder, elbow, hand, front)
        metal = palette.PRECURSOR_METAL
        radius = self.anatomy.hand_radius
        canvas.fill_shaded_ellipse((hand[0] - radius, hand[1] - radius, hand[0] + radius, hand[1] + radius), metal if front else Ramp(metal.shade, metal.shade, metal.base))
        if front:
            canvas.fill_rect((hand[0] - 1, hand[1] - radius + 1, hand[0] + 1, hand[1] - radius + 1), self.eco.light)

    def paint_effect(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        if pose.effect is not Effect.RELEASE:
            super().paint_effect(canvas, skeleton, pose)
            return
        for offset in (8, 15, 22):
            canvas.draw_line((CENTER_X - offset, FEET_Y - 1), (CENTER_X - offset - 4, FEET_Y - 7), self.eco.base)
            canvas.draw_line((CENTER_X + offset, FEET_Y - 1), (CENTER_X + offset + 4, FEET_Y - 7), self.eco.base)
        canvas.fill_rect((CENTER_X - 26, FEET_Y, CENTER_X + 26, FEET_Y), self.eco.light)


class OrmosArtist(FighterArtist):
    """Old green sage: hunched, green skin, long white beard and bushy brows, a log hat sprouting leaves,
    sand-linen robe with a moss sash, gnarled wooden staff topped with a yellow eco orb."""

    # Light linen, so the dark log hat and the green skin both stand out against it.
    ROBE = Ramp(shade=(164, 138, 100), base=(206, 184, 136), light=(236, 222, 178))
    SASH: Color = (92, 150, 70)
    BEARD = Ramp(shade=(186, 188, 180), base=(232, 232, 222), light=(255, 255, 248))
    LOG = Ramp(shade=(92, 60, 36), base=(132, 90, 54), light=(176, 130, 82))
    LEAF = Ramp(shade=(56, 120, 50), base=(96, 170, 70), light=(160, 216, 110))
    STAFF = Ramp(shade=(90, 60, 38), base=(128, 88, 56), light=(166, 122, 80))

    def place_head(self, shoulder: Point) -> Point:
        # Bent with age: the head hangs forward of the shoulders.
        return shoulder[0] + 4, shoulder[1] - self.anatomy.head_radius - 1

    def paint_back_extras(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        hand_x, hand_y = skeleton.back_hand
        # The staff slides in his grip when the hand rises, so the orb never leaves the frame.
        top_y = max(hand_y - STAFF_REACH, STAFF_TOP_MIN_Y)
        canvas.draw_line((hand_x - 1, hand_y + 12), (hand_x - 1, top_y), self.STAFF.base)
        canvas.draw_line((hand_x, hand_y + 12), (hand_x, top_y + 2), self.STAFF.shade)
        canvas.draw_line((hand_x - 1, top_y), (hand_x - 4, top_y - 3), self.STAFF.base)
        canvas.draw_line((hand_x - 1, top_y), (hand_x + 2, top_y - 3), self.STAFF.base)
        canvas.fill_ellipse((hand_x - 4, top_y - 7, hand_x + 1, top_y - 2), self.eco.base)
        canvas.put_pixel(hand_x - 2, top_y - 6, self.eco.light)

    def paint_torso(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        (shoulder_x, shoulder_y), (hip_x, hip_y) = skeleton.shoulder, skeleton.hip
        hem = FEET_Y - 4
        canvas.fill_polygon([(shoulder_x - 6, shoulder_y), (shoulder_x + 6, shoulder_y), (hip_x + 6, hip_y),
                             (hip_x + 9, hem), (hip_x - 9, hem), (hip_x - 6, hip_y)], self.ROBE.base)
        canvas.fill_polygon([(shoulder_x - 6, shoulder_y), (shoulder_x - 2, shoulder_y), (hip_x - 2, hip_y),
                             (hip_x - 4, hem), (hip_x - 9, hem), (hip_x - 6, hip_y)], self.ROBE.shade)
        canvas.draw_line((shoulder_x + 5, shoulder_y + 1), (hip_x + 8, hem - 1), self.ROBE.light)
        canvas.fill_rect((hip_x - 6, hip_y - 2, hip_x + 6, hip_y), self.SASH)
        canvas.fill_polygon([(hip_x + 3, hip_y), (hip_x + 6, hip_y), (hip_x + 5, hip_y + 7)], self.SASH)
        for x in range(hip_x - 8, hip_x + 9, 3):
            canvas.put_pixel(x, hem, self.ROBE.shade)

    def paint_boot(self, canvas: Canvas, ankle: Point, front: bool) -> None:
        x, y = ankle
        canvas.fill_ellipse((x - 2, y - 1, x + 4, y + 2), self.skin.base if front else self.skin.shade)

    def paint_head(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        x, y = skeleton.head
        radius = self.anatomy.head_radius
        canvas.fill_ellipse((x - radius - 1, y - 2, x - radius + 3, y + 4), self.BEARD.shade)
        canvas.fill_shaded_ellipse((x - radius, y - radius, x + radius, y + radius), self.skin)
        canvas.fill_polygon([(x + 3, y), (x + radius + 3, y + 1), (x + radius, y + 3)], self.skin.base)
        # Long beard falling over the chest.
        canvas.fill_polygon([(x - 2, y + 2), (x + radius + 1, y + 2), (x + radius, y + 9), (x + 3, y + 16), (x, y + 9)], self.BEARD.base)
        canvas.fill_polygon([(x - 2, y + 2), (x + 1, y + 3), (x + 2, y + 14), (x, y + 9)], self.BEARD.shade)
        canvas.draw_line((x + 4, y + 4), (x + 4, y + 12), self.BEARD.light)
        if pose.hurt:
            self.paint_eye(canvas, x + 3, y - 2, pose)
        else:
            canvas.fill_rect((x + 2, y - 1, x + 4, y - 1), palette.PUPIL)
        canvas.fill_polygon([(x, y - 3), (x + 6, y - 4), (x + 5, y - 2), (x + 1, y - 2)], self.BEARD.base)
        # Log hat: a cut stump with growth rings and a sprout of leaves.
        hat_top = y - radius - 4
        canvas.fill_rect((x - radius, hat_top, x + radius - 1, y - radius + 2), self.LOG.base)
        canvas.fill_rect((x - radius, hat_top, x - radius + 2, y - radius + 2), self.LOG.shade)
        canvas.fill_ellipse((x - radius, hat_top - 2, x + radius - 1, hat_top + 1), self.LOG.light)
        canvas.draw_line((x - 2, hat_top - 1), (x + 2, hat_top - 1), self.LOG.shade)
        canvas.fill_polygon([(x, hat_top - 1), (x - 5, hat_top - 6), (x - 1, hat_top - 4)], self.LEAF.base)
        canvas.fill_polygon([(x + 1, hat_top - 1), (x + 5, hat_top - 7), (x + 3, hat_top - 2)], self.LEAF.light)
        canvas.draw_line((x - 3, hat_top - 4), (x - 1, hat_top - 2), self.LEAF.shade)

    def paint_effect(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        super().paint_effect(canvas, skeleton, pose)
        if pose.effect is Effect.CHARGE:
            hand_x, hand_y = skeleton.back_hand
            orb_y = max(hand_y - STAFF_REACH, STAFF_TOP_MIN_Y) - 4
            canvas.fill_ellipse((hand_x - 7, orb_y - 5, hand_x + 4, orb_y + 6), (*self.eco.light, 140))


class VargoArtist(FighterArtist):
    """Desert colossus: bare muscular arms, khaki armour vest, bandolier, metal mask-helmet with a glowing
    visor, a big shoulder plate and a heavy eco cannon held in the lead hand."""

    VEST = Ramp(shade=(120, 104, 70), base=(166, 146, 100), light=(206, 190, 140))
    STRAP: Color = (78, 52, 36)
    BEARD: Color = (60, 40, 32)
    CANNON = Ramp(shade=(52, 56, 70), base=(84, 90, 108), light=(136, 144, 162))

    def paint_torso(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        (shoulder_x, shoulder_y), (hip_x, hip_y) = skeleton.shoulder, skeleton.hip
        fill_v_torso(canvas, skeleton.shoulder, skeleton.hip, self.anatomy, self.VEST)
        canvas.draw_line((shoulder_x - 7, shoulder_y + 1), (hip_x + 5, hip_y - 2), self.STRAP)
        canvas.draw_line((shoulder_x - 6, shoulder_y + 1), (hip_x + 6, hip_y - 2), self.STRAP)
        for step in range(1, 4):
            bullet_x = shoulder_x - 7 + step * 4
            bullet_y = shoulder_y + 1 + step * (hip_y - shoulder_y - 3) // 4
            canvas.put_pixel(bullet_x, bullet_y - 1, self.eco.light)
        canvas.fill_rect((hip_x - 6, hip_y - 2, hip_x + 6, hip_y), self.STRAP)
        canvas.fill_rect((hip_x - 6, hip_y, hip_x + 6, hip_y + 2), self.limb.base)
        canvas.fill_shaded_ellipse((shoulder_x + 1, shoulder_y - 4, shoulder_x + 12, shoulder_y + 4), palette.PRECURSOR_METAL)
        canvas.draw_line((shoulder_x + 3, shoulder_y - 3), (shoulder_x + 10, shoulder_y - 3), palette.PRECURSOR_METAL.light)

    def paint_head(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        x, y = skeleton.head
        radius = self.anatomy.head_radius
        canvas.fill_rect((x - 2, y + 3, x + 1, y + 7), self.skin.shade)
        canvas.fill_ellipse((x - radius, y - radius + 1, x + radius + 1, y + radius + 1), self.skin.base)
        canvas.fill_polygon([(x, y + 3), (x + radius + 2, y + 2), (x + radius, y + 7), (x + 1, y + 7)], self.BEARD)
        # Mask-helmet: a metal dome down to the nose, a dark visor band with one glowing slit.
        metal = palette.PRECURSOR_METAL
        canvas.fill_shaded_ellipse((x - radius - 1, y - radius - 2, x + radius + 2, y + 3), metal)
        canvas.fill_rect((x - 1, y - 2, x + radius + 2, y), palette.OUTLINE)
        if pose.hurt:
            canvas.fill_rect((x + 1, y - 1, x + radius + 1, y - 1), palette.WHITE)
        else:
            canvas.fill_rect((x + 1, y - 1, x + radius + 1, y - 1), self.eco.light)
        canvas.fill_rect((x - 2, y - radius - 4, x + 1, y - radius - 2), metal.light)

    def paint_front_extras(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        hand_x, hand_y = skeleton.front_hand
        cannon = self.CANNON
        # Heavy cannon held at the hip line of the lead hand, barrel forward, eco coil glowing on the side.
        canvas.fill_rect((hand_x - 6, hand_y - 3, hand_x + 3, hand_y + 2), cannon.base)
        canvas.fill_rect((hand_x + 3, hand_y - 2, hand_x + 13, hand_y + 1), cannon.shade)
        canvas.fill_rect((hand_x + 3, hand_y - 2, hand_x + 13, hand_y - 2), cannon.light)
        canvas.fill_rect((hand_x + 13, hand_y - 3, hand_x + 15, hand_y + 2), cannon.base)
        for coil_x in range(hand_x - 4, hand_x + 2, 2):
            canvas.put_pixel(coil_x, hand_y - 1, self.eco.base)
        canvas.fill_rect((hand_x - 6, hand_y + 2, hand_x - 4, hand_y + 5), cannon.shade)


class KraggArtist(FighterArtist):
    """Gang boss on a hover chair: huge belly in a wine-red velvet jacket with gold buttons, slicked-back
    hair, thin moustache, double chin, gold rings; the chair floats on an orange eco thruster."""

    JACKET = Ramp(shade=(96, 26, 46), base=(144, 44, 68), light=(194, 86, 104))
    SHIRT: Color = (230, 222, 196)
    GOLD = Ramp(shade=(176, 128, 36), base=(232, 188, 72), light=(255, 236, 150))
    HAIR: Color = (36, 30, 40)
    CHAIR = palette.PRECURSOR_METAL

    def place_head(self, shoulder: Point) -> Point:
        return shoulder[0] + 3, shoulder[1] - self.anatomy.head_radius - 1

    def paint_back_extras(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        (shoulder_x, shoulder_y), (hip_x, hip_y) = skeleton.shoulder, skeleton.hip
        chair = self.CHAIR
        canvas.fill_polygon([(hip_x - 15, hip_y + 2), (hip_x - 11, shoulder_y - 8), (hip_x - 5, shoulder_y - 8), (hip_x - 5, hip_y + 2)], chair.shade)
        canvas.draw_line((hip_x - 11, shoulder_y - 7), (hip_x - 6, shoulder_y - 7), chair.light)

    def paint_leg(self, canvas: Canvas, hip: Point, knee: Point, ankle: Point, front: bool) -> None:
        """Seated: short legs dangle over the seat edge whatever the pose; the chair does the moving."""
        hip_x, hip_y = hip
        tone = self.limb.base if front else self.limb.shade
        offset = 0 if front else -3
        knee_seat = (hip_x + 9 + offset, hip_y + 2)
        foot = (hip_x + 10 + offset, hip_y + 9)
        fill_limb(canvas, (hip_x + offset, hip_y), knee_seat, 3.2, 2.6, tone)
        fill_limb(canvas, knee_seat, foot, 2.4, 2.0, tone)
        canvas.fill_ellipse((foot[0] - 1, foot[1] - 1, foot[0] + 4, foot[1] + 2), palette.OUTLINE if front else self.HAIR)

    def paint_torso(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        (shoulder_x, shoulder_y), (hip_x, hip_y) = skeleton.shoulder, skeleton.hip
        jacket = self.JACKET
        canvas.fill_ellipse((hip_x - 12, shoulder_y - 2, hip_x + 13, hip_y + 5), jacket.base)
        canvas.fill_ellipse((hip_x - 12, shoulder_y - 2, hip_x - 2, hip_y + 5), jacket.shade)
        canvas.fill_ellipse((hip_x + 1, shoulder_y + 1, hip_x + 12, hip_y + 4), self.SHIRT)
        canvas.draw_line((hip_x + 8, shoulder_y + 2), (hip_x + 11, hip_y), jacket.light)
        for button_y in range(shoulder_y + 4, hip_y + 2, 4):
            canvas.put_pixel(hip_x + 3, button_y, self.GOLD.base)
        canvas.fill_rect((shoulder_x - 2, shoulder_y - 2, shoulder_x + 4, shoulder_y), self.GOLD.shade)

    def paint_head(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        x, y = skeleton.head
        radius = self.anatomy.head_radius
        skin = self.skin
        canvas.fill_ellipse((x - 2, y + 2, x + radius + 3, y + radius + 4), skin.shade)
        canvas.fill_shaded_ellipse((x - radius, y - radius, x + radius + 1, y + radius + 1), skin)
        canvas.fill_ellipse((x - radius, y - radius - 1, x + radius, y - 1), self.HAIR)
        canvas.fill_polygon([(x - radius, y - 3), (x - radius - 3, y - 1), (x - radius, y + 1)], self.HAIR)
        self.paint_eye(canvas, x + 3, y - 1, pose, height=2)
        canvas.fill_rect((x + radius - 1, y + 1, x + radius + 2, y + 2), skin.shade)
        canvas.draw_line((x + 2, y + 3), (x + radius + 2, y + 3), self.HAIR)
        canvas.put_pixel(x - 2, y + 2, self.GOLD.light)

    def paint_arm(self, canvas: Canvas, shoulder: Point, elbow: Point, hand: Point, front: bool) -> None:
        super().paint_arm(canvas, shoulder, elbow, hand, front)
        canvas.put_pixel(hand[0], hand[1] - 1, self.GOLD.light if front else self.GOLD.shade)

    def paint_front_extras(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        hip_x, hip_y = skeleton.hip
        chair = self.CHAIR
        # Seat front and hover hull under the belly.
        canvas.fill_polygon([(hip_x - 16, hip_y + 4), (hip_x + 13, hip_y + 4), (hip_x + 10, hip_y + 10), (hip_x - 13, hip_y + 10)], chair.base)
        canvas.fill_rect((hip_x - 16, hip_y + 4, hip_x + 13, hip_y + 4), chair.light)
        canvas.fill_polygon([(hip_x - 13, hip_y + 10), (hip_x + 10, hip_y + 10), (hip_x + 6, hip_y + 13), (hip_x - 9, hip_y + 13)], chair.shade)
        for light_x in (hip_x - 8, hip_x - 1, hip_x + 6):
            canvas.put_pixel(light_x, hip_y + 7, self.eco.light)

    def paint_effect(self, canvas: Canvas, skeleton: Skeleton, pose: Pose) -> None:
        super().paint_effect(canvas, skeleton, pose)
        hip_x, hip_y = skeleton.hip
        # Thruster flame under the hull: longer when climbing or dashing.
        flame = 3 + (3 if pose.front_foot[1] >= 4 or pose.lean >= 6 else 0) + (pose.bob % 2)
        canvas.fill_polygon([(hip_x - 6, hip_y + 14), (hip_x + 3, hip_y + 14), (hip_x - 2, hip_y + 14 + flame)], (*self.eco.base, 210))
        canvas.fill_polygon([(hip_x - 4, hip_y + 14), (hip_x + 1, hip_y + 14), (hip_x - 2, hip_y + 13 + flame // 2 + 1)], self.eco.light)


SKIN_LIGHT = Ramp(shade=(198, 132, 92), base=(238, 182, 132), light=(255, 214, 172))
SKIN_TAN = Ramp(shade=(150, 96, 66), base=(200, 140, 100), light=(232, 180, 140))
SAGE_SKIN = Ramp(shade=(70, 130, 80), base=(110, 176, 104), light=(164, 214, 140))
METAL_HEAD_HIDE = Ramp(shade=(44, 38, 64), base=(70, 60, 98), light=(108, 96, 146))
PIP_FUR = Ramp(shade=(190, 96, 24), base=(240, 140, 40), light=(255, 196, 100))
LURKER_HIDE = Ramp(shade=(84, 62, 130), base=(122, 96, 178), light=(166, 142, 218))


def build_artists() -> dict[str, FighterArtist]:
    return {
        "kael": KaelArtist(
            anatomy=Anatomy(leg_length=22, torso_height=16, shoulder_half_width=6, waist_half_width=4, head_radius=5,
                            thigh_width=2.6, shin_width=2.0, upper_arm_width=2.2, forearm_width=1.9, hand_radius=2, arm_length=16),
            skin=SKIN_LIGHT,
            limb=Ramp(shade=(52, 50, 66), base=(80, 76, 96), light=(118, 114, 138)),
            sleeve=KaelArtist.VEST,
            boot=Ramp(shade=(78, 52, 40), base=(118, 80, 56), light=(160, 116, 80)),
            eco=palette.ECO_GREEN,
            special_poses=[
                Pose(bob=3, front_hand=(5, 7), back_hand=(-2, 9), effect=Effect.CHARGE),
                Pose(lean=1, front_foot=(4, 7), back_foot=(-3, 9), front_hand=(5, -16), back_hand=(-8, 5), effect=Effect.RELEASE),
                Pose(lean=1, front_foot=(4, 5), back_foot=(-4, 6), front_hand=(3, -13), back_hand=(-8, 6), effect=Effect.FOLLOW),
            ],
        ),
        "pip": PipArtist(
            anatomy=Anatomy(leg_length=12, torso_height=10, shoulder_half_width=5, waist_half_width=4, head_radius=6,
                            thigh_width=2.2, shin_width=1.7, upper_arm_width=1.6, forearm_width=1.4, hand_radius=2,
                            arm_length=10, reach=0.65),
            skin=PIP_FUR,
            limb=PIP_FUR,
            sleeve=PIP_FUR,
            boot=PipArtist.CREAM,
            eco=palette.ECO_BLUE,
            special_poses=[
                Pose(bob=2, lean=-3, front_hand=(3, 8), back_hand=(-3, 8), effect=Effect.CHARGE),
                Pose(lean=8, front_foot=(11, 4), back_foot=(-12, 5), front_hand=(17, 4), back_hand=(-12, 3), effect=Effect.RELEASE),
                Pose(lean=5, front_foot=(8, 2), back_foot=(-9, 3), front_hand=(13, 7), back_hand=(-9, 6), effect=Effect.FOLLOW),
            ],
        ),
        "grondak": GrondakArtist(
            anatomy=Anatomy(leg_length=18, torso_height=19, shoulder_half_width=10, waist_half_width=7, head_radius=5,
                            thigh_width=3.6, shin_width=3.0, upper_arm_width=3.4, forearm_width=3.2, hand_radius=4,
                            arm_length=18, reach=1.15),
            skin=METAL_HEAD_HIDE,
            limb=METAL_HEAD_HIDE,
            sleeve=METAL_HEAD_HIDE,
            boot=palette.PRECURSOR_METAL,
            eco=palette.ECO_RED,
            special_poses=[
                Pose(front_hand=(3, -15), back_hand=(-2, -15), effect=Effect.CHARGE),
                Pose(bob=4, front_hand=(11, 18), back_hand=(-6, 18), front_foot=(8, 0), back_foot=(-8, 0), effect=Effect.RELEASE),
                Pose(bob=3, front_hand=(9, 16), back_hand=(-6, 16), front_foot=(8, 0), back_foot=(-8, 0)),
            ],
        ),
        "ormos": OrmosArtist(
            anatomy=Anatomy(leg_length=18, torso_height=14, shoulder_half_width=6, waist_half_width=5, head_radius=6,
                            thigh_width=2.0, shin_width=1.6, upper_arm_width=1.8, forearm_width=1.5, hand_radius=2,
                            arm_length=14, reach=0.95, legs_behind_torso=True),
            skin=SAGE_SKIN,
            limb=SAGE_SKIN,
            sleeve=OrmosArtist.ROBE,
            boot=SAGE_SKIN,
            eco=palette.ECO_YELLOW,
        ),
        "vargo": VargoArtist(
            anatomy=Anatomy(leg_length=22, torso_height=18, shoulder_half_width=9, waist_half_width=6, head_radius=5,
                            thigh_width=3.2, shin_width=2.6, upper_arm_width=3.2, forearm_width=2.8, hand_radius=3,
                            arm_length=17, reach=1.05),
            skin=SKIN_TAN,
            limb=Ramp(shade=(64, 66, 50), base=(92, 94, 72), light=(130, 132, 104)),
            sleeve=SKIN_TAN,
            boot=Ramp(shade=(78, 52, 40), base=(118, 80, 56), light=(160, 116, 80)),
            eco=palette.ECO_DARK,
            special_poses=[
                Pose(bob=2, lean=-1, front_hand=(8, 6), back_hand=(4, 8), effect=Effect.CHARGE),
                Pose(lean=-2, front_foot=(8, 0), front_hand=(13, 2), back_hand=(5, 5), effect=Effect.RELEASE),
                Pose(lean=-1, front_hand=(11, 3), back_hand=(4, 7), effect=Effect.FOLLOW),
            ],
        ),
        "kragg": KraggArtist(
            anatomy=Anatomy(leg_length=16, torso_height=16, shoulder_half_width=9, waist_half_width=12, head_radius=5,
                            thigh_width=3.0, shin_width=2.4, upper_arm_width=3.0, forearm_width=2.8, hand_radius=3,
                            arm_length=14, reach=0.9),
            skin=Ramp(shade=(200, 144, 126), base=(236, 186, 164), light=(255, 218, 200)),
            limb=KraggArtist.JACKET,
            sleeve=KraggArtist.JACKET,
            boot=KraggArtist.JACKET,
            eco=palette.ECO_ORANGE,
            special_poses=[
                Pose(bob=1, lean=-3, front_hand=(4, 8), back_hand=(-3, 8), effect=Effect.CHARGE),
                Pose(lean=8, front_hand=(15, 3), back_hand=(-8, 4), effect=Effect.RELEASE),
                Pose(lean=6, front_hand=(12, 5), back_hand=(-7, 6), effect=Effect.FOLLOW),
            ],
        ),
    }
