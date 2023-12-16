import discord
import datetime
from discord.ext import commands
from database.utils import check_user_cooldown, check_card_ownership
from database.cards import get_random_card
from database.dust import get_dust_balance, update_dust_balance, calculate_dust_earned
from utils.views import ClaimView


rarity_colors = {
    'legendary': discord.Colour.orange(),
    'epic': discord.Colour.purple(),
    'rare': discord.Colour.dark_blue(),
    'uncommon': discord.Colour.green(),
    'common': discord.Colour.greyple(),  
}

collection_icons= {
    'forsaken': "https://static.wikia.nocookie.net/wowpedia/images/7/72/Forsaken_Crest.png/revision/latest?cb=20151113054325",
    'scourge': "https://static.wikia.nocookie.net/wowpedia/images/3/37/Warcraft_III_Reforged_-_Undead_Icon.png/revision/latest?cb=20210227012440",
    'alliance': "https://static.wikia.nocookie.net/wowpedia/images/d/da/Alliance_Crest.png/revision/latest?cb=20180710141058",
    'night elves': "https://static.wikia.nocookie.net/wowpedia/images/b/bc/Warcraft_III_Reforged_-_Night_Elves_Icon.png/revision/latest?cb=20210227012747",
    'scarlet crusade': "https://static.wikia.nocookie.net/wowpedia/images/7/72/Scarlet_Crusade_logo.png/revision/latest?cb=20080730021543",
    'horde': "https://static.wikia.nocookie.net/wowpedia/images/0/08/Horde_Crest.png/revision/latest?cb=20151113053903",
    "quel'thalas": "https://static.wikia.nocookie.net/wowpedia/images/d/d9/Icon_of_Blood.png/revision/latest?cb=20151113053547",
    'dragon flights': "https://static.wikia.nocookie.net/wowpedia/images/a/a4/Dracthyr_Crest.png/revision/latest?cb=20221115173914",
    'blackrock' : "https://static.wikia.nocookie.net/wowpedia/images/1/1d/Blackrock_Crest.png/revision/latest?cb=20141010174912",
    'old gods': "https://static.wikia.nocookie.net/wowpedia/images/7/7a/Void_Elf_Crest_%28early%29.png/revision/latest?cb=20171104172306"
    }

class Random(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @discord.slash_command(description="Get a random card")
    async def random(self, ctx):
        try:
            user_id = str(ctx.author.id)
            server_id = str(ctx.guild.id)

            can_request, cooldown_end = check_user_cooldown(user_id, server_id)
            if not can_request:
                current_time = datetime.datetime.now()
                if cooldown_end is not None:
                    remaining_time = cooldown_end - current_time
                    hours, remainder = divmod(int(remaining_time.total_seconds()), 3600)
                    minutes, seconds = divmod(remainder, 60)

                    time_str = f"{hours}h {minutes}m {seconds}s"
                    await ctx.respond(f"You have reached your limit of 5 requests per hour. Please wait for {time_str} before trying again.", ephemeral=True)
                else:
                    await ctx.respond("You are currently on cooldown, but the remaining time could not be calculated.", ephemeral=True)
                return

            card = get_random_card()
            if card:
                card_id, name, collection_name, title, quote, image_url, rarity = card

                if check_card_ownership(user_id, card_id, server_id):
                    dust_earned = calculate_dust_earned(rarity)
                    update_dust_balance(user_id, server_id, dust_earned)
                    await ctx.respond(f"You already own {name}. You earned {dust_earned} dust!", ephemeral=True)
                else:
                    rarity = rarity.lstrip()
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

                    await ctx.respond(embed=embed, view=ClaimView(card_id, user_id))  
            else:
                await ctx.respond("No cards available.")

        except Exception as e:
            await ctx.respond(f"An error occurred: {e}", ephemeral=True)


def setup(bot):
    bot.add_cog(Random(bot))