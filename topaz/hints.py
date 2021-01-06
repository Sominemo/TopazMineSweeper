def hints(mines):
    cache = []

    for row in range(len(mines)):
        cache.append([])
        for col in range(len(mines[row])):
            cache[row].append(0)

            if row > 0 and mines[row - 1][col] == 1:
                cache[row][col] += 1

            if row < len(mines) - 1 and mines[row + 1][col] == 1:
                cache[row][col] += 1

            if col > 0 and mines[row][col - 1] == 1:
                cache[row][col] += 1

            if col < len(mines[row]) - 1 and mines[row][col + 1] == 1:
                cache[row][col] += 1

            if row > 0 and col > 0 and mines[row - 1][col - 1] == 1:
                cache[row][col] += 1

            if row > 0 and col < len(mines[row]) - 1 and mines[row - 1][col + 1] == 1:
                cache[row][col] += 1

            if row < len(mines) - 1 and col > 0 and mines[row + 1][col - 1] == 1:
                cache[row][col] += 1

            if row < len(mines) - 1 and col < len(mines[row]) - 1 and mines[row + 1][col + 1] == 1:
                cache[row][col] += 1

    return cache
