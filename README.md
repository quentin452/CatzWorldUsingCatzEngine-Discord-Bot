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

- `/set_rss_channel`
  - Set the channel where updated devlogs will be displayed.

- `/get_all_rss` (REQUIRE ADMINISTRATOR PERMISSIONS)
  - Retrieve all devlogs from your itch.io game.

- `/get_last_rss`
  - Retrieve last devlog from your itch.io game.

#### Itch.io Files

- `/set_download_channel`
  - Set the channel where updated download files will be displayed.

- `/get_all_download` (REQUIRE ADMINISTRATOR PERMISSIONS)
  - Retrieve all downloadable files from your itch.io game.

- `/get_last_download`
  - Retrieve the last downloadable file from your itch.io game.

### Itch.io feedbacks and reports

- `/set_ticket_channel` (REQUIRE ADMINISTRATOR PERMISSIONS) 
  - Set the channel where ticket dashboard/embed for ticket will be displayed.

- `/close_ticket` (REQUIRE ADMINISTRATOR PERMISSIONS)
  - Close a Ticket

- `/set_feedback_channel` (REQUIRE ADMINISTRATOR PERMISSIONS)
  - Set the channel where ticket dashboard/embed for feedback will be displayed.

- `/submit_feedback [query]`
  - Give feedback for the itch io game.

- `/view_feedbacks` (REQUIRE ADMINISTRATOR PERMISSIONS)
  - See all feedbacks given by users

### Logging

- `/set_on_channel_logs` (REQUIRE ADMINISTRATOR PERMISSIONS)
  - Sets the log channel for (Channel) logging events.

- `/set_on_commands_logs_channel` (REQUIRE ADMINISTRATOR PERMISSIONS)
  - Sets the log channel for (Commands) logging events.

- `/set_on_file_watch_logs_channel` (REQUIRE ADMINISTRATOR PERMISSIONS)
  - Sets the log channel for (File Watch) logging events.

- `/set_on_member_logs_channel` (REQUIRE ADMINISTRATOR PERMISSIONS)
  - Sets the log channel for (Members) logging events.

- `/set_on_message_logs_channel` (REQUIRE ADMINISTRATOR PERMISSIONS)
  - Sets the log channel for (Message) logging events.

- `/set_on_music_logs_channel` (REQUIRE ADMINISTRATOR PERMISSIONS)
  - Sets the log channel for (Musics) logging events.

- `/set_on_reaction_logs_channel` (REQUIRE ADMINISTRATOR PERMISSIONS)
  - Sets the log channel for (Reaction) logging events.

- `/set_on_ready_logs_channel` (REQUIRE ADMINISTRATOR PERMISSIONS)
  - Sets the log channel for (Ready) logging events.

- `/set_on_user_logs_channel` (REQUIRE ADMINISTRATOR PERMISSIONS)
  - Sets the log channel for (Users) logging events.

- `/set_on_voice_state_logs_channel` (REQUIRE ADMINISTRATOR PERMISSIONS)
  - Sets the log channel for (Voice/Stream State) logging events.

#### Other

- `/hello [query]`
  - Simply say hello to `query`.

- `/reset_channel` (REQUIRE ADMINISTRATOR PERMISSIONS)
  - Reset all messages from the channel (use with caution).

- `/help_cat`
  - Retrieve a list of all commands of the bot

- `/role_menu` (REQUIRE ADMINISTRATOR PERMISSIONS)
  - Add a sort of reaction role menu

- `/simulate_boost` (REQUIRE ADMINISTRATOR PERMISSIONS)
  - Simulate a boost

- `/restart` (REQUIRE ADMINISTRATOR PERMISSIONS)
  - Restart the bot

- `/play_song [url]`
  - Play music from YouTube link in music vocal room 

- `/stop_song`
  - stop music from voice music

### 📝 Note

This bot code is (probably) intended to be used only for one server due to json caching

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

- `/set_rss_channel`
  - Définissez le canal sur lequel les devlogs mis à jour seront affichés.

