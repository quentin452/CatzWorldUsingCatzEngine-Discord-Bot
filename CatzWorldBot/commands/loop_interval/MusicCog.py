import discord
from discord.ext import commands, tasks
from utils.Constants import ConstantsClass
# Remplacer par l'ID du canal spécifique
class PeriodicTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_channel.start()
        self.voice_channel = ConstantsClass.load_channel_template(self, ConstantsClass.MUSIC_SAVE_FOLDER + '/on_music_channel.json', 'on_music_channel')

    def cog_unload(self):
        self.check_channel.cancel()

    @tasks.loop(minutes=4)
    async def check_channel(self):
        self.voice_channel = ConstantsClass.load_channel_template(self, ConstantsClass.MUSIC_SAVE_FOLDER + '/on_music_channel.json', 'on_music_channel')
        channel = self.bot.get_channel(self.voice_channel)
        if channel:
            async for message in channel.history(limit=1):
                last_message = message
                # Vérifiez si le dernier message contient une instance de HelpPagination
                if not last_message.embeds or (last_message.components and not isinstance(last_message.components[0], discord.ui.View)):
                    # Récupération du contexte du message
                    ctx = await self.bot.get_context(last_message)
                    # Vérifiez si la commande help_cat existe et invoquez-la avec le contexte
                    command = self.bot.get_command('help_cat')
                    if command is not None:
                        await ctx.invoke(command, 'MusicCog')
                break  # Nous avons seulement besoin du dernier message, donc nous sortons de la boucle

    @check_channel.before_loop
    async def before_check_channel(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(PeriodicTask(bot))