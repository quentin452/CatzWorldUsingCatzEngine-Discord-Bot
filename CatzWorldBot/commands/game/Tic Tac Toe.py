import discord
from discord.ext import commands
from discord.ui import Button, View

class TicTacToeGame:
    def __init__(self, player1, player2):
        self.board = [' ' for _ in range(9)]
        self.current_winner = None
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1

    def available_moves(self):
        return [i for i, spot in enumerate(self.board) if spot == ' ']

    def make_move(self, square, letter):
        if self.board[square] == ' ':
            self.board[square] = letter
            if self.winner(square, letter):
                self.current_winner = letter
            return True
        return False

    def winner(self, square, letter):
        row_ind = square // 3
        row = self.board[row_ind*3:(row_ind+1)*3]
        if all([s == letter for s in row]):
            return True
        col_ind = square % 3
        column = [self.board[col_ind+i*3] for i in range(3)]
        if all([s == letter for s in column]):
            return True
        if square % 2 == 0:
            diagonal1 = [self.board[i] for i in [0, 4, 8]]
            if all([s == letter for s in diagonal1]):
                return True
            diagonal2 = [self.board[i] for i in [2, 4, 6]]
            if all([s == letter for s in diagonal2]):
                return True
        return False

    def print_board(self):
        return '\n'.join(['| ' + ' | '.join(self.board[i*3:(i+1)*3]) + ' |' for i in range(3)])

class TicTacToeView(View):
    def __init__(self, game, restart_callback):
        super().__init__(timeout=180)
        self.game = game
        self.restart_callback = restart_callback
        self.add_buttons()

    def add_buttons(self):
        for i in range(9):
            button = Button(label=str(i + 1), style=discord.ButtonStyle.secondary, row=i//3)
            button.callback = self.create_callback(i)
            self.add_item(button)

    def create_callback(self, move_index):
        async def callback(interaction: discord.Interaction):
            if interaction.user != self.game.current_player:
                await interaction.response.send_message("Ce n'est pas votre tour!", ephemeral=True)
                return

            letter = 'X' if self.game.current_player == self.game.player1 else 'O'
            if not self.game.make_move(move_index, letter):
                await interaction.response.send_message("Cet emplacement est déjà pris. Choisissez un autre emplacement.", ephemeral=True)
                return

            for item in self.children:
                if isinstance(item, Button) and item.label == str(move_index + 1):
                    item.label = letter
                    item.style = discord.ButtonStyle.primary if letter == 'X' else discord.ButtonStyle.success
                    item.disabled = True
                    break

            await interaction.response.edit_message(view=self)

            if self.game.current_winner:
                for child in self.children:
                    child.disabled = True
                await interaction.followup.send(f'Le joueur {interaction.user.mention} ({letter}) a gagné!\n{self.game.print_board()}')
                self.end_game()
                return

            if not self.game.available_moves():
                for child in self.children:
                    child.disabled = True
                await interaction.followup.send('Partie nulle!\n' + self.game.print_board())
                self.end_game()
                return

            self.game.current_player = self.game.player2 if self.game.current_player == self.game.player1 else self.game.player1
        return callback

    def end_game(self):
        self.game = None
        self.stop()

        self.restart_callback()

class TicTacToeCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}
        self.pending_invites = {}

    @commands.command(help="Invite un joueur pour commencer une partie de Tic Tac Toe.")
    async def ttt(self, ctx, opponent: discord.Member):
        if ctx.author == opponent:
            await ctx.send("Vous ne pouvez pas jouer contre vous-même.")
            return

        if ctx.author in self.pending_invites.values() or ctx.author in self.active_games:
            await ctx.send("Vous avez déjà une invitation en attente ou vous êtes déjà dans une partie.")
            return

        self.pending_invites[ctx.author] = opponent

        view = discord.ui.View()
        confirm_button = discord.ui.Button(style=discord.ButtonStyle.success, label=f"Accepter {ctx.author.display_name}")
        confirm_button.callback = self.accept_invite(ctx.author, opponent)
        view.add_item(confirm_button)

        deny_button = discord.ui.Button(style=discord.ButtonStyle.danger, label=f"Refuser {ctx.author.display_name}")
        deny_button.callback = self.deny_invite(ctx.author)
        view.add_item(deny_button)

        message = await ctx.send(f"{opponent.mention}, {ctx.author.mention} vous invite à jouer à Tic Tac Toe.", view=view)

    def accept_invite(self, player1, player2):
        async def callback(interaction: discord.Interaction):
            if interaction.user == player2:
                game = TicTacToeGame(player1, player2)
                self.active_games[player1] = game
                self.active_games[player2] = game

                view = TicTacToeView(game, self.restart_callback(player1, player2))
                await interaction.message.edit(content=f"{player1.mention} vs {player2.mention}\nTour de {player1.mention} (X)", view=view)

                del self.pending_invites[player1]
            else:
                await interaction.response.send_message("Vous n'êtes pas autorisé à répondre à cette invitation.", ephemeral=True)
        return callback

    def deny_invite(self, player1):
        async def callback(interaction: discord.Interaction):
            if interaction.user == player1 and player1 in self.pending_invites:
                await interaction.response.send_message("Invitation refusée.")
                del self.pending_invites[player1]
        return callback

    def restart_callback(self, player1, player2):
        def callback():
            if player1 in self.active_games:
                del self.active_games[player1]
            if player2 in self.active_games:
                del self.active_games[player2]
        return callback

    @ttt.error
    async def ttt_error(self, ctx, error):
        await ctx.send(f'Une erreur est survenue : {error}')

async def setup(bot):
    await bot.add_cog(TicTacToeCommands(bot))
