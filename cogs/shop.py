import discord
import datetime
from discord.ext import commands
from database.shop import get_shop_inventory
from database.utils import check_card_ownership, check_user_dust_balance

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

class ShopView(discord.ui.View):
    def __init__(self, shop_inventory, user_id, initial_index=0):
        super().__init__()
        self.shop_inventory = shop_inventory
        self.user_id = user_id
        self.current_index = initial_index
        self.update_buttons()

    def update_buttons(self):
        # Enable/Disable Previous button
        self.children[0].disabled = self.current_index <= 0

        # Enable/Disable Next button
        self.children[1].disabled = self.current_index >= len(self.shop_inventory) - 1

        # Check card ownership and dust balance for enabling/disabling Craft button
        card_id, cost = self.shop_inventory[self.current_index][0], self.shop_inventory[self.current_index][-1]
        owns_card = check_card_ownership(str(self.user_id), card_id)
        has_enough_dust = check_user_dust_balance(str(self.user_id), cost)
        self.children[2].disabled = owns_card or not has_enough_dust

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.grey)
    async def show_previous(self, button, interaction):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.grey)
    async def show_next(self, button, interaction):
        if self.current_index < len(self.shop_inventory) - 1:
            self.current_index += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="Craft", style=discord.ButtonStyle.green)
    async def craft_card(self, button, interaction):
        card = self.shop_inventory[self.current_index]
        card_id, card_cost = card[0], card[-1]  # Assuming the cost is the last element
        if craft_card(interaction.user.id, card_id, interaction.guild.id, card_cost):
            await interaction.response.send_message(f"You have crafted {card[1]}!", ephemeral=True)
        else:
            await interaction.response.send_message("Not enough dust or an error occurred.", ephemeral=True)
        self.update_buttons()
        await interaction.edit_original_message(view=self)

    def create_embed(self):
        card = self.shop_inventory[self.current_index]
        card_id, name, collection_name, title, quote, image_url, rarity, cost = card  # Corrected to unpack 8 elements

        color = rarity_colors.get(rarity.lower(), discord.Colour.default())  # Get color based on rarity

        embed = discord.Embed(
            title=name,  # Card's name
            description=title,  # Card's title
            color=color  # Set color based on rarity
        )
        embed.set_thumbnail(url=image_url)  # Set thumbnail based on collection
        embed.set_author(name=collection_name)  # Set author to collection name
        embed.set_footer(text=f"Cost: {cost} dust | Card {self.current_index + 1} of {len(self.shop_inventory)}")

        return embed

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="View the card shop")
    async def shop(self, ctx):
        user_id = ctx.author.id
        shop_inventory = get_shop_inventory() 
        view = ShopView(shop_inventory, user_id)
        await ctx.send(embed=view.create_embed(), view=view)


def setup(bot):
    bot.add_cog(Shop(bot))