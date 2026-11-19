import unittest
from types import SimpleNamespace
from unittest.mock import patch

from pico2d import (
    SDL_BUTTON_LEFT,
    SDL_MOUSEBUTTONDOWN,
    SDL_MOUSEMOTION,
)

from gameworld import GameWorld
from poppy import CANVAS_HEIGHT, CANVAS_WIDTH


class GameWorldTests(unittest.TestCase):
    def test_requires_initialization_before_drawing(self):
        with self.assertRaisesRegex(RuntimeError, "must be initialized"):
            GameWorld().draw()

    def test_initializes_and_delegates_lifecycle_to_player_and_poppy(self):
        event = SimpleNamespace(type=SDL_MOUSEMOTION, x=600, y=300)
        with (
            patch("gameworld.Poppy") as poppy_class,
            patch("gameworld.Player") as player_class,
        ):
            world = GameWorld()

            self.assertEqual(world.canvas_size, (CANVAS_WIDTH, CANVAS_HEIGHT))
            world.initialize()
            world.handle_event(event)
            world.update(0.25)
            world.draw()

            poppy = poppy_class.return_value
            player = player_class.return_value
            poppy_class.assert_called_once_with()
            poppy.update.assert_called_once_with(0.25)
            poppy.draw.assert_called_once_with()
            player_class.assert_called_once_with(poppy)
            player.handle_event.assert_called_once_with(event)
            player.update.assert_called_once_with(0.25)
            player.draw.assert_called_once_with()

            world.finalize()

        self.assertIsNone(world.poppy)
        self.assertIsNone(world.player)

    def test_forwards_input_events_to_player(self):
        mouse_event = SimpleNamespace(type=SDL_MOUSEMOTION, x=600, y=300)
        with (
            patch("gameworld.Poppy"),
            patch("gameworld.Player") as player_class,
        ):
            world = GameWorld()
            world.initialize()
            world.handle_event(mouse_event)

        player_class.return_value.handle_event.assert_called_once_with(
            mouse_event
        )

    def test_player_command_moves_poppy_without_moving_player(self):
        event = SimpleNamespace(
            type=SDL_MOUSEBUTTONDOWN,
            button=SDL_BUTTON_LEFT,
            x=600,
            y=300,
        )
        with (
            patch("poppy.load_image"),
            patch("player.load_image"),
        ):
            world = GameWorld()
            world.initialize()
            player_start = (world.player.x, world.player.y)

            world.handle_event(event)
            world.update(0.1)

        self.assertEqual((world.poppy.x, world.poppy.y), (430.0, 300.0))
        self.assertEqual((world.player.x, world.player.y), player_start)
        self.assertEqual(world.player.state, "command")


if __name__ == "__main__":
    unittest.main()
