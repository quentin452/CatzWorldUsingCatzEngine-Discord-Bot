import os
from utils.Constants import ConstantsClass
from utils.async_logs import LogMessageAsync

def load_config():
    # Vérifier et créer les fichiers si nécessaire pour l'API key itch.io
    create_file_if_not_exists(ConstantsClass.SECURITY_FOLDER + ConstantsClass.ITCH_IO_GAME_API_KEY + ".txt", ConstantsClass.ITCH_IO_GAME_API_KEY)
    create_file_if_not_exists(ConstantsClass.SECURITY_FOLDER + ConstantsClass.ITCH_IO_GAME_ID + ".txt", ConstantsClass.ITCH_IO_GAME_ID)
    create_file_if_not_exists(ConstantsClass.SECURITY_FOLDER + ConstantsClass.DISCORD_BOT_TOKEN + ".txt", ConstantsClass.DISCORD_BOT_TOKEN)

    # Lire les valeurs depuis les fichiers
    api_key = read_file(ConstantsClass.SECURITY_FOLDER + ConstantsClass.ITCH_IO_GAME_API_KEY + ".txt")
    game_id = read_file(ConstantsClass.SECURITY_FOLDER + ConstantsClass.ITCH_IO_GAME_ID + ".txt")
    token = read_file(ConstantsClass.SECURITY_FOLDER + ConstantsClass.DISCORD_BOT_TOKEN + ".txt")

    # Vérifier si les valeurs sont vides et afficher un message approprié si nécessaire
    if not api_key:
        LogMessageAsync.LogAsync("Veuillez mettre votre API key de votre jeu d'itch.io dans le fichier " + ConstantsClass.SECURITY_FOLDER + ConstantsClass.ITCH_IO_GAME_API_KEY + ".txt")
    if not game_id:
        LogMessageAsync.LogAsync("Veuillez mettre l'ID de votre jeu itch.io dans le fichier " + ConstantsClass.SECURITY_FOLDER + ConstantsClass.ITCH_IO_GAME_ID + ".txt")
    if not token:
        LogMessageAsync.LogAsync("Veuillez mettre le token de votre bot discord dans le fichier " + ConstantsClass.SECURITY_FOLDER + ConstantsClass.DISCORD_BOT_TOKEN + ".txt")

    return {
        'api_key': api_key,
        'game_id': game_id,
        'token': token
    }

def create_file_if_not_exists(file_path, default_content=''):
    if not os.path.exists(file_path):
        with open(file_path, ConstantsClass.WRITE_TO_FILE) as f:
            f.write(default_content)

def read_file(file_path):
    with open(file_path, ConstantsClass.READ_FILE) as f:
        return f.read().strip()
