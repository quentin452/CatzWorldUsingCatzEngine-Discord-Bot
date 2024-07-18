import discord
from discord.ext import commands
from discord.ui import View, Button
import time

class RPSGame:
    def __init__(self, player1, player2):
        self.moves = {player1: None, player2: None}
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.start_time = time.time()

    def make_move(self, player, move):
        if move.lower() not in ['rock', 'paper', 'scissors']:
            return False
        self.moves[player] = move.lower()
        return True

    def determine_winner(self):
        move1 = self.moves[self.player1]
        move2 = self.moves[self.player2]

        if move1 == move2:
            return None  # Tie
        elif (move1 == 'rock' and move2 == 'scissors') or \
             (move1 == 'paper' and move2 == 'rock') or \
             (move1 == 'scissors' and move2 == 'paper'):
            return self.player1
        else:
            return self.player2

    def print_moves(self):
        return f"{self.player1.display_name}: {self.moves[self.player1]}\n{self.player2.display_name}: {self.moves[self.player2]}"

class RPSView(View):
    def __init__(self, game, restart_callback, quit_callback):
        super().__init__()
        self.game = game
        self.restart_callback = restart_callback
        self.quit_callback = quit_callback
        self.add_buttons()
        self.start_time = time.time()

    def add_buttons(self):
        accept_button = Button(label="Accept", style=discord.ButtonStyle.success)
        accept_button.callback = self.accept_game_callback
        self.add_item(accept_button)

        quit_button = Button(label="Quit", style=discord.ButtonStyle.danger)
        quit_button.callback = self.quit_game_callback
        self.add_item(quit_button)

    async def accept_game_callback(self, interaction: discord.Interaction):
        if interaction.user != self.game.player2:
            await interaction.response.send_message("You are not authorized to respond to this invitation.", ephemeral=True)
            return

        # Remove Accept button
        for child in self.children:
            if child.label == "Accept":
                self.remove_item(child)
                break

        # Add Rock, Paper, Scissors buttons for every user
        for move in ['rock', 'paper', 'scissors']:
            button = Button(label=move.capitalize(), style=discord.ButtonStyle.secondary)
            button.callback = await self.create_callback(move)
            self.add_item(button)

        # Start the game
        self.game.current_player = self.game.player1
        await interaction.response.edit_message(content=f"{self.game.player1.display_name} vs {self.game.player2.display_name}\nTurn of {self.game.current_player.display_name}", view=self)

    async def create_callback(self, move):
        async def callback(interaction: discord.Interaction):
            if interaction.user != self.game.current_player:
                await interaction.response.send_message("It's not your turn!", ephemeral=True)
                return

            if not self.game.make_move(interaction.user, move):
                await interaction.response.send_message("Invalid move. Please choose Rock, Paper, or Scissors.", ephemeral=True)
                return

            # Update the message to show who has made a move
            await interaction.message.edit(content=f"{self.game.player1.display_name} vs {self.game.player2.display_name}\nTurn of {self.game.current_player.display_name}\n{self.game.player1.display_name}: {'Chosen' if self.game.moves[self.game.player1] else 'Waiting'}\n{self.game.player2.display_name}: {'Chosen' if self.game.moves[self.game.player2] else 'Waiting'}", view=self)

            if self.game.moves[self.game.player1] and self.game.moves[self.game.player2]:
                # Both players have made their moves, determine the winner
                winner = self.game.determine_winner()
                loser = self.game.player2 if winner == self.game.player1 else self.game.player1
                embed = discord.Embed(title=f"Congratulations {winner.display_name}!",
                                      description=f"{winner.display_name} won against {loser.display_name}.",
                                      color=discord.Color.green())
                embed.add_field(name="Moves", value=self.game.print_moves())
                await interaction.response.send_message(embed=embed)
                self.stop()
                return

            # Continue game, switch player and update message
            self.game.current_player = self.game.player2 if self.game.current_player == self.game.player1 else self.game.player1
            await self.update_turn_message(interaction)

        return callback

    async def update_turn_message(self, interaction):
        await interaction.message.edit(content=f"{self.game.player1.display_name} vs {self.game.player2.display_name}\nTurn of {self.game.current_player.display_name}", view=self)

    def end_game(self):
        self.game = None
        self.stop()
        self.restart_callback()

    async def quit_game_callback(self, interaction: discord.Interaction):
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(content=f"{interaction.user.display_name} has quit the game against {self.game.player1.display_name} and {self.game.player2.display_name}.")
        self.end_game()
        self.clear_items()

class RPSCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}
        self.pending_invites = {}

    @commands.command(help="Invite a player to start a game of Rock-Paper-Scissors.")
    async def rps(self, ctx, opponent: discord.Member):
        if ctx.author == opponent:
            await ctx.send("You cannot play against yourself.")
            return

        if ctx.author in self.pending_invites or ctx.author in self.active_games:
            await ctx.send("You already have a pending invite or are already in a game.")
            return

        if opponent in self.pending_invites and self.pending_invites[opponent][0] == ctx.author:
            await ctx.send("You have already sent an invite to this player.")
            return

        self.pending_invites[ctx.author] = (opponent, time.time())

        game = RPSGame(ctx.author, opponent)
        view = RPSView(game, self.restart_callback(ctx.author, opponent), self.quit_callback(ctx.author, opponent))
        await ctx.send(f"{opponent.mention}, {ctx.author.mention} invites you to play Rock-Paper-Scissors. Do you accept?", view=view)

        self.active_games[ctx.author] = game
        self.active_games[opponent] = game

    def restart_callback(self, player1, player2):
        def callback():
            if player1 in self.active_games:
                del self.active_games[player1]
            if player2 in self.active_games:
                del self.active_games[player2]
        return callback

    def quit_callback(self, player1, player2):
        async def callback(interaction: discord.Interaction):
            if player1 in self.active_games:
                del self.active_games[player1]
            if player2 in self.active_games:
                del self.active_games[player2]
        return callback

async def setup(bot):
    await bot.add_cog(RPSCommands(bot))