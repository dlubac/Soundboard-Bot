from glob import glob

from discord.ext import commands


class Meta:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='boards')
    async def boards(self, ctx):
        """
        Send user message with list of boards
        :param ctx: message context
        :return:
        """

        board_map = map(lambda board: board.replace('boards/', ''), glob('boards/*'))
        boards = 'Available soundboards:\n' + '\n'.join(list(board_map))

        await ctx.message.author.send(boards)


def setup(bot):
    bot.add_cog(Meta(bot))
