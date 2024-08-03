import discord
from discord.ext import commands
import asyncio
import aiohttp
import xml.etree.ElementTree as ET
from utils.Constants import ConstantsClass
from utils.config import load_config
from utils.async_logs import LogMessageAsync
import json
from lxml import html

config = load_config()
api_key = config['api_key']
game_id = config['game_id']

class RssCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rss_task = None
        self.getting_rss = False
        self.rss_channel_ids = self.load_rss_channel_ids()
        self.sent_rss_titles = self.load_sent_rss_titles()
        self.bot.loop.create_task(self.run_rss_loop())

    @commands.command(help="Sets the current channel as the rss channel for automatic updates.")
    async def set_rss_channel(self, ctx):
        self.rss_channel_ids[str(ctx.guild.id)] = ctx.channel.id
        self.save_rss_channel_ids()
        await ctx.send(f"L'ID du salon pour les messages RSS a été défini sur {ctx.channel.id} pour le serveur {ctx.guild.name}")

    def load_rss_channel_ids(self):
        try:
            with open(ConstantsClass.RSS_SAVE_FOLDER + ConstantsClass.RSS_CHANNEL_IDS_JSON_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_rss_channel_ids(self):
        with open(ConstantsClass.RSS_SAVE_FOLDER + ConstantsClass.RSS_CHANNEL_IDS_JSON_FILE, 'w') as f:
            json.dump(self.rss_channel_ids, f)

    def load_sent_rss_titles(self):
        try:
            with open(ConstantsClass.RSS_SAVE_FOLDER + ConstantsClass.SENT_RSS_TITLES_JSON_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_sent_rss_titles(self):
        with open(ConstantsClass.RSS_SAVE_FOLDER + ConstantsClass.SENT_RSS_TITLES_JSON_FILE, 'w') as f:
            json.dump(self.sent_rss_titles, f)

    async def generate_embed_from_entry(self, entry):
        title = entry.get('title', 'Pas de titre')
        link = entry.get('link', 'Pas de lien')

        async with aiohttp.ClientSession() as session:
            async with session.get(link) as response:
                if response.status != 200:
                    return f"**{title}**\nImpossible de récupérer la page liée.\n<{link}>"

                content = await response.text()
                doc = html.fromstring(content)
                section = doc.xpath('//section[@class="object_text_widget_widget base_widget user_formatted post_body"]')

                if not section:
                    return f"**{title}**\nContenu non trouvé.\n<{link}>"

                content_html = section[0]
                content = self.extract_text_with_newlines(content_html)

                added = []
                fixed = []
                removed = []
                other = []

                for line in content.split('\n'):
                    stripped_line = line.strip()
                    if stripped_line:
                        lowered_line = stripped_line.lower()
                        if 'added' in lowered_line or 'add' in lowered_line:
                            added.append(f"<:Added:1262441172580831253> {stripped_line}")
                        elif 'fixed' in lowered_line or 'fix' in lowered_line or 'hotfix' in lowered_line:
                            fixed.append(f"<:Fixed:1262441171339448451> {stripped_line}")
                        elif 'removed' in lowered_line or 'delete' in lowered_line or 'remove' in lowered_line:
                            removed.append(f"<:Removed:1262441169904730142> {stripped_line}")
                        else:
                            other.append(f"<:Other:1262453577872576554> {stripped_line}")

                fields = {
                    "Added": "\n".join(added),
                    "Fixed": "\n".join(fixed),
                    "Removed": "\n".join(removed),
                    "Other": "\n".join(other)
                }

                embeds = []
                current_embed = discord.Embed(title=title, url=link, color=discord.Color.blue())
                current_length = 0

                def create_new_embed():
                    nonlocal current_length
                    if current_length > 0:
                        embeds.append(current_embed)
                    current_embed = discord.Embed(title=title, url=link, color=discord.Color.blue())
                    current_length = 0

                def add_field(name, value):
                    nonlocal current_length
                    if len(value) + current_length > 6000:
                        create_new_embed()
                    current_embed.add_field(name=name, value=value, inline=False)
                    current_length += len(value)

                for name, value in fields.items():
                    if value:
                        while len(value) > 1024:
                            part = value[:1020] + " ..."
                            add_field(name, part)
                            value = value[1024:]
                        if value:
                            add_field(name, value)

                if current_embed.fields:
                    embeds.append(current_embed)

                for embed in embeds:
                    embed.add_field(name="See the Complete Devlog", value=f"[Click Here to see details]({link})", inline=False)

                return embeds
                
    def extract_text_with_newlines(self, element):
            text = []
            for elem in element.iter():
                if elem.tag in ('p', 'br', 'div'):
                    text.append('\n')
                if elem.text:
                    text.append(elem.text)
                if elem.tail:
                    text.append(elem.tail)
            return ''.join(text)

    @commands.command(help="Fetches and displays the latest entry from the RSS feed.")
    async def get_last_rss(self, ctx):
        url = ConstantsClass.RSS_URL
        feed = await self.fetch_rss_feed(url)
        if feed:
            last_entry = feed[0]
            embed_or_message = await self.generate_embed_from_entry(last_entry)
            if isinstance(embed_or_message, list):
                for embed in embed_or_message:
                    await ctx.send(embed=embed)
            else:
                await ctx.send(embed_or_message)

    async def last_rss_loop(self, channel):
        role = discord.utils.get(channel.guild.roles, name=ConstantsClass.CATZ_WORLD_ROLE_NAME)
        if role is None:
            await channel.send(f"Le rôle {ConstantsClass.CATZ_WORLD_ROLE_NAME} n'existe pas dans ce serveur.")
            return

        url = ConstantsClass.RSS_URL
        feed = await self.fetch_rss_feed(url)
        if feed:
            new_entries = [entry for entry in feed if entry.get('title') not in self.sent_rss_titles]
            if not new_entries:
                return

            for entry in new_entries:
                embed_or_message = await self.generate_embed_from_entry(entry)
                if isinstance(embed_or_message, list):
                    for embed in embed_or_message:
                        await channel.send(content=f"{role.mention}", embed=embed)
                else:
                    await channel.send(f"{role.mention}\n{embed_or_message}")

                self.sent_rss_titles.append(entry.get('title'))
                self.save_sent_rss_titles()
                break  # Only process the first new entry for now

    async def fetch_rss_feed(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await LogMessageAsync.LogAsync(f"Failed to fetch RSS feed: {resp.status}")
                    return []

                try:
                    tree = ET.fromstring(await resp.text())
                except ET.ParseError as e:
                    await LogMessageAsync.LogAsync(f"Failed to parse RSS feed: {e}")
                    return []

                entries = []

                for item in tree.findall('.//item'):
                    entry = {
                        'title': item.find('title').text,
                        'link': item.find('link').text
                    }
                    entries.append(entry)
                return entries

    async def run_rss_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
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
                            await LogMessageAsync.LogAsync(f"Channel with ID {channel_id} not found in guild {guild_id}.")
                    else:
                        await LogMessageAsync.LogAsync(f"Guild with ID {guild_id} not found.")
            except Exception as e:
                await LogMessageAsync.LogAsync(f"Error in RSS loop: {e}")

            await asyncio.sleep(60)

async def setup(bot):
    await bot.add_cog(RssCommands(bot))