def encode_file(data, file, encode=True):
    if encode:
        b = bytearray(data.encode(encoding="utf-8"))
    else:
        b = data

    for i in range(len(b)):
        b[i] ^= 0xff
    open(file, 'wb').write(b)


def decode_file(file, decode=True, fallback='{}'):
    try:
        b = bytearray(open(file, 'rb').read())
    except FileNotFoundError:
        return fallback
    for i in range(len(b)):
        b[i] ^= 0xff
    if decode:
        return b.decode(encoding="utf-8")
    return b
