from enum import IntFlag


class Color(IntFlag):
    EMPTY = 1
    X = 2
    O = 4

    @property
    def opposite(self):
        if self is Color.EMPTY:
            result = self
        elif self is Color.X:
            result = Color.O
        else:
            result = Color.X
        return result

    def __str__(self):
        if self is Color.EMPTY:
            representation = 'EMPTY'
        elif self is Color.X:
            representation = 'X'
        else:
            representation = 'O'
        return representation
