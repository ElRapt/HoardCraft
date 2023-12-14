import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(description="Displays the list of commands")
    async def help(self, ctx):
        embed = discord.Embed(title="HoardCraft commands", color=discord.Color.blue())
        embed.add_field(name="`/help`", value="Shows this message.", inline=False)
        embed.add_field(name="`/random`", value="Randomly drops a card amongst all cards.", inline=False)
        embed.add_field(name="`/shop`", value="Displays the shop : 3 random cards you can buy with dust.", inline=False)
        embed.add_field(name="`/list`", value="Displays your card collection.", inline=False)
        embed.add_field(name="`/checkdust`", value="Check your dust balance.", inline=False)

        await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Help(bot))
