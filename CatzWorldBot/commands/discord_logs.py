import json
from discord.ext import commands
import discord
import os
from datetime import datetime, timedelta

class DiscordLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = self.load_log_channel()

    def load_log_channel(self):
        if os.path.exists('log_channel.json'):
            with open('log_channel.json', 'r') as f:
                return json.load(f).get('log_channel_id')
        else:
            # Si le fichier n'existe pas, retourne None
            return None

    def save_log_channel(self, channel_id):
        with open('log_channel.json', 'w') as f:
            json.dump({'log_channel_id': channel_id}, f)

    @commands.command()
    async def set_log_channel(self, ctx, channel: discord.TextChannel):
        self.log_channel_id = channel.id
        self.save_log_channel(channel.id)
        await ctx.send(f'Le channel de logs a été défini sur {channel.mention}')

    channel_type_map = {
        discord.ChannelType.text: 'Text',
        discord.ChannelType.voice: 'Voice',
        discord.ChannelType.category: 'Category',
        discord.ChannelType.forum: 'Forum',
        discord.ChannelType.news: 'Announcement',
        discord.ChannelType.stage_voice: 'Stage',
    # Ajoutez d'autres types de canaux ici si nécessaire
    }

    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                if isinstance(entry.target, (discord.VoiceChannel, discord.TextChannel, discord.CategoryChannel)):
                    channel_type = self.channel_type_map.get(entry.target.type, 'Unknown')
                    embed = discord.Embed(title=f'<:Added:1262441172580831253> {channel_type} Channel created by {entry.user.name}', description=f'{entry.user.name} created a new channel : {entry.target.name}', color=discord.Color.green())
                    embed.set_thumbnail(url=entry.user.avatar.url)
                    embed.add_field(name='Channel ID', value=entry.target.id, inline=True)
                    embed.add_field(name='Type', value=channel_type, inline=True)
                    embed.add_field(name='Date', value=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), inline=True)  # Ajout de la date comme un champ
                    await log_channel.send(embed=embed)
            except Exception as e:
                print(f"Erreur lors du logging de l'audit log : {e}")

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            try:
                async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
                    user = entry.user
                    channel_type = self.channel_type_map.get(channel.type, 'Unknown')
                    embed = discord.Embed(
                        title=f'<:Removed:1262441169904730142> {channel_type} Channel supprimé par {user.name}', 
                        description=f'{user.name} a supprimé le channel : {channel.name}', 
                        color=discord.Color.red()
                    )
                    embed.set_thumbnail(url=user.avatar.url)
                    embed.add_field(name='Channel ID', value=channel.id, inline=True)
                    embed.add_field(name='Type', value=channel_type, inline=True)
                    embed.add_field(name='Date', value=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), inline=True)
                    await log_channel.send(embed=embed)
                    break  # Nous avons trouvé l'entrée pertinente, sortons de la boucle
            except Exception as e:
                print(f"Erreur lors du logging de l'audit log : {e}")

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            if not log_channel.permissions_for(log_channel.guild.me).send_messages:
                print(f"Le bot n'a pas la permission d'envoyer des messages dans {log_channel.name}")
                return
            if not log_channel.permissions_for(log_channel.guild.me).embed_links:
                print(f"Le bot n'a pas la permission d'envoyer des embeds dans {log_channel.name}")
                return

            if before.name != after.name:
                embed = discord.Embed(title='Nom d\'utilisateur modifié', description=f'{before.name} a changé son nom en {after.name}', color=discord.Color.blue())
                embed.set_footer(text=f"Date : {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
                await log_channel.send(embed=embed)
            if before.avatar != after.avatar:
                embed = discord.Embed(title='Avatar modifié', description=f'{before.name} a changé son avatar', color=discord.Color.blue())
                embed.set_footer(text=f"Date : {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
                await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            if not log_channel.permissions_for(log_channel.guild.me).send_messages:
                print(f"Le bot n'a pas la permission d'envoyer des messages dans {log_channel.name}")
                return
            if not log_channel.permissions_for(log_channel.guild.me).embed_links:
                print(f"Le bot n'a pas la permission d'envoyer des embeds dans {log_channel.name}")
                return

            if before.status != after.status:
                embed = discord.Embed(title='Statut modifié', description=f'{before.name} est passé de {before.status} à {after.status}', color=discord.Color.blue())
                embed.set_footer(text=f"Date : {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
                await log_channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(DiscordLogs(bot))