import discord
from bot import MyBot
from credentials import load_credentials
from database import init_db

init_db()
credentials = load_credentials('credentials.json')
bot = MyBot()
bot.run(credentials['token'])
