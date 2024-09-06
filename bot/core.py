import discord
import logging
from ast import literal_eval
from base64 import b64decode
from config.settings import __version__
from discord.ext import commands
from bot.commands import get_member, add_badge, register, list_leagues
from bot.util import badge_to_emoji, valid_commands, command_help, parse_id
from bot.models import Trainer
from bot.db_handler import ABP_DB, db_connection


logger = logging.getLogger(__name__)


class MyClient(discord.Client):
    db = db = ABP_DB(db_connection())

    async def on_ready(self):
        logger.info(f'Logged on as {self.user}!')

    async def on_message(self, message):
        logger.info(f'Message from {message.author}: {message.content}')
        # Opens database connection
        

        # Auto create new member if not exists
        MyClient.db.get_or_create(parse_id(message.author.id), message.author.name)

        # ++++++++++++++
        # BOT COMMAND
        # ++++++++++++++
        if message.content.startswith('>>'):
            user_input = message.content[2:].strip().split(' ')
            cmd = user_input[0].lower()
            if cmd not in valid_commands:
                return await message.channel.send('Comando não reconhecido!\nEscreva `>>help` para listar os cmandos disponíveis!')

            #################
            # VERSION
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
                # embed.set_thumbnail(url=message.author.avatar)

                embed.add_field(name='Name', value=trainer.name, inline=True)
                embed.add_field(name='Role', value=trainer.role, inline=False)
                embed.add_field(name='Games', value=trainer.games, inline=True)
                embed.add_field(name='Wins', value=trainer.wins, inline=True)
                embed.add_field(name='Losses', value=trainer.losses, inline=True)
                embed.add_field(name='Badges', value='', inline=False)

                for badge in trainer.badges:
                    embed.add_field(name=badge.title(), value=badge_to_emoji[badge], inline=True)

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

                embed.add_field(name='Name', value=trainer.name, inline=True)
                embed.add_field(name='Role', value=trainer.role, inline=False)
                embed.add_field(name='Games', value=trainer.games, inline=True)
                embed.add_field(name='Wins', value=trainer.wins, inline=True)
                embed.add_field(name='Losses', value=trainer.losses, inline=True)
                embed.add_field(name='Badges', value='', inline=False)

                for badge in trainer.badges:
                    embed.add_field(name=badge.title(), value=badge_to_emoji[badge], inline=True)

                return await message.channel.send(trainer.name, embed=embed)

            #################
            # REGISTER
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

            #################
            # Ranking
            #################
            if cmd in ('ranking', 'rank', 'top'):
                trainers = MyClient.db.top_trainers()
                embed = discord.Embed(color=0x1E1E1E, type='rich')

                for data in trainers:
                    trainer = Trainer(*data)
                    embed.add_field(name=trainer.name, value=f'Games: {trainer.games} ({trainer.wins}/{trainer.losses} | **Badges**: {len(trainer.badges)})', inline=False)
                return await message.channel.send('Top 8 treinadres da liga', embed=embed)

            if cmd in ('leagues', 'ls'):
                data = list_leagues()
                if not data:
                    return await message.channel.send('Não há ligas cadastradas no momento')
                
                embed = discord.Embed(color=0x1E1E1E, type='rich')
                for league in data:
                    season, winner, games, participants = league
                    embed.add_field(name='Season', value=season, inline=False)
                    embed.add_field(name='Partidas', value=games, inline=True)
                    embed.add_field(name='Participantes', value=participants, inline=True)
                    embed.add_field(name='Campeão', value=winner, inline=True)
                
                return await message.channel.send('Ligas:', embed=embed)



        MyClient.db.connection.reset_session()
intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)

