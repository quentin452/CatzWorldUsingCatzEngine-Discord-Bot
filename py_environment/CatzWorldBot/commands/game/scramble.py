import discord
from discord.ext import commands
import random
import asyncio

class ScrambleGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Liste simplifiée de mots courants
        self.word_list = [
            "apple", "banana", "car", "dog", "house", "cat", "book", "pen", "computer", "table",
            "chair", "phone", "shoe", "shirt", "tree", "bed", "light", "window", "door", "key"
        ]
        self.active_games = {}  # Dictionnaire des jeux actifs
        self.game_tasks = {}  # Dictionnaire des tâches de délai

    @commands.command(help="Start a game of scrambled words.")
    async def scramble(self, ctx):
        # Vérifier si une partie est déjà en cours pour ce joueur
        if ctx.channel.id in self.active_games:
            await ctx.send("A game is already active in this channel. Please wait until the current game is over.")
            return
        
        # Choisir un mot au hasard et mélanger ses lettres
        word = random.choice(self.word_list)
        scrambled_word = ''.join(random.sample(word, len(word)))
        
        # Enregistrer le mot original et le canal pour vérification
        self.active_games[ctx.channel.id] = {
            'word': word,
            'scrambled_word': scrambled_word,
            'channel': ctx.channel
        }
        
        # Envoyer le mot mélangé
        await ctx.send(f"Unscramble this word: `{scrambled_word}`\nType your guess in the chat!")

        # Démarrer une tâche asynchrone pour gérer le délai
        if ctx.channel.id in self.game_tasks:
            self.game_tasks[ctx.channel.id].cancel()
        self.game_tasks[ctx.channel.id] = self.bot.loop.create_task(self.end_game_after_timeout(ctx.channel.id))

    async def end_game_after_timeout(self, channel_id):
        await asyncio.sleep(30)  # Attendre 30 secondes
        
        if channel_id in self.active_games:
            channel = self.active_games[channel_id]['channel']
            word = self.active_games[channel_id]['word']
            await channel.send(f"Time's up! The correct word was: `{word}`")
            del self.active_games[channel_id]  # Supprimer le jeu actif
            if channel_id in self.game_tasks:
                self.game_tasks[channel_id].cancel()  # Annuler la tâche de délai si le jeu a expiré

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignorer les messages du bot
        if message.author == self.bot.user:
            return
        
        # Vérifier si un jeu est actif dans le canal
        if message.channel.id in self.active_games:
            game = self.active_games[message.channel.id]
            
            # Vérifier la réponse du joueur
            if message.content.lower() == game['word'].lower():
                await message.channel.send(f"Congratulations {message.author.mention}! You guessed the word correctly!")
                del self.active_games[message.channel.id]  # Supprimer le jeu actif
                if message.channel.id in self.game_tasks:
                    self.game_tasks[message.channel.id].cancel()  # Annuler la tâche de délai si le mot est trouvé avant la fin

# Assurez-vous que le bot est configuré pour ajouter des cogs
async def setup(bot):
    await bot.add_cog(ScrambleGame(bot))
