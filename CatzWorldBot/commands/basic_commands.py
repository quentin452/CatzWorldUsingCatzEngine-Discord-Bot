import discord
from discord.ext import commands
#TODO FIX INTEGRATION UNKNOWN
class BasicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="hello", description="Greets the user with a hello message.")
    async def hello(self, interaction: discord.Interaction, nom: str):
        await interaction.response.send_message(f"Hello {nom}!")

    @hello.autocomplete('nom')
    async def hello_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            discord.app_commands.Choice(name=nom, value=nom)
            for nom in ['Alice', 'Bob', 'Charlie']
            if current.lower() in nom.lower()
        ]

async def setup(bot):
    await bot.add_cog(BasicCommands(bot))