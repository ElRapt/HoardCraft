import discord
from database.utils import ensure_server_exists_in_db

cogs_list = [
    'random',
    'shop',
    'utils',
    'list'
]

rarity_colors = {
    'legendary': discord.Colour.orange(),
    'epic': discord.Colour.purple(),
    'rare': discord.Colour.blue(),
    'uncommon': discord.Colour.green(),
    'common': discord.Colour.greyple(),  
}

collection_icons= {
    'forsaken': "https://static.wikia.nocookie.net/wowpedia/images/7/72/Forsaken_Crest.png/revision/latest?cb=20151113054325",
    'scourge': "https://static.wikia.nocookie.net/wowpedia/images/3/37/Warcraft_III_Reforged_-_Undead_Icon.png/revision/latest?cb=20210227012440",
    'alliance': "https://static.wikia.nocookie.net/wowpedia/images/d/da/Alliance_Crest.png/revision/latest?cb=20180710141058",
    'night elves': "https://static.wikia.nocookie.net/wowpedia/images/b/bc/Warcraft_III_Reforged_-_Night_Elves_Icon.png/revision/latest?cb=20210227012747",
    'scarlet crusade': "https://static.wikia.nocookie.net/wowpedia/images/7/72/Scarlet_Crusade_logo.png/revision/latest?cb=20080730021543",
    'horde': "https://static.wikia.nocookie.net/wowpedia/images/0/08/Horde_Crest.png/revision/latest?cb=20151113053903"
}


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

    