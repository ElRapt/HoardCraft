import discord
from database.utils import ensure_server_exists_in_db

cogs_list = [
    'random',
    'shop',
    'utils',
    'list',
    'help'
]


class MyBot(discord.bot.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for cog in cogs_list:
            self.load_extension(f'cogs.{cog}')

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        for guild in self.guilds:
            ensure_server_exists_in_db(guild.id)

    