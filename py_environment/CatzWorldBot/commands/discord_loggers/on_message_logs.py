from discord.ext import commands
import discord
import re
from datetime import datetime
from utils.Constants import ConstantsClass
from utils.async_logs import LogMessageAsync
from utils.EmbedUtility import *

class OnMessageLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = ConstantsClass.load_channel_template(self, ConstantsClass.LOGS_SAVE_FOLDER + '/on_message_logs.json', 'on_message_logs')
        
    def save_log_channel(self, channel_id):
        ConstantsClass.save_channel_template(self, ConstantsClass.LOGS_SAVE_FOLDER + '/on_message_logs.json', 'on_message_logs', channel_id)
    
    @commands.command(help="Sets the log channel for (Message) logging events. Requires administrator permissions.")
    @commands.has_permissions(administrator=True)
    async def set_on_message_logs_channel(self, ctx):
        self.log_channel_id = ctx.channel.id
        self.save_log_channel(ctx.channel.id)
        await ctx.send(f"L'ID du canal de on_message_logs a été mis à jour à {ctx.channel.id}")

   #TODO FIX CREATED MESSAGES BEFORE LAUNCHING THE BOT CANNOT BE LOGGED
    @commands.Cog.listener()
    async def on_message_delete(self, message): 
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                channel = message.channel
                user = message.author
                embed = discord.Embed(
                    title='Message delete',
                    description=f'A message by {user.name} was deleted in {channel.name}. The message was: "{message.content}"',
                    color=discord.Color.orange()
                )
                embed.set_thumbnail(url=user.avatar.url)
                embed.add_field(name='Channel ID', value=channel.id, inline=True)
                embed.add_field(name='Date', value=discord.utils.utcnow(), inline=True)
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Erreur lors du logging de la suppression : {e}")

    @commands.Cog.listener()#TODO FIX CREATED MESSAGES BEFORE LAUNCHING THE BOT CANNOT BE LOGGED
    async def on_message_edit(self, before, after):
        await ConstantsClass.doNotLogMessagesFromAnotherBot(self, before)
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                if (before.content.strip() == '' and after.content.strip() == ''):
                    return
                embed = MessageEditEmbed(before, after).create()
                await log_channel.send(embed=embed)
            except Exception as e:
                await log_channel.send(f"Error logging message edit: {e}")

    

   
async def setup(bot):
    await bot.add_cog(OnMessageLogs(bot))