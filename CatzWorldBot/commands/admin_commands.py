from discord.ext import commands

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Resets the channel by deleting all messages. Requires administrator permissions.")
    @commands.has_permissions(administrator=True)
    async def reset_channel(self, ctx):
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
        if isinstance(error, commands.MissingPermissions):
             ctx.send('Vous n\'avez pas la permission d\'utiliser cette commande.')
        else:
             ctx.send(f'Une erreur est survenue : {error}')

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
