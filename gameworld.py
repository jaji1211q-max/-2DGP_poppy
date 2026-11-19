from typing import Optional

from poppy import CANVAS_HEIGHT, CANVAS_WIDTH, Poppy


class GameWorld:
    canvas_size = (CANVAS_WIDTH, CANVAS_HEIGHT)

    def __init__(self):
        self.poppy: Optional[Poppy] = None

    def initialize(self):
        self.poppy = Poppy()

    def handle_event(self, event):
        self._get_poppy().handle_event(event)

    def update(self, delta_time):
        self._get_poppy().update(delta_time)

    def draw(self):
        self._get_poppy().draw()

    def finalize(self):
        self.poppy = None

    def _get_poppy(self) -> Poppy:
        if self.poppy is None:
            raise RuntimeError("GameWorld must be initialized before use.")
        return self.poppy

