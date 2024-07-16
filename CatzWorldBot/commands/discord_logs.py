import json
from discord.ext import commands
import discord
import os
import asyncio
from datetime import datetime
from utils.Constants import ConstantsClass
from utils.async_logs import LogMessageAsync
class DiscordLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = self.load_log_channel()
        
       
    def load_log_channel(self):
        if os.path.exists(ConstantsClass.LOGS_SAVE_FOLDER + '/log_channel.json'):
            with open(ConstantsClass.LOGS_SAVE_FOLDER + '/log_channel.json', 'r') as f:
                return json.load(f).get('log_channel_id')
        else:
            return None

    def save_log_channel(self, channel_id):
        with open(ConstantsClass.LOGS_SAVE_FOLDER + '/log_channel.json', 'w') as f:
            json.dump({'log_channel_id': channel_id}, f)  # Corrected the key here

    @commands.command(help="Sets the log channel for logging events. Requires administrator permissions.")
    @commands.has_permissions(administrator=True)
    async def set_log_channel(self, ctx):
        self.log_channel_id = ctx.channel.id
        self.save_log_channel(ctx.channel.id)

    channel_type_map = {
        discord.ChannelType.text: 'Text',
        discord.ChannelType.voice: 'Voice',
        discord.ChannelType.category: 'Category',
        discord.ChannelType.forum: 'Forum',
        discord.ChannelType.news: 'Announcement',
        discord.ChannelType.stage_voice: 'Stage',
        discord.ChannelType.media: 'Media',
        discord.ChannelType.news_thread: 'Announcement Thread',
        discord.ChannelType.private: 'Private',
        discord.ChannelType.private_thread: 'Private Thread',
        discord.ChannelType.public_thread: 'Public thread',
    # Ajoutez d'autres types de canaux ici si nécessaire
    }

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:  # Ne pas logger les messages des autres bots
            return
        
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                embed = discord.Embed(
                    title='Message Edited',
                    color=discord.Color.gold()
                )
                embed.add_field(name='User', value=before.author.mention, inline=False)
                embed.add_field(name='Before', value=before.content or "*(Empty)*", inline=False)
                embed.add_field(name='After', value=after.content or "*(Empty)*", inline=False)
                embed.add_field(name='Channel', value=before.channel.mention, inline=False)
                embed.set_footer(text=f"User ID: {before.author.id}")
                await log_channel.send(embed=embed)
            except Exception as e:
                await log_channel.send(f"Error logging message edit: {e}")
                
    @commands.Cog.listener()
    async def on_member_join(self, member):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                embed = discord.Embed(
                    title='Member Joined',
                    description=f'{member.name}#{member.discriminator} has joined the server',
                    color=discord.Color.green()
                )
                embed.set_thumbnail(url=member.avatar.url)
                embed.add_field(name='Member ID', value=member.id, inline=True)
                embed.add_field(name='Joined At', value=member.joined_at.strftime('%Y-%m-%d %H:%M:%S'), inline=True)
                await log_channel.send(embed=embed)
            except Exception as e:
                    await LogMessageAsync.LogAsync(f"Error logging member join: {e}")

    async def on_ready(self):
        if self.log_channel_id is None:
            self.log_channel_id = self.load_log_channel()

        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                embed = discord.Embed(
                    title='Bot Started',
                    description='The bot is now online and ready to be used.',
                    color=discord.Color.green()
                )
                await log_channel.send(embed=embed)
                await LogMessageAsync.LogAsync("Startup message sent successfully.")
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error sending startup message: {e}")
        else:
            await LogMessageAsync.LogAsync(f"Log channel with ID {self.log_channel_id} not found.")

    async def log_reaction_change(self, reaction, user, action):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                message = reaction.message
                embed = discord.Embed(
                    title=f'Reaction {action.capitalize()}',
                    description=f'{user.name}#{user.discriminator} {action} a reaction',
                    color=discord.Color.blue() if action == "added" else discord.Color.red()
                )
                embed.set_thumbnail(url=user.avatar.url)
                embed.add_field(name='Reaction', value=str(reaction.emoji), inline=True)
                embed.add_field(name='Message ID', value=message.id, inline=True)
                embed.add_field(name='Channel', value=message.channel.name, inline=True)
                embed.add_field(name='Message Content', value=message.content if message.content else 'Embed/Attachment', inline=True)
                embed.add_field(name='Date', value=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), inline=True)
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging reaction {action}: {e}")

    @commands.Cog.listener() #TODO FIX CREATED MESSAGES BEFORE LAUNCHING THE BOT CANNOT BE LOGGED
    async def on_reaction_add(self, reaction, user):
        await self.log_reaction_change(reaction, user, "added")


    @commands.Cog.listener() #TODO FIX CREATED MESSAGES BEFORE LAUNCHING THE BOT CANNOT BE LOGGED
    async def on_reaction_remove(self, reaction, user):
        await self.log_reaction_change(reaction, user, "removed")

    async def log_reaction_change(self, reaction, user, action):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                message = reaction.message
                embed = discord.Embed(
                    title=f'Reaction {action.capitalize()}',
                    description=f'{user.name}#{user.discriminator} {action} a reaction',
                    color=discord.Color.green() if action == "added" else discord.Color.red()
                )
                embed.set_thumbnail(url=user.avatar.url)
                embed.add_field(name='Reaction', value=str(reaction.emoji), inline=True)
                embed.add_field(name='Message ID', value=message.id, inline=True)
                embed.add_field(name='Channel', value=message.channel.name, inline=True)
                embed.add_field(name='Message Content', value=message.content if message.content else 'Embed/Attachment', inline=True)
                embed.add_field(name='Date', value=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), inline=True)
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging reaction {action}: {e}")

    @commands.Cog.listener() # TODO add log server exclusion/expulsions
    async def on_member_remove(self, member):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                embed = discord.Embed(
                    title='Member Left',
                    description=f'{member.name}#{member.discriminator} has left the server',
                    color=discord.Color.red()
                )
                embed.set_thumbnail(url=member.avatar.url)
                embed.add_field(name='Member ID', value=member.id, inline=True)
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging member leave: {e}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                # Check if member moved between voice channels
                if before.channel != after.channel:
                    if before.channel and after.channel:
                        # Member moved from one voice channel to another
                        embed = discord.Embed(
                            title='Member Moved Voice Channels',
                            description=f'{member.name}#{member.discriminator} moved from {before.channel.name} to {after.channel.name}',
                            color=discord.Color.dark_magenta()
                        )
                        await log_channel.send(embed=embed)
                    elif before.channel:
                        # Member left a voice channel
                        embed = discord.Embed(
                            title='Member Left Voice Channel',
                            description=f'{member.name}#{member.discriminator} left voice channel {before.channel.name}',
                            color=discord.Color.red()
                        )
                        await log_channel.send(embed=embed)
                    elif after.channel:
                        # Member joined a voice channel
                        embed = discord.Embed(
                            title='Member Joined Voice Channel',
                            description=f'{member.name}#{member.discriminator} joined voice channel {after.channel.name}',
                            color=discord.Color.green()
                        )
                        await log_channel.send(embed=embed)
                
                #TODO FIX STREAMING SECTION DOES NOT WORK
                # Check if member started or stopped streaming
                before_streaming = any(isinstance(activity, discord.Streaming) for activity in before.activities)
                after_streaming = any(isinstance(activity, discord.Streaming) for activity in after.activities)

                if before_streaming != after_streaming:
                    # Streaming status changed during voice state update
                    embed = discord.Embed(
                        title='Streaming Status Changed',
                        description=f'{member.name}#{member.discriminator} has {"started" if after_streaming else "stopped"} streaming.',
                        color=discord.Color.blue() if after_streaming else discord.Color.dark_blue()
                    )
                    embed.set_thumbnail(url=member.avatar.url)
                    await log_channel.send(embed=embed)

                # Check if member muted or unmuted themselves
                elif before.self_deaf != after.self_deaf:
                    action = 'Muted' if after.self_deaf else 'Unmuted'
                    embed = discord.Embed(
                        title=f'Member {action}',
                        description=f'{member.name}#{member.discriminator} {action.lower()} themselves in {after.channel.name}',
                        color=discord.Color.blue()
                    )
                    await log_channel.send(embed=embed)

            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging voice state update: {e}")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
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

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                channel = messages[0].channel  # Assuming all messages are from the same channel
                async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.message_bulk_delete, limit=1):
                    user = entry.user
                    embed = discord.Embed(
                        title='Bulk message delete',
                        description=f'{len(messages)} messages were deleted by {user.name} in {channel.name}',
                        color=discord.Color.orange()
                    )
                    embed.set_thumbnail(url=user.avatar.url)
                    embed.add_field(name='Channel ID', value=channel.id, inline=True)
                    embed.add_field(name='Date', value=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), inline=True)
                    await log_channel.send(embed=embed)
                    break  # Nous avons trouvé l'entrée pertinente, sortons de la boucle
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Erreur lors du logging de la suppression en masse : {e}")


    @commands.Cog.listener() # UNTESTED AND DONT KNOW HOW TO TEST TODO
    async def on_file_watch_event(self, event_name, watch_dir, filename):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                embed = discord.Embed(
                    title='File Watch Event',
                    description=f'File "{filename}" was renamed in directory "{watch_dir}".',
                    color=discord.Color.orange()
                )
                embed.add_field(name='Event Name', value=event_name, inline=True)
                embed.add_field(name='Directory', value=watch_dir, inline=True)
                embed.add_field(name='Date', value=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), inline=False)
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error logging file watch event: {e}")

    #TODO FIX CREATED MESSAGES BEFORE LAUNCHING THE BOT CANNOT BE LOGGED
    @commands.Cog.listener()
    async def on_message_delete(self, message): 
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                channel = message.channel
                user = message.author  # L'auteur du message
                embed = discord.Embed(
                    title='Message delete',
                    description=f'A message by {user.name} was deleted in {channel.name}. The message was: "{message.content}"',  # Ajoutez le contenu du message ici
                    color=discord.Color.orange()
                )
                embed.set_thumbnail(url=user.avatar.url)
                embed.add_field(name='Channel ID', value=channel.id, inline=True)
                embed.add_field(name='Date', value=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), inline=True)
                await log_channel.send(embed=embed)
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Erreur lors du logging de la suppression : {e}")


    @commands.Cog.listener()
    async def on_command(self, ctx):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                user = ctx.author
                channel = ctx.channel
                command = ctx.command
                channel_type = self.channel_type_map.get(channel.type, 'Unknown')
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

    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                if isinstance(entry.target, (discord.VoiceChannel, discord.TextChannel, discord.CategoryChannel)):
                    if entry.action == discord.AuditLogAction.channel_create:
                        channel_type = self.channel_type_map.get(entry.target.type, 'Unknown')
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
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
                    user = entry.user
                    channel_type = self.channel_type_map.get(channel.type, 'Unknown')
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
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel and before.name != after.name:
            try:
                async for entry in after.guild.audit_logs(action=discord.AuditLogAction.channel_update, limit=1):
                    user = entry.user
                    channel_type = self.channel_type_map.get(after.type, 'Unknown')
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
    await bot.add_cog(DiscordLogs(bot))