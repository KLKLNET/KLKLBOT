import discord
from discord.ext import commands


class _fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Fun commands"""

    def help_custom(self):
        emoji = '🤪'
        label = "Fun Commands"
        description = "Show you Commands of Fun"
        return emoji, label, description

    @commands.group()
    async def __Fun__(self, ctx: commands.Context):
        """`/imagine`, `ship`, `mydog`, `chat`, `translate`, `howgay`, `lesbian`, `cute`, `intelligence`, `chutiya`, `horny`, `tharki`, `gif`, `iplookup`, `weather`, `hug`, `kiss`, `pat`, `cuddle`, `slap`, `tickle`, `spank`, `8ball`, `truth`, `dare`"""
        await ctx.send("😜 This is the Fun Commands group!")

# مهم جدًا علشان يتسجل الـ Cog في البوت
async def setup(bot):
    await bot.add_cog(_fun(bot))
