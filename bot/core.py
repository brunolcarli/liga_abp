import discord
# import logging
from base64 import b64decode
from config.settings import __version__
from discord.ext import commands
from bot.commands import get_member



class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

        if message.content.startswith('>>'):
            user_input = message.content[2:].strip().split(' ')
            if user_input[0].lower() in ('version', 'v'):
                return await message.channel.send(__version__)
            
            if user_input[0].lower() in ('user', 'usr'):
                if len(user_input) < 2:
                    return await message.channel.send('Parâmetro ausente: `@membro`')
                result = get_member(message.author)

                if not result:
                    return await message.channel('Não encontrado')
                name, role, games, wins, losses, badges, _ = result[0]

                # avatar_url = f'{message.author.avatar_url.BASE}/avatars/{message.author.id}/{message.author.avatar}'
                embed = discord.Embed(color=0x1E1E1E, type='rich')
                embed.set_thumbnail(url=message.author.avatar)

                embed.add_field(name='Name', value=name, inline=True)
                embed.add_field(name='Role', value=role, inline=False)
                embed.add_field(name='Games', value=games, inline=True)
                embed.add_field(name='Wins', value=wins, inline=True)
                embed.add_field(name='Losses', value=losses, inline=True)


                temp = f'''
                ```
                Name: {name}
                Role: {role}
                Games: {games}
                Wins: {wins} | Losses: {losses}
                Badges:
                {b64decode(badges)}
                ```
                '''
                return await message.channel.send('Trainer', embed=embed)
            
intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)

