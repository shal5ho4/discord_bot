import discord
import traceback
from discord.ext import commands

import bot_functions
from logger import logger
from settings import *

# Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logger.info(f'✅ Logged in as {bot.user}')
    channel = bot.get_channel(CHANNEL_ID)

    try:
        previous_title = bot_functions.get_previous_title()
        new_title, _ = bot_functions.get_article_title_and_link()
        
        if previous_title != new_title:
            message = bot_functions.get_notification_message()
        else:
            message = None
    except Exception:
        message = f"なにかがおかしいよ <@{USER_ID}>\n```{traceback.format_exc()}```"

    if message:
        await channel.send(message)

bot.run(TOKEN)
