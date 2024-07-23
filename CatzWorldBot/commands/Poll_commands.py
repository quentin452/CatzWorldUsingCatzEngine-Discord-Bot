import discord
from discord.ext import commands
import asyncio

class PollView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
        self.button_message = None  # Store the button message

    @discord.ui.button(label="Create Poll", style=discord.ButtonStyle.primary, custom_id="create_poll_button")
    async def create_poll_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = PollModal(self.cog, self.button_message)  # Pass the button message to the modal
        await interaction.response.send_modal(modal)

class PollModal(discord.ui.Modal):
    def __init__(self, cog, button_message):
        super().__init__(title="Create Poll")
        self.cog = cog
        self.button_message = button_message  # Store the message with the button
        self.add_item(discord.ui.TextInput(label="Poll Title", placeholder="Enter the title of the poll"))
        self.add_item(discord.ui.TextInput(label="Option 1", placeholder="Enter the first option"))
        self.add_item(discord.ui.TextInput(label="Option 2", placeholder="Enter the second option"))
        self.add_item(discord.ui.TextInput(label="Duration (seconds)", placeholder="Enter the duration in seconds"))

    async def on_submit(self, interaction: discord.Interaction):
        title = self.children[0].value
        option1 = self.children[1].value
        option2 = self.children[2].value
        duration = int(self.children[3].value)

        embed = discord.Embed(title=title, description=f"Poll will last for {duration} seconds", color=discord.Color.blue())
        embed.add_field(name="Options", value=f"1️⃣ {option1}\n2️⃣ {option2}", inline=False)
        embed.set_footer(text="React with 1️⃣ or 2️⃣ to vote!")

        # Send the poll message
        try:
            # Send the message and get the sent message object
            poll_message = await interaction.channel.send(embed=embed)
            await poll_message.add_reaction("1️⃣")
            await poll_message.add_reaction("2️⃣")
        except discord.HTTPException as e:
            await interaction.response.send_message(f"Failed to send poll: {e}", ephemeral=True)
            return

        # Acknowledge the modal submission and delete the button message
        await interaction.response.send_message("Poll created successfully!", ephemeral=True)
        
        # Delete the button message
        if self.button_message:
            try:
                await self.button_message.delete()
            except discord.HTTPException as e:
                print(f"Failed to delete button message: {e}")

        # Wait for the poll duration
        await asyncio.sleep(duration)

        # Fetch the updated message
        try:
            poll_message = await interaction.channel.fetch_message(poll_message.id)
            reactions = {reaction.emoji: reaction.count - 1 for reaction in poll_message.reactions}

            total_votes = sum(reactions.values())
            if total_votes == 0:
                total_votes = 1

            def create_bar(votes, total):
                filled_length = int(5 * votes // total)
                bar = '🟩' * filled_length + '⬜' * (5 - filled_length)
                percentage = (votes / total) * 100
                return f"{bar} ({votes} votes - {percentage:.2f}%)"

            option1_bar = create_bar(reactions.get("1️⃣", 0), total_votes)
            option2_bar = create_bar(reactions.get("2️⃣", 0), total_votes)

            embed.clear_fields()
            embed.add_field(name=f"1️⃣ {option1}", value=option1_bar, inline=False)
            embed.add_field(name=f"2️⃣ {option2}", value=option2_bar, inline=False)
            embed.set_footer(text="Poll ended")

            await poll_message.edit(embed=embed)
            await poll_message.clear_reactions()
        except discord.HTTPException as e:
            await interaction.response.send_message(f"Failed to update poll: {e}", ephemeral=True)

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="start_poll", help="Sends a message with a button to create a poll.")
    async def start_poll(self, ctx):
        view = PollView(self)
        # Send the button message and store the message object
        view.button_message = await ctx.send("Click the button below to create a poll:", view=view)

async def setup(bot):
    await bot.add_cog(Poll(bot))
