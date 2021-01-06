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
