import discord
from bot import MyClient
from credentials import load_credentials

credentials = load_credentials('credentials.json')
intents = discord.Intents.default()
client = MyClient(intents=intents)
client.run(credentials['token'])
