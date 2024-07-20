from discord.ext import commands
import discord
#TODO IDK WHY BUT THE VIEW NOT GET SAVED AND SO WHEN I RELAUNCH THE BOT , OLD BUTTONS CANNOT BE CLICKED
#TODO only show the pagination for the user that used the command
class HelpPagination(discord.ui.View):
    def __init__(self, pages, show_buttons=True):
        super().__init__(timeout=None)
        self.pages = pages
        self.current_page = 0
        self.message = None
        self.show_buttons = show_buttons

        if not show_buttons:
            self.clear_items()

    async def show_page(self, interaction=None):
        if not (0 <= self.current_page < len(self.pages)):
            return
        
        embed = self.pages[self.current_page]

        if interaction and isinstance(interaction, discord.Interaction):
            await interaction.response.edit_message(embed=embed, view=self if self.show_buttons else None)
        elif self.message:
            await self.message.edit(embed=embed, view=self if self.show_buttons else None)

    @discord.ui.button(label='⏪', style=discord.ButtonStyle.blurple, custom_id='help_first_page')
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 0
        await self.show_page(interaction)

    @discord.ui.button(label='◀️', style=discord.ButtonStyle.blurple, custom_id='help_previous_page')
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await self.show_page(interaction)

    @discord.ui.button(label='▶️', style=discord.ButtonStyle.blurple, custom_id='help_next_page')
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await self.show_page(interaction)

    @discord.ui.button(label='⏩', style=discord.ButtonStyle.blurple, custom_id='help_last_page')
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = len(self.pages) - 1
        await self.show_page(interaction)

class CustomHelpCommandCog(commands.Cog):
    def __init__(self, bot, categories_per_page=5):
        self.bot = bot
        self.categories_per_page = categories_per_page
        self.pages = []

    def get_pages(self, category_filter=None):
        pages = []
        if category_filter:
            category_list = [(cog_name, cog) for cog_name, cog in self.bot.cogs.items() if cog_name.lower() == category_filter.lower()]
        else:
            category_list = list(self.bot.cogs.items())
        
        num_pages = (len(category_list) + self.categories_per_page - 1) // self.categories_per_page

        for page_num in range(num_pages):
            start_idx = page_num * self.categories_per_page
            end_idx = start_idx + self.categories_per_page
            current_page_categories = category_list[start_idx:end_idx]

            if category_filter:
                embed = discord.Embed(title=f"Help - {category_filter.capitalize()} Category", color=discord.Color.blue())
            else:
                embed = discord.Embed(title=f"Page {page_num + 1}/{num_pages} - Help Categories", color=discord.Color.blue())

            for cog_name, cog in current_page_categories:
                command_list = "\n".join([f"{self.bot.command_prefix}{command.name}: {command.short_doc or 'Aucune description'}" for command in cog.get_commands() if not command.hidden])
                if command_list:
                    embed.add_field(name=cog_name, value=command_list, inline=False)

            pages.append(embed)

        return pages
    
    @commands.command(help="Displays a list of all available help categories or the commands of a specific category.")
    async def help_cat(self, ctx, category: str = None):
        self.pages = self.get_pages(category_filter=category)
        if not self.pages:
            return await ctx.send("Aucune catégorie d'aide trouvée.")

        show_buttons = category is None
        view = HelpPagination(self.pages, show_buttons=show_buttons)
        message = await ctx.send(embed=self.pages[0], view=view if show_buttons else None)
        if show_buttons:
            view.message = message

    async def help_cat_PeriodicTask(self, ctx, category: str = "MusicCog"):
        self.pages = self.get_pages(category_filter=category)
        if not self.pages:
            return await ctx.send("Aucune catégorie d'aide trouvée.")

        show_buttons = category is None
        view = HelpPagination(self.pages, show_buttons=show_buttons)
        message = await ctx.send(embed=self.pages[0], view=view if show_buttons else None)
        if show_buttons:
            view.message = message


    async def send_command_help(self, ctx, command):
        if command.hidden or any(check.__class__.__name__ == 'has_permissions' and check.kwargs.get('administrator', False) for check in command.checks):
            return
        embed = discord.Embed(title=f"Aide pour {self.bot.command_prefix}{command.name}", color=discord.Color.blue())
        embed.add_field(name="Description", value=command.help or "Aucune description", inline=False)
        embed.add_field(name="Utilisation", value=self.get_command_signature(command), inline=False)
        await ctx.send(embed=embed)

    async def send_cog_help(self, ctx, cog):
        command_list = "\n".join([f"{self.bot.command_prefix}{command.name}: {command.help or 'Aucune description'}" for command in cog.get_commands() if not command.hidden])
        if command_list:
            embed = discord.Embed(title=f"Commandes de {cog.qualified_name}", description=command_list, color=discord.Color.blue())
            await ctx.send(embed=embed)

    def get_menu_view(self):
        return HelpPagination(self.pages)

# Enregistrement du cog dans le bot
async def setup(bot):
    await bot.add_cog(CustomHelpCommandCog(bot))
