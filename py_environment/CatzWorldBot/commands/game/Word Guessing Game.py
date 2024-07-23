import discord
from discord.ext import commands
import random

class WordGuessingGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.words = ["python", "javascript", "java", "c++", "csharp", "golang", "ruby", "php", "swift", "kotlin"]
        self.hints = {
            "python": "Un langage de programmation populaire pour l'apprentissage automatique et le développement web",
            "javascript": "Un langage de programmation principalement utilisé pour le développement web interactif",
            "java": "Un langage de programmation orienté objet utilisé pour le développement d'applications",
            "c++": "Un langage de programmation puissant et performant utilisé pour les jeux et les systèmes d'exploitation",
            "csharp": "Un langage de programmation moderne utilisé pour le développement d'applications .NET",
            "golang": "Un langage de programmation compilé et performant utilisé pour les applications web et les systèmes distribués",
            "ruby": "Un langage de programmation dynamique utilisé pour le développement web et l'automatisation",
            "php": "Un langage de programmation principalement utilisé pour le développement web côté serveur",
            "swift": "Un langage de programmation moderne développé par Apple pour iOS, macOS et autres plateformes",
            "kotlin": "Un langage de programmation moderne utilisé pour le développement Android et le développement backend"
        }

    @commands.command(help="Joue à un jeu de devinette de mot.")
    async def devinette_mot(self, ctx):
        """Lance un jeu de devinette de mot."""
        mot_secret = random.choice(self.words)
        essais = 0
        lettres_devinees = []

        await ctx.send(f"J'ai choisi un mot. Devine lequel !\n\nIndice : {self.hints[mot_secret]}")

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and len(msg.content) == 1 and msg.content.isalpha()

        while essais < 6:
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=60.0)
                lettre = msg.content.lower()
                essais += 1

                if lettre in lettres_devinees:
                    await ctx.send(f"Tu as déjà deviné la lettre '{lettre}' ! Essaie encore.")
                elif lettre in mot_secret:
                    lettres_devinees.append(lettre)
                    mot_affiche = "".join([l if l in lettres_devinees else "_" for l in mot_secret])
                    await ctx.send(f"Bien joué ! La lettre '{lettre}' est dans le mot.\n\n{mot_affiche}")
                    if "_" not in mot_affiche:
                        await ctx.send(f"Bravo ! Tu as deviné le mot '{mot_secret}' en {essais} essais.")
                        return
                else:
                    lettres_devinees.append(lettre)
                    await ctx.send(f"La lettre '{lettre}' n'est pas dans le mot. Essaie encore.")

            except TimeoutError:
                await ctx.send(f"Temps écoulé ! Le mot était '{mot_secret}'.")
                return

        await ctx.send(f"Tu as épuisé tes essais ! Le mot était '{mot_secret}'.")

async def setup(bot):
    await bot.add_cog(WordGuessingGame(bot))
