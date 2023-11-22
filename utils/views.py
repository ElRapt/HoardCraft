import discord
from database.claim import de_claim_card, claim_card
from database.dust import get_dust_balance
from database.utils import check_card_ownership
from database.shop import craft_card

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

class ConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = True
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = False
        self.stop()

class PaginatedView(discord.ui.View):
    def __init__(self, cards, user_name, user_id, initial_index=0):
        super().__init__()
        self.cards = cards
        self.user_name = user_name
        self.user_id = user_id 
        self.current_index = initial_index
        self.update_buttons()  

    def update_buttons(self):
        # Update the state of the Previous button
        if self.current_index > 0:
            self.children[0].disabled = False  # Enable Previous button
        else:
            self.children[0].disabled = True   # Disable Previous button

        # Update the state of the Next button
        if self.current_index < len(self.cards) - 1:
            self.children[1].disabled = False  # Enable Next button
        else:
            self.children[1].disabled = True   # Disable Next button

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.grey)
    async def show_previous(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id == self.user_id and self.current_index > 0:
            self.current_index -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.send_message("You do not have permission to do this.", ephemeral=True)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.grey)
    async def show_next(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id == self.user_id and self.current_index < len(self.cards) - 1:
            self.current_index += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.send_message("You do not have permission to do this.", ephemeral=True)

    @discord.ui.button(label="Remove", style=discord.ButtonStyle.danger, custom_id="remove")
    async def remove_card(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id == self.user_id:
            card = self.cards[self.current_index]
            card_name = card[0]  # Get the card's name

            # Ask for confirmation before removing
            confirm_view = ConfirmView()
            await interaction.response.send_message(f"Are you sure you want to un-claim {card_name}?", view=confirm_view, ephemeral=True)
            await confirm_view.wait()

            if confirm_view.value:
                # If confirmed, un-claim the card
                if de_claim_card(interaction.user.id, card_name, interaction.guild.id):
                    await interaction.followup.send(f"{card_name} has been un-claimed successfully.", ephemeral=True)
                else:
                    await interaction.followup.send(f"Failed to un-claim {card_name}.", ephemeral=True)
            else:
                # If cancelled, let the user know
                await interaction.followup.send(f"un-claiming of {card_name} cancelled.", ephemeral=True)

            # Update the original message to remove the buttons
            await interaction.edit_original_response(view=None)
        else:
            await interaction.response.send_message("You do not have permission to do this.", ephemeral=True)


    def create_embed(self):
        card = self.cards[self.current_index]
        name, collection_name, title, quote, image_url, rarity = card
        color = rarity_colors.get(rarity.lower(), discord.Colour.default())  # Get color based on rarity
        icon_url = collection_icons.get(collection_name.lower(), "")  # Get icon URL based on collection

        embed = discord.Embed(
            title=name,  # Card's name
            description=title,  # Card's title
            color=color  # Set color based on rarity
        )
        embed.set_thumbnail(url=icon_url)  # Set thumbnail based on collection
        embed.set_author(name=collection_name)  # Set author to collection name
        embed.set_image(url=image_url)  # Image URL
        embed.set_footer(text=quote)  # Set footer to card's quote

        # Additional text for pagination
        embed.set_footer(text=f"{embed.footer.text} | Card {self.current_index + 1} of {len(self.cards)} | {self.user_name}'s collection")
        return embed

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


class ShopView(discord.ui.View):
    def __init__(self, shop_inventory, user_id, server_id, initial_index=0):
        super().__init__()
        self.shop_inventory = shop_inventory
        self.user_id = user_id
        self.server_id = server_id
        self.current_index = initial_index
        self.update_buttons()

    def update_buttons(self):
        # Enable/Disable Previous button
        self.children[0].disabled = self.current_index <= 0

        # Enable/Disable Next button
        self.children[1].disabled = self.current_index >= len(self.shop_inventory) - 1

        card_id, cost = self.shop_inventory[self.current_index][0], self.shop_inventory[self.current_index][-1]
        
        server_id_int = int(self.server_id)

        owns_card = check_card_ownership(self.user_id, card_id, server_id_int)
        has_enough_dust = get_dust_balance(self.user_id, server_id_int) >= cost

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