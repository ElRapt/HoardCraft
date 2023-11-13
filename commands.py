import discord
from database import get_random_card


rarity_colors = {
    'legendary': discord.Colour.orange(),
    'epic': discord.Colour.purple(),
    'rare': discord.Colour.blue(),
    'uncommon': discord.Colour.green(),
    'common': discord.Colour.greyple(),  
}

collection_icons= {
    'forsaken': "https://static.wikia.nocookie.net/wowpedia/images/7/72/Forsaken_Crest.png/revision/latest?cb=20151113054325",
    'scourge': "https://static.wikia.nocookie.net/wowpedia/images/3/37/Warcraft_III_Reforged_-_Undead_Icon.png/revision/latest?cb=20210227012440",
    'alliance': "https://static.wikia.nocookie.net/wowpedia/images/d/da/Alliance_Crest.png/revision/latest?cb=20180710141058",
    'night elves': "https://static.wikia.nocookie.net/wowpedia/images/b/bc/Warcraft_III_Reforged_-_Night_Elves_Icon.png/revision/latest?cb=20210227012747",
    'scarlet crusade': "https://static.wikia.nocookie.net/wowpedia/images/7/72/Scarlet_Crusade_logo.png/revision/latest?cb=20080730021543",
    'horde': "https://static.wikia.nocookie.net/wowpedia/images/0/08/Horde_Crest.png/revision/latest?cb=20151113053903"
}


def init_bot_commands(bot):

    class ClaimView(discord.ui.View):  # Create a class that subclasses discord.ui.View
        @discord.ui.button(label="Claim", style=discord.ButtonStyle.success, emoji="🏆")  # Create a "Claim" button
        async def claim_callback(self, button, interaction):
            await interaction.response.send_message("Claim successful!")  # Send a message when the button is clicked
            # Add your logic for the claim action here


    @bot.command(description="Get a random card")
    async def random(ctx):
        card = get_random_card()
        
        if card:
            name, collection_name, title, quote, image_url, rarity = card
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

            await ctx.respond(embed=embed, view=ClaimView())
        else:
            await ctx.respond("No cards available.")
