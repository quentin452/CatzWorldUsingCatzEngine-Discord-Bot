import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import json
import signal
import asyncio

class RoleMenuView(discord.ui.View):
    def __init__(self, roles_with_descriptions):
        super().__init__(timeout=None)
        self.roles_with_descriptions = roles_with_descriptions
        self.message_id = None 

        # Create and add the Select dropdown first
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

        # Then add the buttons
        self.add_buttons()

    def add_buttons(self):
        # Add "Remove Free Roles" button
        remove_button = discord.ui.Button(
            label="Remove Free Roles",
            style=discord.ButtonStyle.danger,
            custom_id="remove_roles",
            row=2  # Adjust the row if necessary
        )
        remove_button.callback = self.remove_button_callback
        self.add_item(remove_button)

        # Add "Add Free Roles" button
        all_button = discord.ui.Button(
            label="Add Free Roles",
            style=discord.ButtonStyle.success,
            custom_id="all_roles",
            row=2  # Adjust the row if necessary
        )
        all_button.callback = self.all_button_callback
        self.add_item(all_button)

    async def select_callback(self, interaction: discord.Interaction):
        role_name = interaction.data['values'][0]
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if role:
            await interaction.response.send_message(f"Role {role_name} added!", ephemeral=True)
            await interaction.user.add_roles(role)
        else:
            await interaction.response.send_message(f"Role {role_name} not found!", ephemeral=True)

    async def remove_button_callback(self, interaction: discord.Interaction):
        roles_to_remove = [discord.utils.get(interaction.guild.roles, name=role) for role in self.roles_with_descriptions.keys()]
        roles_to_remove = [role for role in roles_to_remove if role in interaction.user.roles]
        if roles_to_remove:
            await interaction.response.send_message("All free roles have been removed!", ephemeral=True)
            await interaction.user.remove_roles(*roles_to_remove)
        else:
            await interaction.response.send_message("You have no free roles to delete.", ephemeral=True)

    async def all_button_callback(self, interaction: discord.Interaction):
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
        self.role_menu_view = RoleMenuView(self.free_roles_with_descriptions)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def role_menu(self, ctx):
        embed = discord.Embed(title="Roles menu", description="Choose your roles by interacting with the drop-down menu.", color=discord.Color.blue())
        message = await ctx.send(embed=embed, view=self.role_menu_view)
        self.role_menu_view.message_id = message.id  # Définir le message_id

    def get_menu_view(self):
        return RoleMenuView(self.free_roles_with_descriptions)


async def setup(bot):
    await bot.add_cog(RoleMenu(bot))