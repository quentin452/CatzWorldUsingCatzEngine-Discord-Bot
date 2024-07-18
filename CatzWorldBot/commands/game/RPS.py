import discord
from discord.ext import commands
import random
import asyncio
import time

# Classe pour gérer le jeu de Pierre-Papier-Ciseaux
class RPSGame:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.choices = ['pierre', 'papier', 'ciseaux']
        self.start_time = time.time()

    async def play_round(self, ctx):
        # Envoyer un message pour démarrer le jeu
        await ctx.send(f"{self.player1.display_name} vs {self.player2.display_name}. Choisissez parmi : pierre, papier, ciseaux.")

        # Fonction pour gérer les réponses des joueurs
        def check(message):
            return message.author == self.current_player and message.channel == ctx.channel and message.content.lower() in self.choices

        while True:
            try:
                # Attendre la réponse du joueur actuel
                user_choice = await self.bot.wait_for('message', check=check, timeout=60.0)

                # Obtenir le choix du bot de manière aléatoire
                bot_choice = random.choice(self.choices)

                # Déterminer le résultat du round
                result = self.determine_winner(user_choice.content.lower(), bot_choice)

                # Envoyer le résultat du round
                await ctx.send(f"{self.current_player.display_name} a choisi {user_choice.content.lower()}. {self.player2.display_name} a choisi {bot_choice}. Résultat : {result}")

                # Changer de joueur pour le prochain round
                self.current_player = self.player2 if self.current_player == self.player1 else self.player1

            except asyncio.TimeoutError:
                await ctx.send("La partie a expiré. Quitter le jeu.")
                break

    def determine_winner(self, user_choice, bot_choice):
        if user_choice == bot_choice:
            return "Égalité !"
        elif (user_choice == "pierre" and bot_choice == "ciseaux") or \
             (user_choice == "papier" and bot_choice == "pierre") or \
             (user_choice == "ciseaux" and bot_choice == "papier"):
            return f"{self.current_player.display_name} a gagné !"
        else:
            return f"{self.player2.display_name} a gagné !"

# Cog pour gérer les commandes du jeu de pierre-papier-ciseaux
class RPSCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}

    @commands.command(help="Commence une partie de Pierre-Papier-Ciseaux contre un autre joueur.")
    async def rps(self, ctx, opponent: discord.Member):
        if ctx.author == opponent:
            await ctx.send("Vous ne pouvez pas jouer contre vous-même.")
            return

        if ctx.author.id in self.active_games or opponent.id in self.active_games:
            await ctx.send("Un des joueurs est déjà dans une partie en cours.")
            return

        game = RPSGame(ctx.author, opponent)
        self.active_games[ctx.author.id] = game
        self.active_games[opponent.id] = game

        await game.play_round(ctx)

        del self.active_games[ctx.author.id]
        del self.active_games[opponent.id]

async def setup(bot):
    await bot.add_cog(RPSGame(bot))