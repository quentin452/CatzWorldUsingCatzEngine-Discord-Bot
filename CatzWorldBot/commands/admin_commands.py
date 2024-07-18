import discord
from discord.ext import commands

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Définition de la commande slash "reset_channel"
    @commands.command(help="Resets the channel by deleting all messages. Requires administrator permissions.")
    async def reset_channel(self, interaction: discord.Interaction):
        # Vérification des permissions d'administrateur
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
            return

        def check_message(message):
            return True

        deleted = 0
        while True:
            deleted_messages = await interaction.channel.purge(limit=100, check=check_message)
            deleted += len(deleted_messages)
            if len(deleted_messages) < 100:
                break
        await interaction.response.send_message(f"Le salon a été réinitialisé. {deleted} messages ont été supprimés.")

    @reset_channel.error
    async def reset_channel_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message(f'Une erreur est survenue : {error}', ephemeral=True)

def setup(bot):
    # Ajoute le cog au bot
    bot.add_cog(AdminCommands(bot))