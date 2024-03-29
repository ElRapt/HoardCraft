import discord
import datetime
from database.claim import de_claim_card, claim_card
from database.dust import get_dust_balance
from database.cards import get_collections, fetch_cards_by_collection
from database.utils import check_card_ownership, get_next_reset_time
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
    'horde': "https://static.wikia.nocookie.net/wowpedia/images/0/08/Horde_Crest.png/revision/latest?cb=20151113053903",
    "quel'thalas": "https://static.wikia.nocookie.net/wowpedia/images/d/d9/Icon_of_Blood.png/revision/latest?cb=20151113053547",
    'dragon flights': "https://static.wikia.nocookie.net/wowpedia/images/a/a4/Dracthyr_Crest.png/revision/latest?cb=20221115173914",
    'blackrock' : "https://static.wikia.nocookie.net/wowpedia/images/1/1d/Blackrock_Crest.png/revision/latest?cb=20141010174912",
    'old gods': "https://static.wikia.nocookie.net/wowpedia/images/7/7a/Void_Elf_Crest_%28early%29.png/revision/latest?cb=20171104172306"
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
        self.original_cards = cards[:]  
        self.cards = cards
        self.user_name = user_name
        self.user_id = user_id 
        self.current_index = initial_index
        self.update_buttons()  


    def update_buttons(self):
        
        if len(self.children) >= 2:
            
            if self.current_index > 0:
                self.children[0].disabled = False  
            else:
                self.children[0].disabled = True   

            
            if self.current_index < len(self.cards) - 1:
                self.children[1].disabled = False  
            else:
                self.children[1].disabled = True   
        else:
            
            print("Warning: The children list does not contain enough elements.")

            

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
            card_name = card[0]  

            
            confirm_view = ConfirmView()
            await interaction.response.send_message(f"Are you sure you want to un-claim {card_name}?", view=confirm_view, ephemeral=True)
            await confirm_view.wait()

            if confirm_view.value:
                
                if de_claim_card(interaction.user.id, card_name, interaction.guild.id):
                    await interaction.followup.send(f"{card_name} has been un-claimed successfully.", ephemeral=True)
                else:
                    await interaction.followup.send(f"Failed to un-claim {card_name}.", ephemeral=True)
            else:
                
                await interaction.followup.send(f"un-claiming of {card_name} cancelled.", ephemeral=True)

            
            await interaction.edit_original_response(view=None)
        else:
            await interaction.response.send_message("You do not have permission to do this.", ephemeral=True)

    @discord.ui.button(label="Filter", style=discord.ButtonStyle.blurple)
    async def filter_collection(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id == self.user_id:
            collections = get_collections()  
            select_menu = discord.ui.Select(
                placeholder="Choose a collection",
                options=[discord.SelectOption(label=collection) for collection in collections]
            )
            select_menu.callback = self.on_collection_select
            self.add_item(select_menu)
            self.update_buttons()
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.send_message("You do not have permission to do this.", ephemeral=True)


    def filter_cards_by_collection(self, collection_name, interaction):
        self.cards = fetch_cards_by_collection(self.user_id, collection_name)
        if not self.cards:
            
            return False
        self.current_index = 0
        return True

    async def on_collection_select(self, interaction: discord.Interaction):
        select = interaction.data['values'][0]
        if not self.filter_cards_by_collection(select, interaction):
            
            await interaction.response.send_message(f"No cards found in the collection '{select}'.", ephemeral=True)
            return
        self.remove_select_menu()
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)
        
    def remove_select_menu(self):
        self.children = [child for child in self.children if not isinstance(child, discord.ui.Select)]
        
        
    def create_embed(self):
        card = self.cards[self.current_index]
        name, collection_name, title, quote, image_url, rarity = card
        color = rarity_colors.get(rarity.lower(), discord.Colour.default())  
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

        
        embed.set_footer(text=f"{embed.footer.text} | Card {self.current_index + 1} of {len(self.cards)} | {self.user_name}'s collection")
        return embed

class ClaimView(discord.ui.View):  
    def __init__(self, card_id, user_id):
        super().__init__()
        self.card_id = card_id
        self.user_id = user_id  

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
        
        self.children[0].disabled = self.current_index <= 0

        
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
        card_id, card_cost = card[0], card[-1]  
        if craft_card(interaction.user.id, card_id, interaction.guild.id, card_cost):
            await interaction.response.send_message(f"You have crafted {card[1]}!", ephemeral=True)
        else:
            await interaction.response.send_message("Not enough dust or an error occurred.", ephemeral=True)
        self.update_buttons()

    def create_embed(self):
            card = self.shop_inventory[self.current_index]
            card_id, name, collection_name, title, quote, image_url, rarity, cost = card

            color = rarity_colors.get(rarity.lower(), discord.Colour.default())

            embed = discord.Embed(
                title=name,
                description=title,
                color=color
            )
            embed.set_thumbnail(url=image_url)
            embed.set_author(name=collection_name)

            
            reset_time = get_next_reset_time(self.server_id)
            time_remaining = reset_time - datetime.datetime.now()
            hours, remainder = divmod(int(time_remaining.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)

            embed.set_footer(text=f"Cost: {cost} dust | Card {self.current_index + 1} of {len(self.shop_inventory)} | Shop resets in {hours}h {minutes}m {seconds}s")

            return embed
