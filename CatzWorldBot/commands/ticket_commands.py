import discord
from discord.ext import commands
import json
import asyncio

class TicketCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket_channel_id = self.load_ticket_channel_id()  # Chargement initial du canal de ticket
        self.ticket_counter = self.load_ticket_counter()
        self.tickets = self.load_tickets()
        self.delete_lock = asyncio.Lock()
        self.delete_messages = True  # Variable pour contrôler la suppression des messages

    def load_ticket_channel_id(self):
        try:
            with open('ticket_channel_id.json', 'r') as f:
                return int(json.load(f))  # Charger l'ID du canal en tant qu'entier
        except FileNotFoundError:
            return None

    def save_ticket_channel_id(self):
        with open('ticket_channel_id.json', 'w') as f:
            json.dump(self.ticket_channel_id, f)

    def load_ticket_counter(self):
        try:
            with open('ticket_counter.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return 0

    def save_ticket_counter(self):
        with open('ticket_counter.json', 'w') as f:
            json.dump(self.ticket_counter, f)

    def load_tickets(self):
        try:
            with open('tickets.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_tickets(self):
        with open('tickets.json', 'w') as f:
            json.dump(self.tickets, f)

    async def delete_bot_messages(self):
        async with self.delete_lock:
            while self.delete_messages:
                if not self.ticket_channel_id:
                    print("Ticket channel ID not set.")
                    return

                channel = self.bot.get_channel(self.ticket_channel_id)
                if not channel:
                    print(f"Channel with ID {self.ticket_channel_id} not found.")
                    return

                print(f"Deleting bot messages in channel: {channel.name} ({channel.id})")

                try:
                    deleted = await channel.purge(limit=None, check=lambda msg: msg.author.id == self.bot.user.id)
                    print(f"Deleted {len(deleted)} messages.")

                    if len(deleted) == 0:
                        print("No more bot messages to delete. Stopping message deletion.")
                        self.delete_messages = False
                        await self.get_ticket_channel(channel)  # Call get_ticket_channel when stopping deletion
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

    async def get_ticket_channel(self, channel):
        embed = discord.Embed(
            title="Ticket Channel Information",
            description=f"The ticket channel is set to {channel.mention}. Message deletion has stopped.",
            color=discord.Color.blue()
        )
        await channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_ready(self):
        await self.delete_bot_messages()
        print('Bot is ready.')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == self.ticket_channel_id and message.author.id == self.bot.user.id:
            if not self.delete_messages:
                return  # Don't delete messages if delete_messages is False
            await self.delete_bot_messages()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_ticket_channel(self, ctx):
        self.ticket_channel_id = ctx.channel.id
        self.save_ticket_channel_id()
        embed = discord.Embed(
            title="Open A Ticket",
            description="If you need help / want to apply as staff,\nthen open a ticket!\n\nTo open a ticket, press the button.",
            color=discord.Color.blue()
        )
        view = TicketView(self)
        await ctx.send(embed=embed, view=view)
        await ctx.send(f"Ticket channel set to {ctx.channel.mention}")

    @commands.command()
    async def create_ticket(self, ctx, *, description):
        async with self.delete_lock:
            if not self.ticket_channel_id:
                await ctx.send("Ticket channel not set.")
                return

            guild = ctx.guild
            ticket_channel = self.bot.get_channel(self.ticket_channel_id)
            category = ticket_channel.category

            new_ticket_channel = await guild.create_text_channel(f'ticket-{self.ticket_counter}', category=category)

            await new_ticket_channel.set_permissions(guild.default_role, read_messages=False)
            await new_ticket_channel.set_permissions(ctx.author, read_messages=True, send_messages=True)
            for role in guild.roles:
                if role.permissions.administrator:
                    await new_ticket_channel.set_permissions(role, read_messages=True, send_messages=True)

            ticket = {
                'ticket_id': self.ticket_counter,
                'user_id': ctx.author.id,
                'description': description,
                'channel_id': new_ticket_channel.id
            }
            self.tickets.append(ticket)
            self.save_tickets()

            ticket_embed = discord.Embed(title=f"Ticket #{self.ticket_counter}", description=description, color=discord.Color.blue())
            ticket_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
            view = discord.ui.View()
            view.add_item(CloseTicketButton(self, self.ticket_counter))
            await new_ticket_channel.send(embed=ticket_embed, view=view)

            self.ticket_counter += 1
            self.save_ticket_counter()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def close_ticket(self, ctx, ticket_id: int):
        async with self.delete_lock:
            ticket = next((t for t in self.tickets if t['ticket_id'] == ticket_id), None)
            if not ticket:
                await ctx.send(f"No ticket found with ID {ticket_id}.")
                return

            channel_id = ticket['channel_id']
            channel = self.bot.get_channel(channel_id)
            if not channel:
                await ctx.send(f"Ticket channel for ticket #{ticket_id} not found. It might have already been deleted.")
                return

            try:
                await channel.delete()
                self.tickets = [t for t in self.tickets if t['ticket_id'] != ticket_id]
                self.save_tickets()
                await ctx.send(f"Ticket #{ticket_id} closed and deleted.")
            except discord.errors.NotFound:
                pass
            except discord.errors.Forbidden:
                await ctx.send(f"Failed to delete ticket channel for ticket #{ticket_id}: Permission denied.")
            except discord.HTTPException as e:
                await ctx.send(f"Failed to delete ticket channel for ticket #{ticket_id}: {e}")

class TicketView(discord.ui.View):
    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    @discord.ui.button(label="Open a Ticket", style=discord.ButtonStyle.primary)
    async def open_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = OpenTicketModal(self.cog)
        try:
            await interaction.response.send_message("Opening Ticket...", ephemeral=True)
            await modal.callback(interaction)
        except discord.HTTPException as e:
            await interaction.response.send_message(f"Failed to open ticket: {e}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An unexpected error occurred: {e}", ephemeral=True)

class OpenTicketModal(discord.ui.Modal):
    def __init__(self, cog):
        super().__init__(title="Open a Ticket")
        self.cog = cog
        self.add_item(discord.ui.TextInput(label="Description"))

    async def callback(self, interaction: discord.Interaction):
        description = self.children[0].value
        ctx = await self.cog.bot.get_context(interaction.message)
        await self.cog.create_ticket(ctx, description=description)
        await interaction.followup.send("Ticket created!", ephemeral=True)

class CloseTicketButton(discord.ui.Button):
    def __init__(self, cog, ticket_id):
        super().__init__(style=discord.ButtonStyle.danger, label="Close Ticket")
        self.cog = cog
        self.ticket_id = ticket_id

    async def callback(self, interaction: discord.Interaction):
        ctx = await self.cog.bot.get_context(interaction.message)
        await self.cog.close_ticket(ctx, ticket_id=self.ticket_id)

async def setup(bot):
    await bot.add_cog(TicketCommands(bot))