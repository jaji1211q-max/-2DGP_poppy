from math import atan2, hypot, pi
from pathlib import Path

from pico2d import (
    SDL_BUTTON_LEFT,
    SDL_KEYDOWN,
    SDL_KEYUP,
    SDL_MOUSEBUTTONDOWN,
    SDL_MOUSEMOTION,
    SDLK_a,
    SDLK_d,
    SDLK_s,
    SDLK_w,
    load_image,
)

from poppy import CANVAS_HEIGHT, CANVAS_WIDTH


STATE_IDLE = "idle"
STATE_RUN = "run"
STATE_COMMAND = "command"
STATE_GET = "get"

MOVEMENT_SPEED = 300.0
IDLE_DELAY = 3.0
ANIMATION_FRAME_DURATION = 0.1
FRAME_WIDTH = 182
FRAME_HEIGHT = 182
FRAME_STEP = 182
FRAME_COUNT = 8
IDLE_FRAME_BOTTOM = 548
COMMAND_FRAME_BOTTOM = 365
RUN_FRAME_BOTTOM = 182
GET_FRAME_BOTTOM = 0


class Player:
    def __init__(self, poppy):
        image_path = Path(__file__).resolve().with_name("player.png")
        self.image = load_image(str(image_path))
        self.poppy = poppy
        self.x = CANVAS_WIDTH / 4
        self.y = CANVAS_HEIGHT / 2
        self.pressed_keys = set()
        self.state = STATE_IDLE
        self.idle_elapsed = 0.0
        self.idle_animation_elapsed = 0.0
        self.idle_frame_index = 0
        self.animation_elapsed = 0.0
        self.frame_index = 0
        self.is_moving = False
        self.mouse_x = None
        self.mouse_y = None
        self.rotation_angle = 0.0

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            self.pressed_keys.add(event.key)
        elif event.type == SDL_KEYUP:
            self.pressed_keys.discard(event.key)
        elif event.type == SDL_MOUSEMOTION:
            self._set_mouse_position(event.x, event.y)
        elif (
            event.type == SDL_MOUSEBUTTONDOWN
            and event.button == SDL_BUTTON_LEFT
        ):
            self._set_mouse_position(event.x, event.y)
            self.poppy.command_to(self.mouse_x, self.mouse_y)
            self.idle_elapsed = 0.0
            self.idle_animation_elapsed = 0.0
            self.idle_frame_index = 0
            self.state = STATE_COMMAND
            self.animation_elapsed = 0.0
            self.frame_index = 0

    def _set_mouse_position(self, x, y):
        self.mouse_x = x
        self.mouse_y = CANVAS_HEIGHT - y

    def _update_rotation(self):
        if self.mouse_x is None or self.mouse_y is None:
            return

        direction_x = self.mouse_x - self.x
        direction_y = self.mouse_y - self.y
        if direction_x != 0 or direction_y != 0:
            self.rotation_angle = atan2(direction_y, direction_x) + pi / 2

    def update(self, delta_time):
        if delta_time < 0:
            raise ValueError("delta_time must not be negative")

        if self.state == STATE_GET:
            pass
            return

        horizontal = int(
            SDLK_d in self.pressed_keys
        ) - int(SDLK_a in self.pressed_keys)
        vertical = int(SDLK_w in self.pressed_keys) - int(
            SDLK_s in self.pressed_keys
        )
        direction_length = hypot(horizontal, vertical)
        previous_x = self.x
        previous_y = self.y

        if direction_length:
            distance = MOVEMENT_SPEED * delta_time / direction_length
            half_size = FRAME_WIDTH / 2
            self.x = min(
                max(self.x + horizontal * distance, half_size),
                CANVAS_WIDTH - half_size,
            )
            self.y = min(
                max(self.y + vertical * distance, half_size),
                CANVAS_HEIGHT - half_size,
            )

        self.is_moving = self.x != previous_x or self.y != previous_y
        if self.is_moving:
            self._enter_action_state(STATE_RUN)
            self._advance_action_animation(delta_time)
            self._update_rotation()
        elif self.poppy.is_moving:
            self._enter_action_state(STATE_COMMAND)
            self._advance_action_animation(delta_time)
        else:
            self.animation_elapsed = 0.0
            self.frame_index = 0
            previous_idle_elapsed = self.idle_elapsed
            self.idle_elapsed += delta_time

            if self.idle_elapsed >= IDLE_DELAY:
                self.state = STATE_IDLE
                idle_animation_delta = self.idle_elapsed - max(
                    IDLE_DELAY,
                    previous_idle_elapsed,
                )
                self.idle_frame_index, self.idle_animation_elapsed = (
                    self._advance_animation(
                        self.idle_frame_index,
                        self.idle_animation_elapsed,
                        idle_animation_delta,
                        FRAME_COUNT,
                    )
                )
            elif self.state not in (STATE_RUN, STATE_COMMAND):
                self.state = STATE_IDLE

    def _enter_action_state(self, state):
        if self.state != state:
            self.state = state
            self.frame_index = 0
            self.animation_elapsed = 0.0
            self.idle_animation_elapsed = 0.0
            self.idle_frame_index = 0
        self.idle_elapsed = 0.0

    def _advance_action_animation(self, delta_time):
        self.frame_index, self.animation_elapsed = self._advance_animation(
            self.frame_index,
            self.animation_elapsed,
            delta_time,
            FRAME_COUNT,
        )

    @staticmethod
    def _advance_animation(frame_index, elapsed, delta_time, frame_count):
        elapsed += delta_time
        frames_elapsed = int((elapsed + 1e-9) / ANIMATION_FRAME_DURATION)
        if frames_elapsed:
            frame_index = (frame_index + frames_elapsed) % frame_count
            elapsed = max(
                0.0,
                elapsed - frames_elapsed * ANIMATION_FRAME_DURATION,
            )
        return frame_index, elapsed

    def draw(self):
        if self.state == STATE_GET:
            frame_bottom = GET_FRAME_BOTTOM
            frame_index = 0
        elif self.state == STATE_COMMAND and self.poppy.is_moving:
            frame_bottom = COMMAND_FRAME_BOTTOM
            frame_index = self.frame_index
        elif self.state == STATE_RUN and self.is_moving:
            frame_bottom = RUN_FRAME_BOTTOM
            frame_index = self.frame_index
        else:
            frame_bottom = IDLE_FRAME_BOTTOM
            frame_index = self.idle_frame_index if self.state == STATE_IDLE else 0

        self.image.clip_composite_draw(
            FRAME_STEP * frame_index,
            frame_bottom,
            FRAME_WIDTH,
            FRAME_HEIGHT,
            self.rotation_angle,
            "",
            self.x,
            self.y,
            FRAME_WIDTH,
            FRAME_HEIGHT,
        )
