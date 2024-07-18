import discord
from discord.ext import commands

class BasicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Définition de la commande slash "hello"
    @discord.app_commands.command(name="hello", description="Greets the user with a hello message.")
    async def hello(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"Hello {member.mention}!")

async def setup(bot):
    # Ajoute le cog au bot
    await bot.add_cog(BasicCommands(bot))