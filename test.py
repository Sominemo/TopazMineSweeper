# main.py

from ui_bridge.init import launch_ui

if __name__ == '__main__':
    launch_ui()

# generate_new.py

from state_keeper.state import GameState
from topaz.core import TopazGame
from topaz.level import LevelDescriptor
from topaz.hints import hints
import time
import random

from user_space.leaderboard import process_leaderboard


def generate_new(level: LevelDescriptor, first_move_x, first_move_y, seed=None, visuals=None, datafile=None):
    if seed is None:
        seed = time.time_ns()
    random.seed(seed)

    mines = [[0 for row in range(level.level_sizes()[0])] for column in range(level.level_sizes()[1])]
    if visuals is None:
        visuals = [[0 for row in range(level.level_sizes()[0])] for column in range(level.level_sizes()[1])]

    have_mines = level.mines_amount()
    used_mines = 0

    while used_mines < have_mines:
        row = random.randint(0, level.level_sizes()[1] - 1)
        col = random.randint(0, level.level_sizes()[0] - 1)
        if mines[row][col] != 1 and row != first_move_y and col != first_move_x:
            used_mines += 1
            mines[row][col] = 1

    cache = hints(mines)
    game = TopazGame(level, mines, visuals, cache, 1)
    if not (datafile is None):
        game.on_change = lambda state_switch: datafile.changed()
    game.start()
    game.game_done = process_leaderboard
    game.move(first_move_x, first_move_y)

    return GameState(seed, game, first_move_x, first_move_y)


