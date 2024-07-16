import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

class RoleMenuView(discord.ui.View):
    def __init__(self, roles_with_descriptions):
        super().__init__(timeout=None)
        self.roles_with_descriptions = roles_with_descriptions

        select = discord.ui.Select(
            placeholder="Choose a free role",
            custom_id="role_select",
            options=[
                discord.SelectOption(label=f"{emoji} {role}", value=role, description=description)
                for role, (emoji, description) in self.roles_with_descriptions.items()
            ]
        )
        select.callback = self.select_callback
        self.add_item(select)
        
    async def select_callback(self, interaction: discord.Interaction):
        role_name = interaction.data['values'][0]
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if role:
            await interaction.response.send_message(f"Rôle {role_name} added!", ephemeral=True)
            await interaction.user.add_roles(role)
        else:
            await interaction.response.send_message(f"Rôle {role_name} not found!", ephemeral=True)

    @discord.ui.button(label="Remove Free Roles", style=discord.ButtonStyle.danger, custom_id="remove_roles")
    async def remove_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        roles_to_remove = [discord.utils.get(interaction.guild.roles, name=role) for role in self.roles_with_descriptions.keys()]
        roles_to_remove = [role for role in roles_to_remove if role in interaction.user.roles]
        if roles_to_remove:
            await interaction.response.send_message("All free roles have been removed!", ephemeral=True)
            await interaction.user.remove_roles(*roles_to_remove)
        else:
            await interaction.response.send_message("You have no free roles to delete.", ephemeral=True)

    @discord.ui.button(label="Add Free Roles", style=discord.ButtonStyle.success, custom_id="all_roles")
    async def all_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        roles_to_add = [discord.utils.get(interaction.guild.roles, name=role) for role in self.roles_with_descriptions.keys()]
        roles_to_add = [role for role in roles_to_add if role and role not in interaction.user.roles]
        if roles_to_add:
            await interaction.response.send_message("All free roles have been added!", ephemeral=True)
            await interaction.user.add_roles(*roles_to_add)
        else:
            await interaction.response.send_message("You already have all the roles free.", ephemeral=True)

class RoleMenu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.free_roles_with_descriptions = {
            'Biggess Pack Cat Edition ping updates': ('⛏️', 'Get updates for Biggess Pack Cat Edition'),
            'CatWorld game ping updates': ('⚔️', 'Get updates for CatWorld game')
        }

    @commands.command()
    @has_permissions(administrator=True)
    async def role_menu(self, ctx):
        embed = discord.Embed(title="Roles menu", description="Choose your roles by interacting with the drop-down menu.", color=discord.Color.blue())
        view = RoleMenuView(self.free_roles_with_descriptions)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(RoleMenu(bot))