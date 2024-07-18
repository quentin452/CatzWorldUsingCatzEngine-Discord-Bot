import discord
from discord.ext import commands
from utils.Constants import ConstantsClass
from utils.async_logs import LogMessageAsync
from utils.EmbedUtility import *

class OnAdminLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = ConstantsClass.load_channel_template(self, ConstantsClass.LOGS_SAVE_FOLDER + '/on_admin_logs.json', 'on_admin_logs')
        
    def save_log_channel(self, channel_id):
        ConstantsClass.save_channel_template(self, ConstantsClass.LOGS_SAVE_FOLDER + '/on_admin_logs.json', 'on_admin_logs', channel_id)
    
    @commands.command(help="Sets the log channel for (Administration) logging events. Requires administrator permissions.")
    @commands.has_permissions(administrator=True)
    async def set_on_admin_logs_channel(self, ctx):
        self.log_channel_id = ctx.channel.id
        self.save_log_channel(ctx.channel.id)
        await ctx.send(f"L'ID du canal de on_message_logs a été mis à jour à {ctx.channel.id}")

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                embed = discord.Embed(
                    title='Role Created',
                    description=f'Role {role.name} (ID: {role.id}) was created in {role.guild.name}.',
                    color=discord.Color.green()
                )
                embed.add_field(name='Permissions', value=', '.join([perm[0] for perm in role.permissions if perm[1]]), inline=False)
                embed.add_field(name='Date', value=discord.utils.utcnow(), inline=True)
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Erreur lors du logging de la création de rôle : {e}")

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                changes = []
                if before.name != after.name:
                    changes.append(f'Name changed from {before.name} to {after.name}')
                if before.permissions != after.permissions:
                    changes.append('Permissions changed')
                if before.color != after.color:
                    changes.append(f'Color changed from {before.color} to {after.color}')
                if before.position != after.position:
                    changes.append(f'Position changed from {before.position} to {after.position}')
                
                if changes:
                    embed = discord.Embed(
                        title='Role Updated',
                        description=f'Role {before.name} (ID: {before.id}) was updated in {before.guild.name}.',
                        color=discord.Color.orange()
                    )
                    embed.add_field(name='Changes', value='\n'.join(changes), inline=False)
                    embed.add_field(name='Date', value=discord.utils.utcnow(), inline=True)
                    await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Erreur lors du logging de la modification de rôle : {e}")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                embed = discord.Embed(
                    title='Role Deleted',
                    description=f'Role {role.name} (ID: {role.id}) was deleted from {role.guild.name}.',
                    color=discord.Color.red()
                )
                embed.add_field(name='Permissions', value=', '.join([perm[0] for perm in role.permissions if perm[1]]), inline=False)
                embed.add_field(name='Date', value=discord.utils.utcnow(), inline=True)
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Erreur lors du logging de la suppression de rôle : {e}")

    @commands.Cog.listener() #TODO FIX NOT WORK
    async def on_emoji_update(self, before: discord.Emoji, after: discord.Emoji):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                embed = discord.Embed(
                    title='Emoji Updated',
                    description=f'Emoji {before.name} (ID: {before.id}) has been updated.',
                    color=discord.Color.blue()
                )
                embed.add_field(name='Before', value=f'Name: {before.name}\nID: {before.id}\n', inline=False)
                embed.add_field(name='After', value=f'Name: {after.name}\nID: {after.id}\n', inline=False)
                embed.add_field(name='Changes', value=f'{before} -> {after}', inline=False)
                embed.set_thumbnail(url=before.url)
                embed.add_field(name='Date', value=discord.utils.utcnow(), inline=True)
                await log_channel.send(embed=embed)
            except Exception as e:
                # Envoi d'un message d'erreur si quelque chose se passe mal
                await log_channel.send(f"Error logging emoji update: {e}")

    @commands.Cog.listener() #TODO FIX NOT WORK
    async def on_emoji_create(self, emoji: discord.Emoji):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                embed = discord.Embed(
                    title='Emoji Created',
                    description=f'New emoji created: {emoji.name} (ID: {emoji.id})',
                    color=discord.Color.green()
                )
                embed.add_field(name='Name', value=emoji.name, inline=True)
                embed.add_field(name='ID', value=emoji.id, inline=True)
                embed.set_thumbnail(url=emoji.url)
                embed.add_field(name='Date', value=discord.utils.utcnow(), inline=True)
                await log_channel.send(embed=embed)
            except Exception as e:
                await log_channel.send(f"Error logging emoji creation: {e}")

    @commands.Cog.listener() #TODO FIX NOT WORK
    async def on_emoji_delete(self, emoji: discord.Emoji):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                embed = discord.Embed(
                    title='Emoji Deleted',
                    description=f'Emoji deleted: {emoji.name} (ID: {emoji.id})',
                    color=discord.Color.red()
                )
                embed.add_field(name='Name', value=emoji.name, inline=True)
                embed.add_field(name='ID', value=emoji.id, inline=True)
                embed.set_thumbnail(url=emoji.url)
                embed.add_field(name='Date', value=discord.utils.utcnow(), inline=True)
                await log_channel.send(embed=embed)
            except Exception as e:
                await log_channel.send(f"Error logging emoji deletion: {e}")

    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                if before.name != after.name:
                    embed = discord.Embed(
                        title='Server Name Changed',
                        description=f'The server name was changed from "{before.name}" to "{after.name}".',
                        color=discord.Color.orange()
                    )
                    embed.add_field(name='Server ID', value=after.id, inline=True)
                    embed.add_field(name='Date', value=discord.utils.utcnow(), inline=True)
                    await log_channel.send(embed=embed)

                if before.icon != after.icon:
                    embed = discord.Embed(
                        title='Server Icon Changed',
                        description='The server icon was changed.',
                        color=discord.Color.orange()
                    )
                    embed.set_thumbnail(url=after.icon.url)
                    embed.add_field(name='Server ID', value=after.id, inline=True)
                    embed.add_field(name='Date', value=discord.utils.utcnow(), inline=True)
                    await log_channel.send(embed=embed)

                # Vous pouvez ajouter d'autres vérifications pour des modifications supplémentaires ici

            except Exception as e:
                await log_channel.send(f"Error logging server update: {e}")

def setup(bot):
    bot.add_cog(OnAdminLogs(bot))