def gen_name(state: GameState):
    return 'game-' + str(state.salt) + '-' + str(state.first_move_x) + '-' + str(state.first_move_y) + '-' + str(
        time.time() // 1) + '.dat'


# state.py

from topaz.core import TopazGame


class GameState:
    salt = 0
    game: TopazGame = None
    first_move_x = None
    first_move_y = None

    def __init__(self, salt, game: TopazGame, first_move_x, first_move_y):
        self.salt = salt
        self.game = game
        self.first_move_x = first_move_x
        self.first_move_y = first_move_y


# core.py

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
            self.__auto_clean(x + 1, y, c)
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


# hints.py

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


# level.py

class LevelDescriptor:
    level_map = {0: [9, 9, 10], 1: [16, 16, 40], 2: [16, 30, 90]}

    def level_sizes(self):
        return LevelDescriptor.level_map.get(self.level)[0], LevelDescriptor.level_map.get(self.level)[1]

    def mines_amount(self):
        return LevelDescriptor.level_map.get(self.level)[2]

    def __init__(self, n: int):
        self.level = n


# game_tile.py

class GameTile:
    name = 'Tile'


# tiles.py

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


# draw_field.py

from tkinter import *
from tkinter import ttk

from topaz.entities.tiles import UnlockedTile, LockedTile, BombTile
from topaz.level import LevelDescriptor


def draw_field(content, level: LevelDescriptor, field, handler):
    from ui_bridge.ui_controller import UIController

    for row in range(level.level_sizes()[1]):
        for col in range(level.level_sizes()[0]):
            el = field[row][col]
            fr = None
            if isinstance(el, LockedTile):
                fr = ttk.Frame(content, relief='raised', width=30, height=30, borderwidth=0)

                img = None
                if el.state == 1:
                    img = UIController.assets[10]
                if el.state == 2:
                    img = UIController.assets[11]
                if el.state != 0:
                    l = Label(fr, image=img, height=22, width=22)
                    l.grid(column=0, row=0)
                    l.bind("<Button-3>", lambda *a, row=row, col=col: handler(col, row, interaction=2))
            else:
                fr = ttk.Frame(content, width=30, height=30, relief='groove', borderwidth=1)
                if isinstance(el, BombTile):
                    img = UIController.assets[9]
                    Label(fr, image=img, height=25, width=25, bg=('red' if el.boomed else None)).grid(column=0, row=0)
                if isinstance(el, UnlockedTile):
                    img = UIController.assets[el.num]
                    Label(fr, text=str(el.num), image=img, bg='#ddd', height=25, width=25).grid(column=1, row=1)

            if not isinstance(el, LockedTile) or (el.state != 1 and el.state != 2):
                fr.bind("<Button-1>", lambda *a, row=row, col=col: handler(col, row, interaction=1))
            fr.bind("<Button-3>", lambda *a, row=row, col=col: handler(col, row, interaction=2))

            fr.grid(column=col, row=row)


# exit.py

from tkinter import messagebox


def wanna_exit(window):
    from ui_bridge.ui_controller import UIController

    if UIController.state is None or messagebox.askokcancel('Exit', 'Are you sure you want to exit?'):
        window.destroy()


# init.py

import pathlib
import time
import tkinter as tk

from state_keeper.generate_new import generate_new
from ui_bridge.exit import wanna_exit
from topaz.entities.tiles import LockedTile
from topaz.level import LevelDescriptor
from ui_bridge.draw_field import draw_field
from ui_bridge.login import sign_up_ui
from ui_bridge.resource_path import resource_path
from ui_bridge.save import save
from ui_bridge.login import login_ui
from user_space.data_file import DataFile
from user_space.leaderboard import process_leaderboard, leaders_window
from user_space.session import Session
from user_space.user_dir import prepare_personal_folder


def launch_ui():
    window = tk.Tk()
    window.title('Minesweeper')
    window.resizable(False, False)
    window.iconbitmap(default=resource_path('./ui_bridge/assets/mine_icon.ico'))
    window.option_add('*tearOff', False)
    window.protocol("WM_DELETE_WINDOW", lambda *args: wanna_exit(window))

    def handler(*args):
        UIController.state = None
        UIController.saver = None
        UIController.menu['game'].entryconfigure(0, state='disabled')
        UIController.menu['game'].entryconfigure(1, state='disabled')
        UIController.menu['game'].entryconfigure(2, state='normal')
        UIController.menu['users'].entryconfigure(0, state='normal')
        first_paint(
            window, LevelDescriptor(UIController.level.get()),
            lambda x, y, interaction: move_handler(x, y, interaction=1, new_game=True)
        )
        UIController.menu['level'].entryconfigure(0, state='normal')
        UIController.menu['level'].entryconfigure(1, state='normal')
        UIController.menu['level'].entryconfigure(2, state='normal')

    menu = tk.Menu(window)
    window.config(menu=menu)

    from ui_bridge.ui_controller import UIController

    UIController.window = window

    UIController.menu['game'] = tk.Menu(menu)
    menu.add_cascade(label="Game", menu=UIController.menu['game'])

    UIController.menu['leader'] = tk.Menu(menu)
    menu.add_cascade(label="Leaderboard", menu=UIController.menu['leader'])

    UIController.menu['users'] = tk.Menu(menu)
    menu.add_cascade(label="Users", menu=UIController.menu['users'])

    UIController.menu['level'] = tk.Menu(menu)
    menu.add_cascade(label="Level", menu=UIController.menu['level'])

    UIController.menu['game'].add_command(label="Reset", state='disabled', command=handler)
    UIController.menu['game'].add_command(label="Save", state='disabled', command=save)
    UIController.menu['game'].add_command(label="Load...", command=load_ui)
    UIController.menu['game'].add_separator()
    UIController.menu['game'].add_command(label="Exit", command=lambda *args: wanna_exit(window))

    UIController.menu['leader'].add_command(label="See leaderboard", command=leaders_window)

    UIController.menu['level'].add_radiobutton(label="Beginner", variable=UIController.level, value=0)
    UIController.menu['level'].add_radiobutton(label="Amateur", variable=UIController.level, value=1)
    UIController.menu['level'].add_radiobutton(label="Professional", variable=UIController.level, value=2)

    UIController.menu['users'].add_command(label="Log in")
    UIController.menu['users'].add_command(label="Create user", command=lambda: sign_up_ui(lambda: None))

    def update_login_menu():
        usr = Session.get_user()
        if usr is None:
            UIController.menu['users'].entryconfigure(0, label="Log in", command=lambda: login_ui(lambda: None))
            UIController.menu['users'].entryconfigure(1, state='normal')
        else:
            UIController.menu['users'].entryconfigure(0, label='Log out (' + usr.username + ')',
                                                      command=lambda: Session.apply_user(None))
            UIController.menu['users'].entryconfigure(1, state='disabled')

    update_login_menu()
    Session.handlers.append(update_login_menu)

    logo = tk.PhotoImage(file=resource_path('./ui_bridge/assets/mine_logo.png'))
    tk.Label(window, image=logo, height=70).grid(column=1, row=1, rowspan=2)

    name_label = tk.Label(window, text='Topaz Minesweeper')
    name_label.config(font=(None, 12, 'bold'))
    name_label.grid(column=2, row=1, sticky='sw')
    sign = tk.Label(window, text=' Sergey Dilong BS-02')
    sign.grid(column=2, row=2, sticky='nw')
    UIController.sign = sign

    time = tk.Label(window, text='00:00')
    time.grid(column=3, row=1, rowspan=2)

    def tick():
        if UIController.state is None:
            time.config(text='00:00')
            time.after(1000, tick)
            return
        timer = UIController.state.game.timer()
        time.config(text=str(int(timer // 60)).zfill(2) + ':' + str(int(timer % 60)).zfill(2))
        time.after(1000, tick)

    UIController.field = tk.Frame(window)
    UIController.field.grid(column=1, row=3, columnspan=3)

    UIController.level.trace("w", handler)

    handler()
    tick()
    window.mainloop()


def first_paint(window, level, handler):
    from ui_bridge.ui_controller import UIController
    visuals = [[LockedTile() for row in range(level.level_sizes()[0])] for column in range(level.level_sizes()[1])]
    if not (UIController.field is None):
        UIController.field.destroy()
    UIController.field = tk.Frame(window)
    UIController.field.grid(column=1, row=3, columnspan=3)
    draw_field(UIController.field, level, visuals, handler)
    UIController.sign.config(text=' Sergey Dilong BS-02')


def move_handler(x, y, interaction: int, new_game=False):
    from ui_bridge.ui_controller import UIController
    exam_cell = None

    if new_game:
        UIController.state = generate_new(LevelDescriptor(UIController.level.get()), x, y)
    else:
        if UIController.state.game.state == 0:
            UIController.state.game.start()
        if interaction == 1:
            UIController.state.game.move(x, y)
        elif interaction == 2 and isinstance(exam_cell := UIController.state.game.playboard()[y][x], LockedTile):
            if exam_cell.state == 0:
                UIController.state.game.put_flag(x, y)
            elif exam_cell.state == 1:
                UIController.state.game.put_question(x, y)
            elif exam_cell.state == 2:
                UIController.state.game.clear_cell(x, y)
    refresh()


def refresh():
    from ui_bridge.ui_controller import UIController

    playboard = UIController.state.game.playboard()
    if not (UIController.field is None):
        UIController.field.destroy()
    UIController.field = tk.Frame(UIController.window)
    UIController.field.grid(column=1, row=3, columnspan=3)
    draw_field(UIController.field, UIController.state.game.level, playboard,
               move_handler)
    bombs = UIController.state.game.bomb_stats()
    UIController.sign.config(text=' ' + str(bombs) + ' ' + ('bomb' if bombs == 1 else 'bombs' + ' left'))
    menu_state(1 if UIController.state.game.state == 1 else 0)


def menu_state(state):
    from ui_bridge.ui_controller import UIController

    if state == 1:
        UIController.menu['level'].entryconfigure(0, state='disabled')
        UIController.menu['level'].entryconfigure(1, state='disabled')
        UIController.menu['level'].entryconfigure(2, state='disabled')

        UIController.menu['game'].entryconfigure(0, state='normal')
        UIController.menu['game'].entryconfigure(1, state='normal')
        UIController.menu['game'].entryconfigure(2, state='disabled')

        UIController.menu['users'].entryconfigure(0, state='disabled')
    else:
        UIController.menu['level'].entryconfigure(0, state='normal')
        UIController.menu['level'].entryconfigure(1, state='normal')
        UIController.menu['level'].entryconfigure(2, state='normal')

        UIController.menu['game'].entryconfigure(0, state='normal')
        UIController.menu['game'].entryconfigure(1, state='normal')
        UIController.menu['game'].entryconfigure(2, state='normal')

        UIController.menu['users'].entryconfigure(0, state='normal')


def load_flow():
    from ui_bridge.ui_controller import UIController

    f = prepare_personal_folder()
    lst = []

    for fi in f.iterdir():
        lst.append({'file': fi, 'date': fi.stat().st_mtime})

    lst = sorted(lst, key=lambda i: i['date'], reverse=True)
    rm = lst[10:]
    lst = lst[:10]

    for fi in rm:
        fi['file'].unlink()

    saves = []

    for fi in lst:
        saves.append(time.strftime("%b %d %Y %H:%M:%S", time.localtime(fi['date'])))

    choices_var = tk.StringVar(value=saves)

    def restart():
        if UIController.state is not None and UIController.state.game.state != 2:
            UIController.state.game.start()
            refresh()
        w.destroy()

    w = tk.Toplevel(UIController.window)
    w.resizable(False, False)
    w.protocol("WM_DELETE_WINDOW", restart)
    ls = tk.Listbox(w, height=10, listvariable=choices_var)
    ls.pack()

    tk.Button(w, text='OK', command=lambda: load_file(lst[ls.curselection()[0]]['file'])).pack()


def load_file(path: pathlib.Path):
    from ui_bridge.ui_controller import UIController
    UIController.saver = DataFile(path)
    UIController.state = UIController.saver.load()
    UIController.state.game.game_done = process_leaderboard
    refresh()


def load_ui():
    if Session.get_user() is None:
        return login_ui(load_flow)
    load_flow()


# login.py

import tkinter as tk
from tkinter import messagebox
from user_space.login import process_login, sign_up


def login_ui(handler):
    from ui_bridge.ui_controller import UIController

    w = tk.Toplevel(UIController.window)
    w.title('Login')

    tk.Label(w, text='Username: ').pack()
    username = tk.StringVar()
    tk.Entry(w, textvariable=username).pack()

    tk.Label(w, text='\nPassword: ').pack()
    password = tk.StringVar()
    tk.Entry(w, textvariable=password, show="*").pack()

    def success():
        handler()
        w.destroy()

    def error():
        messagebox.showerror(title='Error', message='Incorrect credentials')
        w.lift()

    def go_on():
        process_login(username.get(), password.get(), success, error)

    tk.Button(w, text='OK', command=go_on).pack()
    tk.Button(w, text='Sign Up', command=lambda: sign_up_ui(lambda: None)).pack()


def sign_up_ui(handler):
    from ui_bridge.ui_controller import UIController

    w = tk.Toplevel(UIController.window)
    w.title('Sign Up')

    tk.Label(w, text='New username: ').pack()
    username = tk.StringVar()
    tk.Entry(w, textvariable=username).pack()

    tk.Label(w, text='\nNew password: ').pack()
    password = tk.StringVar()
    tk.Entry(w, textvariable=password, show="*").pack()

    tk.Label(w, text='\nRepeat password: ').pack()
    second_password = tk.StringVar()
    tk.Entry(w, textvariable=second_password, show="*").pack()

    def success():
        handler()
        w.destroy()

    def error():
        messagebox.showerror(title='Error', message='Incorrect credentials')
        w.lift()

    def go_on():
        if len(username.get()) == 0 or len(password.get()) == 0:
            messagebox.showerror(title='Error', message='Credentials can\'t be empty')
            w.lift()
            return
        if second_password.get() != password.get():
            messagebox.showerror(title='Error', message='Passwords don\'t match')
            w.lift()
            return
        sign_up(username.get(), password.get(), success, error)

    tk.Button(w, text='OK', command=go_on).pack()


# resource_path.py

import sys
import os


def resource_path(relative_path):
    return relative_path


# save.py

from state_keeper.generate_new import gen_name
from ui_bridge.login import login_ui
from user_space.data_file import UserDataFile
from user_space.session import Session
from user_space.user_dir import prepare_personal_folder


def save_flow():
    from ui_bridge.ui_controller import UIController

    if UIController.saver is None:
        UIController.saver = UserDataFile(gen_name(UIController.state))
        UIController.state.game.on_change = UIController.saver.changed

    if UIController.state.game.state == 1:
        UIController.state.game.stop()

    UIController.saver.save(UIController.state)
    UIController.level.set(UIController.level.get())
    UIController.saver = None

    f = prepare_personal_folder()
    lst = []

    for fi in f.iterdir():
        lst.append({'file': fi, 'date': fi.stat().st_mtime})

    lst = sorted(lst, key=lambda i: i['date'], reverse=True)[10:]

    for fi in lst:
        fi['file'].unlink()


def save():
    if Session.get_user() is None:
        login_ui(save_flow)
        return
    save_flow()


# ui_controller.py

import tkinter as tk

from state_keeper.state import GameState
from ui_bridge.resource_path import resource_path
from user_space.data_file import DataFile


class UIController:
    level = tk.IntVar()
    state: GameState
    field: tk.Frame
    sign: tk.Label
    window: tk.Tk
    saver: DataFile = None
    menu = {}
    assets = [
        tk.PhotoImage(file=resource_path('./ui_bridge/assets/0.png')),
        tk.PhotoImage(file=resource_path('./ui_bridge/assets/1.png')),
        tk.PhotoImage(file=resource_path('./ui_bridge/assets/2.png')),
        tk.PhotoImage(file=resource_path('./ui_bridge/assets/3.png')),
        tk.PhotoImage(file=resource_path('./ui_bridge/assets/4.png')),
        tk.PhotoImage(file=resource_path('./ui_bridge/assets/5.png')),
        tk.PhotoImage(file=resource_path('./ui_bridge/assets/6.png')),
        tk.PhotoImage(file=resource_path('./ui_bridge/assets/7.png')),
        tk.PhotoImage(file=resource_path('./ui_bridge/assets/8.png')),
        tk.PhotoImage(file=resource_path('./ui_bridge/assets/mine.png')),
        tk.PhotoImage(file=resource_path('./ui_bridge/assets/flag.png')),
        tk.PhotoImage(file=resource_path('./ui_bridge/assets/question.png')),
    ]


# data_file.py

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


# encrypt.py

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


# file_proxy.py

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


# leaderboard.py

from tkinter import messagebox
import tkinter as tk

from topaz.entities.tiles import BombTile
from ui_bridge.login import login_ui
from user_space.local_leaderboard import LocalLeaderboard
from user_space.session import Session


def leaderboard_flow():
    from ui_bridge.ui_controller import UIController
    LocalLeaderboard.update_high_score(
        UIController.state.game.level,
        UIController.state.game.timer()
    )
    messagebox.showinfo('Leaderboard', 'Now your result is featured at the leaderboard')


def process_leaderboard():
    from ui_bridge.ui_controller import UIController

    if UIController.state is None:
        return

    pb = UIController.state.game.playboard()
    for row in range(UIController.state.game.level.level_sizes()[1]):
        for col in range(UIController.state.game.level.level_sizes()[0]):
            if isinstance(pb[row][col], BombTile) and pb[row][col].boomed:
                return

    ch = LocalLeaderboard.check_high_score(UIController.state.game.level)[0]
    if not (ch is True) and LocalLeaderboard.rate(
            UIController.state.game.level,
            UIController.state.game.timer()
    ) <= ch:
        return

    if not messagebox.askyesno(
            'New High Score',
            'New High Score! Would you like to feature yourself at the leaderboard?'
    ):
        return

    if Session.get_user() is None:
        login_ui(leaderboard_flow)
    else:
        leaderboard_flow()


def leaders_window():
    from ui_bridge.ui_controller import UIController

    w = tk.Toplevel(UIController.window)
    w.title('Leaderboard')

    h = LocalLeaderboard.get_high_score()

    for e in h:
        tk.Label(
            w, text=e['user'] + '   |   ' + str(e['level'] + 1) + ' lvl   |   ' + str(int(e['time'] // 60)).zfill(
                2) + ':' + str(int(e['time'] % 60)).zfill(2), width=50, font=16
        ).pack()

    if len(h) == 0:
        tk.Label(w, text='No records yet', width=50).pack()


# local_leaderboard.py

from state_keeper.state import GameState
from topaz.level import LevelDescriptor
from user_space.session import Session
from user_space.user_file import load_leaderboard_file, save_leaderboard_file


class LocalLeaderboard:
    @staticmethod
    def get_high_score():
        f = load_leaderboard_file()  # type: dict
        r = []

        for element in f['top']:
            lvl = LevelDescriptor(element['level'])
            r.append({
                'user': element['user'],
                'level': element['level'],
                'time': element['time'],
                'score': LocalLeaderboard.rate(lvl, element['time'])
            })
        r = sorted(r, key=lambda i: i['score'])[0:20]
        return r

    @staticmethod
    def check_high_score(level):
        c = LocalLeaderboard.get_high_score()
        return True, c
        cr = list(filter(lambda i: i['level'] == level, c))
        if len(cr) == 0:
            return True, c
        return cr[-1], c

    @staticmethod
    def rate(level, time):
        return (time / (level.level_sizes()[0] * level.level_sizes()[1]) / (level.level + 1)) // 1

    @staticmethod
    def update_high_score(level, time):
        c, m = LocalLeaderboard.check_high_score(level)
        rate = LocalLeaderboard.rate(level, time)
        if not isinstance(c, bool) and c >= rate:
            return

        m.insert(0, {
            'user': Session.get_user().username,
            'level': level.level,
            'time': time,
            'score': rate,
        })

        save_leaderboard_file({'top': m})


# login.py

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


# session.py

from user_space.user import User


class Session:
    __user: User = None
    handlers = []

    @staticmethod
    def apply_user(user):
        Session.__user = user
        for handler in Session.handlers:
            handler()

    @staticmethod
    def log_out():
        return

    @staticmethod
    def get_user():
        return Session.__user


# user.py

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password


# user_dir.py

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


# user_file.py

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


