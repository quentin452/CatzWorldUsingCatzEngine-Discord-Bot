from discord.ext import commands
import discord
from datetime import datetime
from utils.Constants import ConstantsClass
from utils.async_logs import LogMessageAsync
from utils.EmbedUtility import *
class OnChannelLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = ConstantsClass.load_channel_template(self,ConstantsClass.LOGS_SAVE_FOLDER + '/on_channel_logs.json','on_channel_logs_id')
        
    def save_log_channel(self, channel_id):
        ConstantsClass.save_channel_template(self,ConstantsClass.LOGS_SAVE_FOLDER + '/on_channel_logs.json','on_channel_logs_id',channel_id)
    
    @commands.command(help="Sets the log channel for (Channel) logging events. Requires administrator permissions.")
    @commands.has_permissions(administrator=True)
    async def set_on_channel_logs(self, ctx):
        self.log_channel_id = ctx.channel.id
        self.save_log_channel(ctx.channel.id)
        await ctx.send(f"L'ID du canal de on_channel_logs a été mis à jour à {ctx.channel.id}")

    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                if isinstance(entry.target, (discord.VoiceChannel, discord.TextChannel, discord.CategoryChannel)):
                    if entry.action == discord.AuditLogAction.channel_create:
                        channel_type = ConstantsClass.channel_type_map.get(entry.target.type, 'Unknown')
                        embed = discord.Embed(title=f'{channel_type} Channel created by {entry.user.name}', description=f'{entry.user.name} created a new channel: {entry.target.name}', color=discord.Color.green())
                    elif entry.action == discord.AuditLogAction.channel_update:
                        changes = [f"{k}: {v[0]} -> {v[1]}" for k, v in entry.changes.items()]
                        change_str = "\n".join(changes)
                        embed = discord.Embed(title=f'Channel updated by {entry.user.name}', description=f'{entry.user.name} updated the channel: {entry.target.name}\nChanges:\n{change_str}', color=discord.Color.blue())
                    else:
                        return  # Skip other actions

                    embed.set_thumbnail(url=entry.user.avatar.url)
                    embed.add_field(name='Channel ID', value=entry.target.id, inline=True)
                    embed.add_field(name='Type', value=channel_type, inline=True)
                    embed.add_field(name='Date', value=discord.utils.utcnow(), inline=True)
                    await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Erreur lors du logging de l'audit log : {e}")

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
                    user = entry.user
                    channel_type = ConstantsClass.channel_type_map.get(channel.type, 'Unknown')
                    embed = discord.Embed(
                        title=f'<:Removed:1262441169904730142> {channel_type} Channel removed by {user.name}', 
                        description=f'{user.name} deleted the channel : {channel.name}', 
                        color=discord.Color.red()
                    )
                    embed.set_thumbnail(url=user.avatar.url)
                    embed.add_field(name='Channel ID', value=channel.id, inline=True)
                    embed.add_field(name='Type', value=channel_type, inline=True)
                    embed.add_field(name='Date', value=discord.utils.utcnow(), inline=True)
                    await log_channel.send(embed=embed)
                    break  # Nous avons trouvé l'entrée pertinente, sortons de la boucle
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Erreur lors du logging de l'audit log : {e}")


    @commands.Cog.listener() #TODO FIX CREATED MESSAGES BEFORE LAUNCHING THE BOT CANNOT BE LOGGED
    async def on_guild_channel_update(self, before, after):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                # Collect before and after permission overwrites
                before_perms = {str(over.id): over for over in before.overwrites}
                after_perms = {str(over.id): over for over in after.overwrites}

                # Check if permissions have changed
                if before_perms != after_perms:
                    async for entry in after.guild.audit_logs(action=discord.AuditLogAction.channel_update, limit=1):
                        user = entry.user
                        channel_type = ConstantsClass.channel_type_map.get(after.type, 'Unknown')
                        embed = discord.Embed(
                            title=f'{channel_type} Channel permissions updated by {user.name}',
                            description=f'The permissions for the channel {after.name} have been updated',
                            color=discord.Color.blue()
                        )
                        embed.set_thumbnail(url=user.avatar.url)
                        embed.add_field(name='Channel ID', value=after.id, inline=True)
                        embed.add_field(name='Date', value=discord.utils.utcnow(), inline=True)
                        await log_channel.send(embed=embed)
                        break  # We have found the relevant entry, let's break the loop

            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error while logging the audit log: {e}")

async def setup(bot):
    await bot.add_cog(OnChannelLogs(bot))