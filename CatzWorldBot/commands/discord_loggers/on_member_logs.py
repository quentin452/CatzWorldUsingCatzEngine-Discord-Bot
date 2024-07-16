from discord.ext import commands
import discord
import asyncio
from datetime import datetime
from utils.Constants import ConstantsClass
from utils.async_logs import LogMessageAsync
from utils.EmbedUtility import *
from commands.discord_loggers.discord_logger_base import DiscordLogs
class OnMemberLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_log_channel_id(self):
        discord_logs_cog = self.bot.get_cog('DiscordLogs')
        if discord_logs_cog is not None:
            return discord_logs_cog.log_channel_id
        return None
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        self.log_channel_id = self.get_log_channel_id()
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                embed = MemberJoinedEmbed(member).create()
                await log_channel.send(embed=embed)
            except Exception as e:
                    await LogMessageAsync.LogAsync(f"Error logging member join: {e}")


    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        self.log_channel_id = self.get_log_channel_id()
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                await asyncio.sleep(1)  # Wait for a second before fetching the audit logs
                async for entry in after.guild.audit_logs(action=discord.AuditLogAction.member_update, limit=1):
                    user = entry.user
                    if before.nick != after.nick:
                        embed = discord.Embed(
                            title='Nickname Changed',
                            description=f'{after.name}#{after.discriminator} changed nickname',
                            color=discord.Color.blue()
                        )
                        embed.set_thumbnail(url=user.avatar.url)
                        embed.add_field(name='Before', value=before.nick if before.nick else 'None', inline=True)
                        embed.add_field(name='After', value=after.nick if after.nick else 'None', inline=True)
                        await log_channel.send(embed=embed)
                    if before.roles != after.roles:
                        added_roles = [role for role in after.roles if role not in before.roles]
                        removed_roles = [role for role in before.roles if role not in after.roles]
                        if added_roles:
                            roles_str = ', '.join([role.name for role in added_roles])
                            embed = discord.Embed(
                                title='Roles Added',
                                description=f'Roles added to {after.name}#{after.discriminator}: {roles_str}',
                                color=discord.Color.gold()
                            )
                            embed.set_thumbnail(url=user.avatar.url)
                            await log_channel.send(embed=embed)
                        if removed_roles:
                            roles_str = ', '.join([role.name for role in removed_roles])
                            embed = discord.Embed(
                                title='Roles Removed',
                                description=f'Roles removed from {after.name}#{after.discriminator}: {roles_str}',
                                color=discord.Color.dark_gold()
                            )
                            embed.set_thumbnail(url=user.avatar.url)
                            await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging member update: {e}")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        self.log_channel_id = self.get_log_channel_id()
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                embed = discord.Embed(
                    title='Member Banned',
                    description=f'{user.name}#{user.discriminator} has been banned from the server',
                    color=discord.Color.dark_red()
                )
                embed.set_thumbnail(url=user.avatar.url)
                embed.add_field(name='Member ID', value=user.id, inline=True)
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging member ban: {e}")

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        self.log_channel_id = self.get_log_channel_id()
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                embed = discord.Embed(
                    title='Member Unbanned',
                    description=f'{user.name}#{user.discriminator} has been unbanned from the server',
                    color=discord.Color.green()
                )
                embed.set_thumbnail(url=user.avatar.url)
                embed.add_field(name='Member ID', value=user.id, inline=True)
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging member unban: {e}")

    @commands.Cog.listener()
    async def on_member_boost(self, member):
        self.log_channel_id = self.get_log_channel_id()
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                embed = discord.Embed(
                    title='Member Boosted Server',
                    description=f'{member.name}#{member.discriminator} has boosted the server!',
                    color=discord.Color.gold()
                )
                embed.set_thumbnail(url=member.avatar.url)
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging member boost: {e}")

async def setup(bot):
    await bot.add_cog(OnMemberLogs(bot))