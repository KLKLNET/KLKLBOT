import discord
from discord.ext import commands
from discord import app_commands, Interaction
from difflib import get_close_matches
from contextlib import suppress
from core import Context
from core.axon import axon
from core.Cog import Cog
from utils.Tools import getConfig
from itertools import chain
import json
from utils import help as vhelp
from utils import Paginator, DescriptionEmbedPaginator, FieldPagePaginator, TextPaginator
import asyncio
from utils.config import serverLink
from utils.Tools import *

color_primary = 0x185fe5  # اللون الرئيسي (أزرق)
color_error = 0xff5555   # لون للأخطاء (أحمر جذاب)
client = axon()

class HelpCommand(commands.HelpCommand):

    async def send_ignore_message(self, ctx, ignore_type: str):
        if ignore_type == "channel":
            await ctx.reply(f"🚫 This channel is ignored.", mention_author=False)
        elif ignore_type == "command":
            await ctx.reply(f"{ctx.author.mention} 🚫 This Command, Channel, or You have been ignored here.", delete_after=6)
        elif ignore_type == "user":
            await ctx.reply(f"🚫 You are ignored.", mention_author=False)

    async def on_help_command_error(self, ctx, error):
        errors = [
            commands.CommandOnCooldown, commands.CommandNotFound,
            discord.HTTPException, commands.CommandInvokeError
        ]
        if not type(error) in errors:
            await self.context.reply(f"Unknown Error Occurred\n{error.original}", mention_author=False)
        else:
            if type(error) == commands.CommandOnCooldown:
                return
        return await super().on_help_command_error(ctx, error)

    async def command_not_found(self, string: str) -> None:
        ctx = self.context
        check_ignore = await ignore_check().predicate(ctx)
        check_blacklist = await blacklist_check().predicate(ctx)

        if not check_blacklist:
            return

        if not check_ignore:
            await self.send_ignore_message(ctx, "command")
            return

        cmds = (str(cmd) for cmd in self.context.bot.walk_commands())
        matches = get_close_matches(string, cmds)

        embed = discord.Embed(
            title="🚨 Command Not Found",
            description=f"Command not found with the name `{string}`.",
            color=color_error
        )
        
        embed.set_author(name="Command Not Found", icon_url=self.context.bot.user.avatar.url)
        embed.set_thumbnail(url=self.context.bot.user.avatar.url)
        embed.set_footer(text=f"Requested By {ctx.author}",
                         icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        if matches:
            match_list = "\n".join([f"{index}. `{match}`" for index, match in enumerate(matches, start=1)])
            embed.add_field(name="Did you mean:", value=match_list, inline=True)
        
        await ctx.reply(embed=embed)

    async def send_bot_help(self, mapping):
        ctx = self.context
        check_ignore = await ignore_check().predicate(ctx)
        check_blacklist = await blacklist_check().predicate(ctx)

        if not check_blacklist:
            return

        if not check_ignore:
            await self.send_ignore_message(ctx, "command")
            return

        data = await getConfig(self.context.guild.id)
        prefix = data["prefix"]
        filtered = await self.filter_commands(self.context.bot.walk_commands(), sort=True)

        # الـ embed الجديدة فقط، مع الوصف اللي عاوزو
        embed = discord.Embed(
            title="🛠️ KLKL Help Menu",
            description=(
                f"**🔵 Server Prefix:** `{prefix}`\n"
                f"**🔴 Total Commands:** `350`\n"
            ),
            color=color_primary
        )
        
        embed.set_thumbnail(url=self.context.bot.user.avatar.url)
        embed.add_field(
            name="🗂️ __**Modules**__",
            value=">>> \n 🔊 Voice\n"
                  " 👾 Games\n"
                  " 🤗 Welcomer\n"
                  " ✅ Autoreact & Responder\n"
                  " 🎖️ Autorole & Invc\n"
                  " ⚡ Fun & AI Image Gen\n"
                  " 🙄 Ignore Channels\n" 
                  " 🔐 Advance Logging\n"
                  " 🕵 Invite Tracker\n",
            inline=False
        )
        
        embed.add_field(
            name="🌟 __**Features**__",
            value=">>> \n 🛡️ Security\n"
                  " 🤖 Automoderation\n"
                  " 🛠️ Utility\n"
                  " 🎺 Music\n"
                  " 👑 Moderation\n"
                  " 🎨 Customrole\n"
                  " 🎉 Giveaway\n" 
                  ' 🎫 Ticket\n'
                  " 🎭 Vanityroles\n",
            inline=False
        )

        embed.set_footer(
            text=f"Requested By {self.context.author} | [Support](discord.gg/7Ydjf6874w)",
            icon_url=self.context.bot.user.avatar.url
        )
        
        # استخدام الـ view مع الـ embed الجديدة فقط
        view = vhelp.View(mapping=mapping, ctx=self.context, homeembed=embed, ui=2)
        await ctx.reply(embed=embed, view=view)  # فقط الـ embed دي

    async def send_command_help(self, command):
        ctx = self.context
        check_ignore = await ignore_check().predicate(ctx)
        check_blacklist = await blacklist_check().predicate(ctx)

        if not check_blacklist:
            return

        if not check_ignore:
            await self.send_ignore_message(ctx, "command")
            return

        sonu = f">>> {command.help}" if command.help else '>>> No Help Provided...'
        embed = discord.Embed(
            description=f"""**Usage Guide:**\n```xml
<[] = optional | ‹› = required\nDon't type these while using Commands```\n{sonu}""",
            color=color_primary
        )
        alias = ' | '.join(command.aliases)

        embed.add_field(name="**Aliases**", value=f"{alias}" if command.aliases else "No Aliases", inline=False)
        embed.add_field(name="**Usage**", value=f"`{self.context.prefix}{command.signature}`\n", inline=False)
        embed.set_author(name=f"🛠️ {command.qualified_name.title()} Command", icon_url=self.context.bot.user.display_avatar.url)
        embed.set_thumbnail(url=self.context.bot.user.avatar.url)
        await self.context.reply(embed=embed, mention_author=False)

    def get_command_signature(self, command: commands.Command) -> str:
        parent = command.full_parent_name
        if len(command.aliases) > 0:
            aliases = ' | '.join(command.aliases)
            fmt = f'[{command.name} | {aliases}]'
            if parent:
                fmt = f'{parent}'
            alias = f'[{command.name} | {aliases}]'
        else:
            alias = command.name if not parent else f'{parent} {command.name}'
        return f'{alias} {command.signature}'

    def common_command_formatting(self, embed_like, command):
        embed_like.title = self.get_command_signature(command)
        if command.description:
            embed_like.description = f'{command.description}\n\n{command.help}'
        else:
            embed_like.description = command.help or 'No help found...'

    async def send_group_help(self, group):
        ctx = self.context
        check_ignore = await ignore_check().predicate(ctx)
        check_blacklist = await blacklist_check().predicate(ctx)

        if not check_blacklist:
            return

        if not check_ignore:
            await self.send_ignore_message(ctx, "command")
            return

        entries = [
            (f"➜ `{self.context.prefix}{cmd.qualified_name}`\n", f"{cmd.short_doc if cmd.short_doc else ''}\n\u200b")
            for cmd in group.commands
        ]

        count = len(group.commands)

        paginator = Paginator(source=FieldPagePaginator(
            entries=entries,
            title=f"🛠️ {group.qualified_name.title()} [{count}]",
            description="< > Duty | [ ] Optional\n",
            color=color_primary,
            per_page=4),
            ctx=self.context)
        await paginator.paginate()

    async def send_cog_help(self, cog):
        ctx = self.context
        check_ignore = await ignore_check().predicate(ctx)
        check_blacklist = await blacklist_check().predicate(ctx)

        if not check_blacklist:
            return

        if not check_ignore:
            await self.send_ignore_message(ctx, "command")
            return

        entries = [
            (f"➜ `{self.context.prefix}{cmd.qualified_name}`", f"{cmd.short_doc if cmd.short_doc else ''}\n\u200b")
            for cmd in cog.get_commands()
        ]
        paginator = Paginator(source=FieldPagePaginator(
            entries=entries,
            title=f"🛠️ {cog.qualified_name.title()} ({len(cog.get_commands())})",
            description="< > Duty | [ ] Optional\n\n",
            color=color_primary,
            per_page=4),
            ctx=self.context)
        await paginator.paginate()

class Help(Cog, name="help"):

    def __init__(self, client: axon):
        self._original_help_command = client.help_command
        attributes = {
            'name': "help",
            'aliases': ['h'],
            'cooldown': commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.user),
            'help': 'Shows help about bot, a command, or a category'
        }
        client.help_command = HelpCommand(command_attrs=attributes)
        client.help_command.cog = self

    async def cog_unload(self):
        self.help_command = self._original_help_command