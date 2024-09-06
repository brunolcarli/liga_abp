from bot.db_handler import ABP_DB, db_connection, execute_query
from bot.util import badge_to_emoji, parse_id
from bot.models import Trainer, Member


def get_member(member):
    db = ABP_DB(db_connection())

    response = db.read_trainer_data(member)
    db.connection.close()
    return response


def add_badge(user, member_id, badge):
    if badge.lower() not in badge_to_emoji.keys():
        raise Exception('INVALID BADGE')
    
    db = ABP_DB(db_connection())
    data = db.read_trainer_data(user)[0]
    user = Trainer(*data)

    if user.role not in ('admin', 'gym_leader'):
        raise Exception('UNAUTHORIZED')

    data2 = db.read_trainer_data(member_id)[0]
    trainer = Trainer(*data2)
    trainer.add_badge(badge)

    query = f'''
            UPDATE Trainer
            SET badges = "{trainer.encode_badges()}"
            WHERE member_id = {str(member_id)}
        '''
    execute_query(db.connection, query)
    return trainer


def register(user, trainer):
    db = ABP_DB(db_connection())
    user = Trainer(*db.read_trainer_data(user.id)[0])
    if user.role not in ('admin', 'gym_leader'):
        raise Exception('UNAUTHORIZED')
    
    member = db.get_member(trainer)
    if not member:
        raise Exception('MEMBER NOT FOUND')
    
    member = Member(*member[0])

    return db.register_trainer(member.member_id, member.username)


def list_leagues():
    db = ABP_DB(db_connection())
    return db.leagues()

def new_league(season):
    db = ABP_DB(db_connection())
    return db.create_league(season)

def get_current_league():
    db = ABP_DB(db_connection())
    return db.current_league()
