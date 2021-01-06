import hashlib
import uuid

from user_space.session import Session
from user_space.user import User
from user_space.user_file import load_user_file, save_user_file


def process_login(username, password, handler, error):
    j = load_user_file()
    if not (username in j):
        error()
        return
    data = j[username]
    if not check_hash(data['pass'], password):
        error()
        return
    Session.apply_user(User(username, password))
    handler()


def sign_up(username, password, handler, error):
    j = load_user_file()
    if username in j:
        error()
        return
    j[username] = {'pass': hash_pass(password)}
    save_user_file(j)
    process_login(username, password, handler, error)


def hash_pass(password, salt=None):
    if salt is None:
        salt = uuid.uuid4().hex
    return hashlib.sha512((password + salt).encode(encoding='utf-8')).hexdigest() + '.' + salt


def check_hash(hash_str, password):
    hash_arr = hash_str.split('.')
    password = hash_pass(password, hash_arr[1])
    return hash_str == password
