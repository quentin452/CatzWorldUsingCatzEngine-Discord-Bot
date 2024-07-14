import discord
from discord.ext import commands
import json
import asyncio
from datetime import datetime

class FeedbackCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.feedback_channel_id = self.load_feedback_channel_id()
        self.feedback_counter = self.load_feedback_counter()
        self.feedbacks = self.load_feedbacks()

        if self.feedback_channel_id:
            bot.loop.create_task(self.delete_bot_messages())

    def load_feedback_channel_id(self):
        try:
            with open('feedback_channel_id.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def save_feedback_channel_id(self):
        with open('feedback_channel_id.json', 'w') as f:
            json.dump(self.feedback_channel_id, f)

    def load_feedback_counter(self):
        try:
            with open('feedback_counter.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return 0

    def save_feedback_counter(self):
        with open('feedback_counter.json', 'w') as f:
            json.dump(self.feedback_counter, f)

    def load_feedbacks(self):
        try:
            with open('feedbacks.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    async def delete_bot_messages(self):
        while True:
            if not self.feedback_channel_id:
                print("Feedback channel ID not set.")
                return

            channel = self.bot.get_channel(self.feedback_channel_id)
            if not channel:
                print(f"Channel with ID {self.feedback_channel_id} not found.")
                return

            print(f"Deleting bot messages in channel: {channel.name} ({channel.id})")

            try:
                deleted = await channel.purge(limit=None, check=lambda msg: msg.author.id == self.bot.user.id)
                print(f"Deleted {len(deleted)} messages.")

                if len(deleted) == 0:
                    print("No more bot messages to delete. Stopping message deletion.")
                    return

            except discord.HTTPException as e:
                if e.code == 429:
                    retry_after = e.retry_after
                    print(f"We are being rate limited. Retry after {retry_after} seconds.")
                    await asyncio.sleep(retry_after)
                    continue
                else:
                    print(f"Failed to delete messages: {e}")
                    return
            except Exception as e:
                print(f"An error occurred: {e}")
                return

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_feedback_channel(self, ctx):
        self.feedback_channel_id = ctx.channel.id
        self.save_feedback_channel_id()
        await ctx.send(f"Feedback channel set to {ctx.channel.mention}")

    @commands.command()
    async def submit_feedback(self, ctx, *, feedback):
        if not self.feedback_channel_id:
            await ctx.send("Feedback channel not set.")
            return

        feedback_entry = {
            'user': ctx.author.name,
            'feedback': feedback,
            'timestamp': datetime.utcnow().isoformat()  # Add current timestamp in ISO format
        }
        self.feedbacks.append(feedback_entry)
        self.save_feedbacks()

        await ctx.send(f"Feedback submitted by {ctx.author.mention}:\n{feedback}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def view_feedbacks(self, ctx):
        if not self.feedbacks:
            await ctx.send("No feedbacks have been submitted.")
            return
        
        feedback_list = "\n\n".join([
            f"**User:** {feedback.get('user', 'Unknown')}\n**Feedback:** {feedback.get('feedback', 'No feedback')}\n**Timestamp:** {feedback.get('timestamp', 'No timestamp')}"
            for feedback in self.feedbacks
        ])
        await ctx.send(f"**List of Feedbacks:**\n\n{feedback_list}")

    async def send_feedback_instructions(self):
        await asyncio.sleep(5)  # Wait for bot to be fully ready
        channel = self.bot.get_channel(self.feedback_channel_id)
        if channel:
            embed = discord.Embed(
                title="How to submit feedback",
                description="To submit feedback, use the command:\n\n`/submit_feedback Your feedback message here`",
                color=discord.Color.blue()
            )
            await channel.send(embed=embed)

    async def setup_feedback(self):
        await self.delete_bot_messages()  # Ensure bot messages are deleted on startup
        await self.send_feedback_instructions()  # Send instructions on how to submit feedback

async def setup(bot):
    feedback_cog = FeedbackCommands(bot)
    await feedback_cog.setup_feedback()
    await bot.add_cog(feedback_cog)