- `/get_all_rss` (EXIGE LES AUTORISATIONS DE L'ADMINISTRATEUR)
  - Récupérez tous les devlogs de votre jeu itch.io.

- `/get_last_rss`
  - Récupérez le dernier devlog de votre jeu itch.io.

#### Fichiers Itch.io

- `/set_download_channel`
  - Définissez le canal sur lequel les fichiers téléchargés mis à jour seront affichés.

- `/get_all_download` (EXIGE LES AUTORISATIONS DE L'ADMINISTRATEUR)
  - Récupérez tous les fichiers téléchargeables de votre jeu itch.io.

- `/get_last_download`
  - Récupérez le dernier fichier téléchargeable de votre jeu itch.io.

### Commentaires et rapports Itch.io

- `/set_ticket_channel` (EXIGER LES AUTORISATIONS DE L'ADMINISTRATEUR) 
  - Définissez le canal sur lequel le tableau de bord du ticket/l'intégration du ticket sera affiché.

- `/close_ticket` (EXIGER LES AUTORISATIONS DE L'ADMINISTRATEUR)
  - Fermer un ticket

- `/set_feedback_channel` (EXIGENCE DES AUTORISATIONS D'ADMINISTRATEUR)
  - Définissez le canal sur lequel le tableau de bord des tickets/l'intégration des commentaires sera affiché.

- `/submit_feedback [requête]`
  - Donnez votre avis sur le jeu itch io.

- `/view_feedbacks` (EXIGENCE DES AUTORISATIONS D'ADMINISTRATEUR)
  - Voir tous les commentaires donnés par les utilisateurs


### Journalisation

- `/set_on_channel_logs` (EXIGER LES AUTORISATIONS DE L'ADMINISTRATEUR)
  - Définit le canal de journalisation pour les événements de journalisation (Channel).

- `/set_on_commands_logs_channel` (EXIGER LES AUTORISATIONS DE L'ADMINISTRATEUR)
  - Définit le canal de journalisation pour les événements de journalisation (Commandes).

- `/set_on_file_watch_logs_channel` (EXIGER DES AUTORISATIONS D'ADMINISTRATEUR)
  - Définit le canal de journalisation pour les événements de journalisation (File Watch).

- `/set_on_member_logs_channel` (EXIGER LES AUTORISATIONS DE L'ADMINISTRATEUR)
  - Définit le canal de journalisation pour les événements de journalisation (membres).

- `/set_on_message_logs_channel` (EXIGER LES AUTORISATIONS DE L'ADMINISTRATEUR)
  - Définit le canal de journalisation pour les événements de journalisation (messages).

- `/set_on_music_logs_channel` (EXIGER LES AUTORISATIONS DE L'ADMINISTRATEUR)
  - Définit le canal de journalisation pour les événements de journalisation (Musique).

- `/set_on_reaction_logs_channel` (EXIGER LES AUTORISATIONS DE L'ADMINISTRATEUR)
  - Définit le canal de journalisation pour les événements de journalisation (réaction).

- `/set_on_ready_logs_channel` (EXIGER LES AUTORISATIONS DE L'ADMINISTRATEUR)
  - Définit le canal de journalisation pour les événements de journalisation (Prêt).

- `/set_on_user_logs_channel` (EXIGER LES AUTORISATIONS DE L'ADMINISTRATEUR)
  - Définit le canal de journalisation pour les événements de journalisation (utilisateurs).

- `/set_on_voice_state_logs_channel` (EXIGER DES AUTORISATIONS D'ADMINISTRATEUR)
  - Définit le canal de journalisation pour les événements de journalisation (Voice/Stream State).

#### Autre

- `/bonjour [requête]`
  - Dites simplement bonjour à « requête ».

- `/reset_channel` (EXIGE LES AUTORISATIONS DE L'ADMINISTRATEUR)
  - Réinitialiser tous les messages de la chaîne (à utiliser avec prudence).

- `/help_cat`
  - Récupérer une liste de toutes les commandes du bot

- `/role_menu` (EXIGE LES AUTORISATIONS DE L'ADMINISTRATEUR)
  - Ajoute un genre de menu de reaction role

- `/simulate_boost` (EXIGENCE DES AUTORISATIONS D'ADMINISTRATEUR)
  - Simuler un boost

- `/play_song [url]`
  - Jouez de la musique à partir d'un lien YouTube dans la salle vocale musicale 

- `/stop_chanson`
  - arrêter la musique de la musique vocale

### 📝 Remarque

Ce bot code est (probablement) destiné à être utilisé uniquement pour un seul serveur en raison de la mise en cache JSON

Assurez-vous que votre bot a les permissions appropriées pour lire et envoyer des messages dans les canaux où vous souhaitez définir les mises à jour. Pour tout problème ou suggestion, veuillez contacter le développeur du bot.

Ce README fournit des instructions de configuration de base et d'utilisation pour votre bot Discord, adapté à la gestion des mises à jour de votre jeu itch.io.
