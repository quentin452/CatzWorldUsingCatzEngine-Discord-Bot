from discord.ext import commands
import discord
from utils.Constants import ConstantsClass
from utils.async_logs import LogMessageAsync
from utils.EmbedUtility import *
class OnMemberLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = ConstantsClass.load_channel_template(self,ConstantsClass.LOGS_SAVE_FOLDER + '/on_member_logs.json','on_member_logs')
        
    def save_log_channel(self, channel_id):
        ConstantsClass.save_channel_template(self,ConstantsClass.LOGS_SAVE_FOLDER + '/on_member_logs.json','on_member_logs',channel_id)
    
    @commands.command(help="Sets the log channel for (Members) logging events. Requires administrator permissions.")
    @commands.has_permissions(administrator=True)
    async def set_on_member_logs_channel(self, ctx):
        self.log_channel_id = ctx.channel.id
        self.save_log_channel(ctx.channel.id)
        await ctx.send(f"L'ID du canal de on_member_logs a été mis à jour à {ctx.channel.id}")
        
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                # Log member nickname change
                if before.nick != after.nick:
                    embed = discord.Embed(
                        title='Member Nickname Changed',
                        description=f'{before.name} changed their nickname from "{before.nick}" to "{after.nick}".',
                        color=discord.Color.orange()
                    )
                    embed.add_field(name='Member ID', value=after.id, inline=True)
                    embed.add_field(name='Date', value=discord.utils.utcnow(), inline=True)
                    await log_channel.send(embed=embed)

                # Log role changes
                before_roles = set(before.roles)
                after_roles = set(after.roles)
                added_roles = after_roles - before_roles
                removed_roles = before_roles - after_roles

                if added_roles:
                    added_roles_names = ', '.join([role.name for role in added_roles])
                    embed = discord.Embed(
                        title='Roles Added',
                        description=f'{after.name} was given the roles: {added_roles_names}.',
                        color=discord.Color.green()
                    )
                    embed.add_field(name='Member ID', value=after.id, inline=True)
                    embed.add_field(name='Date', value=discord.utils.utcnow(), inline=True)
                    await log_channel.send(embed=embed)

                if removed_roles:
                    removed_roles_names = ', '.join([role.name for role in removed_roles])
                    embed = discord.Embed(
                        title='Roles Removed',
                        description=f'{after.name} lost the roles: {removed_roles_names}.',
                        color=discord.Color.red()
                    )
                    embed.add_field(name='Member ID', value=after.id, inline=True)
                    embed.add_field(name='Date', value=discord.utils.utcnow(), inline=True)
                    await log_channel.send(embed=embed)

                # Log changes to avatar
                if before.avatar != after.avatar:
                    embed = discord.Embed(
                        title='Avatar Changed',
                        description=f'{after.name} changed their avatar.',
                        color=discord.Color.orange()
                    )
                    embed.set_thumbnail(url=after.avatar.url)
                    embed.add_field(name='Member ID', value=after.id, inline=True)
                    embed.add_field(name='Date', value=discord.utils.utcnow(), inline=True)
                    await log_channel.send(embed=embed)

            except Exception as e:
                await log_channel.send(f"Error logging member update: {e}")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
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

def setup(bot):
    bot.add_cog(OnMemberLogs(bot))