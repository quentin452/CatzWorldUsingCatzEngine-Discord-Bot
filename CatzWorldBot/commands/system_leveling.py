import discord
from discord.ext import commands
import json
import os
import logging
import time
from utils.Constants import ConstantsClass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LevelingSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.levels = self.load_levels()
        self.cooldowns = {}  # Dictionary to manage user cooldowns
        self.COOLDOWN_TIME = 10  # Cooldown time in seconds
        self.level_channel_id = self.load_level_channel_ids()

    @commands.command(help="Sets the current channel as the level channel for automatic level up update.")
    async def set_levelling_channel(self, ctx):
        self.level_channel_id[str(ctx.guild.id)] = ctx.channel.id
        self.save_level_channel_ids()
        await ctx.send(f"L'ID du salon pour les levels a été défini sur {ctx.channel.id} pour le serveur {ctx.guild.name}")
        
    def load_level_channel_ids(self):
        try:
            with open(ConstantsClass.LEVELING_SAVE_FOLDER + '/sytems_leveling_ids.json', ConstantsClass.READ_FILE) as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_level_channel_ids(self):
        with open(ConstantsClass.LEVELING_SAVE_FOLDER + '/sytems_leveling_ids.json', ConstantsClass.WRITE_TO_FILE) as f:
            json.dump(self.level_channel_id, f)

    def load_levels(self):
        try:
            if os.path.exists(ConstantsClass.LEVELING_SAVE_FILE):
                with open(ConstantsClass.LEVELING_SAVE_FILE, "r") as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            logger.error(f"Error loading levels: {e}")
            return {}

    def save_levels(self):
        try:
            with open(ConstantsClass.LEVELING_SAVE_FILE, "w") as f:
                json.dump(self.levels, f)
        except Exception as e:
            logger.error(f"Error saving levels: {e}")

    def xp_for_next_level(self, level):
        """Returns the XP needed to reach the next level."""
        return 100 * level**2

    def calculate_level(self, xp):
        """Calculates the current level based on XP."""
        level = 1
        while xp >= self.xp_for_next_level(level):
            xp -= self.xp_for_next_level(level)
            level += 1
        return level

    def get_user_rank(self, user_id):
        """Gets the rank of the user in the leaderboard."""
        sorted_levels = sorted(self.levels.items(), key=lambda x: x[1]['xp'], reverse=True)
        for index, (uid, _) in enumerate(sorted_levels):
            if uid == user_id:
                return index + 1
        return None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        user_id = str(message.author.id)
        current_time = time.time()

        # Initialize data for new users
        if user_id not in self.levels:
            self.levels[user_id] = {"xp": 0, "level": 1}
            self.cooldowns[user_id] = 0

        # Check and update cooldown
        last_message_time = self.cooldowns.get(user_id, 0)
        if current_time - last_message_time >= self.COOLDOWN_TIME:
            self.levels[user_id]["xp"] += 10
            new_level = self.calculate_level(self.levels[user_id]["xp"])

            if new_level > self.levels[user_id]["level"]:
                self.levels[user_id]["level"] = new_level

                # Prepare and send the embed
                embed = discord.Embed(
                    color=discord.Color.green()
                )

                # Ajout des informations de l'auteur à l'embed
                embed.set_author(
                    name=f"{message.author.display_name} reached the level {new_level}!",     # Nom de l'auteur
                    icon_url=message.author.avatar.url    # URL de l'avatar de l'auteur
                )

                # Send the embed to the level-up channel
                level_channel_id = self.level_channel_id.get(str(message.guild.id))
                if level_channel_id:
                    channel = self.bot.get_channel(level_channel_id)
                    if channel:
                        try:
                            await channel.send(embed=embed)
                        except discord.DiscordException as e:
                            logger.error(f"Error sending level-up embed: {e}")

            # Update the last message time
            self.cooldowns[user_id] = current_time
            self.save_levels()

    @commands.command(name="level", help="Displays your current level, XP, and rank.")
    async def level(self, ctx):
        user_id = str(ctx.author.id)
        if user_id in self.levels:
            user_data = self.levels[user_id]
            current_level = user_data['level']
            current_xp = user_data['xp']
            xp_for_next = self.xp_for_next_level(current_level)
            xp_needed = xp_for_next - (current_xp % xp_for_next)
            rank = self.get_user_rank(user_id) or "Not ranked"

            embed = discord.Embed(title=f"{ctx.author.name}'s Level Information", color=discord.Color.blue())
            embed.add_field(name="Current Level", value=current_level, inline=False)
            embed.add_field(name="Current XP", value=current_xp, inline=False)
            embed.add_field(name="XP Needed for Next Level", value=xp_needed, inline=False)
            embed.add_field(name="Leaderboard Rank", value=f"Rank {rank}", inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send("You don't have a level yet.")

    @commands.command(name="leaderboard", help="Displays the leaderboard of users by XP.")
    async def leaderboard(self, ctx, page: int = 1):
        """Displays the leaderboard with pagination."""
        # Pagination settings
        ITEMS_PER_PAGE = 10
        sorted_levels = sorted(self.levels.items(), key=lambda x: x[1]['xp'], reverse=True)
        total_pages = (len(sorted_levels) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

        if page < 1 or page > total_pages:
            await ctx.send(f"Page {page} does not exist. Please choose a page between 1 and {total_pages}.")
            return

        start_index = (page - 1) * ITEMS_PER_PAGE
        end_index = start_index + ITEMS_PER_PAGE
        leaderboard_data = sorted_levels[start_index:end_index]

        embed = discord.Embed(title="Leaderboard", color=discord.Color.gold())
        embed.set_footer(text=f"Page {page}/{total_pages}")

        for index, (user_id, data) in enumerate(leaderboard_data, start=start_index + 1):
            try:
                user = await self.bot.fetch_user(int(user_id))
                embed.add_field(name=f"{index}. {user.name}", value=f"Level {data['level']} - {data['xp']} XP", inline=False)
            except discord.DiscordException as e:
                logger.error(f"Error fetching user: {e}")
                embed.add_field(name=f"{index}. User not found", value=f"Level {data['level']} - {data['xp']} XP", inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    # Add the cog to the bot
    await bot.add_cog(LevelingSystem(bot))
