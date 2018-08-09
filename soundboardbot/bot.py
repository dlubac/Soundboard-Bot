import discord
import asyncio
import json
import os
import logging
from discord.ext import commands

# Setup logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# Load opus codec
if not discord.opus.is_loaded():
    discord.opus.load_opus('opus')

# Bot setup
client = commands.Bot(description="Soundboard bot", command_prefix='!', pm_help=True)


async def play_audio(voice_channel, audio_file_path):
    """ Joins a voice channel and plays an audio file

    :param voice_channel: voice channel to join
    :param audio_file_path: relative path to audio file
    :return: none
    """

    logging.info('Playing: ' + audio_file_path)

    voice = await client.join_voice_channel(voice_channel)
    player = voice.create_ffmpeg_player(audio_file_path)
    player.start()

    while not player.is_done():
        await asyncio.sleep(1)

    await voice.disconnect()


async def process_meta_command(message):
    """ Handle meta commands such as !help

    :param message: discord message
    :return: none
    """

    logging.info('Processing meta command: ' + message.content)

    # Read in valid commands
    with open('meta_commands.json', 'r') as f_meta_commands:
        meta_commands_json = json.loads(f_meta_commands.read())

    # Get exact command
    command = str(message.content).lower()

    # Check command validity
    if command not in meta_commands_json['commands']:
        await client.send_message(message.channel, 'Invalid command! Try !help')
        return

    # Handle help command
    if command == '!help':
        help_output = 'Available commands: \n'

        for key, value in meta_commands_json['commands'].items():
            help_output = help_output + key + ': ' + value + '\n'

        await client.send_message(message.channel, help_output)

    # Handle bots command
    elif command == '!bots':
        voice_bots = [f.name for f in os.scandir('../audio') if f.is_dir()]
        voice_bots.sort()
        bot_list_str = 'Available bots: \n'

        for voice_bot in voice_bots:
            bot_list_str = bot_list_str + voice_bot + '\n'

        await client.send_message(message.channel, bot_list_str)
        return

    # Handle example command
    elif command == '!example':
        await client.send_message(message.channel, 'Example command:\n!bdog godgamer')

    # Handle git command
    elif command == '!git':
        await client.send_message(message.channel, 'https://github.com/dlubac/Soundboard-Bot')


async def process_voice_command(message):
    """ Handle commands determined to be a voice command

    :param message: discord message
    :return:
    """

    author_voice_channel = message.author.voice_channel

    voice_bot = str(message.content[1:str(message.content).find(' ')])
    voice_command = str(message.content[str(message.content).find(' ') + 1:]).strip()
    voice_bots = [f.name for f in os.scandir('../audio') if f.is_dir()]

    if voice_bot in voice_bots:
        # Handle 'commands' command
        if voice_command == 'commands':
            bot_commands = []
            bot_commands_str = voice_bot + ' commands:\n'

            # Get all voice commands
            for file in os.listdir('../audio/' + voice_bot + '/'):
                if file.endswith(".mp3"):
                    bot_commands.append(str(file)[:-4])

            bot_commands.sort()

            # Build output string
            for bot_command in bot_commands:
                bot_commands_str = bot_commands_str + bot_command + '\n'

            await client.send_message(message.channel, bot_commands_str)
            return

        # Handle normal voice commands
        if not os.path.isfile('../audio/' + voice_bot + '/' + voice_command + '.mp3'):
            await client.send_message(message.channel, 'Invalid command! Try !' + voice_bot + ' commands')
            return

        else:
            # Join voice server and play audio
            audio_file_path = '../audio/' + voice_bot + '/' + voice_command + '.mp3'
            await play_audio(author_voice_channel, audio_file_path)

    else:
        await client.send_message(message.channel, 'Invalid command! Try !bots')
        return


@client.event
async def on_ready():
    """
    Print basic info on startup

    :return:
    """
    print('Logged in as ' + client.user.name + ' (ID:' + client.user.id + ') | Connected to ' + str(len(client.servers))
          + ' servers | Connected to ' + str(len(set(client.get_all_members()))) + ' users')


@client.event
async def on_message(message):
    """
    Handles parsing of user text input and plays audio clips

    :param message: user input
    """

    # Prevents bot from giving itself commands
    if message.author == client.user:
        return

    # Get message content
    content = str(message.content).lower()

    if content.startswith('!') and content.count(' ') == 0:
        # Capture meta commands
        await process_meta_command(message)

    elif content.startswith('!') and content.count(' ') == 1:
        # Capture voice commands
        await process_voice_command(message)

    else:
        # normal message
        return


def run(secret_env_var: str = 'BOT_SECRET', secret_file_path: str = None):
    """
    Looks for the bot secret in either an environment variable or a file, loads it, and starts the bot
    :param secret_env_var: Optional. Name of environment variable where bot secret is stored
    :param secret_file_path: Optional. Path to file that contains bot secret
    :return:
    """

    try:
        secret = os.environ[secret_env_var]
    except KeyError:
        try:
            with open(secret_file_path, 'r') as f:
                secret = f.read()
        except FileNotFoundError:
            LOGGER.error('Unable to get secret from environment variable "' + secret_env_var + '" or file ' +
                         secret_file_path)
            return
        except TypeError:
            LOGGER.error('Unable to get secret from environment variable "' + secret_env_var +
                         '" and no secret file provided.')
            return

    try:
        client.run(secret)
    except discord.errors.LoginFailure:
        LOGGER.error('Invalid token passed to bot, exiting.')
        return


if __name__ == '__main__':
    run()
