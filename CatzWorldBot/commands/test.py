import discord
from discord.ext import commands
from discord.ui import Button, View

class MyView(View):
    def __init__(self):
        super().__init__()
        self.add_item(Button(label="Cliquez-moi", style=discord.ButtonStyle.primary))

    @discord.ui.button(label="Essaie Mes commandes", style=discord.ButtonStyle.green)
    async def button_callback(self, button, interaction):
        await interaction.response.send_message("Merci d'avoir cliqué sur le bouton!")

@commands.command(help="test")
async def bouton(ctx):
    view = MyView()
    await ctx.send("Voici un bouton :", view=view)

async def setup(bot):
    await bot.add_cog(MyView(bot))