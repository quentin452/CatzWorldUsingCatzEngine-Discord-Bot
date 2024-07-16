

from discord.ext import commands
import discord
import asyncio
from datetime import datetime
from utils.Constants import ConstantsClass
from utils.async_logs import LogMessageAsync
from utils.EmbedUtility import *
from commands.discord_loggers.discord_logger_base import DiscordLogs
class OnReadyLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    def get_log_channel_id(self):
        discord_logs_cog = self.bot.get_cog('DiscordLogs')
        if discord_logs_cog is not None:
            return discord_logs_cog.log_channel_id
        return None
    
    async def on_ready(self):
        self.log_channel_id = self.get_log_channel_id()
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                embed = BotStartedEmbed().create()
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error sending startup message: {e}")
        else:
            await LogMessageAsync.LogAsync(f"Log channel with ID {self.log_channel_id} not found.")

async def setup(bot):
    await bot.add_cog(OnReadyLogs(bot))