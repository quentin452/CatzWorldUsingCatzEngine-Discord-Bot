import os

def load_config():
    # Vérifier et créer les fichiers si nécessaire pour l'API key itch.io
    create_file_if_not_exists('!security/itch_io_api_key.txt', 'itch_io_api_key')
    create_file_if_not_exists('!security/itch_io_game_id.txt', 'itch_io_game_id')
    create_file_if_not_exists('!security/discord_bot_token.txt', 'discord_bot_token_id')

    # Lire les valeurs depuis les fichiers
    api_key = read_file('!security/itch_io_api_key.txt')
    game_id = read_file('!security/itch_io_game_id.txt')
    token = read_file('!security/discord_bot_token.txt')

    # Vérifier si les valeurs sont vides et afficher un message approprié si nécessaire
    if not api_key:
        print("Veuillez mettre votre API key de votre jeu d'itch.io dans le fichier '!security/itch_io_api_key.txt'.")
    if not game_id:
        print("Veuillez mettre l'ID de votre jeu itch.io dans le fichier '!security/itch_io_game_id.txt'.")
    if not token:
        print("Veuillez mettre le token de votre bot discord dans le fichier '!security/discord_bot_token.txt'.")

    return {
        'api_key': api_key,
        'game_id': game_id,
        'token': token
    }

def create_file_if_not_exists(file_path, default_content=''):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write(default_content)

def read_file(file_path):
    with open(file_path, 'r') as f:
        return f.read().strip()
