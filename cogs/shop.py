import discord
import datetime
from discord.ext import commands
from database.shop import get_shop_inventory
from utils.views import ShopView

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @discord.slash_command(description="View the card shop")
    async def shop(self, ctx):
        user_id = ctx.author.id
        server_id = ctx.guild.id
        shop_inventory = get_shop_inventory() 
        view = ShopView(shop_inventory, user_id, server_id)
        await ctx.respond(embed=view.create_embed(), view=view)


def setup(bot):
    bot.add_cog(Shop(bot))