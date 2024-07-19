import discord
from discord.ext import commands
from discord.ui import Button, View
import random
import json
from utils.Constants import ConstantsClass
import os
class StoryGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stories = self.load_stories()
        self.current_story = None
        self.current_player = None
        self.current_choice = None
        self.players = {}  # Stocke les joueurs et leurs scores
        
    def load_stories(self):
        """Charge les histoires depuis un fichier JSON."""
        try:
            filename = ConstantsClass.STORIES_DATA_FOLDER + '/stories.json'
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    stories = json.load(f)
                    if not stories:
                        print("Aucune histoire trouvée dans le fichier.")
                    return stories
            else:
                print("Le fichier des histoires est introuvable.")
                return {}
        except FileNotFoundError:
            print("Le fichier des histoires est introuvable.")
            return {}

    @commands.command(name="histoire", help="Joue à un jeu d'histoire interactive.")
    async def histoire(self, ctx):
        """Lance un jeu d'histoire interactive."""
        if self.current_story is not None:
            await ctx.send("Une partie d'histoire est déjà en cours. Veuillez attendre la fin de la partie actuelle.")
            return

        if not self.stories:
            await ctx.send("Aucune histoire n'est disponible.")
            return

        self.current_story = random.choice(list(self.stories.values()))
        self.current_player = ctx.author
        self.players[self.current_player.id] = {"score": 0}
        self.current_choice = None

        await self.show_story_part(ctx)

    async def show_story_part(self, ctx_or_interaction):
        """Affiche une partie de l'histoire et les choix possibles."""
        if self.current_story:
            # Déterminer si l'argument est un contexte ou une interaction
            if isinstance(ctx_or_interaction, discord.Interaction):
                ctx = ctx_or_interaction
            else:
                ctx = ctx_or_interaction
            
            current_part = self.current_story.get(self.current_choice or "start", None)
            if current_part:
                embed = discord.Embed(
                    title=self.current_story.get("title", "Aventure"),
                    description=current_part.get("text", "Texte de l'histoire non disponible."),
                    color=discord.Color.blue()
                )
                choices = current_part.get("choices", [])
                if choices:
                    view = StoryChoiceView(self, choices)
                    if isinstance(ctx, discord.Interaction):
                        await ctx.response.edit_message(embed=embed, view=view)  # Edit the original message
                    else:
                        await ctx.send(embed=embed, view=view)
                else:
                    if isinstance(ctx, discord.Interaction):
                        await ctx.response.edit_message(embed=embed)
                    else:
                        await ctx.send(embed=embed)
                    await self.end_story(ctx)
            else:
                if isinstance(ctx, discord.Interaction):
                    await ctx.response.send_message("Erreur : partie d'histoire introuvable.")
                else:
                    await ctx.send("Erreur : partie d'histoire introuvable.")
                self.current_story = None

    async def handle_choice(self, interaction: discord.Interaction, choice_index):
        """Gère le choix du joueur."""
        if self.current_story:
            current_part = self.current_story.get(self.current_choice, None)
            choices = current_part.get("choices", []) if current_part else []
            if 0 <= choice_index < len(choices):
                self.current_choice = choices[choice_index].get("next_part")
                await self.show_story_part(interaction)  # Pass the interaction object
            else:
                if not interaction.response.is_done():
                    await interaction.response.send_message("Choix invalide.")
        else:
            if not interaction.response.is_done():
                await interaction.response.send_message("Aucune histoire en cours.")

    async def end_story(self, ctx):
        """Termine l'histoire et affiche le score."""
        self.current_story = None
        self.current_choice = None
        score = self.players.get(self.current_player.id, {}).get("score", 0)
        await ctx.send(f"Fin de l'histoire ! Votre score : {score}")

class StoryChoiceView(View):
    def __init__(self, game, choices):
        super().__init__()
        self.game = game
        self.max_buttons = 5  # Limitez le nombre de boutons à 5 ou moins
        for i, choice in enumerate(choices[:self.max_buttons]):
            self.add_item(StoryChoiceButton(choice, i))

    def disable_all_buttons(self):
        """Désactive tous les boutons de la vue."""
        for child in self.children:
            if isinstance(child, Button):
                child.disabled = True
        self.stop()  # Arrête la vue et désactive les interactions futures

class StoryChoiceButton(Button):
    def __init__(self, choice, index):
        super().__init__(label=choice["text"], style=discord.ButtonStyle.blurple)
        self.choice_index = index

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.view.game.handle_choice(interaction, self.choice_index)
        self.view.disable_all_buttons()  # Désactivez après avoir géré le choix

class StoryChoiceButton(Button):
    def __init__(self, choice, index):
        super().__init__(label=choice["text"], style=discord.ButtonStyle.blurple)
        self.choice_index = index

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.view.game.handle_choice(interaction, self.choice_index)
        self.view.disable_all_buttons()  # Désactivez après avoir géré le choix

async def setup(bot):
    await bot.add_cog(StoryGame(bot))