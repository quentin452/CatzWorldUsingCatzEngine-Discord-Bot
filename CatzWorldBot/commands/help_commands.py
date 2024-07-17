from discord.ext import commands
import discord

class CustomHelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_embed_pages(self, ctx, pages):
        if not pages:
            await ctx.send("Aucune page à afficher.")
            return
        
        current_page = 0
        message = await ctx.send(embed=pages[current_page])

        # Ajouter les réactions pour la pagination
        if len(pages) > 1:
            await message.add_reaction('◀️')  # Flèche gauche
            await message.add_reaction('▶️')  # Flèche droite

            def check(reaction, user):
                return user == ctx.message.author and reaction.message.id == message.id and str(reaction.emoji) in ['◀️', '▶️']

            while True:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)

                    if str(reaction.emoji) == '▶️' and current_page < len(pages) - 1:
                        current_page += 1
                        await message.edit(embed=pages[current_page])
                    elif str(reaction.emoji) == '◀️' and current_page > 0:
                        current_page -= 1
                        await message.edit(embed=pages[current_page])

                    await message.remove_reaction(reaction, user)

                except TimeoutError:
                    break

    @commands.command(help="Affiche une liste de toutes les catégories d'aide disponibles.")
    async def help_cat(self, ctx):
        pages = []
        for cog_name, cog in self.bot.cogs.items():
            command_list = "\n".join([f"{self.bot.command_prefix}{command.name}: {command.short_doc or 'Aucune description'}" for command in cog.get_commands() if not command.hidden])
            if command_list:
                embed = discord.Embed(title=f"{cog_name}", description=command_list, color=discord.Color.blue())
                pages.append(embed)

        await self.send_embed_pages(ctx, pages)

    async def send_bot_help(self, mapping):
        pages = []
        for cog, commands in mapping.items():
            cog_name = cog.qualified_name if cog else "Non catégorisé"
            command_list = "\n".join([f"{self.bot.command_prefix}{command.name}: {command.help or 'Aucune description'}" for command in commands if not command.hidden])
            if command_list:
                embed = discord.Embed(title=f"{cog_name}", description=command_list, color=discord.Color.blue())
                pages.append(embed)

        await self.send_embed_pages(ctx, pages)

    async def send_command_help(self, command):
        if command.hidden or any(check.__class__.__name__ == 'has_permissions' and check.kwargs.get('administrator', False) for check in command.checks):
            return
        embed = discord.Embed(title=f"Aide pour {self.bot.command_prefix}{command.name}", color=discord.Color.blue())
        embed.add_field(name="Description", value=command.help or "Aucune description", inline=False)
        embed.add_field(name="Utilisation", value=self.get_command_signature(command), inline=False)
        await ctx.send(embed=embed)

    async def send_cog_help(self, cog):
        command_list = "\n".join([f"{self.bot.command_prefix}{command.name}: {command.help or 'Aucune description'}" for command in cog.get_commands() if not command.hidden])
        if command_list:
            embed = discord.Embed(title=f"Commandes de {cog.qualified_name}", description=command_list, color=discord.Color.blue())
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CustomHelpCommand(bot))