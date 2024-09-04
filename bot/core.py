import discord
import logging
from ast import literal_eval
from base64 import b64decode
from config.settings import __version__
from discord.ext import commands
from bot.commands import get_member
from bot.util import badge_to_emoji


class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

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
                name, role, games, wins, losses, badges, _ = result[0]

                embed = discord.Embed(color=0x1E1E1E, type='rich')
                embed.set_thumbnail(url=message.author.avatar)

                embed.add_field(name='Name', value=name, inline=True)
                embed.add_field(name='Role', value=role, inline=False)
                embed.add_field(name='Games', value=games, inline=True)
                embed.add_field(name='Wins', value=wins, inline=True)
                embed.add_field(name='Losses', value=losses, inline=True)
                badges = literal_eval(b64decode(badges).decode('utf-8'))
                embed.add_field(name='Badges', value='', inline=False)
                for badge in badges:
                    embed.add_field(name=badge.title(), value=badge_to_emoji(badge), inline=True)

                return await message.channel.send('Trainer', embed=embed)
            
intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)

