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
