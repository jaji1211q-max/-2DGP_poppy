import unittest
from types import SimpleNamespace
from unittest.mock import patch

from pico2d import SDL_MOUSEMOTION

from gameworld import GameWorld
from poppy import CANVAS_HEIGHT, CANVAS_WIDTH


class GameWorldTests(unittest.TestCase):
    def test_requires_initialization_before_drawing(self):
        with self.assertRaisesRegex(RuntimeError, "must be initialized"):
            GameWorld().draw()

    def test_initializes_and_delegates_lifecycle_to_poppy(self):
        event = SimpleNamespace(type=SDL_MOUSEMOTION, x=600, y=300)
        with patch("gameworld.Poppy") as poppy_class:
            world = GameWorld()

            self.assertEqual(world.canvas_size, (CANVAS_WIDTH, CANVAS_HEIGHT))
            world.initialize()
            world.handle_event(event)
            world.update(0.25)
            world.draw()

            poppy = poppy_class.return_value
            poppy_class.assert_called_once_with()
            poppy.handle_event.assert_called_once_with(event)
            poppy.update.assert_called_once_with(0.25)
            poppy.draw.assert_called_once_with()

            world.finalize()

        self.assertIsNone(world.poppy)

    def test_forwards_mouse_events_to_poppy(self):
        mouse_event = SimpleNamespace(type=SDL_MOUSEMOTION, x=600, y=300)
        with patch("gameworld.Poppy") as poppy_class:
            world = GameWorld()
            world.initialize()
            world.handle_event(mouse_event)

        poppy_class.return_value.handle_event.assert_called_once_with(mouse_event)


if __name__ == "__main__":
    unittest.main()
