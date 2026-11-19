import unittest
from math import atan2, pi
from types import SimpleNamespace
from unittest.mock import Mock, patch

from pico2d import (
    SDL_BUTTON_LEFT,
    SDL_BUTTON_RIGHT,
    SDL_KEYDOWN,
    SDL_KEYUP,
    SDL_MOUSEBUTTONDOWN,
    SDL_MOUSEMOTION,
    SDLK_d,
    SDLK_w,
)

from player import (
    ANIMATION_FRAME_DURATION,
    COMMAND_FRAME_BOTTOM,
    FRAME_HEIGHT,
    FRAME_STEP,
    FRAME_WIDTH,
    GET_FRAME_BOTTOM,
    IDLE_DELAY,
    IDLE_FRAME_BOTTOM,
    MOVEMENT_SPEED,
    RUN_FRAME_BOTTOM,
    STATE_COMMAND,
    STATE_GET,
    STATE_IDLE,
    STATE_RUN,
    Player,
)


class PlayerTests(unittest.TestCase):
    def setUp(self):
        self.poppy = Mock()
        self.poppy.is_moving = False
        with patch("player.load_image") as load_image:
            self.player = Player(self.poppy)
        self.image = load_image.return_value

    def press(self, key):
        self.player.handle_event(SimpleNamespace(type=SDL_KEYDOWN, key=key))

    def release(self, key):
        self.player.handle_event(SimpleNamespace(type=SDL_KEYUP, key=key))

    def click(self, button, x, y):
        self.player.handle_event(
            SimpleNamespace(
                type=SDL_MOUSEBUTTONDOWN,
                button=button,
                x=x,
                y=y,
            )
        )

    def move_mouse(self, x, y):
        self.player.handle_event(
            SimpleNamespace(type=SDL_MOUSEMOTION, x=x, y=y)
        )

    def test_wasd_moves_player_and_enters_run_state(self):
        self.press(SDLK_d)
        self.player.update(0.5)

        self.assertEqual(self.player.state, STATE_RUN)
        self.assertAlmostEqual(self.player.x, 350.0)

    def test_diagonal_run_speed_is_normalized(self):
        self.press(SDLK_d)
        self.press(SDLK_w)
        self.player.update(0.5)

        distance = MOVEMENT_SPEED * 0.5 / 2**0.5
        self.assertAlmostEqual(self.player.x, 200 + distance)
        self.assertAlmostEqual(self.player.y, 300 + distance)

    def test_run_animation_uses_the_run_sprite_row(self):
        self.press(SDLK_d)
        self.player.update(ANIMATION_FRAME_DURATION)
        self.player.draw()

        self.image.clip_composite_draw.assert_called_once_with(
            FRAME_STEP,
            RUN_FRAME_BOTTOM,
            FRAME_WIDTH,
            FRAME_HEIGHT,
            0.0,
            "",
            self.player.x,
            self.player.y,
            FRAME_WIDTH,
            FRAME_HEIGHT,
        )

    def test_player_faces_the_mouse_while_running(self):
        self.move_mouse(600, 300)
        self.press(SDLK_d)
        self.player.update(0.1)

        self.assertAlmostEqual(self.player.rotation_angle, pi / 2)

    def test_player_rotation_uses_canvas_mouse_coordinates(self):
        self.move_mouse(200, 100)
        self.press(SDLK_w)
        self.player.update(0.1)

        self.assertAlmostEqual(
            self.player.rotation_angle,
            atan2(200, 0) + pi / 2,
        )

    def test_player_does_not_rotate_toward_mouse_while_stationary(self):
        self.move_mouse(600, 300)
        self.player.update(0.1)

        self.assertEqual(self.player.rotation_angle, 0.0)

    def test_player_enters_idle_after_three_seconds_without_activity(self):
        self.press(SDLK_d)
        self.player.update(0.1)
        self.release(SDLK_d)
        self.player.update(IDLE_DELAY - 0.01)

        self.assertEqual(self.player.state, STATE_RUN)

        self.player.update(0.01)

        self.assertEqual(self.player.state, STATE_IDLE)

    def test_idle_animation_uses_and_advances_first_sprite_row(self):
        self.player.update(IDLE_DELAY + ANIMATION_FRAME_DURATION)
        self.player.draw()

        self.assertEqual(self.player.state, STATE_IDLE)
        self.image.clip_composite_draw.assert_called_once_with(
            FRAME_STEP,
            IDLE_FRAME_BOTTOM,
            FRAME_WIDTH,
            FRAME_HEIGHT,
            0.0,
            "",
            self.player.x,
            self.player.y,
            FRAME_WIDTH,
            FRAME_HEIGHT,
        )

    def test_left_click_commands_poppy_to_cursor_position(self):
        self.click(SDL_BUTTON_LEFT, 600, 200)

        self.poppy.command_to.assert_called_once_with(600, 400)
        self.assertEqual(self.player.state, STATE_COMMAND)

    def test_right_click_does_not_command_poppy(self):
        self.click(SDL_BUTTON_RIGHT, 600, 200)

        self.poppy.command_to.assert_not_called()
        self.assertEqual(self.player.state, STATE_IDLE)

    def test_command_state_uses_command_sprite_row(self):
        self.poppy.is_moving = True
        self.player.update(ANIMATION_FRAME_DURATION)
        self.player.draw()

        self.assertEqual(self.player.state, STATE_COMMAND)
        self.image.clip_composite_draw.assert_called_once_with(
            FRAME_STEP,
            COMMAND_FRAME_BOTTOM,
            FRAME_WIDTH,
            FRAME_HEIGHT,
            0.0,
            "",
            self.player.x,
            self.player.y,
            FRAME_WIDTH,
            FRAME_HEIGHT,
        )

    def test_command_click_does_not_move_player(self):
        original_position = (self.player.x, self.player.y)
        self.click(SDL_BUTTON_LEFT, 600, 200)
        self.player.update(0.1)

        self.assertEqual((self.player.x, self.player.y), original_position)

    def test_get_state_is_reserved_without_movement_implementation(self):
        self.player.state = STATE_GET
        self.press(SDLK_d)
        self.player.update(1.0)
        self.player.draw()

        self.assertEqual(self.player.state, STATE_GET)
        self.assertEqual((self.player.x, self.player.y), (200, 300))
        self.image.clip_composite_draw.assert_called_once_with(
            0,
            GET_FRAME_BOTTOM,
            FRAME_WIDTH,
            FRAME_HEIGHT,
            0.0,
            "",
            200,
            300,
            FRAME_WIDTH,
            FRAME_HEIGHT,
        )

    def test_run_animation_wraps_after_all_frames(self):
        self.press(SDLK_d)
        for _ in range(8):
            self.player.update(ANIMATION_FRAME_DURATION)

        self.assertEqual(self.player.frame_index, 0)


if __name__ == "__main__":
    unittest.main()
