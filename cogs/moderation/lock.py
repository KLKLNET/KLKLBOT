import discord
from discord.ext import commands
from discord import ui

class LockUnlockView(ui.View):
    def __init__(self, channel, author, ctx):
        super().__init__(timeout=120)
        self.channel = channel
        self.author = author
        self.ctx = ctx  
        self.message = None  

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("You are not allowed to interact with this!", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for item in self.children:
            if item.label != "Delete":
                item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except Exception:
                pass

    @ui.button(label="Unlock", style=discord.ButtonStyle.success)
    async def unlock(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.channel.set_permissions(interaction.guild.default_role, send_messages=True)
        await interaction.response.send_message(f"{self.channel.mention} has been unlocked.", ephemeral=True)

        embed = discord.Embed(
            description=f"📺 **Channel**: {self.channel.mention}\n✅ **Status**: Unlocked\n⚙️**Reason:** Unlock request by {self.author}",
            color=0x000000
        )
        embed.add_field(name="👑 **Moderator:**", value=self.ctx.author.mention, inline=False)
        embed.set_author(name=f"Successfully Unlocked {self.channel.name}", icon_url="https://cdn.discordapp.com/attachments/1428481917396848793/1429842264502571028/07996634fe922922.png?ex=68f79be1&is=68f64a61&hm=f5b77dd9a9147d51947e1194e36ceb30ba91f6a55912553f11359a4db3bc939f&")
        await self.message.edit(embed=embed, view=self)

        for item in self.children:
            if item.label != "Delete":
                item.disabled = True
        await self.message.edit(view=self)

    @ui.button(style=discord.ButtonStyle.gray, emoji="🗑️")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()


class Lock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = discord.Color.from_rgb(0, 0, 0)

    @commands.hybrid_command(
        name="lock",
        help="Locks a channel to prevent sending messages.",
        usage="lock <channel>",
        aliases=["lockchannel"])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def lock_command(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel 
        if channel.permissions_for(ctx.guild.default_role).send_messages is False:
            embed = discord.Embed(
                description=f"**📺 Channel**: {channel.mention}\n✅ **Status**: Already Locked",
                color=self.color
            )
            embed.set_author(name=f"{channel.name} is Already Locked", icon_url="https://cdn.discordapp.com/attachments/1428481917396848793/1429842264502571028/07996634fe922922.png?ex=68f79be1&is=68f64a61&hm=f5b77dd9a9147d51947e1194e36ceb30ba91f6a55912553f11359a4db3bc939f&")
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
            view = LockUnlockView(channel=channel, author=ctx.author, ctx=ctx)  
            message = await ctx.send(embed=embed, view=view)
            view.message = message
            return

        await channel.set_permissions(ctx.guild.default_role, send_messages=False)

        embed = discord.Embed(
            description=f"📺 **Channel**: {channel.mention}\n✅ **Status**: Locked\n⚙️ **Reason:** Lock request by {ctx.author}",
            color=self.color
        )
        embed.add_field(name="👑 **Moderator:**", value=ctx.author.mention, inline=False)
        embed.set_author(name=f"Successfully Locked {channel.name}", icon_url="https://cdn.discordapp.com/attachments/1428481917396848793/1429842264502571028/07996634fe922922.png?ex=68f79be1&is=68f64a61&hm=f5b77dd9a9147d51947e1194e36ceb30ba91f6a55912553f11359a4db3bc939f&")
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        view = LockUnlockView(channel=channel, author=ctx.author, ctx=ctx)  
        message = await ctx.send(embed=embed, view=view)
        view.message = message


"""
@ KLKL
    + Discord: khaledfaied
    + Community: https://discord.gg/7Ydjf6874w (KLKL Development)
    + for any queries Go Community or DM me😎.
"""