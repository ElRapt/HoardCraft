import discord
import datetime
from discord.ext import commands
from database.utils import check_user_cooldown, check_card_ownership
from database.cards import get_random_card
from database.dust import update_dust_balance, calculate_dust_earned
from database.claim import claim_card


class ClaimView(discord.ui.View):  
    def __init__(self, card_id, user_id):
        super().__init__()
        self.card_id = card_id
        self.user_id = user_id  # Store the user's ID who requested the card

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.success, emoji="🏆")
    async def claim_callback(self, button, interaction):
        if str(interaction.user.id) == self.user_id:
            if claim_card(interaction.user.id, self.card_id, interaction.guild.id):
                await interaction.response.send_message("Card claimed!", ephemeral=True)
            else:
                await interaction.response.send_message("Card not available.", ephemeral=True)
        else:
            await interaction.response.send_message("You cannot claim this card as it was not requested by you.", ephemeral=True)

class Random(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @commands.slash_command(description="Get a random card")
    async def random(self, ctx):
        user_id = str(ctx.author.id)
        server_id = str(ctx.guild.id)
        
        can_request, cooldown_end = check_user_cooldown(str(ctx.author.id))
        if not can_request:
            current_time = datetime.datetime.now()
            remaining_time = cooldown_end - current_time
            hours, remainder = divmod(int(remaining_time.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)

            # Format the remaining time in a user-friendly way
            time_str = f"{hours}h {minutes}m {seconds}s"
            await ctx.respond(f"You have reached your limit of 5 requests per hour. Please wait for {time_str} before trying again.", ephemeral=True)
            return
        
        card = get_random_card()
    
        if card:
            card_id, name, collection_name, title, quote, image_url, rarity = card

            if check_card_ownership(user_id, card_id):
                # User already owns this card, give dust instead
                dust_earned = calculate_dust_earned(rarity)
                update_dust_balance(user_id, server_id, dust_earned)
                await ctx.respond(f"You already own {name}. You earned {dust_earned} dust!", ephemeral=True)
            else:
                # User doesn't own the card, allow them to claim
                color = rarity_colors.get(rarity, discord.Colour.default())  
                icon_url = collection_icons.get(collection_name.lower(), "")  

                embed = discord.Embed(
                    title=name,
                    description=title,
                    color=color
                )
                embed.set_thumbnail(url=icon_url)
                embed.set_author(name=collection_name)
                embed.set_image(url=image_url)
                embed.set_footer(text=quote)

                await ctx.respond(embed=embed, view=ClaimView(card_id, user_id))  # Pass the card ID and user's ID to ClaimView
        else:
            await ctx.respond("No cards available.")

def setup(bot):
    bot.add_cog(Random(bot))