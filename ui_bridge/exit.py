from tkinter import messagebox


def wanna_exit(window):
    from ui_bridge.ui_controller import UIController

    if UIController.state is None or messagebox.askokcancel('Exit', 'Are you sure you want to exit?'):
        window.destroy()
