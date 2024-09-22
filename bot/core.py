import discord
import logging
from config.settings import __version__
from discord.ext import commands
from bot.commands import BotCommands
from bot.util import parse_id, badge_to_emoji
from bot.models import Trainer, GymLeader
from bot.db_handler import ABP_DB, db_connection


logger = logging.getLogger(__name__)


class MyClient(discord.Client):
    db = db = ABP_DB(db_connection())

    async def on_ready(self):
        logger.info(f'Logged on as {self.user}!')

    async def on_message(self, message):
        logger.info(f'Message from {message.author}: {message.content}')
        MyClient.db.connection.reset_session()
        # Auto create new member if not exists
        MyClient.db.get_or_create(parse_id(message.author.id), message.author.name)

        # ++++++++++++++
        # BOT COMMAND
        # ++++++++++++++
        if message.content.startswith('>>'):
            user_input = message.content[2:].strip().split(' ')
            cmd = user_input[0].lower()
            if cmd not in BotCommands.valid_commands:
                return await message.channel.send('Comando não reconhecido!\nEscreva `>>help` para listar os comandos disponíveis!')

            #################
            # help
            #################
            if cmd in ('help', 'h'):
                if len(user_input) > 2:
                    param = user_input[-1]
                    if param in BotCommands.valid_commands:
                        return await message.channel.send(BotCommands.command_help[param])
                    return await message.channel.send('Parâmetro não reconhecido')
                help_list = BotCommands.command_help['help']
                page1, page2 = help_list.split('- `register`')
                await message.channel.send(page1)
                return await message.channel.send(f'- `register`{page2}')

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
                    return await message.channel.send('Não encontrado')
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
                if len(user_input) < 2:
                    return await message.channel.send('Parâmetro ausente(s): `@membro`')
                target = message.mentions
                if not target:
                    return await message.channel.send('Parâmetro ausente(s): `@membro`')
                else:
                    target = target[0]

                try:
                    trainer, badge = BotCommands.add_badge(message.author.id, target.id)
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
            # if cmd in ('register', 'rg'):
            #     if len(user_input) < 2:
            #         return await message.channel.send('Parâmetro(s) ausente(s): `@membro`')

            #     target = message.mentions
            #     if not target:
            #         return await message.channel.send('Parâmetro(s) ausente(s): `@membro`, liga')
            #     else:
            #         target = target[0]
            #     try:
            #         result = BotCommands.register(message.author, target.id)
            #     except Exception as err:
            #         if error_message == 'MEMBER NOT FOUND':
            #             return await message.channel.send('Mmebro não registrado, é necessário que o membro marcado envie ao menos uma mensagem no chat, assim seu registro de membro será realizado automaticamente. Uma vez registrado você poderá executar novamente este comando!')

            #     trainer = Trainer(*result[0])
            #     embed = discord.Embed(color=0x1E1E1E, type='rich')

            #     embed.set_thumbnail(url=target.avatar)
            #     embed.add_field(name='Name', value=trainer.name, inline=True)
            #     embed.add_field(name='Role', value=trainer.role, inline=False)
            #     embed.add_field(name='Games', value=trainer.games, inline=True)
            #     embed.add_field(name='Wins', value=trainer.wins, inline=True)
            #     embed.add_field(name='Losses', value=trainer.losses, inline=True)
            #     embed.add_field(name='Liga atual', value=trainer.current_league, inline=False)
            #     embed.add_field(name='Ligas vencidas', value=trainer.leagues_win, inline=True)
            #     embed.add_field(name='Badges', value='', inline=False)
                
            #     for badge in trainer.badges:
            #         embed.add_field(name=badge.title(), value=badge_to_emoji[badge], inline=True)

            #     embed.add_field(name='Ligas jogadas', value=' - '.join(str(league) for league in trainer.leagues_participated), inline=False)

            #     return await message.channel.send(trainer.name, embed=embed)

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

                leader = GymLeader(*BotCommands.get_leader(message.author.id))
                if leader.role != 'gym_leader':
                    return await message.channel.send('Não autorizado')
                
                result = BotCommands.battle_report(leader.member_id, target.id, condition)

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
                data = BotCommands.list_leagues()
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
                user = Trainer(*BotCommands.get_member(message.author.id)[0])
                if user.role != 'admin':
                    return await message.channel.send('Não autorizado!')

                if len(user_input) < 2:
                    return await message.channel.send('Parâmetro(s) ausente(s): season')

                season = user_input[-1]
                league = BotCommands.new_league(season)[-1]

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
                data = BotCommands.get_current_league()
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
                if len(user_input) < 3:
                    return await message.channel.send('Parâmetro(s) ausente(s): `@member`, `liga`')
                target = message.mentions
                if not target:
                    return await message.channel.send('Parâmetro(s) ausente(s): `@membro`, `liga`')
                else:
                    target = target[0]

                user = Trainer(*BotCommands.get_member(message.author.id)[0])

                # if user.role 'admin':
                #     return await message.channel.send('Não autorizado!')

                
                season = user_input[-1]
                
                try:
                    result = BotCommands.register_trainer_to_league(season, target.id)
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
                admins = BotCommands.list_admins()
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
                
                user = Trainer(*BotCommands.get_member(message.author.id)[0])

                if user.role != 'admin':
                    return await message.channel.send('Não autorizado!')
                
                target = message.mentions
                if not target:
                    return await message.channel.send('Parâmetro(s) ausente(s): `@membro`')
                else:
                    target = target[0]
                leader = GymLeader(*BotCommands.register_leader(target.id, target.name, user_input[-2], user_input[-1])[0])

                embed = discord.Embed(color=0x1E1E1E, type='rich')
                embed.set_thumbnail(url=target.avatar)
                embed.add_field(name='Name', value=leader.name, inline=True)
                embed.add_field(name='Liga', value=leader.league, inline=False)
                embed.add_field(name='Partidas', value=leader.games, inline=True)
                embed.add_field(name='Score', value=f'({leader.wins}/{leader.losses})', inline=True)
                embed.add_field(name='Tipo', value=f'{badge_to_emoji[leader.type]} {leader.type}', inline=False)
                
                return await message.channel.send('', embed=embed)

            #################
            # Listar lider
            #################
            if cmd in ('leaders', 'gyms', 'gym_leaders', 'gls', 'gl'):
                leaders = BotCommands.get_leaders()
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
                
                user = Trainer(*BotCommands.get_member(message.author.id)[0])

                if user.role != 'admin':
                    return await message.channel.send('Não autorizado!')
                
                target = message.mentions
                if not target:
                    return await message.channel.send('Parâmetro(s) ausente(s): `@membro`')
                else:
                    target = target[0]
                
                season = user_input[-1]
                result = BotCommands.close_league(str(target.id), target.name, season)
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

