from math import atan2, hypot, pi
from pathlib import Path

from pico2d import (
    SDL_KEYDOWN,
    SDL_KEYUP,
    SDL_MOUSEMOTION,
    SDLK_a,
    SDLK_d,
    SDLK_DOWN,
    SDLK_LEFT,
    SDLK_RIGHT,
    SDLK_s,
    SDLK_UP,
    SDLK_w,
    load_image,
)


CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
MOVEMENT_SPEED = 300.0
ANIMATION_FRAME_DURATION = 0.1
WALK_FRAME_COUNT = 8
FRAME_LEFT = 96
FRAME_BOTTOM = 688
FRAME_WIDTH = 96
FRAME_HEIGHT = 168
FRAME_STEP = 176


class Poppy:
    def __init__(self):
        image_path = Path(__file__).resolve().with_name("poppy.png")
        self.image = load_image(str(image_path))
        self.x = CANVAS_WIDTH / 2
        self.y = CANVAS_HEIGHT / 2
        self.pressed_keys = set()
        self.animation_elapsed = 0.0
        self.frame_index = 0
        self.mouse_x = None
        self.mouse_y = None
        self.rotation_angle = 0.0

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            self.pressed_keys.add(event.key)
        elif event.type == SDL_KEYUP:
            self.pressed_keys.discard(event.key)
        elif event.type == SDL_MOUSEMOTION:
            self.mouse_x = event.x
            self.mouse_y = CANVAS_HEIGHT - event.y
            self._update_rotation()

    def _update_rotation(self):
        if self.mouse_x is None or self.mouse_y is None:
            return

        direction_x = self.mouse_x - self.x
        direction_y = self.mouse_y - self.y
        if direction_x == 0 and direction_y == 0:
            return

        self.rotation_angle = atan2(direction_y, direction_x) + pi / 2

    def update(self, delta_time):
        if delta_time < 0:
            raise ValueError("delta_time must not be negative")

        horizontal = int(
            SDLK_RIGHT in self.pressed_keys or SDLK_d in self.pressed_keys
        ) - int(SDLK_LEFT in self.pressed_keys or SDLK_a in self.pressed_keys)
        vertical = int(
            SDLK_UP in self.pressed_keys or SDLK_w in self.pressed_keys
        ) - int(SDLK_DOWN in self.pressed_keys or SDLK_s in self.pressed_keys)

        direction_length = hypot(horizontal, vertical)
        if direction_length == 0:
            self.animation_elapsed = 0.0
            self.frame_index = 0
            self._update_rotation()
            return

        distance = MOVEMENT_SPEED * delta_time / direction_length
        half_width = FRAME_WIDTH / 2
        half_height = FRAME_HEIGHT / 2
        self.x = min(
            max(self.x + horizontal * distance, half_width),
            CANVAS_WIDTH - half_width,
        )
        self.y = min(
            max(self.y + vertical * distance, half_height),
            CANVAS_HEIGHT - half_height,
        )

        self.animation_elapsed += delta_time
        frames_elapsed = int(
            (self.animation_elapsed + 1e-9) / ANIMATION_FRAME_DURATION
        )
        if frames_elapsed:
            self.frame_index = (self.frame_index + frames_elapsed) % WALK_FRAME_COUNT
            self.animation_elapsed = max(
                0.0,
                self.animation_elapsed - frames_elapsed * ANIMATION_FRAME_DURATION,
            )

        self._update_rotation()

    def draw(self):
        self.image.clip_composite_draw(
            FRAME_LEFT + self.frame_index * FRAME_STEP,
            FRAME_BOTTOM,
            FRAME_WIDTH,
            FRAME_HEIGHT,
            self.rotation_angle,
            "",
            self.x,
            self.y,
            FRAME_WIDTH,
            FRAME_HEIGHT,
        )
