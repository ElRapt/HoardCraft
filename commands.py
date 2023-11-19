import discord
import datetime
from database.cards import get_random_card, get_user_collection
from database.dust import get_dust_balance, calculate_dust_earned, update_dust_balance
from database.shop import get_shop_inventory, craft_card
from database.utils import check_card_ownership, check_user_dust_balance, check_user_cooldown, reset_cooldown
from database.claim import claim_card, de_claim_card


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



    @bot.command(description="Get a random card")
    async def random(ctx):
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

    @bot.command(description="List the user's cards")
    async def mylist(ctx):
        cards = get_user_collection(ctx.author.id, ctx.guild.id)
        if cards:
            view = PaginatedView(cards, ctx.author.name, ctx.author.id)
            await ctx.respond("Displaying your collection.", ephemeral=True)
            await ctx.respond(embed=view.create_embed(), view=view)
        else:
            await ctx.respond("No cards available.")


    @bot.command(description="Check your dust balance")
    async def checkdust(ctx):
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



    @bot.command(description="View the card shop")
    async def shop(ctx):
        user_id = ctx.author.id
        shop_inventory = get_shop_inventory() 
        view = ShopView(shop_inventory, user_id)
        await ctx.send(embed=view.create_embed(), view=view)


    
    @bot.command(description="Reset cooldown for admins")
    async def resetcooldown(ctx):
        reset_cooldown(str(ctx.author.id))
        await ctx.respond("Your cooldown has been reset.", ephemeral=True)



