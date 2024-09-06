import logging
import mysql.connector
from mysql.connector import Error
from config.settings import MYSQL_CONFIG
from base64 import b64encode, b64decode
from ast import literal_eval


logger = logging.getLogger(__name__)


def db_connection(
    host_name=MYSQL_CONFIG['MYSQL_HOST'],
    user_name=MYSQL_CONFIG['MYSQL_USER'],
    port=MYSQL_CONFIG['MYSQL_PORT'],
    user_password=MYSQL_CONFIG['MYSQL_PASSWORD'],
    db=MYSQL_CONFIG['MYSQL_DATABASE'],
    ):
    """
    Connects with database.
    """
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            port=port,
            db=db,
            auth_plugin='mysql_native_password'
        )
    except Error as err:
        logger.error('Error: %s', str(err))

    return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
    except Error as err:
        logger.error('Error: %s', str(err))


def read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        logger.error('Error: %s', str(err))


class ABP_DB:
    def __init__(self, connection):
        self.connection = connection


    def get_member(self, _id):
        query = f'''
            SELECT member_id, username, role from Member
            WHERE member_id = "{_id}"
        '''
        result = read_query(self.connection, query)
        return result

    def get_trainer(self, _id):
        query = f'''
            SELECT username, games, wins, losses, badges
            FROM Trainer
            WHERE member_id = {str(_id)}
        '''
        result = read_query(self.connection, query)
        return result

    def read_trainer_data(self, _id):
        query = f'''
            SELECT Trainer.username, role, games, wins, losses, badges, Trainer.member_id, current_league, leagues_participated, leagues_win
            FROM Member
            INNER JOIN Trainer
            WHERE Member.member_id = Trainer.member_id
            AND Member.member_id = {_id}
        '''
        result = read_query(self.connection, query)
        return result

    def get_or_create(self, member_id, username):
        query = f'''
            SELECT * FROM Member WHERE member_id = {member_id}
        '''
        result = read_query(self.connection, query)
        if result:
            logger.debug('Member already registered')
            return result
        
        new_member = f'''
            INSERT INTO Member (discord_id, member_id, username, role)
            VALUES ({str(member_id)}, {str(member_id)}, "{str(username)}", "trainer")
        '''

        try:
            execute_query(self.connection, new_member)
            result = read_query(self.connection, query)
        except:
            logger.info('Failed to register new member %s', f'{username}:{member_id}')
        else:
            logger.info('Registered new member %s', f'{username}:{member_id}')

        return result

    def register_trainer(self, member_id, username):
        new_member = f'''
            INSERT INTO Trainer (discord_id, member_id, username, games, wins, losses, badges)
            VALUES ({str(member_id)}, {str(member_id)}, "{username}", 0, 0, 0, "W10=")
        '''

        try:
            execute_query(self.connection, new_member)
        except:
            logger.info('Failed to register new trainer %s', f'{username}:{member_id}')
        else:
            logger.info('Registered new trainer %s', f'{username}:{member_id}')

        return self.read_trainer_data(member_id)

    def update_trainer_badges(self, member_id, b64badge_string):
        
        query = f'''
            UPDATE Trainer
            SET badges = {b64badge_string}
            WHERE member_id = {str(member_id)}
        '''
        
        try:
            result = execute_query(self.connection, query)
            logger.info('Added badge to %s', f'{member_id}')
            return result
        except:
            logger.info('Failed to add badge on trainer %s', f'{member_id}')
            return False

    def top_trainers(self):
        query = '''
            SELECT Trainer.username, role, games, wins, losses, badges, Trainer.member_id, current_league, leagues_participated, leagues_win
            FROM Member
            INNER JOIN Trainer
            WHERE Member.member_id = Trainer.member_id
            ORDER BY wins
            LIMIT 8;
        '''
        result = read_query(self.connection, query)
        return result

    def leagues(self):
        query = '''
            SELECT * FROM Leagues;
        '''
        return read_query(self.connection, query)

    def create_league(self, season):
        query = f'''
            INSERT INTO Leagues (season)
            VALUES ('{season}');
        '''
        try:
            execute_query(self.connection, query)
        except:
            logger.info('Failed to register new league %s', f'{season}')
        else:
            logger.info('Registered new league %s', f'{season}')

        return read_query(self.connection, f"SELECT * FROM Leagues WHERE season = {season};")

    def current_league(self):
        query = '''
            SELECT * FROM Leagues
            WHERE winner IS NULL;
        '''
        return read_query(self.connection, query)

    def join_league(self, season, member_id):
        leagues_participated = read_query(self.connection, f"SELECT leagues_participated from Trainer WHERE member_id = {str(member_id)};")[0][0]
        self.connection.reset_session()
        if leagues_participated == b'0' or leagues_participated == '0' or not leagues_participated:
            leagues_participated = 'W10='
        
        leagues_participated = literal_eval(b64decode(leagues_participated).decode('utf-8'))
        if int(season) in leagues_participated:
            raise Exception('ALREADY REGISTERED IN THIS LEAGUE')
        
        leagues_participated.append(int(season))
        leagues_participated = b64encode(str(leagues_participated).encode('utf-8')).decode('utf-8')
        query = f'''
            UPDATE Trainer
            SET current_league = "{season}",
                leagues_participated = "{leagues_participated}"
            WHERE member_id = {str(member_id)};
        '''
        execute_query(self.connection, query)
        self.connection.reset_session()

        query = f'''
            UPDATE Leagues
            SET participants = participants + 1
            WHERE season = {str(season)};
        '''
        execute_query(self.connection, query)
        self.connection.reset_session()

        return self.read_trainer_data(member_id)

    def report(self, leader_id, trainer_id, result):
        # update trainer table
        result = 0 if result == 'v' else 1
        query = f'''
            UPDATE Trainer
            SET wins = wins + {result},
                losses = losses + {int(not result)},
                games = games + 1
            WHERE member_id = {str(trainer_id)};
        '''
        execute_query(self.connection, query)
        self.connection.reset_session()

        # update leader table
        result = 1 if result == 'v' else 0
        query = f'''
            UPDATE Leader
            SET wins = wins + {result},
                losses = losses + {int(not result)},
                games = games + 1
            WHERE member_id = {str(trainer_id)};
        '''
        execute_query(self.connection, query)
        self.connection.reset_session()

        # update leagues table
        query = f'''
            UPDATE Leagues
            SET games = games + 1
            WHERE season = (
                SELECT current_league
                FROM Trainer
                WHERE member_id = {str(trainer_id)}
            );
        '''
        execute_query(self.connection, query)
        self.connection.reset_session()

        return self.read_trainer_data(trainer_id)
    