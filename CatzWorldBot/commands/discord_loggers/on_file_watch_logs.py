from discord.ext import commands
import discord
from datetime import datetime
from utils.Constants import ConstantsClass
from utils.async_logs import LogMessageAsync
from utils.EmbedUtility import *
class OnFileWatch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = ConstantsClass.load_channel_template(self,ConstantsClass.LOGS_SAVE_FOLDER + '/on_file_watch_logs.json','on_file_watch_logs')
        
    def save_log_channel(self, channel_id):
        ConstantsClass.save_channel_template(self,ConstantsClass.LOGS_SAVE_FOLDER + '/on_file_watch_logs.json','on_file_watch_logs',channel_id)
    
    @commands.command(help="Sets the log channel for (File Watch) logging events. Requires administrator permissions.")
    @commands.has_permissions(administrator=True)
    async def set_on_file_watch_logs_channel(self, ctx):
        self.log_channel_id = ctx.channel.id
        self.save_log_channel(ctx.channel.id)
        await ctx.send(f"L'ID du canal de on_file_watch_logs a été mis à jour à {ctx.channel.id}")

    @commands.Cog.listener() # UNTESTED AND DONT KNOW HOW TO TEST TODO
    async def on_file_watch_event(self, event_name, watch_dir, filename):
        if self.log_channel:
            try:
                embed = discord.Embed(
                    title='File Watch Event',
                    description=f'File "{filename}" was renamed in directory "{watch_dir}".',
                    color=discord.Color.orange()
                )
                embed.add_field(name='Event Name', value=event_name, inline=True)
                embed.add_field(name='Directory', value=watch_dir, inline=True)
                embed.add_field(name='Date', value=discord.utils.utcnow(), inline=False)
                await self.log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging file watch event: {e}")


def setup(bot):
    bot.add_cog(OnFileWatch(bot))