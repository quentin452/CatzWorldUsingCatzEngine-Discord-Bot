import discord
from discord.ext import commands
from discord.ui import Button, View
import random

# Données du jeu
zones = ['Foret', 'Plage', 'Montagne', 'Marais']
trésors = {'Foret': 10, 'Plage': 15, 'Montagne': 5, 'Marais': 20}  # Points pour chaque zone
pièges = {'Foret': -5, 'Plage': -3, 'Montagne': -10, 'Marais': -8}  # Pénalités pour chaque zone

class TreasureHuntView(View):
    def __init__(self):
        super().__init__()
        self.trésors_trouvés = 0
        self.zone_actuelle = None

    @discord.ui.button(label='Explorer la Foret', style=discord.ButtonStyle.green)
    async def forest_button(self, interaction: discord.Interaction, button: Button):
        await self.explore('Foret', interaction)

    @discord.ui.button(label='Explorer la Plage', style=discord.ButtonStyle.blurple)
    async def beach_button(self, interaction: discord.Interaction, button: Button):
        await self.explore('Plage', interaction)

    @discord.ui.button(label='Explorer la Montagne', style=discord.ButtonStyle.grey)
    async def mountain_button(self, interaction: discord.Interaction, button: Button):
        await self.explore('Montagne', interaction)

    @discord.ui.button(label='Explorer le Marais', style=discord.ButtonStyle.red)
    async def swamp_button(self, interaction: discord.Interaction, button: Button):
        await self.explore('Marais', interaction)

    async def explore(self, zone, interaction):
        self.zone_actuelle = zone
        result = random.choice(['trésor', 'piège'])
        if result == 'trésor':
            points = trésors[zone]
            self.trésors_trouvés += points
            await interaction.response.send_message(f"Vous avez trouvé un trésor dans la {zone} et gagné {points} points ! Vous avez maintenant {self.trésors_trouvés} points.")
        else:
            points = pièges[zone]
            self.trésors_trouvés += points
            await interaction.response.send_message(f"Vous êtes tombé dans un piège dans la {zone} et perdu {abs(points)} points. Vous avez maintenant {self.trésors_trouvés} points.")

class TreasureHunt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def start_hunt(self, ctx):
        view = TreasureHuntView()
        await ctx.send('Bienvenue dans le jeu de la chasse au trésor ! Cliquez sur les boutons pour explorer différentes zones.', view=view)

async def setup(bot):
    await bot.add_cog(TreasureHunt(bot))