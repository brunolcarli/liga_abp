import re

def parse_id(_id):
    """
    Parses <@1234567> kind of ids to numeric only 1234567
    """    
    _id = str(_id)
    if '@' in _id:
        return str(_id.split('@')[1][:-1])
    return _id


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
    'report', 'rp', 'res'  # GAME REPORT
    'register', 'rg',  # REGISTER TRAINER
    'help', 'h'  # HELP COMMAND
}



command_help = {
    'version': 'Exibe a versão do bot/serviço! | alias: [v] | \nEx:\n\t `>>version`',
    'trainer': 'Exibe informaç˜es do treinador da liga! |alias: [user, usr, trainer_card, card] | Parâmetros: [@usuario] | \nEx:\n\t `>>trainer @beelzebruno`',
    'give': 'Confere uma insígnia à um Treinador | alias: [add_badge] | Parâmetros: [@usuario, nome da insígnia] |\n Ex:\n\t `>>give @beelzebruno ice`\nPRIVILÉGIOS: Apenas membros `admin` e `gym_leader` podem usar este recurso!',
    'ranking': 'Lista os top8 jogadores baseado n número de vitórias | alias: [rank, top] | \nEx:\n\t `>>vtop`',
    'leaders': 'Lista os líderes de ginásios da liga | alias: [gyms, gym_leaders, gl, gls] | \nEx:\n\t `>>gl`',
    'admins': 'Lista os organizadores da liga | alias: [adms] | \nEx:\n\t `>>adms`',
    'register': 'Registra um treinador| alias: [rg] | Parâmetros: [@usuario] | \nEx:\n\t `>>rg @beelebruno` \nPRIVILÉGIOS: Apenas membros `admin` e `gym_leader` podem usar este recurso!',
    'report': 'Registra o resultado de uma partida entre um líder de ginásio e um treinador | alias: [rp, res] | Parâmetros: [@usuario, resultado líder (v/f)] | \nEx: Líder reporta vitória contra  beelzebruno \n\t `>>res @beelebruno` v \nEx: Líder reporta derrota contra  beelzebruno\n\t `>>res @beelebruno` f \nPRIVILÉGIOS: Apenas membros `admin` e `gym_leader` podem usar este recurso!',
    'leagues': 'Lista as ligas cadastradas | alias: [ls] | \nEx: \n\t `>>ls`',
    'leagues': 'Informações da iga atual em andamento | alias: [lg] | \nEx: \n\t `>>lg`',
}
command_help['help'] = 'Comandos disponíveis: ' + '\n'.join(f'- `{cmd}` : {description}' for cmd, description in command_help.items())
