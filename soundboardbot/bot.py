import logging
import os
from glob import glob

import discord
from discord.ext import commands

# Setup logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# Bot setup
bot = commands.Bot(description="Soundboard bot", command_prefix='!', pm_help=True)


@bot.event
async def on_ready():
    """
    Print basic info on startup and load extensions
    :return:
    """
    LOGGER.info('Starting generation and loading of board cogs')

    boards = list(map(lambda b: b.replace('boards/', '').lower(), glob('boards/*')))
    for board in boards:
        template_text = populate_board_template('templates/board.template', board)

        with open('cogs/' + board + '.py', 'w') as f:
            f.write(template_text)

        bot.load_extension('cogs.' + board)


def populate_board_template(template: str, class_name: str) -> str:
    """
    Generate a cog script from a template
    :param template: path to template
    :param class_name: name of class in cog
    :return: text of python script
    """

    LOGGER.info('Generating board template for ' + class_name)
    with open(template, 'r') as f:
        template_text = f.read()

    template_text = template_text.replace('<className>', class_name.capitalize())
    template_text = template_text.replace('<commandName>', class_name)

    return template_text


def run(token_env_var: str = 'BOT_TOKEN', token_file_path: str = None):
    """
    Looks for the bot token in either an environment variable or a file, loads it, and starts the bot
    :param token_env_var: Optional. Name of environment variable where bot token is stored
    :param token_file_path: Optional. Path to file that contains bot token
    :return:
    """

    try:
        token = os.environ[token_env_var]
    except KeyError:
        try:
            with open(token_file_path, 'r') as f:
                token = f.read()
        except FileNotFoundError:
            LOGGER.error('Unable to get token from environment variable "' + token_env_var + '" or file ' +
                         token_file_path)
            return
        except TypeError:
            LOGGER.error('Unable to get token from environment variable "' + token_env_var +
                         '" and no token file provided.')
            return

    try:
        bot.run(token)
    except discord.LoginFailure:
        LOGGER.error('Invalid token passed to bot, exiting.')
        return


if __name__ == '__main__':
    run(token_file_path='config/bot_token')
