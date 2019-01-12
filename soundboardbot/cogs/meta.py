import logging
from glob import glob

from discord import utils
from discord.ext import commands

from soundboardbot.models.bot_role import BotRole
from soundboardbot.config.help_message import HELP_MESSAGE
from soundboardbot.utils import sb_utils

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


class Meta:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help')
    async def help(self, ctx):
        """
        Send user message will basic usage info
        :param ctx: message context
        """
        await ctx.message.author.send(HELP_MESSAGE)
        await ctx.message.delete()

    @commands.command(name='boards')
    async def boards(self, ctx):
        """
        Send user message with list of boards
        :param ctx: message context
        """
        board_map = map(lambda board: board.replace('boards/', ''), glob('boards/*'))
        boards = 'Available soundboards:\n' + '\n'.join(list(board_map))

        await ctx.message.author.send(boards)
        await ctx.message.delete()

    @commands.command(name='setup')
    async def setup(self, ctx):
        """
        Setup roles for the bot
        :param ctx: message context
        """
        guild = ctx.message.guild
        roles = guild.roles
        role_names = [role.name for role in roles]

        if sb_utils.has_role(ctx.message.author, BotRole.OWNER.value) or BotRole.OWNER.value not in role_names:
            bot_roles = [role.value for role in BotRole]
            for role in bot_roles:
                if role not in role_names:
                    await guild.create_role(name=role)
                    LOGGER.info(f'Created role {role}')
                else:
                    LOGGER.info(f'Role {role} already exists')
        else:
            await ctx.message.author.send('You must have the BotOwner role to run the !setup command.')

        await ctx.message.delete()

    @commands.command(name='register')
    async def register(self, ctx):
        """
        Registers a user to use the bot
        :param ctx: Message context
        """
        roles = [role.name for role in ctx.message.author.roles]

        if BotRole.USER.value not in roles:
            bot_user_role = utils.get(ctx.guild.roles, name=BotRole.USER.value)
            await ctx.message.author.add_roles(bot_user_role)
            await ctx.message.author.send('You are now registered to use the bot. Try typing !help to get started.')
            LOGGER.info(f'Registered user {ctx.message.author}')
        else:
            await ctx.message.author.send('You are already registered to use the bot')

        await ctx.message.delete()


def setup(bot):
    bot.add_cog(Meta(bot))
