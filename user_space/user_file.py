import json

from user_space.file_proxy import decode_file, encode_file
from user_space.user_dir import prepare_user_data_dir


def load_user_file() -> dict:
    d = prepare_user_data_dir()
    return json.loads(decode_file(d / 'users.dat'))


def save_user_file(data):
    d = prepare_user_data_dir() / 'users.dat'
    encode_file(json.dumps(data), d)


def load_leaderboard_file() -> dict:
    d = prepare_user_data_dir()
    return json.loads(decode_file(d / 'leaders.dat', fallback='{"top": []}'))


def save_leaderboard_file(data):
    d = prepare_user_data_dir() / 'leaders.dat'
    encode_file(json.dumps(data), d)
