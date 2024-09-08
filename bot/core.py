import discord
import logging
from ast import literal_eval
from base64 import b64decode
from config.settings import __version__
from discord.ext import commands
from bot.commands import get_member, add_badge, register, list_leagues, new_league, get_current_league, register_trainer_to_league, battle_report, list_admins, register_leader, get_leaders, close_league
from bot.util import badge_to_emoji, valid_commands, command_help, parse_id
from bot.models import Trainer, GymLeader
from bot.db_handler import ABP_DB, db_connection


logger = logging.getLogger(__name__)


class MyClient(discord.Client):
    db = db = ABP_DB(db_connection())

    async def on_ready(self):
        logger.info(f'Logged on as {self.user}!')

    async def on_message(self, message):
        logger.info(f'Message from {message.author}: {message.content}')

        # Auto create new member if not exists
        MyClient.db.get_or_create(parse_id(message.author.id), message.author.name)

        # ++++++++++++++
        # BOT COMMAND
        # ++++++++++++++
        if message.content.startswith('>>'):
            user_input = message.content[2:].strip().split(' ')
            cmd = user_input[0].lower()
            if cmd not in valid_commands:
                return await message.channel.send('Comando não reconhecido!\nEscreva `>>help` para listar os comandos disponíveis!')

            #################
            # help
            #################
            if cmd in ('help', 'h'):
                return await message.channel.send(command_help['help'])

            #################
            # VERSION
            #################
            if user_input[0].lower() in ('version', 'v'):
                return await message.channel.send(__version__)
            
            #################
            # TRAINER CARD
            #################
            if user_input[0].lower() in ('user', 'usr', 'card', 'trainer_card', 'trainer'):
                if len(user_input) < 2:
                    return await message.channel.send('Parâmetro ausente: `@membro`')
    
                result = MyClient.db.read_trainer_data(parse_id(user_input[1]))

                if not result:
                    return await message.channel('Não encontrado')
                trainer = Trainer(*result[0])
                embed = discord.Embed(color=0x1E1E1E, type='rich')
                target = message.mentions
                embed.set_thumbnail(url=target[0].avatar)

                embed.add_field(name='Name', value=trainer.name, inline=True)
                embed.add_field(name='Role', value=trainer.role, inline=False)
                embed.add_field(name='Games', value=trainer.games, inline=True)
                embed.add_field(name='Wins', value=trainer.wins, inline=True)
                embed.add_field(name='Losses', value=trainer.losses, inline=True)
                embed.add_field(name='Liga atual', value=trainer.current_league, inline=False)
                embed.add_field(name='Ligas vencidas', value=trainer.leagues_win, inline=True)
                embed.add_field(name='Badges', value='', inline=False)
                
                for badge in trainer.badges:
                    embed.add_field(name=badge.title(), value=badge_to_emoji[badge], inline=True)

                embed.add_field(name='Ligas jogadas', value=' - '.join(str(league) for league in trainer.leagues_participated), inline=False)

                return await message.channel.send('Trainer', embed=embed)
            
            #################
            # ADD BADGE
            #################
            if cmd in ('add_badge', 'give'):
                if len(user_input) < 3:
                    return await message.channel.send('Parâmetro(s) ausente(s): `@membro`, nome da insignia')
                badge = user_input[-1]
                target = message.mentions
                if not target:
                    return await message.channel.send('Parâmetro(s) ausente(s): `@membro`, nome da insignia')
                else:
                    target = target[0]

                try:
                    trainer = add_badge(message.author.id, target.id, user_input[2])
                except Exception as err:
                    error_message = str(err)
                    if error_message == 'INVALID BADGE':
                        return await message.channel.send(f'Insígnia inválida, opções válida: {", ".join(f"`{b}`" for b in badge_to_emoji.keys())}!')
                    if error_message == 'UNAUTHORIZED':
                        return await message.channel.send('Não autorizado à realizar esta ação!')
                else:
                    return await message.channel.send(f'{trainer.name} recebeu a insígnia {badge_to_emoji[badge]}')

            #################
            # REGISTER
            #################
            if cmd in ('register', 'rg'):
                if len(user_input) < 2:
                    return await message.channel.send('Parâmetro(s) ausente(s): `@membro`')

                target = message.mentions
                if not target:
                    return await message.channel.send('Parâmetro(s) ausente(s): `@membro`, nome da insignia')
                else:
                    target = target[0]

                result = register(message.author, target.id)

                trainer = Trainer(*result[0])
                embed = discord.Embed(color=0x1E1E1E, type='rich')

                embed = discord.Embed(color=0x1E1E1E, type='rich')
                embed.set_thumbnail(url=target.avatar)
                embed.add_field(name='Name', value=trainer.name, inline=True)
                embed.add_field(name='Role', value=trainer.role, inline=False)
                embed.add_field(name='Games', value=trainer.games, inline=True)
                embed.add_field(name='Wins', value=trainer.wins, inline=True)
                embed.add_field(name='Losses', value=trainer.losses, inline=True)
                embed.add_field(name='Liga atual', value=trainer.current_league, inline=False)
                embed.add_field(name='Ligas vencidas', value=trainer.leagues_win, inline=True)
                embed.add_field(name='Badges', value='', inline=False)
                
                for badge in trainer.badges:
                    embed.add_field(name=badge.title(), value=badge_to_emoji[badge], inline=True)

                embed.add_field(name='Ligas jogadas', value=' - '.join(str(league) for league in trainer.leagues_participated), inline=False)

                return await message.channel.send(trainer.name, embed=embed)

            #################
            # REPORT
            #################
            if cmd in ('report', 'rp', 'res'):
                if len(user_input) < 3:
                    return await message.channel.send('Parâmetro(s) ausente(s): `@membro` [v/f]')
                condition = user_input[-1].lower()
                if condition not in 'vf':
                    return await message.channel.send('Parâmetro(s) incorreto: `v` se o lider venceu, `f` se o treinador venceu!')
                
                target = message.mentions
                if not target:
                    return await message.channel.send('Parâmetro(s) ausente(s): `@membro`, nome da insignia')
                else:
                    target = target[0]

                leader = Trainer(*get_member(message.author.id)[0])
                if leader.role != 'gym_leader':
                    return await message.channel.send('Não autorizado')
                
                result = battle_report(leader.member_id, target.id, condition)

                trainer = Trainer(*result[0])
                embed = discord.Embed(color=0x1E1E1E, type='rich')
                embed.set_thumbnail(url=target.avatar)
                embed.add_field(name='Name', value=trainer.name, inline=True)
                embed.add_field(name='Role', value=trainer.role, inline=False)
                embed.add_field(name='Games', value=trainer.games, inline=True)
                embed.add_field(name='Wins', value=trainer.wins, inline=True)
                embed.add_field(name='Losses', value=trainer.losses, inline=True)
                embed.add_field(name='Liga atual', value=trainer.current_league, inline=False)
                embed.add_field(name='Ligas vencidas', value=trainer.leagues_win, inline=True)
                embed.add_field(name='Badges', value='', inline=False)
                
                for badge in trainer.badges:
                    embed.add_field(name=badge.title(), value=badge_to_emoji[badge], inline=True)

                embed.add_field(name='Ligas jogadas', value=' - '.join(str(league) for league in trainer.leagues_participated), inline=False)
                
                return await message.channel.send(f'Relatório registrado.\nPerfil do desafiante:', embed=embed)

            #################
            # Ranking
            #################
            if cmd in ('ranking', 'rank', 'top'):
                trainers = MyClient.db.top_trainers()
                embed = discord.Embed(color=0x1E1E1E, type='rich')

                for data in trainers[::-1]:
                    trainer = Trainer(*data)
                    if trainer.role != 'trainer':
                        continue
                    embed.add_field(name=trainer.name, value=f'Games: {trainer.games} ({trainer.wins}/{trainer.losses} | **Badges**: {len(trainer.badges)})', inline=False)
                return await message.channel.send('Top 8 treinadres da liga', embed=embed)

            #################
            # Listar Ligas
            #################
            if cmd in ('leagues', 'ls'):
                data = list_leagues()
                if not data:
                    return await message.channel.send('Não há ligas cadastradas no momento')
                
                embed = discord.Embed(color=0x1E1E1E, type='rich')
                for league in data:
                    season, winner, games, participants = league
                    if winner is None:
                        winner = ':grey_question:'
                    embed.add_field(name='Season', value=season, inline=False)
                    embed.add_field(name='Partidas', value=games, inline=True)
                    embed.add_field(name='Participantes', value=participants, inline=True)
                    embed.add_field(name='Campeão', value=winner, inline=True)
                
                return await message.channel.send('Ligas:', embed=embed)

            #################
            # Criar Liga
            #################
            if cmd in ('create_league', 'new_league', 'nl', 'cl'):
                user = Trainer(*get_member(message.author.id)[0])
                if user.role != 'admin':
                    return await message.channel.send('Não autorizado!')

                if len(user_input) < 2:
                    return await message.channel.send('Parâmetro(s) ausente(s): season')

                season = user_input[-1]
                league = new_league(season)[-1]

                season, winner, games, participants = league
                if winner is None:
                    winner = ':grey_question:'
                embed = discord.Embed(color=0x1E1E1E, type='rich')
                embed.add_field(name='Season', value=season, inline=False)
                embed.add_field(name='Partidas', value=games, inline=True)
                embed.add_field(name='Participantes', value=participants, inline=True)
                embed.add_field(name='Campeão', value=winner, inline=True)

                return await message.channel.send('Liga registrada', embed=embed)

            #################
            # Liga atual
            #################
            if cmd in ('league', 'lg'):
                data = get_current_league()
                if not data:
                    return await message.channel.send('Nenhuma liga em andamento atualmente!')
                
                season, winner, games, participants = data[-1]
                if winner is None:
                    winner = ':grey_question:'

                embed = discord.Embed(color=0x1E1E1E, type='rich')
                embed.add_field(name='Season', value=season, inline=False)
                embed.add_field(name='Partidas', value=games, inline=True)
                embed.add_field(name='Participantes', value=participants, inline=True)
                embed.add_field(name='Campeão', value=winner, inline=True)
                
                return await message.channel.send('Liga atual', embed=embed)

            #################
            # Registrar treinador em uma liga
            #################
            if cmd in ('join_league', 'jl'):
                user = Trainer(*get_member(message.author.id)[0])
                if user.role != 'admin':
                    return await message.channel.send('Não autorizado!')

                if len(user_input) < 3:
                    return await message.channel.send('Parâmetro(s) ausente(s): `@member`, `season`')

                target = message.mentions
                if not target:
                    return await message.channel.send('Parâmetro(s) ausente(s): `@membro`, season')
                else:
                    target = target[0]
                season = user_input[-1]
                
                try:
                    result = register_trainer_to_league(season, target.id)
                except Exception as err:
                    return await message.channel.send(str(err))
                
                trainer = Trainer(*result[0])

                embed = discord.Embed(color=0x1E1E1E, type='rich')
                embed.set_thumbnail(url=target.avatar)
                embed.add_field(name='Name', value=trainer.name, inline=True)
                embed.add_field(name='Role', value=trainer.role, inline=False)
                embed.add_field(name='Games', value=trainer.games, inline=True)
                embed.add_field(name='Wins', value=trainer.wins, inline=True)
                embed.add_field(name='Losses', value=trainer.losses, inline=True)
                embed.add_field(name='Liga atual', value=trainer.current_league, inline=False)
                embed.add_field(name='Ligas vencidas', value=trainer.leagues_win, inline=True)
                embed.add_field(name='Badges', value='', inline=False)
                
                for badge in trainer.badges:
                    embed.add_field(name=badge.title(), value=badge_to_emoji[badge], inline=True)

                embed.add_field(name='Ligas jogadas', value=' - '.join(str(league) for league in trainer.leagues_participated), inline=False)

                return await message.channel.send('Treinadoor registrado', embed=embed)

            #################
            # Listar admins
            #################
            if cmd in ('admins', 'adms'):
                admins = list_admins()
                if not admins:
                    return await message.channel.send('Nã há organizadores registrados')

                embed = discord.Embed(color=0x1E1E1E, type='rich')
                for admin in admins:
                    embed.add_field(name='Nome', value=admin[0], inline=False)
                return await message.channel.send('Lista de organizadores', embed=embed)
        
            #################
            # Registrar lider
            #################
            if cmd in ('create_leader', 'make_leader', 'mkleader'):
                if len(user_input) < 4:
                        return await message.channel.send('Parâmetro(s) ausente(s): `@membro`, `tipo`, `season`')
                
                user = Trainer(*get_member(message.author.id)[0])

                if user.role != 'admin':
                    return await message.channel.send('Não autorizado!')
                
                target = message.mentions
                if not target:
                    return await message.channel.send('Parâmetro(s) ausente(s): `@membro`')
                else:
                    target = target[0]
                leader = GymLeader(*register_leader(target.id, target.name, user_input[-2], user_input[-1])[0])

                embed = discord.Embed(color=0x1E1E1E, type='rich')
                embed.set_thumbnail(url=target.avatar)
                embed.add_field(name='Name', value=leader.name, inline=True)
                embed.add_field(name='Liga', value=leader.league, inline=False)
                embed.add_field(name='Partidas', value=leader.games, inline=True)
                embed.add_field(name='Score', value=f'({leader.wins}/{leader.losses})', inline=True)
                embed.add_field(name='Tipo', value=f'{badge_to_emoji[leader.type]} {leader.type}', inline=False)
                
                return await message.channel.send('', embed=embed)

            #################
            # Registrar lider
            #################
            if cmd in ('leaders', 'gyms', 'gym_leaders', 'gls', 'gl'):
                leaders = get_leaders()
                if not leaders:
                    return await message.channel.send('Nenhum líder cadastrado')
            
                embed = discord.Embed(color=0x1E1E1E, type='rich')
                for record in leaders:
                    leader = GymLeader(*record)
                    embed.add_field(name='Name', value=f'({leader.league}) {leader.name} {badge_to_emoji[leader.type]} {leader.type.title()}', inline=True)
                    embed.add_field(name='Games', value=leader.games, inline=True)
                    embed.add_field(name='Score', value=f'({leader.wins}/{leader.losses})', inline=True)
                    embed.add_field(name='------------', value='', inline=False)

                return await message.channel.send('Líderes de Ginásio:', embed=embed)

            #################
            # Fechar liga (declarar campeão)
            #################
            if cmd in ('close_league', 'mkchampion', 'mkwinner', 'end_season', 'clg'):
                if len(user_input) < 3:
                    return await message.channel.send('Parâmetro(s) ausente(s): `@membro`, `season`')
                
                user = Trainer(*get_member(message.author.id)[0])

                if user.role != 'admin':
                    return await message.channel.send('Não autorizado!')
                
                target = message.mentions
                if not target:
                    return await message.channel.send('Parâmetro(s) ausente(s): `@membro`')
                else:
                    target = target[0]
                
                season = user_input[-1]
                result = close_league(str(target.id), target.name, season)
                _, winner, games, participants = result[0]
                embed = discord.Embed(color=0x1E1E1E, type='rich')
                embed.add_field(name='Season', value=season, inline=False)
                embed.add_field(name='Campeão :trophy:', value=winner, inline=True)
                embed.add_field(name='Batalhas', value=games, inline=False)
                embed.add_field(name='N˚ de participantes', value=participants, inline=True)

                return await message.channel.send('Liga encerrada', embed=embed)

        MyClient.db.connection.reset_session()
intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)

