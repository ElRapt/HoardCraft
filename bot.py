import discord
from commands import init_bot_commands

class MyBot(discord.bot.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        init_bot_commands(self)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    