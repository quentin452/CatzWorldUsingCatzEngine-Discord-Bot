from discord.ext import commands
import discord
from utils.Constants import ConstantsClass
from utils.async_logs import LogMessageAsync
from datetime import datetime

class OnUserlogs(commands.Cog):
    def __init__(self, bot, discord_logs_cog):
        self.bot = bot
        self.discord_logs_cog = discord_logs_cog

    def get_log_channel_id(self):
        discord_logs_cog = self.bot.get_cog('DiscordLogs')
        if discord_logs_cog is not None:
            return discord_logs_cog.log_channel_id
        return None
    
    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry):
        log_channel_id =self.get_log_channel_id()
        log_channel = self.bot.get_channel(log_channel_id)
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
                    embed.add_field(name='Date', value=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), inline=True)
                    await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Erreur lors du logging de l'audit log : {e}")

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        log_channel_id = self.get_log_channel_id()
        log_channel = self.bot.get_channel(log_channel_id)
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
                    embed.add_field(name='Date', value=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), inline=True)
                    await log_channel.send(embed=embed)
                    break  # Nous avons trouvé l'entrée pertinente, sortons de la boucle
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Erreur lors du logging de l'audit log : {e}")

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        log_channel_id = self.get_log_channel_id()
        log_channel = self.bot.get_channel(log_channel_id)
        if log_channel and before.name != after.name:
            try:
                async for entry in after.guild.audit_logs(action=discord.AuditLogAction.channel_update, limit=1):
                    user = entry.user
                    channel_type = ConstantsClass.channel_type_map.get(after.type, 'Unknown')
                    embed = discord.Embed(
                        title=f'<:Fixed:1262441171339448451> {channel_type} Channel renamed by {user.name}',
                        description=f'The channel {before.name} has been renamed to {after.name}',
                        color=discord.Color.blue()
                    )
                    embed.set_thumbnail(url=user.avatar.url)
                    embed.add_field(name='Channel ID', value=after.id, inline=True)
                    embed.add_field(name='Date', value=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), inline=True)
                    await log_channel.send(embed=embed)
                    break  # We have found the relevant entry, let's break the loop
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error while logging the audit log: {e}")

async def setup(bot):
    discord_logs_cog = bot.get_cog('DiscordLogs')
    await bot.add_cog(OnUserlogs(bot, discord_logs_cog))
