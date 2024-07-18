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

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                channel = messages[0].channel
                async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.message_bulk_delete, limit=1):
                    user = entry.user
                    embed = discord.Embed(
                        title='Bulk message delete',
                        description=f'{len(messages)} messages were deleted by {user.name} in {channel.name}',
                        color=discord.Color.orange()
                    )
                    embed.set_thumbnail(url=user.avatar.url)
                    embed.add_field(name='Channel ID', value=channel.id, inline=True)
                    embed.add_field(name='Date', value=discord.utils.utcnow(), inline=True)
                    await log_channel.send(embed=embed)
                    break
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Erreur lors du logging de la suppression en masse : {e}")

    @commands.Cog.listener() # TODO FIX NOT WORKING
    async def on_message(self, message):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel and not message.author.bot:
            try:
                invite_pattern = r"(https:\/\/discord\.gg\/[a-zA-Z0-9]+|https:\/\/discordapp\.com\/invite\/[a-zA-Z0-9]+|discord\.gg\/[a-zA-Z0-9]+|discordapp\.com\/invite\/[a-zA-Z0-9]+)"
                invites = re.findall(invite_pattern, message.content)
                if invites:
                    user = message.author
                    channel = message.channel
                    invite_links = ', '.join(invites)
                    embed = discord.Embed(
                        title='Invitation link posted',
                        description=f'{user.name} posted an invitation link in {channel.name}: {invite_links}',
                        color=discord.Color.blue()
                    )
                    embed.set_thumbnail(url=user.avatar.url)
                    embed.add_field(name='Channel ID', value=channel.id, inline=True)
                    embed.add_field(name='Date', value=discord.utils.utcnow(), inline=True)
                    await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Erreur lors du logging des invitations : {e}")

async def setup(bot):
    await bot.add_cog(OnMessageLogs(bot))