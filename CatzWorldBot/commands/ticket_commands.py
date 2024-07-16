import discord
from discord.ext import commands
import json
import asyncio
from utils.Constants import ConstantsClass
from utils.async_logs import LogMessageAsync
class TicketCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket_counter = self.load_ticket_counter()
        self.tickets = self.load_tickets()
        self.delete_lock = asyncio.Lock()
        self.delete_messages = True
        self.ticket_channel_id = self.load_ticket_channel_id()
        self.cooldowns = {}
        self.cooldown_time = 10
        self.ticket_messages = self.load_ticket_messages()  # Load ticket messages
        
        # Send close ticket buttons after loading tickets and messages
        bot.loop.create_task(self.send_close_ticket_buttons())

    def get_menu_view(self):
        return TicketView(self)
        
    def load_ticket_channel_id(self):
        try:
            with open(ConstantsClass.TICKET_SAVE_FOLDER + '/ticket_channel_id.json', 'r') as f:
                return int(json.load(f))  # Return the channel ID as an integer
        except FileNotFoundError:
            return None  # Return None if file not found

    def save_ticket_channel_id(self):
        with open(ConstantsClass.TICKET_SAVE_FOLDER + '/ticket_channel_id.json', 'w') as f:
            json.dump(self.ticket_channel_id, f)

    def load_ticket_counter(self):
        try:
            with open(ConstantsClass.TICKET_SAVE_FOLDER + '/ticket_counter.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return 0

    def save_ticket_counter(self):
        with open(ConstantsClass.TICKET_SAVE_FOLDER + '/ticket_counter.json', 'w') as f:
            json.dump(self.ticket_counter, f)

    def load_tickets(self):
        try:
            with open(ConstantsClass.TICKET_SAVE_FOLDER + '/tickets.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_tickets(self):
        with open(ConstantsClass.TICKET_SAVE_FOLDER + '/tickets.json', 'w') as f:
            json.dump(self.tickets, f)

    def load_ticket_messages(self):
        try:
            with open(ConstantsClass.TICKET_SAVE_FOLDER + '/ticket_messages.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_ticket_messages(self):
        with open(ConstantsClass.TICKET_SAVE_FOLDER + '/ticket_messages.json', 'w') as f:
            json.dump(self.ticket_messages, f)

    async def send_close_ticket_buttons(self):
        for ticket in self.tickets:
            channel_id = ticket['channel_id']
            channel = self.bot.get_channel(channel_id)
            if channel:
                message_id = self.ticket_messages.get(ticket['ticket_id'])
                if message_id:
                    try:
                        message = await channel.fetch_message(message_id)
                        if message:
                            view = TicketView(self)
                            view.add_item(CloseTicketButton(self, ticket['ticket_id']))
                            await message.edit(view=view)
                        else:
                            await LogMessageAsync.LogAsync(f"Failed to fetch ticket message for ticket ID {ticket['ticket_id']}")
                    except discord.HTTPException as e:
                        await LogMessageAsync.LogAsync(f"Failed to edit ticket message for ticket ID {ticket['ticket_id']}: {e}")
                else:
                    await LogMessageAsync.LogAsync(f"Ticket message ID not found for ticket ID {ticket['ticket_id']}")

    async def send_ticket_creation_message(self, channel):
        try:
            if channel.id != self.ticket_channel_id:
                return
            
            ticket_exists = any(ticket['channel_id'] == channel.id for ticket in self.tickets)
            
            if not ticket_exists:
                embed = discord.Embed(
                    title="Open A Ticket",
                    description="If you need help / want to apply as staff,\nthen open a ticket!\n\nTo open a ticket, press the button.",
                    color=discord.Color.blue()
                )
                view = TicketView(self)
                await channel.send(embed=embed, view=view)
                await channel.send(f"Ticket channel set to {channel.mention}")
        except discord.HTTPException as e:
            await LogMessageAsync.LogAsync(f"Failed to send ticket creation message: {e}")
        except Exception as e:
            await LogMessageAsync.LogAsync(f"An error occurred while sending ticket creation message: {e}")
    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if interaction.type == discord.InteractionType.component:
            if interaction.data["custom_id"].startswith("close_ticket"):
                ticket_id = int(interaction.data["custom_id"].split("_")[-1])
                await self.close_ticket(interaction, ticket_id=ticket_id)
                await interaction.response.send_message("Ticket fermé", ephemeral=True)

    @commands.command(help="Sets the current channel as the ticket channel for creating and managing tickets. Requires administrator permissions.")
    @commands.has_permissions(administrator=True)
    async def set_ticket_channel(self, ctx):
        self.ticket_channel_id = ctx.channel.id
        self.save_ticket_channel_id()
        if not self.delete_messages:
            self.delete_messages = True
            
    async def create_ticket(self, user, interaction, description):
        async with self.delete_lock:
            try:
                if not self.ticket_channel_id:
                    await interaction.followup.send("Ticket channel not set.", ephemeral=True)
                    return

                now = discord.utils.utcnow()
                last_ticket_time = self.cooldowns.get(user.id)

                if last_ticket_time and (now - last_ticket_time).total_seconds() < self.cooldown_time:
                    wait_time = self.cooldown_time - (now - last_ticket_time).total_seconds()
                    await interaction.followup.send(f"Please wait {int(wait_time)} seconds before creating another ticket.", ephemeral=True)
                    return

                guild = interaction.guild
                ticket_channel = self.bot.get_channel(self.ticket_channel_id)
                if not ticket_channel:
                    await interaction.followup.send("Ticket channel not found.", ephemeral=True)
                    return

                category = ticket_channel.category

                new_ticket_channel = await guild.create_text_channel(f'ticket-{self.ticket_counter}', category=category)

                await new_ticket_channel.set_permissions(guild.default_role, read_messages=False)
                await new_ticket_channel.set_permissions(user, read_messages=True, send_messages=True)
                for role in guild.roles:
                    if role.permissions.administrator:
                        await new_ticket_channel.set_permissions(role, read_messages=True, send_messages=True)

                ticket_message = f"{user.mention}, votre ticket a été créé!"
                ticket_embed = discord.Embed(title=f"Ticket #{self.ticket_counter}", description=description, color=discord.Color.blue())
                ticket_embed.set_author(name=user.name, icon_url=user.avatar.url)
                view = TicketView(self)
                view.add_item(CloseTicketButton(self, self.ticket_counter))

                ticket_message = await new_ticket_channel.send(ticket_message, embed=ticket_embed, view=view)
                self.ticket_messages[self.ticket_counter] = ticket_message.id  # Store the ticket message ID
                self.save_ticket_messages()

                # Save ticket details to JSON
                ticket = {
                    'ticket_id': self.ticket_counter,
                    'user_id': user.id,
                    'user': user.name,
                    'description': description,
                    'channel_id': new_ticket_channel.id,
                    'message_id': ticket_message.id  # Store the ticket message ID
                }
                self.tickets.append(ticket)
                self.save_tickets()

                self.ticket_counter += 1
                self.save_ticket_counter()

                self.cooldowns[user.id] = now

                channel = self.bot.get_channel(self.ticket_channel_id)
                await channel.send("Ticket created!")  # Removed ephemeral=True

            except discord.HTTPException as e:
                await LogMessageAsync.LogAsync(f"Failed to create ticket: {e}")
                await interaction.followup.send(f"Failed to create ticket: {e}", ephemeral=True)

            except Exception as e:
                await LogMessageAsync.LogAsync(f"An unexpected error occurred: {e}")
                await interaction.followup.send(f"An unexpected error occurred: {e}", ephemeral=True)

    @commands.command(help="Closes a ticket and deletes its associated channel based on the provided ticket ID. Requires administrator permissions.")
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

            user_id = ticket['user_id']
            user = self.bot.get_user(user_id)

            try:
                await channel.delete()
                del self.ticket_messages[ticket_id]  # Remove from ticket messages dictionary
                self.tickets = [t for t in self.tickets if t['ticket_id'] != ticket_id]
                self.save_tickets()
                self.save_ticket_messages()

                if user:
                    await ctx.send(f"Ticket #{ticket_id} closed and deleted. {user.mention} a été pingé.", allowed_mentions=discord.AllowedMentions(users=True))
                else:
                    await ctx.send(f"Ticket #{ticket_id} closed and deleted. (User not found)")
            except discord.errors.NotFound:
                pass
            except discord.errors.Forbidden:
                await ctx.send(f"Failed to delete ticket channel for ticket #{ticket_id}: Permission denied.")
            except discord.HTTPException as e:
                await ctx.send(f"Failed to delete ticket channel for ticket #{ticket_id}: {e}")

class TicketView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="Open a Ticket", style=discord.ButtonStyle.primary, custom_id="open_ticket_button")
    async def open_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = OpenTicketModal(self.cog)
        await interaction.response.send_modal(modal)

class OpenTicketModal(discord.ui.Modal):
    def __init__(self, cog):
        super().__init__(title="None")
        self.cog = cog
        self.add_item(discord.ui.TextInput(label="Description"))

    async def on_submit(self, interaction: discord.Interaction):
        description = self.children[0].value

        now = discord.utils.utcnow()
        last_ticket_time = self.cog.cooldowns.get(interaction.user.id)

        if last_ticket_time and (now - last_ticket_time).total_seconds() < self.cog.cooldown_time:
            wait_time = self.cog.cooldown_time - (now - last_ticket_time).total_seconds()
            await interaction.followup.send(f"Please wait {int(wait_time)} seconds before creating another ticket.", ephemeral=True)
            return

        try:
            await interaction.response.defer()
            await self.cog.create_ticket(interaction.user, interaction, description=description)

        except discord.HTTPException as e:
            await LogMessageAsync.LogAsync(f"Failed to create ticket: {e}")
            await interaction.followup.send(f"Failed to create ticket: {e}", ephemeral=True)
        except Exception as e:
            await LogMessageAsync.LogAsync(f"An unexpected error occurred: {e}")
            await interaction.followup.send(f"An unexpected error occurred: {e}", ephemeral=True)
        
class CloseTicketButton(discord.ui.Button):
    def __init__(self, cog, ticket_id):
        super().__init__(style=discord.ButtonStyle.danger, label="Close Ticket", custom_id=f"close_ticket_{ticket_id}")
        self.cog = cog
        self.ticket_id = ticket_id

    async def callback(self, interaction: discord.Interaction):
        ctx = await self.cog.bot.get_context(interaction.message)
        await self.cog.close_ticket(ctx, ticket_id=self.ticket_id)

async def setup(bot):
    await bot.add_cog(TicketCommands(bot))
