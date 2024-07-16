import os
#from async_logs import LogMessageAsync

class ConstantsClass:
    @staticmethod
    def get_github_project_directory():
        return os.getcwd()

    SECURITY_FOLDER = "!security/"
    ITCH_IO_GAME_API_KEY = "itch_io_api_key"
    ITCH_IO_GAME_ID = "itch_io_game_id"
    DISCORD_BOT_TOKEN = "discord_bot_token"
    ROLE_NAME = "CatWorld game ping updates"
    URL_GAME_NAME = "catzworld"
    RSS_URL = f"https://iamacatfrdev.itch.io/{URL_GAME_NAME}/devlog.rss"
    RSS_CHANNEL_IDS_JSON_FILE ="/rss_channel_ids.json"
    SENT_RSS_TITLES_JSON_FILE = "/sent_rss_titles.json"

    FEED_BACK_SAVE_FOLDER = get_github_project_directory() + "/CatzWorldBot/saves/feedbacks"
    DOWNLOAD_SAVE_FOLDER = get_github_project_directory() + "/CatzWorldBot/saves/downloads"
    RSS_SAVE_FOLDER = get_github_project_directory() + "/CatzWorldBot/saves/rss"
    TICKET_SAVE_FOLDER = get_github_project_directory() + "/CatzWorldBot/saves/tickets"
    ROLE_SAVE_FOLDER = get_github_project_directory() + "/CatzWorldBot/saves/free_roles"
    LOGS_SAVE_FOLDER = get_github_project_directory() + "/CatzWorldBot/saves/free_roles"

    READ_FILE = "r"
    WRITE_TO_FILE = "w"

    
#LogMessageAsync.LogAsync("The github Project Directory is :", ConstantsClass.get_github_project_directory())