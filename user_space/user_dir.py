import os
import sys
import pathlib

from user_space.session import Session


def get_user_data_dir() -> pathlib.Path:
    if sys.platform == "win32":
        return pathlib.Path(os.path.expandvars("%LOCALAPPDATA%"))
    elif sys.platform == "linux":
        return pathlib.Path(os.path.expandvars("$XDG_DATA_HOME"))
    elif sys.platform == "darwin":
        return pathlib.Path.home() / "Library/Application Support"


def prepare_user_data_dir() -> pathlib.Path:
    d = get_user_data_dir() / "topaz_minesweeper"
    try:
        d.mkdir(parents=True)
    except FileExistsError:
        pass

    return d


def prepare_personal_folder(user: str = None):
    if user is None:
        user = Session.get_user().username

    d = prepare_user_data_dir() / user
    try:
        d.mkdir(parents=True)
    except FileExistsError:
        pass

    return d
