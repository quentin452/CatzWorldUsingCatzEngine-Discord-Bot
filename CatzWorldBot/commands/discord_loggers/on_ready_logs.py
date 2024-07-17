

from discord.ext import commands
import discord
import asyncio
from datetime import datetime
from utils.Constants import ConstantsClass
from utils.async_logs import LogMessageAsync
from utils.EmbedUtility import *
class OnReadyLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = ConstantsClass.load_channel_template(self,ConstantsClass.LOGS_SAVE_FOLDER + '/on_ready_logs.json','on_ready_logs')
        
    def save_log_channel(self, channel_id):
        ConstantsClass.save_channel_template(self,ConstantsClass.LOGS_SAVE_FOLDER + '/on_ready_logs.json','on_ready_logs',channel_id)
    
    @commands.command(help="Sets the log channel for (Ready) logging events. Requires administrator permissions.")
    @commands.has_permissions(administrator=True)
    async def set_on_ready_logs_channel(self, ctx):
        self.log_channel_id = ctx.channel.id
        self.save_log_channel(ctx.channel.id)
        await ctx.send(f"L'ID du canal de on_ready_logs a été mis à jour à {ctx.channel.id}")
    
    async def on_ready(self):
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