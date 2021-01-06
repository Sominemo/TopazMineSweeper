from topaz.core import TopazGame


class GameState:
    salt = 0
    game: TopazGame = None
    first_move_x = None
    first_move_y = None

    def __init__(self, salt, game: TopazGame, first_move_x, first_move_y):
        self.salt = salt
        self.game = game
        self.first_move_x = first_move_x
        self.first_move_y = first_move_y
