from math import hypot
from pathlib import Path

from pico2d import load_image


CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
MOVEMENT_SPEED = 300.0
ANIMATION_FRAME_DURATION = 0.1
IDLE_DELAY = 3.0
WALK_FRAME_COUNT = 8
IDLE_FRAME_COUNT = 8
FRAME_LEFT = 96
FRAME_BOTTOM = 688
IDLE_FRAME_BOTTOM = 856
FRAME_WIDTH = 96
FRAME_HEIGHT = 168
FRAME_STEP = 176


class Poppy:
    def __init__(self):
        image_path = Path(__file__).resolve().with_name("poppy.png")
        self.image = load_image(str(image_path))
        self.x = CANVAS_WIDTH / 2
        self.y = CANVAS_HEIGHT / 2
        self.target_x = None
        self.target_y = None
        self.animation_elapsed = 0.0
        self.frame_index = 0
        self.idle_elapsed = 0.0
        self.idle_animation_elapsed = 0.0
        self.idle_frame_index = 0
        self.is_idle = False

    @property
    def is_moving(self):
        return self.target_x is not None

    def command_to(self, x, y):
        half_width = FRAME_WIDTH / 2
        half_height = FRAME_HEIGHT / 2
        self.target_x = min(max(x, half_width), CANVAS_WIDTH - half_width)
        self.target_y = min(max(y, half_height), CANVAS_HEIGHT - half_height)

        if self.target_x == self.x and self.target_y == self.y:
            self.target_x = None
            self.target_y = None

    def update(self, delta_time):
        if delta_time < 0:
            raise ValueError("delta_time must not be negative")

        previous_x = self.x
        previous_y = self.y
        if self.is_moving:
            direction_x = self.target_x - self.x
            direction_y = self.target_y - self.y
            distance_to_target = hypot(direction_x, direction_y)
            distance = MOVEMENT_SPEED * delta_time

            if distance_to_target <= distance:
                self.x = self.target_x
                self.y = self.target_y
                self.target_x = None
                self.target_y = None
            elif distance_to_target > 0:
                self.x += direction_x * distance / distance_to_target
                self.y += direction_y * distance / distance_to_target

        if self.x != previous_x or self.y != previous_y:
            self.idle_elapsed = 0.0
            self.idle_animation_elapsed = 0.0
            self.idle_frame_index = 0
            self.is_idle = False
            self.frame_index, self.animation_elapsed = self._advance_animation(
                self.frame_index,
                self.animation_elapsed,
                delta_time,
                WALK_FRAME_COUNT,
            )
        else:
            self.animation_elapsed = 0.0
            self.frame_index = 0
            previous_idle_elapsed = self.idle_elapsed
            self.idle_elapsed += delta_time

            if self.idle_elapsed >= IDLE_DELAY:
                self.is_idle = True
                idle_animation_delta = self.idle_elapsed - max(
                    IDLE_DELAY,
                    previous_idle_elapsed,
                )
                self.idle_frame_index, self.idle_animation_elapsed = (
                    self._advance_animation(
                        self.idle_frame_index,
                        self.idle_animation_elapsed,
                        idle_animation_delta,
                        IDLE_FRAME_COUNT,
                    )
                )

    @staticmethod
    def _advance_animation(frame_index, elapsed, delta_time, frame_count):
        elapsed += delta_time
        frames_elapsed = int(
            (elapsed + 1e-9) / ANIMATION_FRAME_DURATION
        )
        if frames_elapsed:
            frame_index = (frame_index + frames_elapsed) % frame_count
            elapsed = max(
                0.0,
                elapsed - frames_elapsed * ANIMATION_FRAME_DURATION,
            )

        return frame_index, elapsed

    def draw(self):
        frame_bottom = IDLE_FRAME_BOTTOM if self.is_idle else FRAME_BOTTOM
        frame_index = self.idle_frame_index if self.is_idle else self.frame_index
        self.image.clip_composite_draw(
            FRAME_LEFT + frame_index * FRAME_STEP,
            frame_bottom,
            FRAME_WIDTH,
            FRAME_HEIGHT,
            0.0,
            "",
            self.x,
            self.y,
            FRAME_WIDTH,
            FRAME_HEIGHT,
        )
