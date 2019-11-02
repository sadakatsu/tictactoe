from __future__ import annotations
from typing import List, Optional
from .color import Color
from .coordinate import Coordinate
from .status import Status


class Game:
    def __init__(self, source: Game = None):
        if source:
            self.active: Optional[Color] = source.active
            self.board: List[Color] = source.board[:]
            self.status: Status = source.status
            self._hash: int = source._hash
        else:
            self.active: Optional[Color] = Color.X
            self.board: List[Color] = [Color.EMPTY for _ in Coordinate]
            self.status: Status = Status.IN_PROGRESS

            self._hash: int = 0
            for _ in Coordinate:
                self._hash = (self._hash << 3) + Color.EMPTY

    @property
    def legal_moves(self):
        return (c for c in Coordinate if self.board[c] is Color.EMPTY) if self.status is Status.IN_PROGRESS else ()

    def play(self, move: Coordinate):
        assert self.status is Status.IN_PROGRESS
        assert self.board[move] is Color.EMPTY
        next_game = Game(source=self)
        next_game._set(move, self.active)
        if next_game._is_won(move, self.active):
            next_game.active = None
            next_game.status = Status.X_WON if self.active is Color.X else Status.O_WON
        elif next_game._is_drawn():
            next_game.active = None
            next_game.status = Status.DRAW
        else:
            next_game.active = self.active.opposite
        return next_game

    def _set(self, move: Coordinate, color: Color):
        self.board[move] = color

        offset = move * 3
        empty_mask = Color.EMPTY << offset
        new_mask = color << offset
        self._hash = self._hash ^ empty_mask ^ new_mask

    def _is_won(self, move: Coordinate, color: Color):
        won = False
        for line in move.get_lines():
            won = True
            for coordinate in line:
                if coordinate is not move and self.board[coordinate] is not color:
                    won = False
            if won:
                break
        return won

    def _is_drawn(self):
        drawn = True
        for color in self.board:
            if color is Color.EMPTY:
                drawn = False
                break
        return drawn

    def __getitem__(self, coordinate: Coordinate):
        return self.board[coordinate]

    def __hash__(self):
        return self._hash

    def __str__(self):
        representation = f'Status: {self.status}\nActive: {self.active.__str__()}\n'
        previous: Coordinate = None
        for coordinate in Coordinate:
            if previous is not None:
                if coordinate.row == previous.row:
                    representation += ' '
                else:
                    representation += '\n'
            representation += Game._represent_color(self.board[coordinate])
            previous = coordinate
        return representation + '\n'

    @staticmethod
    def _represent_color(color: Color):
        if color is Color.EMPTY:
            representation = '_'
        elif color is Color.X:
            representation = 'X'
        else:
            representation = 'O'
        return representation
