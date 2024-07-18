import discord
from discord.ext import commands


slash_command_test = discord.SlashCommandGroup("slash_command_test", "Math related commands")
class BasicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Définition de la commande slash "hello"
   # @commands.command(help="Greets the user with a hello message.")
    @slash_command_test.command(help="Greets the user with a hello message.")
    async def hello(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"Hello {member.mention}!")

def setup(bot):
    # Ajoute le cog au bot
    bot.add_cog(BasicCommands(bot))