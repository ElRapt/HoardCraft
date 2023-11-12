import discord

def init_bot_commands(bot):

    class MyView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
        @discord.ui.button(label="Click me!", style=discord.ButtonStyle.success, emoji="😎") # Create a button with the label "😎 Click me!" with color Blurple
        async def button_callback(self, button, interaction):
            await interaction.response.send_message("You clicked the button!") # Send a message when the button is clicked

    @bot.command(description="Test button") # Create a slash command
    async def button(ctx):
        await ctx.respond("This is a button!", view=MyView()) # Send a message with our View class that contains the button