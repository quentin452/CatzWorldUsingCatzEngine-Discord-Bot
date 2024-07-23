import discord
from discord.ext import commands
from discord.ui import Button, View
import random
import json
import os
import logging
from utils.Constants import ConstantsClass

logging.basicConfig(level=logging.DEBUG)

# Game Data
zones = ['Forest', 'Beach', 'Mountain', 'Swamp']
treasures = {'Forest': 10, 'Beach': 15, 'Mountain': 5, 'Swamp': 20}  # Points for each zone
traps = {'Forest': -5, 'Beach': -3, 'Mountain': -10, 'Swamp': -8}  # Penalties for each zone

class TreasureHuntView(View):
    def __init__(self, player_data):
        super().__init__()
        self.player_data = player_data
        self.current_zone = None

    @discord.ui.button(label='Explore the Forest', style=discord.ButtonStyle.green)
    async def forest_button(self, interaction: discord.Interaction, button: Button):
        await self.explore('Forest', interaction)

    @discord.ui.button(label='Explore the Beach', style=discord.ButtonStyle.blurple)
    async def beach_button(self, interaction: discord.Interaction, button: Button):
        await self.explore('Beach', interaction)

    @discord.ui.button(label='Explore the Mountain', style=discord.ButtonStyle.grey)
    async def mountain_button(self, interaction: discord.Interaction, button: Button):
        await self.explore('Mountain', interaction)

    @discord.ui.button(label='Explore the Swamp', style=discord.ButtonStyle.red)
    async def swamp_button(self, interaction: discord.Interaction, button: Button):
        await self.explore('Swamp', interaction)

    async def explore(self, zone, interaction):
        self.current_zone = zone
        result = random.choice(['treasure', 'trap'])
        if result == 'treasure':
            points = treasures[zone]
            self.player_data['points'] += points
            self.player_data['successes'] += 1
            await interaction.response.send_message(f"You found a treasure in the {zone} and gained {points} points! You now have {self.player_data['points']} points.", delete_after=5)
        else:
            points = traps[zone]
            self.player_data['points'] += points
            self.player_data['failures'] += 1
            await interaction.response.send_message(f"You fell into a trap in the {zone} and lost {abs(points)} points. You now have {self.player_data['points']} points.", delete_after=5)
        self.save_data()

    def save_data(self):
        os.makedirs(os.path.dirname(ConstantsClass.TREASURE_HUNT_SAVE_FILE), exist_ok=True)
        try:
            with open(ConstantsClass.TREASURE_HUNT_SAVE_FILE, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        data[self.player_data['id']] = self.player_data
        with open(ConstantsClass.TREASURE_HUNT_SAVE_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        logging.debug(f"Saved data: {self.player_data}")

class TreasureHunt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.player_data = self.load_data()

    def load_data(self):
        try:
            with open(ConstantsClass.TREASURE_HUNT_SAVE_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @commands.command()
    async def start_hunt(self, ctx):
        user_id = str(ctx.author.id)
        if user_id not in self.player_data:
            self.player_data[user_id] = {
                'id': user_id,
                'nickname': ctx.author.display_name,
                'points': 0,
                'successes': 0,
                'failures': 0
            }
        view = TreasureHuntView(self.player_data[user_id])
        await ctx.send('Welcome to the treasure hunt game! Click the buttons to explore different zones.', view=view)

    @commands.command()
    async def hunt_stats(self, ctx):
        user_id = str(ctx.author.id)
        if user_id in self.player_data:
            stats = self.player_data[user_id]
            await ctx.send(f"Statistics for {ctx.author.display_name}:\nPoints: {stats['points']}\nSuccesses: {stats['successes']}\nFailures: {stats['failures']}")
        else:
            await ctx.send("No statistics found for you. Play first to get statistics.")

async def setup(bot):
    await bot.add_cog(TreasureHunt(bot))
