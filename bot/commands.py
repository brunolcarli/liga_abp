from bot.db_handler import ABP_DB, db_connection
from bot.util import badge_to_emoji, parse_id
from bot.models import Trainer, Member


def get_member(member):
    db = ABP_DB(db_connection())
    if isinstance(member, str):
        response = db.read_trainer_data(parse_id(member))
        return response

    response = db.read_trainer_data(parse_id(str(member.id)))
    return response


def add_badge(user, member_id, badge):
    if badge.lower() not in badge_to_emoji.keys():
        raise Exception('INVALID BADGE')

    user = Trainer(*get_member(user)[0])
    if user.role not in ('admin', 'gym_leader'):
        raise Exception('UNAUTHORIZED')
    member_id = parse_id(str(member_id))

    trainer = Trainer(*get_member(parse_id(str(member_id))[0]))
    trainer.add_badge(badge)
    return trainer


def register(user, trainer):
    user = Trainer(*get_member(user)[0])
    if user.role not in ('admin', 'gym_leader'):
        raise Exception('UNAUTHORIZED')
    
    _id = parse_id(trainer)
    db = ABP_DB(db_connection())
    member = db.get_member(_id)
    if not member:
        raise Exception('MEMBER NOT FOUND')
    
    member = Member(*member[0])

    return db.register_trainer(member.member_id, member.username)

