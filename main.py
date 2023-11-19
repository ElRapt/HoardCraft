import discord
from bot import MyBot
from credentials import load_credentials
from database.init_db import init_db

init_db()
credentials = load_credentials('credentials.json')
intents = discord.Intents.default()
bot = MyBot(intents=intents)

bot.run(credentials['token'])
