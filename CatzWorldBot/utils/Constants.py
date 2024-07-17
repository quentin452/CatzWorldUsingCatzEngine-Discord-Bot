import os
import json
import discord
class ConstantsClass:
    @staticmethod
    def get_github_project_directory():
        return os.getcwd()

    SECURITY_FOLDER = "!security/"
    ITCH_IO_GAME_API_KEY = "itch_io_api_key"
    ITCH_IO_GAME_ID = "itch_io_game_id"
    DISCORD_BOT_TOKEN = "discord_bot_token"
    CATZ_WORLD_ROLE_NAME = "CatWorld game ping updates"
    MEMBER_ROLE_NAME = "@Members"
    VERIFIED_ROLE_NAME = "verified"
    URL_GAME_NAME = "catzworld"
    RSS_URL = f"https://iamacatfrdev.itch.io/{URL_GAME_NAME}/devlog.rss"
    RSS_CHANNEL_IDS_JSON_FILE ="/rss_channel_ids.json"
    SENT_RSS_TITLES_JSON_FILE = "/sent_rss_titles.json"

    FEED_BACK_SAVE_FOLDER = get_github_project_directory() + "/CatzWorldBot/saves/feedbacks"
    DOWNLOAD_SAVE_FOLDER = get_github_project_directory() + "/CatzWorldBot/saves/downloads"
    RSS_SAVE_FOLDER = get_github_project_directory() + "/CatzWorldBot/saves/rss"
    TICKET_SAVE_FOLDER = get_github_project_directory() + "/CatzWorldBot/saves/tickets"
    ROLE_SAVE_FOLDER = get_github_project_directory() + "/CatzWorldBot/saves/free_roles"
    LOGS_SAVE_FOLDER = get_github_project_directory() + "/CatzWorldBot/saves/logs"
    MUSIC_SAVE_FOLDER = get_github_project_directory() + "/CatzWorldBot/saves/musics"

    READ_FILE = "r"
    WRITE_TO_FILE = "w"


    channel_type_map = {
        discord.ChannelType.text: 'Text',
        discord.ChannelType.voice: 'Voice',
        discord.ChannelType.category: 'Category',
        discord.ChannelType.forum: 'Forum',
        discord.ChannelType.news: 'Announcement',
        discord.ChannelType.stage_voice: 'Stage',
        discord.ChannelType.media: 'Media',
        discord.ChannelType.news_thread: 'Announcement Thread',
        discord.ChannelType.private: 'Private',
        discord.ChannelType.private_thread: 'Private Thread',
        discord.ChannelType.public_thread: 'Public thread',
    # Ajoutez d'autres types de canaux ici si nécessaire
    }

    async def doNotLogMessagesFromAnotherBot(self,before):
        if before.author.bot:  # Ne pas logger les messages des autres bots
            return          

    def load_channel_template(self,json_folder_and_name,key):
        if os.path.exists(json_folder_and_name):
            with open(json_folder_and_name, 'r') as f:
                return json.load(f).get(key)
        else:
            return None

    def save_channel_template(self, json_folder_and_name, key, channel_id):
        with open(json_folder_and_name, 'w') as f:
            json.dump({key: channel_id}, f)

   