import discord
from database import get_random_card, get_user_collection, claim_card


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

    class ClaimView(discord.ui.View):  
        def __init__(self, card_name):
            super().__init__()
            self.card_name = card_name  # Store the card's name as an attribute

        @discord.ui.button(label="Claim", style=discord.ButtonStyle.success, emoji="🏆")
        async def claim_callback(self, button, interaction):
            # Use self.card_name to get the card's name
            if claim_card(interaction.user.id, self.card_name, interaction.guild.id):
                await interaction.response.send_message("Card claimed!", ephemeral=True)
            else:
                await interaction.response.send_message("Card not available.", ephemeral=True)

    class PaginatedView(discord.ui.View):
        def __init__(self, cards, initial_index=0):
            super().__init__()
            self.cards = cards
            self.current_index = initial_index

        @discord.ui.button(label="Previous", style=discord.ButtonStyle.grey)
        async def show_previous(self, button: discord.ui.Button, interaction: discord.Interaction):
            if self.current_index > 0:
                self.current_index -= 1
                await interaction.response.edit_message(embed=self.create_embed())

        @discord.ui.button(label="Next", style=discord.ButtonStyle.grey)
        async def show_next(self, button: discord.ui.Button, interaction: discord.Interaction):
            if self.current_index < len(self.cards) - 1:
                self.current_index += 1
                await interaction.response.edit_message(embed=self.create_embed())

        def create_embed(self):
            card = self.cards[self.current_index]
            embed_color = rarity_colors.get(card[5].lower(), discord.Colour.default())  # Get color based on rarity

            embed = discord.Embed(
                title=card[0],  # Card's name
                description=f"{card[1]}\n{card[2]}\n{card[3]}",  # Collection, Title, Quote
                color=embed_color  # Set color based on rarity
            )
            embed.set_image(url=card[4])  # Image URL
            embed.set_footer(text=f"Card {self.current_index + 1} of {len(self.cards)}")
            return embed



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

            await ctx.respond(embed=embed, view=ClaimView(name))
        else:
            await ctx.respond("No cards available.")

    @bot.command(description="List the user's cards")
    async def mylist(ctx):
        cards = get_user_collection(ctx.author.id, ctx.guild.id)
        if cards:
            view = PaginatedView(cards)
            await ctx.send(embed=view.create_embed(), view=view)
        else:
            await ctx.send("No cards available.")

        