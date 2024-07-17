import discord
from discord.ext import commands
from utils.Constants import ConstantsClass

class RulesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @commands.command(help="Give server rules")
    async def rules_cat(self, ctx):
        # Define the embed content
        embed = discord.Embed(
            title="Server Rules",
            description=(
                "## **General Server Rules**\n"
                "• No blank, inappropriate, sexually explicit, or offensive nicknames.\n"
                "• No unreadable Unicode nicknames.\n"
                "• No blank, inappropriate, sexually explicit, or offensive profile pictures.\n"
                "• No members under 18 years old.\n"
                "• Moderators may use their discretion regardless of the rules.\n"
                "• Report any rule loopholes.\n\n"
                "## **Text Chat Rules**\n"
                "• No questioning or @mentioning mods (use ⁠💥-issues-💥 for support).\n"
                "• No @everyone/@here without permission.\n"
                "• No @mentioning spam.\n"
                "• No NSFW content.\n"
                "• No personal information sharing.\n"
                "• No personal attacks, witch hunting, harassment, sexism, racism, hate speech, or offensive language.\n"
                "• No spamming or excessive messaging.\n"
                "• No walls of text or overusing emojis/reactions.\n"
                "• Keep conversations in English.\n"
                "• Moderators can delete or edit posts.\n"
                "• Use allowed bot commands only.\n"
                "• No channel hopping.\n"
                "• Stay on-topic.\n\n"
                "## **Voice Chat Rules**\n"
                "• No channel hopping.\n"
                "• No annoying, loud, or high-pitched noises.\n"
                "• Minimize background noise.\n"
                "• Moderators may disconnect for poor sound quality.\n"
                "• Moderators can disconnect, mute, deafen, or move members.\n\n"
                "## **Bot Specific Rules**\n"
                "• No command spam.\n"
                "• Use bot commands only in ⁠🤖-bot-🤖.\n\n"
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="Please click on '✅' to access the rest of the server (by clicking, you agree to follow ALL the rules mentioned above).")
        
        # Send the embed with the persistent view
        view = RulesView()
        message = await ctx.send(embed=embed, view=view)

    def get_menu_view(self):
        return RulesView()

class RulesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None  # Utilisé pour stocker la valeur si nécessaire

    @discord.ui.button(emoji='✅', custom_id='accept_rules')
    async def accept_rules(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        guild = interaction.guild
        role = discord.utils.get(guild.roles, name=ConstantsClass.VERIFIED_ROLE_NAME)

        if role:
            try:
                await member.add_roles(role)
                await interaction.response.send_message(f"Role {role.name} added to {member.display_name}", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("I don't have permission to add roles.", ephemeral=True)
            except discord.HTTPException:
                await interaction.response.send_message("Failed to add role.", ephemeral=True)
        else:
            await interaction.response.send_message("Role not found.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RulesCog(bot))
