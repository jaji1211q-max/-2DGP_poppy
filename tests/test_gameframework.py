import unittest
from types import SimpleNamespace
from unittest.mock import Mock, call, patch

from pico2d import SDL_KEYDOWN, SDL_QUIT, SDLK_ESCAPE, SDLK_RIGHT

from gameframework import run


class GameFrameworkTests(unittest.TestCase):
    def test_runs_game_world_and_cleans_up_after_quit(self):
        quit_event = SimpleNamespace(type=SDL_QUIT)
        game_world = Mock(canvas_size=(800, 600))
        with (
            patch("gameframework.open_canvas") as open_canvas,
            patch("gameframework.close_canvas") as close_canvas,
            patch("gameframework.get_events", side_effect=[[], [quit_event]]),
            patch(
                "gameframework.get_time",
                side_effect=[0.0, 0.0, 0.01, 0.02, 0.03],
            ),
            patch("gameframework.clear_canvas") as clear_canvas,
            patch("gameframework.update_canvas") as update_canvas,
            patch("gameframework.delay") as delay,
        ):
            run(game_world)

        open_canvas.assert_called_once_with(800, 600)
        self.assertEqual(
            game_world.mock_calls,
            [
                call.initialize(),
                call.update(0.01),
                call.draw(),
                call.finalize(),
            ],
        )
        clear_canvas.assert_called_once_with()
        update_canvas.assert_called_once_with()
        delay.assert_called_once()
        close_canvas.assert_called_once_with()

    def test_escape_exits_without_forwarding_the_key_event(self):
        escape_event = SimpleNamespace(type=SDL_KEYDOWN, key=SDLK_ESCAPE)
        game_world = Mock(canvas_size=(800, 600))
        with (
            patch("gameframework.open_canvas"),
            patch("gameframework.close_canvas") as close_canvas,
            patch("gameframework.get_events", return_value=[escape_event]),
            patch("gameframework.get_time", return_value=0.0),
        ):
            run(game_world)

        game_world.initialize.assert_called_once_with()
        game_world.handle_event.assert_not_called()
        game_world.update.assert_not_called()
        game_world.draw.assert_not_called()
        game_world.finalize.assert_called_once_with()
        close_canvas.assert_called_once_with()

    def test_always_closes_canvas_when_world_drawing_fails(self):
        game_world = Mock(canvas_size=(800, 600))
        game_world.draw.side_effect = RuntimeError("drawing failed")
        with (
            patch("gameframework.open_canvas"),
            patch("gameframework.close_canvas") as close_canvas,
            patch("gameframework.get_events", return_value=[]),
            patch("gameframework.get_time", side_effect=[0.0, 0.0, 0.01]),
            patch("gameframework.clear_canvas"),
            patch("gameframework.update_canvas"),
        ):
            with self.assertRaisesRegex(RuntimeError, "drawing failed"):
                run(game_world)

        game_world.finalize.assert_called_once_with()
        close_canvas.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
