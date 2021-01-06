from time import time

from topaz.entities.tiles import BombTile, LockedTile, UnlockedTile
from topaz.level import LevelDescriptor


class TopazGame:
    def __init__(self, level, mines, visuals, cache, state=0, duration=0, on_change=lambda state_switch=None: None):
        self.level = level  # type: LevelDescriptor
        self.mines = mines  # type: list[list[bool]]
        self.visuals = visuals  # type: list[list[int]] # 0 - locked, 1 - unlocked, 3 - question, 4 - flag, 5 - bomb
        self.cache = cache  # list[list[int]]
        self.duration = duration  # int
        self.state = state  # int
        self.started = 0  # int
        self.on_change = on_change
        self.game_done = lambda: None

    def bomb_stats(self):
        placed_guesses = 0
        for row in range(self.level.level_sizes()[1]):
            for col in range(self.level.level_sizes()[0]):
                if self.visuals[row][col] == 4 and (self.mines[row][col] == 1 or self.state != 2):
                    placed_guesses += 1

        return self.level.mines_amount() - placed_guesses

    def start(self):
        if self.state == 2:
            return 0
        self.state = 1
        self.started = time() // 1
        self.on_change()
        return 1

    def stop(self):
        if self.state == 2:
            return 0
        self.duration += self.timer()
        self.started = 0
        self.state = 0
        self.on_change()
        return 1

    def timer(self):
        if self.state != 1:
            return self.duration
        return self.duration + (time() // 1 - self.started)

    def move(self, x, y):
        if self.state != 1:
            return 0
        if self.mines[y][x] == 1:
            self.visuals[y][x] = 5
            self.stop()
            self.state = 2
            self.game_done()
            self.on_change()
            return 1

        self.__auto_clean(x, y, [], allow_nonzero=True)

        cleared_fields = 0
        clear_fields = 0
        for row in range(self.level.level_sizes()[1]):
            for col in range(self.level.level_sizes()[0]):
                if self.mines[row][col] != 1:
                    if self.visuals[row][col] == 1:
                        cleared_fields += 1
                    clear_fields += 1

        if cleared_fields == clear_fields:
            self.stop()
            self.state = 2
            self.game_done()

        self.on_change()
        return 1

    def put_question(self, x, y):
        if self.state != 1:
            return 0
        if self.visuals[y][x] != 0 and self.visuals[y][x] != 4:
            return 0
        self.visuals[y][x] = 3
        self.on_change()
        return 1

    def put_flag(self, x, y):
        if self.state != 1:
            return 0
        if self.visuals[y][x] != 0 and self.visuals[y][x] != 3:
            return 0
        self.visuals[y][x] = 4
        self.on_change()
        return 1

    def clear_cell(self, x, y):
        if self.state != 1:
            return 0
        if self.visuals[y][x] != 3 and self.visuals[y][x] != 4:
            return 0
        self.visuals[y][x] = 0
        self.on_change()
        return 1

    def __auto_clean(self, x, y, c, allow_nonzero=False):
        if c is None:
            c = []
        if [x, y] in c:
            return
        c.append([x, y])
        if (self.cache[y][x] == 0 and self.mines[y][x] != 1) or (self.cache[y][x] > 0 and allow_nonzero):
            self.visuals[y][x] = 1
        elif self.cache[y][x] > 0 and self.mines[y][x] != 1:
            self.visuals[y][x] = 1
            return
        else:
            return

        if y > 0:
            self.__auto_clean(x, y - 1, c)
        if y < self.level.level_sizes()[1] - 1:
            self.__auto_clean(x, y + 1, c)
        if x > 0:
            self.__auto_clean(x - 1, y, c)
        if x < self.level.level_sizes()[0] - 1:
            self.__auto_clean(x+1, y, c)
        if y > 0 and x > 0:
            self.__auto_clean(x - 1, y - 1, c)
        if y > 0 and x < self.level.level_sizes()[0] - 1:
            self.__auto_clean(x + 1, y - 1, c)
        if y < self.level.level_sizes()[1] - 1 and x > 0:
            self.__auto_clean(x - 1, y + 1, c)
        if y < self.level.level_sizes()[1] - 1 and x < self.level.level_sizes()[0] - 1:
            self.__auto_clean(x + 1, y + 1, c)

    def playboard(self):
        data = []

        for y in range(self.level.level_sizes()[1]):
            data.append([])
            for x in range(self.level.level_sizes()[0]):
                visual = self.visuals[y][x]
                mine = self.mines[y][x]
                if visual == 5:
                    data[y].append(BombTile(boomed=True))
                    continue
                if self.state == 2 and mine == 1:
                    data[y].append(BombTile())
                    continue
                if visual == 0:
                    data[y].append(LockedTile())
                    continue
                if visual == 3:
                    data[y].append(LockedTile(state=2))
                    continue
                if visual == 4:
                    data[y].append(LockedTile(state=1))
                    continue
                if visual == 1:
                    data[y].append(UnlockedTile(num=self.cache[y][x]))
                    continue
                data[y].append(LockedTile(state=1))
        return data
