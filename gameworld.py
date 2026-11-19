from typing import Optional

from player import Player
from poppy import CANVAS_HEIGHT, CANVAS_WIDTH, Poppy


class GameWorld:
    canvas_size = (CANVAS_WIDTH, CANVAS_HEIGHT)

    def __init__(self):
        self.poppy: Optional[Poppy] = None
        self.player: Optional[Player] = None

    def initialize(self):
        self.poppy = Poppy()
        self.player = Player(self.poppy)

    def handle_event(self, event):
        self._get_player().handle_event(event)

    def update(self, delta_time):
        self._get_poppy().update(delta_time)
        self._get_player().update(delta_time)

    def draw(self):
        self._get_poppy().draw()
        self._get_player().draw()

    def finalize(self):
        self.poppy = None
        self.player = None

    def _get_poppy(self) -> Poppy:
        if self.poppy is None:
            raise RuntimeError("GameWorld must be initialized before use.")
        return self.poppy

    def _get_player(self) -> Player:
        if self.player is None:
            raise RuntimeError("GameWorld must be initialized before use.")
        return self.player
