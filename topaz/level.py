class LevelDescriptor:
    level_map = {0: [9, 9, 10], 1: [16, 16, 40], 2: [16, 30, 90]}

    def level_sizes(self):
        return LevelDescriptor.level_map.get(self.level)[0], LevelDescriptor.level_map.get(self.level)[1]

    def mines_amount(self):
        return LevelDescriptor.level_map.get(self.level)[2]

    def __init__(self, n: int):
        self.level = n
