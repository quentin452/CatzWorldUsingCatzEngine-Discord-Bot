# 🚨 WARNING: THIS BOT MAY BE BUGGED 🚨

# 🤖 Discord Bot Readme

## 🌐 English Translation

### 🎉 Introduction

Welcome to the README for the Discord bot designed to keep your server updated with devlogs and file downloads from your itch.io game. This bot helps you manage notifications directly from your game's updates to your Discord server.

### 🎯 Why Use This Bot?

This bot is essential if you have an itch.io game and want to keep your server members informed about updates such as devlogs and downloadable files.

### ⚙️ Setup Instructions

#### Create Required Files:
- Create the following files in the `!security` folder:
  - `discord_bot_token.txt`
  - `itch_io_api_key.txt`
  - `itch_io_game_id.txt`

#### Token and Keys:
- Open `discord_bot_token.txt` and paste your Discord bot token from the "Discord Developer Portal".
- Open `itch_io_api_key.txt` and paste your itch.io API key for your game.
- Open `itch_io_game_id.txt` and paste your itch.io game ID.

#### Running the Bot:
- Open `main.py` using a Python interpreter to start the bot.

### 📜 Commands

#### Itch.io Devlogs

- `!set_rss_channel`
  - Set the channel where updated devlogs will be displayed.

- `!get_all_rss` (REQUIRE ADMINISTRATOR PERMISSIONS)
  - Retrieve all devlogs from your itch.io game.

- `!get_last_rss`
  - Retrieve last devlog from your itch.io game.

#### Itch.io Files

- `!set_download_channel`
  - Set the channel where updated download files will be displayed.

- `!get_all_download` (REQUIRE ADMINISTRATOR PERMISSIONS)
  - Retrieve all downloadable files from your itch.io game.

- `!get_last_download`
  - Retrieve the last downloadable file from your itch.io game.

#### Other

- `!hello [iamacat]`
  - Simply say hello to `iamacat`.

- `!reset_channel` (REQUIRE ADMINISTRATOR PERMISSIONS)
  - Reset all messages from the channel (use with caution).

- `!help_cat`
  - Retrieve a list of all commands of the bot

### 📝 Note

Ensure your bot has appropriate permissions to read and send messages in the channels where you intend to set updates. For any issues or suggestions, please contact the bot developer.

This README provides basic setup and usage instructions for your Discord bot tailored for managing itch.io game updates.

## 🌐 French Translation

### 🎉 Introduction

Bienvenue dans le README du bot Discord conçu pour maintenir votre serveur à jour avec les devlogs et les téléchargements de fichiers de votre jeu sur itch.io. Ce bot vous aide à gérer les notifications directement depuis les mises à jour de votre jeu vers votre serveur Discord.

### 🎯 Pourquoi Utiliser Ce Bot ?

Ce bot est essentiel si vous avez un jeu sur itch.io et que vous souhaitez tenir les membres de votre serveur informés des mises à jour telles que les devlogs et les fichiers téléchargeables.

### ⚙️ Instructions de Configuration

#### Création des Fichiers Requis :
- Créez les fichiers suivants dans le dossier `!security` :
  - `discord_bot_token.txt`
  - `itch_io_api_key.txt`
  - `itch_io_game_id.txt`

#### Jetons et Clés :
- Ouvrez `discord_bot_token.txt` et collez-y le token de votre bot Discord provenant du "Portail des Développeurs Discord".
- Ouvrez `itch_io_api_key.txt` et collez-y la clé API de votre jeu itch.io.
- Ouvrez `itch_io_game_id.txt` et collez-y l'ID de votre jeu itch.io.

#### Lancer le Bot :
- Ouvrez `main.py` avec un interpréteur Python pour démarrer le bot.

### 📜 Commandes

#### Journaux de développement d'Itch.io

- `!set_rss_channel`
  - Définissez le canal sur lequel les devlogs mis à jour seront affichés.

- `!get_all_rss` (EXIGE LES AUTORISATIONS DE L'ADMINISTRATEUR)
  - Récupérez tous les devlogs de votre jeu itch.io.

- `!get_last_rss`
  - Récupérez le dernier devlog de votre jeu itch.io.

#### Fichiers Itch.io

- `!set_download_channel`
  - Définissez le canal sur lequel les fichiers téléchargés mis à jour seront affichés.

- `!get_all_download` (EXIGE LES AUTORISATIONS DE L'ADMINISTRATEUR)
  - Récupérez tous les fichiers téléchargeables de votre jeu itch.io.

- `!get_last_download`
  - Récupérez le dernier fichier téléchargeable de votre jeu itch.io.

#### Autre

- `!bonjour [iamacat]`
  - Dites simplement bonjour à « iamacat ».

- `!reset_channel` (EXIGE LES AUTORISATIONS DE L'ADMINISTRATEUR)
  - Réinitialiser tous les messages de la chaîne (à utiliser avec prudence).

- `!help_cat`
  - Récupérer une liste de toutes les commandes du bot

### 📝 Remarque

Assurez-vous que votre bot a les permissions appropriées pour lire et envoyer des messages dans les canaux où vous souhaitez définir les mises à jour. Pour tout problème ou suggestion, veuillez contacter le développeur du bot.

Ce README fournit des instructions de configuration de base et d'utilisation pour votre bot Discord, adapté à la gestion des mises à jour de votre jeu itch.io.
