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
