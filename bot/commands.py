from bot.db_handler import ABP_DB, db_connection

def get_member(member):
    # print(member.id)
    print(dir(member))

    db = ABP_DB(db_connection())
    return db.read_trainer_data(str(member.id))
