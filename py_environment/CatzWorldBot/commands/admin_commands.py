import discord
from discord.ext import commands

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Définition de la commande textuelle "reset_channel"
    @commands.command(name="reset_channel", help="Réinitialise le salon en supprimant tous les messages. Nécessite des permissions d'administrateur.")
    @commands.has_permissions(administrator=True)
    async def reset_channel(self, ctx):
        # Vérification des permissions d'administrateur
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("Vous n'avez pas la permission d'utiliser cette commande.")
            return

        def check_message(message):
            return True

        deleted = 0
        while True:
            deleted_messages = await ctx.channel.purge(limit=100, check=check_message)
            deleted += len(deleted_messages)
            if len(deleted_messages) < 100:
                break
        await ctx.send(f"Le salon a été réinitialisé. {deleted} messages ont été supprimés.")

    @reset_channel.error
    async def reset_channel_error(self, ctx, error):
        await ctx.send(f'Une erreur est survenue : {error}')

async def setup(bot):
    # Ajoute le cog au bot
    await bot.add_cog(AdminCommands(bot))
