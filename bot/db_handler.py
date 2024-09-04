import logging
import mysql.connector
from mysql.connector import Error
from config.settings import MYSQL_CONFIG


logger = logging.getLogger(__name__)


def db_connection(
    host_name=MYSQL_CONFIG['MYSQL_HOST'],
    user_name=MYSQL_CONFIG['MYSQL_USER'],
    port=MYSQL_CONFIG['MYSQL_PORT'],
    user_password=MYSQL_CONFIG['MYSQL_PASSWORD'],
    db=MYSQL_CONFIG['MYSQL_DATABASE']
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
            db=db
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

    def read_trainer_data(self, _id):
        query = f'''
            SELECT Trainer.username, role, games, wins, losses, badges, Trainer.member_id
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
            logger.info('Member already registered')
            return result
        
        new_member = f'''
            INSERT INTO Member (discord_id, member_id, username, role)
            VALUES ({str(member_id)}, {str(member_id)}, "{str(username)}", "trainer")
        '''
        print(new_member)
        try:
            execute_query(self.connection, new_member)
            result = read_query(self.connection, query)
        except:
            logger.info('Failed to register new member %s', f'{username}:{member_id}')
        else:
            logger.info('Registered new member %s', f'{username}:{member_id}')

        return result

