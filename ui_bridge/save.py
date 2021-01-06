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

