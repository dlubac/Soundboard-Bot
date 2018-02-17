import discord
import asyncio
import json
import os
import logging
from discord.ext import commands

# Load opus codec
if not discord.opus.is_loaded():
    discord.opus.load_opus('opus')

# Bot setup
client = commands.Bot(description="Soundboard bot", command_prefix='!', pm_help=True)


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

    # Get author info
    author = message.author
    author_voice_channel = message.author.voice_channel

    # Get message content
    content = str(message.content).lower()

    # Handle meta commands
    if content.startswith('!') and content.count(' ') == 0:

        # Read in valid commands
        with open('meta_commands.json', 'r') as f_meta_commands:
            meta_commands_json = json.loads(f_meta_commands.read())

        # Get exact command
        command = content[1:]

        # Check command validity
        if command not in meta_commands_json['commands']:
            await client.send_message(message.channel, 'Invalid command! Try !help')
            return

        # Handle help command
        if command == 'help':
            help_output = 'Available commands: \n'

            for key, value in meta_commands_json['commands'].items():
                help_output = help_output + key + ': ' + value + '\n'

            await client.send_message(message.channel, help_output)

        # Handle bots command
        if command == 'bots':
            voice_bots = [f.name for f in os.scandir('../audio') if f.is_dir()]
            bot_list = 'Available bots: \n'

            for voice_bot in voice_bots:
                bot_list = bot_list + voice_bot + '\n'

            await client.send_message(message.channel, bot_list)
            return

        # Handle example command
        if command == 'example':
            await client.send_message(message.channel, 'Example command:\n!bdog godgamer')

    # Handle voice commands
    elif content.startswith('!') and content.count(' ') == 1:
        voice_bot = str(message.content[1:str(message.content).find(' ')])
        voice_command = str(message.content[str(message.content).find(' ') + 1:]).strip()
        voice_bots = [f.name for f in os.scandir('../audio') if f.is_dir()]

        if voice_bot in voice_bots:
            # Handle 'command' command
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
                logging.info('Playing: ' + voice_bot + '/' + voice_command+ '.mp3')
                voice = await client.join_voice_channel(author_voice_channel)
                player = voice.create_ffmpeg_player('../audio/' + voice_bot + '/' + voice_command + '.mp3')
                # player.volume = 0.6
                player.start()

                while not player.is_done():
                    await asyncio.sleep(1)

                await voice.disconnect()

        else:
            await client.send_message(message.channel, 'Invalid command! Try !bots')
            return

    else:
        # normal message
        return


if __name__ == '__main__':
    """
    Reads in bot secret and starts bot

    """

    with open('bot-secret.txt', 'r') as f:
        bot_secret = f.read()

    client.run(bot_secret)
