from discord.ext import commands
import json
import os
from utils.Constants import ConstantsClass

class TestCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.scores = self.load_scores()

    def load_scores(self):
        # Assurer que le répertoire existe
        os.makedirs(os.path.dirname(ConstantsClass.SCORE_SAVE_FILE), exist_ok=True)
        
        # Charger les scores à partir du fichier JSON, s'il existe
        if os.path.exists(ConstantsClass.SCORE_SAVE_FILE):
            with open(ConstantsClass.SCORE_SAVE_FILE, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    # En cas de fichier JSON corrompu ou vide
                    return {}
        else:
            return {}

    def save_scores(self):
        # Assurer que le répertoire existe
        os.makedirs(os.path.dirname(ConstantsClass.SCORE_SAVE_FILE), exist_ok=True)
        
        # Sauvegarder les scores dans le fichier JSON
        with open(ConstantsClass.SCORE_SAVE_FILE, 'w') as f:
            json.dump(self.scores, f, indent=4)  # Utilisation de indent=4 pour la lisibilité

    @commands.command(name="test", help="Incréments your score and displays it.")
    async def test(self, ctx):
        user_id = str(ctx.author.id)
        user_name = str(ctx.author.name)

        if user_id in self.scores:
            self.scores[user_id]['score'] += 1
        else:
            self.scores[user_id] = {'name': user_name, 'score': 1}

        self.save_scores()

        await ctx.send(f"Your score is now {self.scores[user_id]['score']}")

async def setup(bot):
    # Ajoute le cog au bot
    await bot.add_cog(TestCommands(bot))
