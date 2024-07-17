import discord
from datetime import datetime
from utils.ColorUtility import ColorUtilityClass

class EmbedUtilityClass:

    @staticmethod
    def create_embed(title=None, description=None, color=None, thumbnail_url=None, fields=None, footer_text=None, image_url=None):
        embed = discord.Embed(
            title=title or "",
            description=description or "",
            color=color or discord.Color.default()
        )
        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)
        if fields:
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
        if footer_text:
            embed.set_footer(text=footer_text)
        if image_url:
            embed.set_image(url=image_url)
        embed.add_field(name='Date', value=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), inline=True)
        return embed
    

class MusicTopGGVoteEmbed(EmbedUtilityClass):
    def __init__(self, user):
        self.title = 'TopGG Vote Received'
        self.description = f"{user.name} ({user.id}) has voted for the bot on TopGG."
        self.color = 0x008000  # Green color for positive events
        self.thumbnail_url = user.avatar.url
        self.fields = [
            ('User', user.mention, True),
            ('User ID', str(user.id), False)
        ]

    def create(self):
        return super().create_embed(
            title=self.title,
            description=self.description,
            color=self.color,
            thumbnail_url=self.thumbnail_url,
            fields=self.fields
        )
    
class MusicPlayerErrorEmbed(EmbedUtilityClass):
    def __init__(self, error_message):
        self.title = 'Music Player Error'
        self.description = f"An error occurred in the music player:\n```\n{error_message}\n```"
        self.color = 0xFF0000  # Red color for errors
        self.fields = []

    def create(self):
        return super().create_embed(
            title=self.title,
            description=self.description,
            color=self.color,
            fields=self.fields
        )
    
class MusicAudioEventEmbed(EmbedUtilityClass):
    def __init__(self, event_type, details):
        self.title = 'Music Audio Event'
        self.description = f"An audio event occurred: {event_type}\nDetails:\n```\n{details}\n```"
        self.color = 0x0000FF  # Blue color for informational events
        self.fields = []

    def create(self):
        return super().create_embed(
            title=self.title,
            description=self.description,
            color=self.color,
            fields=self.fields
        )

class MusicNoResultEmbed(EmbedUtilityClass):
    def __init__(self, query):
        self.title = 'Music No Result'
        self.description = f"No results found for query:\n```\n{query}\n```"
        self.color = 0xFFA500  # Orange color for warnings
        self.fields = []

    def create(self):
        return super().create_embed(
            title=self.title,
            description=self.description,
            color=self.color,
            fields=self.fields
        )

class MusicQueueEndEmbed(EmbedUtilityClass):
    def __init__(self):
        self.title = 'Music Queue End'
        self.description = "The music queue has ended."
        self.color = 0x008000  # Green color for positive events
        self.fields = []

    def create(self):
        return super().create_embed(
            title=self.title,
            description=self.description,
            color=self.color,
            fields=self.fields
        )

class MusicTrackEventEmbed(EmbedUtilityClass):
    def __init__(self, event_type, track):
        self.title = 'Music Track Event'
        self.description = f"A track event occurred: {event_type}\nTrack:\n```\n{track}\n```"
        self.color = 0x0000FF  # Blue color for informational events
        self.fields = []

    def create(self):
        return super().create_embed(
            title=self.title,
            description=self.description,
            color=self.color,
            fields=self.fields
        )

class MusicTracksAddEmbed(EmbedUtilityClass):
    def __init__(self, tracks):
        self.title = 'Music Tracks Add'
        self.description = f"Tracks added:\n```\n{tracks}\n```"
        self.color = 0x008000  # Green color for positive events
        self.fields = []

    def create(self):
        return super().create_embed(
            title=self.title,
            description=self.description,
            color=self.color,
            fields=self.fields
        )

class MessageEditEmbed(EmbedUtilityClass):
    def __init__(self, before, after):
        self.title = 'Message Edited'
        self.description = ''
        self.color = ColorUtilityClass.get_color('edit')
        self.thumbnail_url = before.author.avatar.url
        self.fields = [
            ('User', before.author.mention, True),
            ('Channel', before.channel.mention, True),
            ('Before', before.content, False),
            ('After', after.content, False),
            ('User ID', f"{before.author.id}", False)
        ]

    def create(self):
        return super().create_embed(
            title=self.title,
            description=self.description,
            color=self.color,
            thumbnail_url=self.thumbnail_url,
            fields=self.fields
        )


class ProfilePictureChangedEmbed(EmbedUtilityClass):
    def __init__(self, before, after):
        self.title = 'Profile Picture Changed'
        self.description = ''
        self.color = ColorUtilityClass.get_color('default')
        self.thumbnail_url = before.avatar.url
        self.fields = [
            ('User', before.mention, True),
            ('User ID', before.id, True),
            ('Before', "Old profile picture above", False),
            ('After', "New profile picture below", False),
        ]

    def create(self):
        return super().create_embed(
            title=self.title,
            description=self.description,
            color=self.color,
            thumbnail_url=self.thumbnail_url,
            fields=self.fields
        )


class MemberJoinedEmbed(EmbedUtilityClass):
    def __init__(self, member):
        self.title = 'Member Joined'
        self.description=f'{member.name}#{member.discriminator} has joined the server',
        self.color = ColorUtilityClass.get_color('join')
        self.fields = [
            ('Member ID', member.id, True),
            ('Joined At', member.joined_at.strftime('%Y-%m-%d %H:%M:%S'), True),
        ]

    def create(self):
        return super().create_embed(
            title=self.title,
            description=self.description,
            color=self.color,
            fields=self.fields
        )

class BotStartedEmbed(EmbedUtilityClass):
    def __init__(self):
        self.title = 'Bot Started'
        self.description = "The bot is now online and ready to be used."
        self.color = ColorUtilityClass.get_color('join')

    def create(self):
        return super().create_embed(
            title=self.title,
            description=self.description,
            color=self.color,
        )


class ReactionAddedEmbed(EmbedUtilityClass):
    def __init__(self, author, reaction, user, action, message):
        self.title = f'Reaction {action.capitalize()}'
        self.description = f'{user.name}#{user.discriminator} {action} a reaction'
        self.color = ColorUtilityClass.get_color('default') if action == "added" else ColorUtilityClass.get_color('leave')
        self.thumbnail_url = user.avatar.url
        self.fields = [
            ('Reaction', str(reaction.emoji), True),
            ('Message ID', message.id, True),
            ('Channel', message.channel.name, True),
            ('Message Content', message.content if message.content else 'Embed/Attachment', True),
            ('User ID', f"{author.id}", False)  
        ]

    def create(self):
        return super().create_embed(
            title=self.title,
            description=self.description,
            color=self.color,
            thumbnail_url=self.thumbnail_url,
            fields=self.fields
        )


