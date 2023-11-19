import discord
from commands import init_bot_commands
from database.utils import ensure_server_exists_in_db

class MyBot(discord.bot.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        init_bot_commands(self)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        for guild in self.guilds:
            ensure_server_exists_in_db(guild.id)

    