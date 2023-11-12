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

    class TestView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
        @discord.ui.button(label="Click me!", style=discord.ButtonStyle.success, emoji="😎") # Create a button with the label "😎 Click me!" with color Blurple
        async def button_callback(self, button, interaction):
            await interaction.response.send_message("You clicked the button!") # Send a message when the button is clicked

    @bot.command(description="Test button") # Create a slash command
    async def button(ctx):
        await ctx.respond("This is a button!", view=TestView()) # Send a message with our View class that contains the button

    @bot.command(description="Create Sylvanas")
    async def sylvanas(ctx):
        embed = discord.Embed(
            title="Sylvanas Windrunner",
            description="The Banshee Queen",
            color=discord.Colour.orange(), # Pycord provides a class with default colors you can choose from
        )
        embed.set_author(name="Forsaken", icon_url="https://static.wikia.nocookie.net/wowpedia/images/7/72/Forsaken_Crest.png/revision/latest?cb=20151113054325")
        embed.set_image(url="https://static.wikia.nocookie.net/wow/images/e/e2/Sylvanas_JCC.jpg/revision/latest/scale-to-width-down/392?cb=20230811211943&path-prefix=fr")
        embed.set_footer(text='"We are the Forsaken. We will slaughter anyone who stands in our way."')

        await ctx.respond(embed=embed) # Send the embed with some text
 

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
            embed.set_author(name=collection_name, icon_url=icon_url)
            embed.set_image(url=image_url)
            embed.set_footer(text=quote)

            await ctx.respond(embed=embed)
        else:
            await ctx.respond("No cards available.")
