import os

class ConstantsClass:
    @staticmethod
    def get_github_project_directory():
        return os.getcwd()

    SECURITY_FOLDER = "!security/"

    DISCORD_BOT_CLIENT_ID = "discord_bot_client_id"
    DISCORD_BOT_CLIENT_SECRET = "discord_bot_client_secret"
    DISCORD_BOT_INVITE_LINK = "discord_bot_invite_link"
    DISCORD_BOT_LOGIN_URL = "discord_bot_login_url"
    DISCORD_BOT_REDIRECT_URL = "discord_bot_redirect_url"

    READ_FILE = "r"
    WRITE_TO_FILE = "w"