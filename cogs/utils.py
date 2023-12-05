import discord
import datetime
from discord.ext import commands
from database.utils import check_user_cooldown, check_card_ownership, reset_cooldown
from database.dust import get_dust_balance


class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @discord.slash_command(description="Check your dust balance")
    async def checkdust(self, ctx):
        user_id = str(ctx.author.id)
        server_id = str(ctx.guild.id)

        dust_balance = get_dust_balance(user_id, server_id)

        thumbnail_url = "https://static.wikia.nocookie.net/hearthstone/images/6/6f/ArcaneDustIcon-62x90.png/revision/latest?cb=20160124205848"  

        embed = discord.Embed(
            title="Dust Balance",
            description=f"{ctx.author.display_name}, here's your dust balance:",
            color=discord.Color.blue()  # You can change the color
        )
        embed.set_thumbnail(url=thumbnail_url)
        embed.add_field(name="Balance", value=f"{dust_balance} dust", inline=False)
        embed.set_footer(text="HoardCraft Dust System")

        await ctx.respond(embed=embed)

    @commands.has_permissions(administrator=True)
    @discord.slash_command(description="Reset cooldown for admins")
    async def resetcooldown(self, ctx):
        reset_cooldown(str(ctx.author.id), str(ctx.guild.id))   
        await ctx.respond("Your cooldown has been reset.", ephemeral=True)
    
def setup(bot):
    bot.add_cog(Utils(bot))