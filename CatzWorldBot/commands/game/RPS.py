import discord
from discord.ext import commands
from discord.ui import View, Button
import time
import random
import json
import os
from utils.Constants import ConstantsClass

# Classe pour le jeu RPS
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

# Vue pour le jeu RPS
class RPSView(View):
    def __init__(self, game, restart_callback, quit_callback, bot_game=False):
        super().__init__()
        self.game = game
        self.restart_callback = restart_callback
        self.quit_callback = quit_callback
        self.bot_game = bot_game
        self.add_buttons()
        self.start_time = time.time()

    def add_buttons(self):
        if not self.bot_game:
            accept_button = Button(label="Accept", style=discord.ButtonStyle.success, emoji="✅")
            accept_button.callback = self.accept_game_callback
            self.add_item(accept_button)

        quit_button = Button(label="Quit", style=discord.ButtonStyle.danger, emoji="❌")
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

        await self.start_game(interaction)

    async def start_game(self, interaction):
        # Add Rock, Paper, Scissors buttons for every user
        for move in ['rock', 'paper', 'scissors']:
            emoji = {"rock": "✊", "paper": "✋", "scissors": "✌️"}[move]
            button = Button(label=move.capitalize(), style=discord.ButtonStyle.secondary, emoji=emoji)
            button.callback = await self.create_callback(move)
            self.add_item(button)

        embed = discord.Embed(title=f"Rock-Paper-Scissors: {self.game.player1.display_name} vs {self.game.player2.display_name}", color=discord.Color.blurple())
        embed.add_field(name="Current Status", value=f"{self.game.player1.display_name}: Waiting\n{self.game.player2.display_name}: Waiting")
        await interaction.response.edit_message(content=None, embed=embed, view=self)

    async def create_callback(self, move):
        async def callback(interaction: discord.Interaction):
            if interaction.user not in [self.game.player1, self.game.player2]:
                await interaction.response.send_message("You are not a participant in this game!", ephemeral=True)
                return

            if not self.game.make_move(interaction.user, move):
                await interaction.response.send_message("Invalid move. Please choose Rock, Paper, or Scissors.", ephemeral=True)
                return

            if self.bot_game and interaction.user == self.game.player1:
                # If playing against bot, bot makes a move
                bot_move = random.choice(['rock', 'paper', 'scissors'])
                self.game.make_move(self.game.player2, bot_move)

            # Update the embed to show who has made a move
            embed = discord.Embed(title=f"Rock-Paper-Scissors: {self.game.player1.display_name} vs {self.game.player2.display_name}", color=discord.Color.blurple())
            embed.add_field(name="Current Status", value=f"{self.game.player1.display_name}: {'Chosen' if self.game.moves[self.game.player1] else 'Waiting'}\n{self.game.player2.display_name}: {'Chosen' if self.game.moves[self.game.player2] else 'Waiting'}")

            await interaction.message.edit(embed=embed, view=self)

            if self.game.moves[self.game.player1] and self.game.moves[self.game.player2]:
                # Both players have made their moves, determine the winner
                winner = self.game.determine_winner()
                if winner is None:
                    result = "It's a tie!"
                    color = discord.Color.yellow()
                else:
                    result = f"The winner is {winner.display_name}!"
                    color = discord.Color.green()

                result_embed = discord.Embed(title="Game Result", description=result, color=color)
                result_embed.add_field(name="Moves", value=self.game.print_moves())
                await interaction.response.send_message(embed=result_embed)
                await self.disable_all_buttons(interaction)
                self.end_game()
                return

            # Continue game, switch player and update embed
            self.game.current_player = self.game.player2 if self.game.current_player == self.game.player1 else self.game.player1
            embed = discord.Embed(title=f"Rock-Paper-Scissors: {self.game.player1.display_name} vs {self.game.player2.display_name}", color=discord.Color.blurple())
            embed.add_field(name="Current Status", value=f"{self.game.player1.display_name}: {'Chosen' if self.game.moves[self.game.player1] else 'Waiting'}\n{self.game.player2.display_name}: {'Chosen' if self.game.moves[self.game.player2] else 'Waiting'}")
            await interaction.message.edit(embed=embed, view=self)

        return callback

    async def disable_all_buttons(self, interaction):
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

    def end_game(self):
        self.game = None
        self.stop()
        self.restart_callback()

    async def quit_game_callback(self, interaction: discord.Interaction):
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(content=f"{interaction.user.display_name} has quit the game against {self.game.player1.display_name} and {self.game.player2.display_name}.")
        await self.disable_all_buttons(interaction)
        self.stop()
        await self.quit_callback(interaction)

