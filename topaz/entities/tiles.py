from topaz.entities.game_tile import GameTile


class UnlockedTile(GameTile):
    num = 0
    name = 'Unlocked Tile'

    def __init__(self, num: int = 0):
        self.num = num


class LockedTile(GameTile):
    state = 0  # 0 - none, 1 - flag, 2 - question
    name = 'Locked Tile'

    def __init__(self, state: int = 0):
        self.state = state


class BombTile(GameTile):
    boomed = False
    name = 'Bomb Tile'

    def __init__(self, boomed: bool = False):
        self.boomed = boomed
