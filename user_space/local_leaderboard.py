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
