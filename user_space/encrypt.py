def pass_shift(p, string, decrypt=False):
    c = []
    for i in range(len(string)):
        k = p[i % len(p)]
        if decrypt:
            e = chr((ord(string[i]) - ord(k) + 256) % 256)
        else:
            e = chr(ord(string[i]) + ord(k) % 256)
        c.append(e)
    r = ''.join(c)
    return r
