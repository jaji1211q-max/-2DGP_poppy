import unittest
from unittest.mock import patch

from poppy import (
    ANIMATION_FRAME_DURATION,
    FRAME_BOTTOM,
    FRAME_HEIGHT,
    FRAME_LEFT,
    FRAME_STEP,
    FRAME_WIDTH,
    IDLE_DELAY,
    IDLE_FRAME_BOTTOM,
    IDLE_FRAME_COUNT,
    MOVEMENT_SPEED,
    WALK_FRAME_COUNT,
    Poppy,
)


class PoppyTests(unittest.TestCase):
    def setUp(self):
        with patch("poppy.load_image") as load_image:
            self.poppy = Poppy()
        self.image = load_image.return_value

    def test_command_moves_toward_target_at_a_consistent_speed(self):
        self.poppy.command_to(750, 300)
        self.poppy.update(1.0)

        self.assertAlmostEqual(self.poppy.x, 700.0)
        self.assertAlmostEqual(self.poppy.y, 300.0)
        self.assertTrue(self.poppy.is_moving)

    def test_diagonal_command_uses_normalized_movement(self):
        self.poppy.command_to(600, 500)
        self.poppy.update(0.5)

        self.assertAlmostEqual(
            self.poppy.x - 400.0,
            MOVEMENT_SPEED * 0.5 / 2**0.5,
        )
        self.assertAlmostEqual(
            self.poppy.y - 300.0,
            MOVEMENT_SPEED * 0.5 / 2**0.5,
        )

    def test_command_stops_at_target_without_overshooting(self):
        self.poppy.command_to(410, 300)
        self.poppy.update(1.0)

        self.assertEqual((self.poppy.x, self.poppy.y), (410, 300))
        self.assertFalse(self.poppy.is_moving)

    def test_command_target_stays_inside_canvas(self):
        self.poppy.command_to(-100, 1000)
        self.poppy.update(10.0)

        self.assertEqual(self.poppy.x, FRAME_WIDTH / 2)
        self.assertEqual(self.poppy.y, 600 - FRAME_HEIGHT / 2)
        self.assertFalse(self.poppy.is_moving)

    def test_command_to_current_position_does_not_start_movement(self):
        self.poppy.command_to(self.poppy.x, self.poppy.y)

        self.assertFalse(self.poppy.is_moving)

    def test_negative_delta_time_is_rejected(self):
        with self.assertRaises(ValueError):
            self.poppy.update(-0.1)

    def test_poppy_does_not_rotate_toward_the_command_target(self):
        self.poppy.command_to(600, 300)
        self.poppy.draw()

        self.image.clip_composite_draw.assert_called_once_with(
            FRAME_LEFT,
            FRAME_BOTTOM,
            FRAME_WIDTH,
            FRAME_HEIGHT,
            0.0,
            "",
            400.0,
            300.0,
            FRAME_WIDTH,
            FRAME_HEIGHT,
        )

    def test_walk_animation_advances_while_following_a_command(self):
        self.poppy.command_to(700, 300)
        self.poppy.update(ANIMATION_FRAME_DURATION)
        self.poppy.draw()

        self.image.clip_composite_draw.assert_called_once_with(
            FRAME_LEFT + FRAME_STEP,
            FRAME_BOTTOM,
            FRAME_WIDTH,
            FRAME_HEIGHT,
            0.0,
            "",
            self.poppy.x,
            self.poppy.y,
            FRAME_WIDTH,
            FRAME_HEIGHT,
        )

    def test_walk_animation_wraps_after_all_frames(self):
        self.poppy.command_to(700, 300)
        for _ in range(WALK_FRAME_COUNT):
            self.poppy.update(ANIMATION_FRAME_DURATION)

        self.assertEqual(self.poppy.frame_index, 0)

    def test_idle_animation_starts_after_three_seconds_at_rest(self):
        self.poppy.update(IDLE_DELAY - 0.01)
        self.assertFalse(self.poppy.is_idle)

        self.poppy.update(0.01)
        self.assertTrue(self.poppy.is_idle)
        self.poppy.draw()

        self.image.clip_composite_draw.assert_called_once_with(
            FRAME_LEFT,
            IDLE_FRAME_BOTTOM,
            FRAME_WIDTH,
            FRAME_HEIGHT,
            0.0,
            "",
            400.0,
            300.0,
            FRAME_WIDTH,
            FRAME_HEIGHT,
        )

    def test_idle_animation_loops(self):
        self.poppy.update(IDLE_DELAY)
        for _ in range(IDLE_FRAME_COUNT):
            self.poppy.update(ANIMATION_FRAME_DURATION)

        self.assertEqual(self.poppy.idle_frame_index, 0)

    def test_starting_a_command_resets_idle_and_run_animations(self):
        self.poppy.update(IDLE_DELAY)
        self.poppy.command_to(700, 300)
        self.poppy.update(ANIMATION_FRAME_DURATION)

        self.assertFalse(self.poppy.is_idle)
        self.assertEqual(self.poppy.idle_elapsed, 0.0)
        self.assertEqual(self.poppy.frame_index, 1)


if __name__ == "__main__":
    unittest.main()
