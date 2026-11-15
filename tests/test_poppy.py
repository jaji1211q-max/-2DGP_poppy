import unittest
from types import SimpleNamespace
from unittest.mock import patch

from pico2d import (
    SDL_KEYDOWN,
    SDL_KEYUP,
    SDLK_d,
    SDLK_LEFT,
    SDLK_RIGHT,
    SDLK_UP,
)

from poppy import FRAME_BOTTOM, FRAME_HEIGHT, FRAME_LEFT, FRAME_WIDTH, Poppy


class PoppyTests(unittest.TestCase):
    def setUp(self):
        with patch("poppy.load_image") as load_image:
            self.poppy = Poppy()
        self.image = load_image.return_value

    def press(self, key):
        self.poppy.handle_event(SimpleNamespace(type=SDL_KEYDOWN, key=key))

    def release(self, key):
        self.poppy.handle_event(SimpleNamespace(type=SDL_KEYUP, key=key))

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

    def test_draw_uses_the_first_sprite_frame(self):
        self.poppy.draw()

        self.image.clip_draw.assert_called_once_with(
            FRAME_LEFT,
            FRAME_BOTTOM,
            FRAME_WIDTH,
            FRAME_HEIGHT,
            400.0,
            300.0,
            FRAME_WIDTH,
            FRAME_HEIGHT,
        )


if __name__ == "__main__":
    unittest.main()
