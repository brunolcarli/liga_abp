from ast import literal_eval
from base64 import b64decode, b64encode
from bot.util import badge_to_emoji


class Trainer:
    def __init__(self, name, role, games, wins, losses, badges, member_id):
        self.name = name
        self.role = role
        self.games = games
        self.wins = wins
        self.losses = losses
        self.badges = literal_eval(b64decode(badges).decode('utf-8'))
        self.member_id = member_id

    def __repr__(self):
        return f'{self.name} {self.id}'

    def add_badge(self, badge):
        if badge in self.badges:
            return self.badges
        self.badges.append(badge)
        return self.badges

    def encode_badges(self):
        return b64encode(str(self.badges).encode('utf8')).decode('utf-8')