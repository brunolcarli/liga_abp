from ast import literal_eval



class Member:
    def __init__(self, member_id, username, role):
        self.member_id = member_id
        self.username = username
        self.role = role


class Trainer:
    def __init__(self, name, role, games, wins, losses, badges, member_id, current_league, leagues_participated, leagues_win):
        self.name = name
        self.role = role
        self.games = games
        self.wins = wins
        self.losses = losses
        self.badges = literal_eval(badges.decode())
        self.member_id = member_id
        self.current_league = current_league
        self.leagues_participated = literal_eval(leagues_participated.decode())
        self.leagues_win = leagues_win
        
    def __repr__(self):
        return f'{self.name} {self.member_id}'

    def add_badge(self, badge):
        if badge in self.badges:
            return self.badges
        self.badges.append(badge)
        return self.badges

    def encode_badges(self):
        return str(self.badges)


class GymLeader:
    def __init__(self, username, games, wins, losses, member_id, league, type):
        self.name = username
        self.games = games
        self.wins = wins
        self.losses = losses
        self.member_id = member_id
        self.league = league
        self.type = type
