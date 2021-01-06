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
