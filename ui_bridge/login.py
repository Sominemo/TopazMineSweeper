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
