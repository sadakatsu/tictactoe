from enum import IntEnum


class Coordinate(IntEnum):
    C00 = 0
    C01 = 1
    C02 = 2
    C10 = 3
    C11 = 4
    C12 = 5
    C20 = 6
    C21 = 7
    C22 = 8

    @property
    def row(self):
        return self // 3

    @property
    def column(self):
        return self % 3

    @property
    def on_left_diagonal(self):
        return self.row == self.column

    @property
    def on_right_diagonal(self):
        return self.row == 2 - self.column

    def get_row(self):
        return (Coordinate(self.row * 3 + i) for i in range(3))

    def get_column(self):
        return (Coordinate(i * 3 + self.column) for i in range(3))

    def get_left_diagonal(self):
        return () if not self.on_left_diagonal else (Coordinate(i * 3 + i) for i in range(3))

    def get_right_diagonal(self):
        return () if not self.on_right_diagonal else (Coordinate(i * 3 + (2 - i)) for i in range(3))

    def get_lines(self):
        yield self.get_row()
        yield self.get_column()
        if self.on_left_diagonal:
            yield self.get_left_diagonal()
        if self.on_right_diagonal:
            yield self.get_right_diagonal()

    def __str__(self):
        return f'({self.row}, {self.column})'
