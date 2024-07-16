from discord.ext import commands
import discord
import asyncio
from datetime import datetime
from utils.Constants import ConstantsClass
from utils.async_logs import LogMessageAsync
from utils.EmbedUtility import *
from commands.discord_loggers.discord_logger_base import DiscordLogs
class OnCommandsLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    def get_log_channel_id(self):
        discord_logs_cog = self.bot.get_cog('DiscordLogs')
        if discord_logs_cog is not None:
            return discord_logs_cog.log_channel_id
        return None
    
    @commands.Cog.listener()
    async def on_command(self, ctx):
        self.log_channel_id = self.get_log_channel_id()
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                user = ctx.author
                channel = ctx.channel
                command = ctx.command
                channel_type = ConstantsClass.channel_type_map.get(channel.type, 'Unknown')
                embed = discord.Embed(
                    title=f'Command used by {user.name}', 
                    description=f'{user.name} used the command : {command}', 
                    color=discord.Color.blue()
                )
                embed.set_thumbnail(url=user.avatar.url)
                embed.add_field(name='Channel Name', value=channel.name, inline=True)
                embed.add_field(name='Channel ID', value=channel.id, inline=True)
                embed.add_field(name='Type', value=channel_type, inline=True)
                embed.add_field(name='Date', value=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), inline=True)
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Erreur lors du logging de la commande : {e}")


async def setup(bot):
    await bot.add_cog(OnCommandsLogs(bot))