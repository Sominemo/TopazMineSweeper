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
