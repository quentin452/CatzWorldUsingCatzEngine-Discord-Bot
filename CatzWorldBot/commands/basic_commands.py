import discord
from discord.ext import commands

class BasicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Définition de la commande "hello"
    @commands.command(name="hello", help="Greets the user with a hello message.")
    async def hello(self, ctx, member: discord.Member):
        # Envoie du message de salutation
        await ctx.send(f"Hello {member.mention}!")

        # Récupération du système de leveling
        leveling_system = self.bot.get_cog('LevelingSystem')
        if leveling_system is None:
            await ctx.send("Le système de leveling n'est pas disponible.")
            return

        # Récupération du niveau de l'utilisateur
        user_id = str(member.id)
        if user_id in leveling_system.levels:
            new_level = leveling_system.levels[user_id]["level"]
        else:
            await ctx.send(f"{member.mention} n'a pas encore de niveau.")
            return

        # Préparation de l'embed
        embed = discord.Embed(
            color=discord.Color.green()
        )

        # Ajout des informations de l'auteur à l'embed
        embed.set_author(
            name=f"{member.display_name} is level {new_level}!",     # Nom de l'auteur
            icon_url=member.avatar.url    # URL de l'avatar de l'auteur
        )

        # Envoi de l'embed dans le même canal
        await ctx.send(embed=embed)

async def setup(bot):
    # Ajoute le cog au bot
    await bot.add_cog(BasicCommands(bot))
