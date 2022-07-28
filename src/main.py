# TODO: ADD PROPER LOGGING SUPPORT

import colorama

from game import Game
from params import GameParams
from player import Player

colorama.init()


def main():
    p1t = Player
    p2t = Player
    params = GameParams()
    g = Game(4, p1t, p2t, game_params=params, seed=100)
    g.play(log=True, log_p=True)
    g.player_1.close()
    g.player_2.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
