# todo add a timer to not create alot of tickets at the same time
# fix when relaunching bot , cannot clicks on buttons like Close Ticket/Open Ticket
# add persistant data structure to save tickets messages
import discord
from discord.ext import commands
import json
import asyncio

class TicketCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket_counter = self.load_ticket_counter()
        self.tickets = self.load_tickets()
        self.delete_lock = asyncio.Lock()
        self.delete_messages = True 
        self.ticket_channel_id = self.load_ticket_channel_id()
        if self.ticket_channel_id:
            bot.loop.create_task(self.delete_bot_messages())

    def load_ticket_channel_id(self):
        try:
            with open('ticket_channel_id.json', 'r') as f:
                return int(json.load(f))  # Return the channel ID as an integer
        except FileNotFoundError:
            return None  # Return None if file not found

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
                        await self.send_ticket_creation_message(channel)  # Call send_ticket_channel_info when stopping deletion
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

    async def send_ticket_creation_message(self, channel):
        try:
            embed = discord.Embed(
                title="Open A Ticket",
                description="If you need help / want to apply as staff,\nthen open a ticket!\n\nTo open a ticket, press the button.",
                color=discord.Color.blue()
            )
            view = TicketView(self)
            await channel.send(embed=embed, view=view)
            await channel.send(f"Ticket channel set to {channel.mention}")
        except discord.HTTPException as e:
            print(f"Failed to send ticket creation message: {e}")
        except Exception as e:
            print(f"An error occurred while sending ticket creation message: {e}")

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if interaction.type == discord.InteractionType.component:
            if interaction.data["custom_id"] == "close_ticket":
                ctx = await self.bot.get_context(interaction.message)
                ticket_id = int(interaction.data["values"][0])
                await self.close_ticket(ctx, ticket_id=ticket_id)
                await interaction.response.send_message("Ticket fermé", ephemeral=True)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_ticket_channel(self, ctx):
        self.ticket_channel_id = ctx.channel.id
        self.save_ticket_channel_id()
        if not self.delete_messages:
            self.delete_messages = True  # Activer la suppression des messages si ce n'était pas déjà le cas
            await self.delete_bot_messages()  # Démarre le processus de suppression des messages
        embed = discord.Embed(
            title="Open A Ticket",
            description="If you need help / want to apply as staff,\nthen open a ticket!\n\nTo open a ticket, press the button.",
            color=discord.Color.blue()
        )
        view = TicketView(self)
        await ctx.send(embed=embed, view=view)
        await ctx.send(f"Ticket channel set to {ctx.channel.mention}")
        
    @commands.command()
    async def create_ticket(self, user, ctx, *, description):
        async with self.delete_lock:
            if not self.ticket_channel_id:
                await ctx.send("Ticket channel not set.")
                return

            guild = ctx.guild
            ticket_channel = self.bot.get_channel(self.ticket_channel_id)
            category = ticket_channel.category

            new_ticket_channel = await guild.create_text_channel(f'ticket-{self.ticket_counter}', category=category)

            await new_ticket_channel.set_permissions(guild.default_role, read_messages=False)
            await new_ticket_channel.set_permissions(user, read_messages=True, send_messages=True)
            for role in guild.roles:
                if role.permissions.administrator:
                    await new_ticket_channel.set_permissions(role, read_messages=True, send_messages=True)

            ticket = {
                'ticket_id': self.ticket_counter,
                'user_id': user.id,
                'user': user.name,
                'description': description,
                'channel_id': new_ticket_channel.id
            }
            self.tickets.append(ticket)
            self.save_tickets()

            ticket_embed = discord.Embed(title=f"Ticket #{self.ticket_counter}", description=description, color=discord.Color.blue())
            ticket_embed.set_author(name=user.name, icon_url=user.avatar.url)
            view = discord.ui.View()
            view.add_item(CloseTicketButton(self, self.ticket_counter))

            # Construction du message sans mention automatique
            ticket_message = f"{user.mention}, votre ticket a été créé!"
            await new_ticket_channel.send(ticket_message, embed=ticket_embed, view=view)

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

            # Fetching user who created the ticket
            user_id = ticket['user_id']
            user = self.bot.get_user(user_id)

            try:
                await channel.delete()
                self.tickets = [t for t in self.tickets if t['ticket_id'] != ticket_id]
                self.save_tickets()

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
        super().__init__()
        self.cog = cog

    @discord.ui.button(label="Open a Ticket", style=discord.ButtonStyle.primary)
    async def open_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = OpenTicketModal(self.cog)
        try:
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
        
        try:
            # Defer the interaction response
            await interaction.response.defer()
            
            # Create the ticket using the cog's create_ticket method
            await self.cog.create_ticket(interaction.user, ctx, description=description)
            
            # Send a follow-up message to the interaction to indicate success
            await interaction.followup.send("Ticket created!")
        except discord.HTTPException as e:
            await interaction.followup.send(f"Failed to create ticket: {e}")
        except Exception as e:
            await interaction.followup.send(f"An unexpected error occurred: {e}")

class CloseTicketButton(discord.ui.Button):
    def __init__(self, cog, ticket_id):
        super().__init__(style=discord.ButtonStyle.danger, label="Close Ticket", custom_id="close_ticket")
        self.cog = cog
        self.ticket_id = ticket_id
    async def callback(self, interaction: discord.Interaction):
        ctx = await self.cog.bot.get_context(interaction.message)
        await self.cog.close_ticket(ctx, ticket_id=self.ticket_id)

async def setup(bot):
    await bot.add_cog(TicketCommands(bot))