# Classe des commandes RPS
class RPSCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}
        self.pending_invites = {}
        self.game_stats = self.load_game_stats()

    def load_game_stats(self):
        # Assurer que le répertoire existe
        os.makedirs(os.path.dirname(ConstantsClass.STATS_SAVE_FILE), exist_ok=True)

        # Charger les statistiques à partir du fichier JSON
        if os.path.exists(ConstantsClass.STATS_SAVE_FILE):
            with open(ConstantsClass.STATS_SAVE_FILE, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        else:
            return {}

    def save_game_stats(self):
        # Assurer que le répertoire existe
        os.makedirs(os.path.dirname(ConstantsClass.STATS_SAVE_FILE), exist_ok=True)

        # Sauvegarder les statistiques dans le fichier JSON
        with open(ConstantsClass.STATS_SAVE_FILE, 'w') as f:
            json.dump(self.game_stats, f, indent=4)

    @commands.command(help="Invite a player to start a game of Rock-Paper-Scissors.")
    async def rps(self, ctx, opponent: discord.Member = None):
        if opponent is None:
            await ctx.send("Please mention a member to play against. For example: `/rps @member`")
            await self.send_game_stats(ctx.channel, ctx.author)
            return

        if ctx.author == opponent:
            await ctx.send("You cannot play against yourself.")
            return

        if opponent.bot:
            await ctx.send("You cannot play against a bot.")
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

    async def send_game_stats(self, channel, member):
        stats_embed = discord.Embed(title=f"Rock-Paper-Scissors Statistics for {member.display_name}", color=discord.Color.blurple())

        if member.id not in self.game_stats:
            stats_embed.add_field(name="Games Played", value="0")
            stats_embed.add_field(name="Games Won", value="0")
            stats_embed.add_field(name="Games Lost", value="0")
            stats_embed.add_field(name="Last Played", value="Never")
        else:
            stats = self.game_stats[member.id]
            stats_embed.add_field(name="Games Played", value=stats['games_played'])
            stats_embed.add_field(name="Games Won", value=stats['games_won'])
            stats_embed.add_field(name="Games Lost", value=stats['games_lost'])
            stats_embed.add_field(name="Last Played", value=stats['last_played'])

        await channel.send(embed=stats_embed)

    async def play_against_bot(self, ctx):
        bot_user = ctx.bot.user
        game = RPSGame(ctx.author, bot_user)
        view = RPSView(game, self.restart_callback(ctx.author, bot_user), self.quit_callback(ctx.author, bot_user), bot_game=True)
        self.active_games[ctx.author] = game
        await view.start_game(ctx)

    def update_game_stats(self, winner, loser):
        # Update winner stats
        if winner.id not in self.game_stats:
            self.game_stats[winner.id] = {'games_played': 0, 'games_won': 0, 'games_lost': 0, 'last_played': ''}
        self.game_stats[winner.id]['games_played'] += 1
        self.game_stats[winner.id]['games_won'] += 1
        self.game_stats[winner.id]['last_played'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

        # Update loser stats
        if loser.id not in self.game_stats:
            self.game_stats[loser.id] = {'games_played': 0, 'games_won': 0, 'games_lost': 0, 'last_played': ''}
        self.game_stats[loser.id]['games_played'] += 1
        self.game_stats[loser.id]['games_lost'] += 1
        self.game_stats[loser.id]['last_played'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

        self.save_game_stats()

    def restart_callback(self, player1, player2):
        def callback():
            if player1 in self.active_games:
                del self.active_games[player1]
            if player2 in self.active_games:
                del self.active_games[player2]
            if player1 in self.pending_invites:
                del self.pending_invites[player1]
            if player2 in self.pending_invites:
                del self.pending_invites[player2]
        return callback

    def quit_callback(self, player1, player2):
        async def callback(interaction: discord.Interaction):
            if player1 in self.active_games:
                del self.active_games[player1]
            if player2 in self.active_games:
                del self.active_games[player2]
            if player1 in self.pending_invites:
                del self.pending_invites[player1]
            if player2 in self.pending_invites:
                del self.pending_invites[player2]
            await interaction.message.channel.send(f"{player1.display_name} and {player2.display_name} can now start a new game if they want.")
        return callback

async def setup(bot):
    await bot.add_cog(RPSCommands(bot))
