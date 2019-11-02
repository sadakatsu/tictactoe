from game.color import Color
from game.coordinate import Coordinate
from game.game import Game
from agent.random import RandomAgent

if __name__ == '__main__':
    agent = RandomAgent()

    game = Game()
    while not game.status.over:
        print(game)
        print()

        action = agent.select(game)
        print(action)
        print()

        game = game.play(action)
    print(game)
