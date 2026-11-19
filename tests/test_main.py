import unittest
from unittest.mock import patch

import main


class MainTests(unittest.TestCase):
    def test_runs_the_game_framework_with_a_game_world(self):
        with (
            patch("main.run") as run,
            patch("main.GameWorld") as game_world_class,
        ):
            main.main()

        game_world_class.assert_called_once_with()
        run.assert_called_once_with(game_world_class.return_value)


if __name__ == "__main__":
    unittest.main()
