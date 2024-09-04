import discord
import logging
from ast import literal_eval
from base64 import b64decode
from config.settings import __version__
from discord.ext import commands
from bot.commands import get_member, add_badge
from bot.util import badge_to_emoji
from bot.models import Trainer
from bot.db_handler import ABP_DB, db_connection


class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

        # Opens database connection
        db = ABP_DB(db_connection())

        # Auto create new member if not exists
        db.get_or_create(message.author.id, message.author.name)

        # close database cnnection and free alocated memory for it
        db.connection.close()
        del db

        # BOT COMMAND
        if message.content.startswith('>>'):
            user_input = message.content[2:].strip().split(' ')

            # VERSION
            if user_input[0].lower() in ('version', 'v'):
                return await message.channel.send(__version__)
            
            # TRAINER CARD
            if user_input[0].lower() in ('user', 'usr', 'card', 'trainer_card', 'trainer'):
                if len(user_input) < 2:
                    return await message.channel.send('Parâmetro ausente: `@membro`')
                result = get_member(message.author)

                if not result:
                    return await message.channel('Não encontrado')

                trainer = Trainer(*result[0])

                embed = discord.Embed(color=0x1E1E1E, type='rich')
                embed.set_thumbnail(url=message.author.avatar)

                embed.add_field(name='Name', value=trainer.name, inline=True)
                embed.add_field(name='Role', value=trainer.role, inline=False)
                embed.add_field(name='Games', value=trainer.games, inline=True)
                embed.add_field(name='Wins', value=trainer.wins, inline=True)
                embed.add_field(name='Losses', value=trainer.losses, inline=True)
                embed.add_field(name='Badges', value='', inline=False)
                for badge in trainer.badges:
                    embed.add_field(name=badge.title(), value=badge_to_emoji(badge), inline=True)

                return await message.channel.send('Trainer', embed=embed)
            if user_input[0].lower() in ('add_badge', 'give'):
                if len(user_input) < 3:
                    return await message.channel.send('Parâmetro(s) ausente(s): `@membro`, nome da insignia')
                print(user_input)
                try:
                    add_badge(message.author, user_input[1], user_input[2])
                except Exception as err:
                    error_message = str(err)
                    if error_message == 'INVALID BADGE':
                        return await message.channel.send(f'Insígnia inválida, opções válida: {", ".join(f"`{b}`" for b in badge_to_emoji.keys())}!')
                    if error_message == 'UNAUTHORIZED':
                        return await message.channel.send('Não autorizado à realizar esta ação!')



intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)

