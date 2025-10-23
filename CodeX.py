import os
import asyncio
import traceback
import logging
import sys
from threading import Thread
from datetime import datetime
import time  # لتسجيل وقت التشغيل
import aiohttp
import discord
from discord.ext import commands
from dotenv import load_dotenv

# تهيئة نظام التسجيل (logging) مع دعم UTF-8
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler('bot.log', encoding='utf-8'), logging.StreamHandler()], encoding='utf-8')
logger = logging.getLogger(__name__)

# تحميل المتطلبات بشكل أفضل
try:
    os.system("python -m pip install -r requirements.txt")
except Exception as e:
    logger.error(f"Error installing requirements: {e}")

from core import Context
from core.Cog import Cog
from core.axon import axon
from utils.Tools import *
from utils.config import *

import jishaku
import cogs

# إعدادات Jishaku
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "False"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"

load_dotenv()
TOKEN = os.getenv("TOKEN")

# تحقق من الـ TOKEN
if not TOKEN:
    logger.error("TOKEN not found in .env file! Please add it and restart.")
    exit(1)

client = axon()
tree = client.tree

async def on_ready():
    start_time = time.time()
    await client.wait_until_ready()
    end_time = time.time()
    startup_duration = end_time - start_time
    
    # ASCII Art مع ألوان، لكن استخدم طريقة بديلة إذا كان في مشكلة
    ascii_art = """
██╗  ██╗██╗     ██╗  ██╗██╗         ██╗  ██╗███████╗██████╗ ███████╗
██║ ██╔╝██║     ██║ ██╔╝██║         ██║  ██║██╔════╝██╔══██╗██╔════╝
█████╔╝ ██║     █████╔╝ ██║         ███████║█████╗  ██████╔╝█████╗  
██╔═██╗ ██║     ██╔═██╗ ██║         ██╔══██║██╔══╝  ██╔══██╗██╔══╝  
██║  ██╗███████╗██║  ██╗███████╗    ██║  ██║███████╗██║  ██║███████╗
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝    ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
    """
    logger.info(ascii_art)  # استخدم النص فقط دون ألوان لتجنب الأخطاء
    logger.info("Loaded & Online!")
    logger.info(f"Logged in as: {client.user}")
    logger.info(f"Connected to: {len(client.guilds)} guilds")
    logger.info(f"Connected to: {len(client.users)} users")
    logger.info(f"Startup time: {startup_duration:.2f} seconds")
    try:
        synced = await client.tree.sync()
        all_commands = list(client.commands)
        logger.info(f"Synced Total {len(all_commands)} Client Commands and {len(synced)} Slash Commands")
    except Exception as e:
        logger.error(f"Error syncing commands: {e}")
        traceback.print_exc()

client.event(on_ready)

async def on_command_completion(context: commands.Context) -> None:
    if context.author.id == 1360373818148913362:
        return

    full_command_name = context.command.qualified_name
    split = full_command_name.split("\n")
    executed_command = str(split[0])
    webhook_url = "https://discord.com/api/webhooks/1428492678479483031/QjZ7s6ix_jERVZ4WIP4n6kiwTztFPknk0NNT7uzLjd66xIKjGDNjHheBlj1HXbb7iccX"
    
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(webhook_url, session=session)
        if context.guild:
            try:
                embed = discord.Embed(color=0x000000)
                avatar_url = context.author.avatar.url if context.author.avatar else context.author.default_avatar.url
                embed.set_author(name=f"Executed {executed_command} Command By : {context.author}", icon_url=avatar_url)
                embed.set_thumbnail(url=avatar_url)
                embed.add_field(name=" Command Name :", value=f"{executed_command}", inline=False)
                embed.add_field(name=" Command Executed By :", value=f"{context.author} | ID: [{context.author.id}](https://discord.com/users/{context.author.id})", inline=False)
                embed.add_field(name=" Command Executed In :", value=f"{context.guild.name} | ID: [{context.guild.id}](https://discord.com/guilds/{context.guild.id})", inline=False)
                embed.add_field(name=" Command Executed In Channel :", value=f"{context.channel.name} | ID: [{context.channel.id}](https://discord.com/channels/{context.guild.id}/{context.channel.id})", inline=False)
                embed.timestamp = datetime.utcnow()
                embed.set_footer(text="KLKL ❤️", icon_url=client.user.display_avatar.url)
                await webhook.send(embed=embed)
            except Exception as e:
                logger.error(f'Command failed: {e}')
        else:
            try:
                embed1 = discord.Embed(color=0x000000)
                avatar_url = context.author.avatar.url if context.author.avatar else context.author.default_avatar.url
                embed1.set_author(name=f"Executed {executed_command} Command By : {context.author}", icon_url=avatar_url)
                embed1.set_thumbnail(url=avatar_url)
                embed1.add_field(name=" Command Name :", value=f"{executed_command}", inline=False)
                embed1.add_field(name=" Command Executed By :", value=f"{context.author} | ID: [{context.author.id}](https://discord.com/users/{context.author.id})", inline=False)
                embed1.set_footer(text="KLKL", icon_url=client.user.display_avatar.url)
                await webhook.send(embed=embed1)
            except Exception as e:
                logger.error(f'Command failed: {e}')

client.event(on_command_completion)

from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "KLKL 2026 - The Ultimate Edition!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    server = Thread(target=run)
    server.start()

keep_alive()

async def main():
    # استخدام cls على Windows
    if os.name == 'nt':  # nt تعني Windows
        os.system('cls')
    else:
        os.system('clear')
    await client.load_extension("jishaku")
    await client.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
