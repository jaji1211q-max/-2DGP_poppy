import unittest
from math import atan2, pi
from types import SimpleNamespace
from unittest.mock import patch

from pico2d import (
    SDL_KEYDOWN,
    SDL_KEYUP,
    SDL_MOUSEMOTION,
    SDLK_d,
    SDLK_LEFT,
    SDLK_RIGHT,
    SDLK_UP,
)

from poppy import (
    ANIMATION_FRAME_DURATION,
    FRAME_BOTTOM,
    FRAME_HEIGHT,
    FRAME_LEFT,
    FRAME_STEP,
    FRAME_WIDTH,
    WALK_FRAME_COUNT,
    Poppy,
)


class PoppyTests(unittest.TestCase):
    def setUp(self):
        with patch("poppy.load_image") as load_image:
            self.poppy = Poppy()
        self.image = load_image.return_value

    def press(self, key):
        self.poppy.handle_event(SimpleNamespace(type=SDL_KEYDOWN, key=key))

    def release(self, key):
        self.poppy.handle_event(SimpleNamespace(type=SDL_KEYUP, key=key))

    def move_mouse(self, x, y):
        self.poppy.handle_event(
            SimpleNamespace(type=SDL_MOUSEMOTION, x=x, y=y)
        )

    def test_moves_at_a_consistent_speed(self):
        self.press(SDLK_RIGHT)
        self.poppy.update(1.0)

        self.assertAlmostEqual(self.poppy.x, 700.0)
        self.assertEqual(self.poppy.y, 300.0)

    def test_wasd_controls_are_supported(self):
        self.press(SDLK_d)
        self.poppy.update(0.5)

        self.assertAlmostEqual(self.poppy.x, 550.0)

    def test_diagonal_movement_is_normalized(self):
        self.press(SDLK_RIGHT)
        self.press(SDLK_UP)
        self.poppy.update(1.0)

        self.assertAlmostEqual(self.poppy.x - 400.0, 300.0 / 2**0.5)
        self.assertAlmostEqual(self.poppy.y - 300.0, 300.0 / 2**0.5)

    def test_key_release_stops_movement(self):
        self.press(SDLK_RIGHT)
        self.release(SDLK_RIGHT)
        self.poppy.update(1.0)

        self.assertEqual(self.poppy.x, 400.0)

    def test_opposite_directions_cancel(self):
        self.press(SDLK_LEFT)
        self.press(SDLK_RIGHT)
        self.poppy.update(1.0)

        self.assertEqual(self.poppy.x, 400.0)

    def test_movement_stays_inside_canvas(self):
        self.press(SDLK_LEFT)
        self.poppy.update(10.0)

        self.assertEqual(self.poppy.x, FRAME_WIDTH / 2)

    def test_negative_delta_time_is_rejected(self):
        with self.assertRaises(ValueError):
            self.poppy.update(-0.1)

    def test_mouse_to_the_right_rotates_poppy_toward_the_pointer(self):
        self.move_mouse(600, 300)

        self.assertAlmostEqual(self.poppy.rotation_angle, pi / 2)

    def test_mouse_screen_y_is_converted_to_canvas_coordinates(self):
        self.move_mouse(400, 100)

        self.assertAlmostEqual(self.poppy.rotation_angle, pi)

    def test_rotation_tracks_a_stationary_pointer_as_poppy_moves(self):
        self.move_mouse(600, 300)
        self.press(SDLK_UP)
        self.poppy.update(0.1)

        self.assertAlmostEqual(
            self.poppy.rotation_angle,
            atan2(-30, 200) + pi / 2,
        )

    def test_pointer_at_poppy_position_keeps_the_previous_rotation(self):
        self.move_mouse(600, 300)
        self.move_mouse(400, 300)

        self.assertAlmostEqual(self.poppy.rotation_angle, pi / 2)

    def test_draw_uses_the_first_frame_of_the_second_sprite_row(self):
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

    def test_walk_animation_advances_when_moving(self):
        self.press(SDLK_RIGHT)
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

    def test_draw_uses_the_mouse_facing_angle(self):
        self.move_mouse(600, 300)
        self.poppy.draw()

        self.image.clip_composite_draw.assert_called_once_with(
            FRAME_LEFT,
            FRAME_BOTTOM,
            FRAME_WIDTH,
            FRAME_HEIGHT,
            pi / 2,
            "",
            400.0,
            300.0,
            FRAME_WIDTH,
            FRAME_HEIGHT,
        )

    def test_walk_animation_wraps_after_all_frames(self):
        self.press(SDLK_RIGHT)
        for _ in range(WALK_FRAME_COUNT):
            self.poppy.update(ANIMATION_FRAME_DURATION)

        self.assertEqual(self.poppy.frame_index, 0)

    def test_walk_animation_resets_when_movement_stops(self):
        self.press(SDLK_RIGHT)
        self.poppy.update(ANIMATION_FRAME_DURATION)
        self.release(SDLK_RIGHT)
        self.poppy.update(ANIMATION_FRAME_DURATION)

        self.assertEqual(self.poppy.frame_index, 0)


if __name__ == "__main__":
    unittest.main()
