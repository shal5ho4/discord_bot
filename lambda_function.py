import bot_functions
from settings import *

import traceback

def lambda_handler(event=None, context=None):
    try:
        previous_title = bot_functions.get_previous_title()
        new_title, _ = bot_functions.get_article_title_and_link()
        
        if previous_title != new_title:
            message = bot_functions.get_notification_message()
            bot_functions.set_new_title(new_title)
        else:
            message = None
    except Exception:
        message = f"なにかがおかしいよ <@{USER_ID}>\n```{traceback.format_exc()}```"
    
    if message:
        bot_functions.send_discord_webhook(message, WEBHOOK_URL)
    
    return {'statusCode': 200, 'body': 'Update check complete'}


if __name__ == '__main__':
    lambda_handler()

# import discord
# import traceback
# from discord.ext import commands, tasks

# import bot_functions
# from logger import logger
# from settings import *

# # Discord
# intents = discord.Intents.default()
# intents.message_content = True
# bot = commands.Bot(command_prefix="!", intents=intents)

# @bot.event
# async def on_ready():
#     logger.info(f'✅ Logged in as {bot.user}')
#     check_for_updates.start()

# @tasks.loop(hours=1)
# async def check_for_updates():
#     print('checking for updates...')

#     channel = bot.get_channel(CHANNEL_ID)
#     try:
#         previous_title = bot_functions.get_previous_title()
#         new_title, _ = bot_functions.get_article_title_and_link()
        
#         if previous_title != new_title:
#             message = bot_functions.get_notification_message()
#             bot_functions.set_new_title(new_title)
#         else:
#             message = None
#     except Exception:
#         message = f"なにかがおかしいよ <@{USER_ID}>\n```{traceback.format_exc()}```"

#     if message:
#         await channel.send(message)

#     print('done!')

# bot.run(TOKEN)
