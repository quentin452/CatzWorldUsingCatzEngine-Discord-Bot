import discord
from discord.ext import commands
import feedparser
import requests
import re
from bs4 import BeautifulSoup
import json
from Constants import ConstantsClass
from config import load_config
import asyncio

config = load_config()
api_key = config['api_key']
game_id = config['game_id']

class RssCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rss_task = None
        self.getting_rss = False
        self.rss_channel_ids = self.load_rss_channel_ids()
        self.sent_rss_titles = self.load_sent_rss_titles()  # Load sent RSS titles from file
        self.bot.loop.create_task(self.run_rss_loop())
        self.sent_rss_titles = []  # Initialize as needed
        self.rss_channel_ids = {}  # Initialize as needed
        
    def load_rss_channel_ids(self):
        try:
            with open(ConstantsClass.RSS_SAVE_FOLDER + ConstantsClass.RSS_CHANNEL_IDS_JSON_FILE, ConstantsClass.READ_FILE) as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_rss_channel_ids(self):
        with open(ConstantsClass.RSS_SAVE_FOLDER + ConstantsClass.RSS_CHANNEL_IDS_JSON_FILE, ConstantsClass.WRITE_TO_FILE) as f:
            json.dump(self.rss_channel_ids, f)

    def load_sent_rss_titles(self):
        try:
            with open(ConstantsClass.RSS_SAVE_FOLDER + ConstantsClass.SENT_RSS_TITLES_JSON_FILE, ConstantsClass.READ_FILE) as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_sent_rss_titles(self):
        with open(ConstantsClass.RSS_SAVE_FOLDER + ConstantsClass.SENT_RSS_TITLES_JSON_FILE, ConstantsClass.WRITE_TO_FILE) as f:
            json.dump(self.sent_rss_titles, f)

    def remove_extra_newlines(self, text):
        # Replace multiple newlines with a single newline
        return re.sub(r'\n\s*\n+', '\n\n', text)

    async def generate_embed_from_entry(self, entry):
        title = entry.get('title', 'Pas de titre')
        link = entry.get('link', 'Pas de lien')
        response = requests.get(link)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            section = soup.find('section', {'class': 'object_text_widget_widget base_widget user_formatted post_body'})

            if section:
                content = section.get_text(separator='\n')
                content = self.remove_extra_newlines(content)

                added = []
                fixed = []
                removed = []
                other = []

                for line in content.split('\n'):
                    stripped_line = line.strip()
                    if stripped_line:
                        if 'Added' in stripped_line or 'Add' in stripped_line:
                            added.append(f"<:Added:1262441172580831253> {stripped_line}")
                        elif 'Fixed' in stripped_line or 'Fix' in stripped_line or 'HotFix' in stripped_line:
                            fixed.append(f"<:Fixed:1262441171339448451> {stripped_line}")
                        elif 'Removed' in stripped_line or 'Delete' in stripped_line or 'Remove' in stripped_line:
                            removed.append(f"<:Removed:1262441169904730142> {stripped_line}")
                        else:
                            other.append(f"<:Other:1262453577872576554> {stripped_line}")

                embed = discord.Embed(title=title, url=link, color=discord.Color.blue())

                if added:
                    embed.add_field(name="Added", value="\n".join(added), inline=False)
                if fixed:
                    embed.add_field(name="Fixed", value="\n".join(fixed), inline=False)
                if removed:
                    embed.add_field(name="Removed", value="\n".join(removed), inline=False)
                if other:
                    embed.add_field(name="Other", value="\n".join(other), inline=False)

                embed.set_image(url="https://cdn.discordapp.com/attachments/1261580670057316453/1262477940843745422/DEVLOGS.webp?ex=6696bdb4&is=66956c34&hm=ec81d9d015b61327ab4d1e2bfb5f9638c148879429a0d9c76a3c6832138f8117&")
                # Add link to the devlog directly in the embed
                embed.add_field(name="See the Complete Devlog", value=f"[Click Here to see details]({link})", inline=False)
                return embed
            else:
                return f"**{title}**\nContenu non trouvé.\n<{link}>"
        else:
            return f"**{title}**\nImpossible de récupérer la page liée.\n<{link}>"

    @commands.command(help="Fetches and displays the latest entry from the RSS feed.")
    async def get_last_rss(self, ctx):
        feed = feedparser.parse(ConstantsClass.RSS_URL)
        if 'entries' in feed:
            last_entry = feed.entries[0]
            embed_or_message = await self.generate_embed_from_entry(last_entry)
            if isinstance(embed_or_message, discord.Embed):
                embed = embed_or_message
                message = await ctx.send(embed=embed)
            else:
                await ctx.send(embed_or_message)
        else:
            await ctx.send('Impossible de récupérer le flux RSS.')

    @commands.command(help="Fetches and displays all entries from the RSS feed. Requires administrator permissions.")
    @commands.has_permissions(administrator=True)
    async def get_all_rss(self, ctx):
        feed = feedparser.parse(ConstantsClass.RSS_URL)
        if 'entries' in feed:
            for entry in feed.entries:
                embed_or_message = await self.generate_embed_from_entry(entry)
                if isinstance(embed_or_message, discord.Embed):
                    embed = embed_or_message
                    message = await ctx.send(embed=embed)
                else:
                    await ctx.send(embed_or_message)
        else:
            await ctx.send('Impossible de récupérer le flux RSS.')

    async def last_rss_loop(self, channel):
        role = discord.utils.get(channel.guild.roles, name=ConstantsClass.ROLE_NAME)

        if role is None:
            await channel.send(f"Le rôle {ConstantsClass.ROLE_NAME} n'existe pas dans ce serveur.")
            return

        feed = feedparser.parse(ConstantsClass.RSS_URL)
        if 'entries' in feed:
            new_entries = [entry for entry in feed.entries if entry.get('title', 'Pas de titre') not in self.sent_rss_titles]

            if not new_entries:
                return

            for entry in new_entries:
                embed_or_message = await self.generate_embed_from_entry(entry)
                if isinstance(embed_or_message, discord.Embed):
                    await channel.send(content=f"{role.mention}", embed=embed_or_message)
                else:
                    await channel.send(f"{role.mention}\n{embed_or_message}")

                # Update sent RSS titles
                self.sent_rss_titles.append(entry.get('title'))
                self.save_sent_rss_titles()  # Save sent RSS titles to file
                break  # Only process the first new entry for now
        else:
            await channel.send(f"{role.mention} Impossible de récupérer le flux RSS.")

    async def send_button_message(self, channel, emoji, message, link):
        message_content = f"{emoji} {message}"
        await channel.send(message_content)

    async def run_rss_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            for guild_id, channel_id in self.rss_channel_ids.items():
                guild = self.bot.get_guild(int(guild_id))
                if guild:
                    channel = guild.get_channel(int(channel_id))
                    if channel:
                        if not self.getting_rss:
                            self.getting_rss = True
                            await self.last_rss_loop(channel)
                            self.getting_rss = False
                    else:
                        print(f"Channel with ID {channel_id} not found in guild {guild_id}.")
                else:
                    print(f"Guild with ID {guild_id} not found.")
            await asyncio.sleep(60)

async def setup(bot):
    await bot.add_cog(RssCommands(bot))