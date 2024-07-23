import discord

class ColorUtilityClass:

    colors = {
        'edit': discord.Color.gold(),
        'join': discord.Color.green(),
        'leave': discord.Color.red(),
        'default': discord.Color.blue()
    }

    @staticmethod
    def get_color(action):
        return ColorUtilityClass.colors.get(action, discord.Color.default())
