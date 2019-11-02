from random import choice
from game.game import Game


class RandomAgent:
    @staticmethod
    def select(game: Game):
        return choice([option for option in game.legal_moves])
