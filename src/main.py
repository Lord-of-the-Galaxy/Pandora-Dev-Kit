# TODO: ADD PROPER LOGGING SUPPORT

import colorama

from agent import NullPlayer
from game import Game
from params import GameParams
from player import Player

colorama.init()


def main():
    p1t = Player
    p2t = Player
    params = GameParams()
    g = Game(5, p1t, p2t, game_params=params, seed=120)
    g.play(log=True, log_p=False)
    g.player_1.close()
    g.player_2.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
