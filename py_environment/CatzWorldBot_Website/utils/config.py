import os
from utils.Constants import ConstantsClass

def load_config():
    # Vérifier et créer les fichiers si nécessaire pour l'API key itch.io
    create_file_if_not_exists(ConstantsClass.SECURITY_FOLDER + ConstantsClass.DISCORD_BOT_CLIENT_ID + ".txt", ConstantsClass.DISCORD_BOT_CLIENT_ID)
    create_file_if_not_exists(ConstantsClass.SECURITY_FOLDER + ConstantsClass.DISCORD_BOT_CLIENT_SECRET + ".txt", ConstantsClass.DISCORD_BOT_CLIENT_SECRET)
    create_file_if_not_exists(ConstantsClass.SECURITY_FOLDER + ConstantsClass.DISCORD_BOT_INVITE_LINK + ".txt", ConstantsClass.DISCORD_BOT_INVITE_LINK)
    create_file_if_not_exists(ConstantsClass.SECURITY_FOLDER + ConstantsClass.DISCORD_BOT_LOGIN_URL + ".txt", ConstantsClass.DISCORD_BOT_LOGIN_URL)
    create_file_if_not_exists(ConstantsClass.SECURITY_FOLDER + ConstantsClass.DISCORD_BOT_REDIRECT_URL + ".txt", ConstantsClass.DISCORD_BOT_REDIRECT_URL)

    # Lire les valeurs depuis les fichiers
    bot_client_id = read_file(ConstantsClass.SECURITY_FOLDER + ConstantsClass.DISCORD_BOT_CLIENT_ID + ".txt")
    bot_client_secret = read_file(ConstantsClass.SECURITY_FOLDER + ConstantsClass.DISCORD_BOT_CLIENT_SECRET + ".txt")
    bot_invite_link = read_file(ConstantsClass.SECURITY_FOLDER + ConstantsClass.DISCORD_BOT_INVITE_LINK + ".txt")
    bot_login_url = read_file(ConstantsClass.SECURITY_FOLDER + ConstantsClass.DISCORD_BOT_LOGIN_URL + ".txt")
    bot_redirect_url = read_file(ConstantsClass.SECURITY_FOLDER + ConstantsClass.DISCORD_BOT_REDIRECT_URL + ".txt")

    return {
        'bot_client_id': bot_client_id,
        'bot_client_secret': bot_client_secret,
        'bot_invite_link': bot_invite_link,
        'bot_login_url': bot_login_url,
        'bot_redirect_url': bot_redirect_url
    }

def create_file_if_not_exists(file_path, default_content=''):
    if not os.path.exists(file_path):
        with open(file_path, ConstantsClass.WRITE_TO_FILE) as f:
            f.write(default_content)

def read_file(file_path):
    with open(file_path, ConstantsClass.READ_FILE) as f:
        return f.read().strip()
