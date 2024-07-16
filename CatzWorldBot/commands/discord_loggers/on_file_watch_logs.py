from discord.ext import commands
import discord
import asyncio
from datetime import datetime
from utils.Constants import ConstantsClass
from utils.async_logs import LogMessageAsync
from utils.EmbedUtility import *
from commands.discord_loggers.discord_logger_base import DiscordLogs
class OnFileWatch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    def get_log_channel_id(self):
        discord_logs_cog = self.bot.get_cog('DiscordLogs')
        if discord_logs_cog is not None:
            return discord_logs_cog.log_channel_id
        return None
    
    @commands.Cog.listener() # UNTESTED AND DONT KNOW HOW TO TEST TODO
    async def on_file_watch_event(self, event_name, watch_dir, filename):
        log_channel = self.get_log_channel_id()
        if log_channel:
            try:
                embed = discord.Embed(
                    title='File Watch Event',
                    description=f'File "{filename}" was renamed in directory "{watch_dir}".',
                    color=discord.Color.orange()
                )
                embed.add_field(name='Event Name', value=event_name, inline=True)
                embed.add_field(name='Directory', value=watch_dir, inline=True)
                embed.add_field(name='Date', value=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), inline=False)
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging file watch event: {e}")


async def setup(bot):
    await bot.add_cog(OnFileWatch(bot))