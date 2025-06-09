import json
import requests
import traceback

from parser import ArticleParser, ArticleListParser
from settings import *


def lambda_handler(event:dict={}, context=None):
    is_test = event.get('test', False)
    status = 200
    body = '✅ Update check complete'

    try:
        list_parser = ArticleListParser(WEEKLY_URL)
        previous_title = get_previous_title()
        new_title = list_parser.title 
        
        if previous_title != new_title or is_test:
            article_parser = ArticleParser(list_parser.link)
            message = article_parser.get_notification_message()
            set_previous_title(new_title)
        else:
            print('lambda_handler: Check complete. No updates found.')
            message = None

    except Exception as e:
        status = 503
        body = '❌ Update check failed'
        message = f"なにかがおかしいよ <@{USER_ID}>\n```{traceback.format_exc()}```"
        print(repr(e))
    
    if message:
        add_message = event.get('add_message')
        if add_message:
            message = f'{add_message}\n' + message
        if status != 200 or is_test:
            webhook_url = WEBHOOK_URL_DEBUG
        else:
            webhook_url = WEBHOOK_URL

        print('lambda_handler: Check complete. Sending message...')
        try:
            send_discord_webhook(webhook_url, message)
        except Exception as e:
            status = 503
            body = '❌ Send webhook failed'
            print(repr(e))
    
    return {'statusCode': status, 'body': body}


def send_discord_webhook(webhook_url: str, message: str):
    headers = {'Content-Type': 'application/json'}
    data = {'content': message}
    response = requests.post(webhook_url, data=json.dumps(data), headers=headers)

    if not response.ok:
        raise Exception(f'send_discord_webhook: request failed with status code {response.status_code}')


if __name__ == '__main__':
    event = {
        'test': True,
        'add_message': '※ 6/9修正版'
    }
    lambda_handler(event)


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
