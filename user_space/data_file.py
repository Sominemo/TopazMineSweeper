import base64
import hashlib
import json
import pathlib

from state_keeper.state import GameState
from topaz.level import LevelDescriptor
from user_space.encrypt import pass_shift
from user_space.file_proxy import encode_file, decode_file
from user_space.session import Session
from user_space.user_dir import prepare_personal_folder


class DataFile:
    def __init__(self, file: pathlib.Path):
        self.file = file
        self.__integrity = file.exists()

    def is_saved(self):
        return self.__integrity

    def save(self, data):
        e = DataFile.__encode(data)
        s = json.dumps(e)
        p = hashlib.md5(Session.get_user().password.encode(encoding='utf-8')).digest().hex()

        r = pass_shift(p, s)

        encode_file(r, self.file)

        self.__integrity = True
        return

    def load(self):
        f = decode_file(self.file)

        p = hashlib.md5(Session.get_user().password.encode(encoding='utf-8')).digest().hex()

        r = pass_shift(p, f, decrypt=True)

        self.__integrity = True
        return DataFile.__decode(json.loads(r))

    def changed(self, state_switch):
        self.__integrity = False

    @staticmethod
    def __encode(state: GameState):
        if state.game.state == 1:
            raise PermissionError("You can't save a running game")

        return {
            's': state.salt,
            'x': state.first_move_x,
            'y': state.first_move_y,
            'l': state.game.level.level,
            't': state.game.timer(),
            'p': state.game.state,
            'v': state.game.visuals,
        }

    @staticmethod
    def __decode(o):
        from state_keeper.generate_new import generate_new
        state = generate_new(
            level=LevelDescriptor(o['l']),
            first_move_x=o['x'],
            first_move_y=o['y'],
            seed=o['s'],
            visuals=o['v']
        )

        state.game.duration = o['t']
        state.game.state = o['p']

        return state


class UserDataFile(DataFile):
    def __init__(self, name: str, user: str = None):
        f = prepare_personal_folder(user)
        super().__init__(f / name)
