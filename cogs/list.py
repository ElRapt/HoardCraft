import discord
import datetime
from discord.ext import commands
from database.cards import get_user_collection
from database.claim import claim_card, de_claim_card
from utils.views import PaginatedView, ConfirmView

class List(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(description="List the user's cards")
    async def list(self, ctx):
        cards = get_user_collection(ctx.author.id, ctx.guild.id)
        if cards:
            view = PaginatedView(cards, ctx.author.name, ctx.author.id)
            await ctx.respond("Displaying your collection.", ephemeral=True)
            await ctx.respond(embed=view.create_embed(), view=view)
        else:
            await ctx.respond("No cards available.")

def setup(bot):
    bot.add_cog(List(bot))


