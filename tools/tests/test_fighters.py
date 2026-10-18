"""Fighter puppets: inverse kinematics, sheet layout, frames that stay inside their cell."""

import math
import random

import fighters


def test_solve_joint_keeps_both_segment_lengths_when_in_reach() -> None:
    # Arrange
    rng = random.Random()
    upper, lower = rng.uniform(8, 12), rng.uniform(8, 12)
    start = (32, 20)
    end = (start[0] + rng.randint(-6, 6), start[1] + rng.randint(6, 12))
    # Act
    joint, reached = fighters.solve_joint(start, end, upper, lower, bend=-1)
    # Assert
    assert reached == end
    assert abs(math.dist(start, joint) - upper) <= 1.5
    assert abs(math.dist(joint, end) - lower) <= 1.5


def test_solve_joint_pulls_an_unreachable_end_back_to_full_length() -> None:
    # Arrange
    upper, lower = 8.0, 8.0
    start = (10, 10)
    # Act
    _, reached = fighters.solve_joint(start, (60, 10), upper, lower, bend=1)
    # Assert
    assert math.dist(start, reached) <= upper + lower + 1


def test_layout_counts_every_pose_once() -> None:
    # Act
    layout = fighters.build_layout()
    # Assert
    frames = [index for animation in layout["animations"].values() for index in animation["frames"]]
    assert frames == list(range(layout["frame_count"]))
    assert layout["frame_size"] == fighters.FRAME_SIZE


def test_every_sheet_matches_the_layout_and_keeps_bodies_in_frame() -> None:
    # Arrange
    layout = fighters.build_layout()
    # Act & Assert
    for name, artist in fighters.build_artists().items():
        sheet = artist.render_sheet()
        assert sheet.size == (layout["frame_count"] * fighters.FRAME_SIZE, fighters.FRAME_SIZE), name
        idle = artist.render_frame(fighters.IDLE[0]).image.getchannel("A")
        assert idle.crop((0, 0, fighters.FRAME_SIZE, 1)).getextrema()[1] == 0, f"{name} idle touches the top edge"
