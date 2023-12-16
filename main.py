import discord
from bot import MyBot
from utils.credentials import load_credentials
from database.init_db import init_db
from utils.cache import CooldownCache

init_db()
credentials = load_credentials('credentials.json')
intents = discord.Intents.default()
bot = MyBot(intents=intents)

bot.run(credentials['token'])
