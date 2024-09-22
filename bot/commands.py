from bot.db_handler import ABP_DB, db_connection, execute_query
from bot.util import badge_to_emoji
from bot.models import Trainer, Member, GymLeader


class BotCommands:
    badge_to_emoji = {
        'ice': ':snowflake:',
        'bug': ':beetle:',
        'grass': ':seedling:',
        'water': ':droplet:',
        'normal': ':white_square_button:',
        'psychic': ':eye:',
        'ghost': ':badge_ghost:',
        'electric': ':zap:'
    }


    valid_commands = {
        'version', 'v',  # VERSION
        'user', 'usr', 'card', 'trainer_card', 'trainer',  # TRAINER INFO
        'add_badge', 'give',  # ADD BADGE
        'ranking', 'rank', 'top',  # RANKING
        'leagues', 'ls',  # LIST LEAGUES
        'league', 'lg',  # CURRENT LEAGUE INFO
        'leaders', 'gyms', 'gym_leaders', 'gls', 'gl',  # GYM LEADERS LISTAGE
        'admins', 'adms',  # LIST ADMINS
        'report', 'rp', 'res',  # GAME REPORT
        'register', 'rg',  # REGISTER TRAINER,
        'create_league', 'new_league', 'nl', 'cl',  ## CREATE NEW LEAGUE
        'join_league', 'jl',  ## Register Trainer into a league
        'create_leader', 'make_leader', 'mkleader',  # REGISTER GYM LEADER
        'close_league', 'mkchampion', 'mkwinner', 'end_season', 'clg',  # CLOSE LEAGUE
        'help', 'h'  # HELP COMMAND
    }



    command_help = {
        'version': 'Exibe a versão do bot/serviço! | alias: [v] | \nEx:\n\t `>>version`',
        'trainer': 'Exibe informações do treinador da liga! |alias: [user, usr, trainer_card, card] | Parâmetros: [@usuario] | \nEx:\n\t `>>trainer @beelzebruno`',
        'give': 'Confere uma insígnia à um Treinador | alias: [add_badge] | Parâmetros: [@usuario, nome da insígnia] |\n Ex:\n\t `>>give @beelzebruno ice`\nPRIVILÉGIOS: Apenas membros `admin` e `gym_leader` podem usar este recurso!',
        'ranking': 'Lista os top8 jogadores baseado n número de vitórias | alias: [rank, top] | \nEx:\n\t `>>top`',
        'leaders': 'Lista os líderes de ginásios da liga | alias: [gyms, gym_leaders, gl, gls] | \nEx:\n\t `>>gl`',
        'admins': 'Lista os organizadores da liga | alias: [adms] | \nEx:\n\t `>>adms`',
        'register': 'Registra um treinador| alias: [rg] | Parâmetros: [@usuario] | \nEx:\n\t `>>rg @beelebruno` \nPRIVILÉGIOS: Apenas membros `admin` e `gym_leader` podem usar este recurso!',
        'report': 'Registra o resultado de uma partida entre um líder de ginásio e um treinador | alias: [rp, res] | Parâmetros: [@usuario, resultado líder (v/f)] | \nEx: Líder reporta vitória contra  beelzebruno \n\t `>>res @beelebruno` v \nEx: Líder reporta derrota contra  beelzebruno\n\t `>>res @beelebruno` f \nPRIVILÉGIOS: Apenas membros `admin` e `gym_leader` podem usar este recurso!',
        'leagues': 'Lista as ligas cadastradas | alias: [ls] | \nEx: \n\t `>>ls`',
        'league': 'Informações da liga atual em andamento | alias: [lg] | \nEx: \n\t `>>lg`',
        'create_league': 'Cadastra uma nova liga| alias: [new_league, nl, cl] |  Parâmetros: [season] | \nEx: \n\t `>>create_league 2024`',
        'join_league': 'Cadastra um treinador em uma liga| alias: [join_league, jl] |  Parâmetros: [@membro, season] | \nEx: \n\t `>>join_league @beelzebruno 2024`',
        'create_leader': 'Cadastra um treinador em uma liga| alias: [create_leade, make_leader, mkleader] |  Parâmetros: [@membro, tipo, season] | \nEx: \n\t `>>mkleader @beelzebruno ice 2024`',
        'close_league': 'Fecha uma liga declarando o campeão| alias: [mkchampion, mkwinner, end_season, clg] |  Parâmetros: [@membro, season] | \nEx: \n\t `>>close_league @beelzebruno 2024`',
    }
    command_help['help'] = 'Comandos disponíveis: ' + '\n'.join(f'- `{cmd}` : {description}' for cmd, description in command_help.items())

    @staticmethod
    def get_leader(member):
        db = ABP_DB(db_connection())

        response = db.get_leaders()
        db.connection.close()
        leader = None
        for i in response:
            if str(member) == str(i[4]):
                leader = i
                break
        return leader

    @staticmethod
    def get_member(member):
        db = ABP_DB(db_connection())

        response = db.read_trainer_data(member)
        db.connection.close()
        return response

    @staticmethod
    def add_badge(user, member_id, badge):
        if badge.lower() not in badge_to_emoji.keys():
            raise Exception('INVALID BADGE')
        
        db = ABP_DB(db_connection())
        data = BotCommands.get_leader(user)
        user = GymLeader(*data)

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

    @staticmethod
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

    @staticmethod
    def list_leagues():
        db = ABP_DB(db_connection())
        return db.leagues()

    @staticmethod
    def new_league(season):
        db = ABP_DB(db_connection())
        return db.create_league(season)

    @staticmethod
    def get_current_league():
        db = ABP_DB(db_connection())
        return db.current_league()

    @staticmethod
    def register_trainer_to_league(season, member_id):
        db = ABP_DB(db_connection())
        return db.join_league(season, member_id)

    @staticmethod
    def battle_report(leader_id, trainer_id, result):
        db = ABP_DB(db_connection())
        return db.report(leader_id, trainer_id, result)

    @staticmethod
    def list_admins():
        db = ABP_DB(db_connection())
        return db.get_admins()

    @staticmethod
    def register_leader(member_id, username, _type, league):
        db = ABP_DB(db_connection())
        return db.create_leader(member_id, username, _type, league)

    @staticmethod
    def get_leaders():
        db = ABP_DB(db_connection())
        return db.get_leaders()

    @staticmethod
    def close_league(winner_id, winner_name, season):
        db = ABP_DB(db_connection())
        return db.close_league(winner_id, winner_name, season)

