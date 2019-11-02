from enum import Enum
from .color import Color


class Status(Enum):
    IN_PROGRESS = (False, None, 'In Progress')
    DRAW = (True, None, 'Draw')
    X_WON = (True, Color.X, 'X won')
    O_WON = (True, Color.O, 'O won')

    def __init__(self, over, winner, representation):
        self.over = over
        self.winner = winner
        self._representation = representation

    def __str__(self):
        return self._representation
