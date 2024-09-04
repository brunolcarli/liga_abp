from bot.db_handler import ABP_DB, db_connection
from bot.util import badge_to_emoji
from bot.models import Trainer


def get_member(member):
    db = ABP_DB(db_connection())
    if isinstance(member, str):
        return db.read_trainer_data(member)
    return db.read_trainer_data(str(member.id))


def add_badge(user, member_id, badge):
    if badge.lower() not in badge_to_emoji.keys():
        raise Exception('INVALID BADGE')

    user = Trainer(*get_member(user)[0])
    if user.role not in ('admin', 'gym_leader'):
        raise Exception('UNAUTHORIZED')
    
    trainer = Trainer(*get_member(member_id)[0])
    trainer.add_badge(badge)
    