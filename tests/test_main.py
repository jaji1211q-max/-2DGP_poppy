import unittest
from types import SimpleNamespace
from unittest.mock import patch

from pico2d import SDL_MOUSEMOTION, SDL_QUIT

import main


class MainTests(unittest.TestCase):
    def test_runs_a_frame_then_closes_the_canvas_on_quit(self):
        quit_event = SimpleNamespace(type=SDL_QUIT)
        with (
            patch("main.open_canvas") as open_canvas,
            patch("main.close_canvas") as close_canvas,
            patch("main.get_events", side_effect=[[], [quit_event]]),
            patch("main.get_time", side_effect=[0.0, 0.0, 0.01, 0.02, 0.03]),
            patch("main.clear_canvas") as clear_canvas,
            patch("main.update_canvas") as update_canvas,
            patch("main.delay") as delay,
            patch("main.Poppy") as poppy_class,
        ):
            main.main()

        open_canvas.assert_called_once_with(800, 600)
        poppy_class.return_value.update.assert_called_once_with(0.01)
        poppy_class.return_value.draw.assert_called_once_with()
        clear_canvas.assert_called_once_with()
        update_canvas.assert_called_once_with()
        delay.assert_called_once()
        close_canvas.assert_called_once_with()

    def test_forwards_mouse_motion_to_poppy(self):
        mouse_event = SimpleNamespace(type=SDL_MOUSEMOTION, x=600, y=300)
        quit_event = SimpleNamespace(type=SDL_QUIT)
        with (
            patch("main.open_canvas"),
            patch("main.close_canvas") as close_canvas,
            patch(
                "main.get_events",
                side_effect=[[mouse_event], [quit_event]],
            ),
            patch("main.get_time", side_effect=[0.0, 0.0, 0.01, 0.02, 0.03]),
            patch("main.clear_canvas"),
            patch("main.update_canvas"),
            patch("main.delay"),
            patch("main.Poppy") as poppy_class,
        ):
            main.main()

        poppy_class.return_value.handle_event.assert_called_once_with(mouse_event)
        close_canvas.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
