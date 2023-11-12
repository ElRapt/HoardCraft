import discord
from bot import MyBot
from credentials import load_credentials

credentials = load_credentials('credentials.json')
bot = MyBot()
bot.run(credentials['token'])
