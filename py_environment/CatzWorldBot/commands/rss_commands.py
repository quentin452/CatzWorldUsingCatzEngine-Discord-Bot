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
                embed.add_field(name="See the Complete Devlog", value=f"[Click Here to see details]({link})", inline=False)
                return embed

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
            if isinstance(embed_or_message, discord.Embed):
                await ctx.send(embed=embed_or_message)
            else:
                await ctx.send(embed_or_message)

    @commands.command(help="Fetches and displays all entries from the RSS feed. Requires administrator permissions.")
    @commands.has_permissions(administrator=True)
    async def get_all_rss(self, ctx):
        url = ConstantsClass.RSS_URL
        feed = await self.fetch_rss_feed(url)
        if feed:
            for entry in feed:
                embed_or_message = await self.generate_embed_from_entry(entry)
                if isinstance(embed_or_message, discord.Embed):
                    await ctx.send(embed=embed_or_message)
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
                if isinstance(embed_or_message, discord.Embed):
                    await channel.send(content=f"{role.mention}", embed=embed_or_message)
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