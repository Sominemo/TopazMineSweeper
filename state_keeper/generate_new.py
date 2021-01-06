from state_keeper.state import GameState
from topaz.core import TopazGame
from topaz.level import LevelDescriptor
from topaz.hints import hints
import time
import random

from user_space.leaderboard import process_leaderboard


def generate_new(level: LevelDescriptor, first_move_x, first_move_y, seed=None, visuals=None, datafile=None):
    if seed is None:
        seed = time.time_ns()
    random.seed(seed)

    mines = [[0 for row in range(level.level_sizes()[0])] for column in range(level.level_sizes()[1])]
    if visuals is None:
        visuals = [[0 for row in range(level.level_sizes()[0])] for column in range(level.level_sizes()[1])]

    have_mines = level.mines_amount()
    used_mines = 0

    while used_mines < have_mines:
        row = random.randint(0, level.level_sizes()[1] - 1)
        col = random.randint(0, level.level_sizes()[0] - 1)
        if mines[row][col] != 1 and row != first_move_y and col != first_move_x:
            used_mines += 1
            mines[row][col] = 1

    cache = hints(mines)
    game = TopazGame(level, mines, visuals, cache, 1)
    if not (datafile is None):
        game.on_change = lambda state_switch: datafile.changed()
    game.start()
    game.game_done = process_leaderboard
    game.move(first_move_x, first_move_y)

    return GameState(seed, game, first_move_x, first_move_y)


def gen_name(state: GameState):
    return 'game-' + str(state.salt) + '-' + str(state.first_move_x) + '-' + str(state.first_move_y) + '-' + str(
        time.time() // 1) + '.dat'
