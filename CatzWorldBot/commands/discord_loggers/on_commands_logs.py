from discord.ext import commands
import discord
import asyncio
from datetime import datetime
from utils.Constants import ConstantsClass
from utils.async_logs import LogMessageAsync
from utils.EmbedUtility import *
class OnCommandsLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = ConstantsClass.load_channel_template(self,ConstantsClass.LOGS_SAVE_FOLDER + '/on_commands_logs.json','on_commands_logs')
        
    def save_log_channel(self, channel_id):
        ConstantsClass.save_channel_template(self,ConstantsClass.LOGS_SAVE_FOLDER + '/on_commands_logs.json','on_commands_logs',channel_id)
    
    @commands.command(help="Sets the log channel for (Commands) logging events. Requires administrator permissions.")
    @commands.has_permissions(administrator=True)
    async def set_on_commands_logs_channel(self, ctx):
        self.log_channel_id = ctx.channel.id
        self.save_log_channel(ctx.channel.id)
        await ctx.send(f"L'ID du canal de on_commands_logs a été mis à jour à {ctx.channel.id}")
    
    @commands.Cog.listener()
    async def on_command(self, ctx):
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
                embed.add_field(name='Date', value=discord.utils.utcnow(), inline=True)
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Erreur lors du logging de la commande : {e}")


def setup(bot):
    bot.add_cog(OnCommandsLogs(bot))