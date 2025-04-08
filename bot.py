import os
import discord
import dotenv
from discord.ext import commands

import bot_functions

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)

TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
USER_ID = int(os.getenv('USER_ID'))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    
    latest_title, _ = bot_functions.get_article_title_and_link()
    previous_title = bot_functions.get_previous_title()

    if latest_title != previous_title:
        channel = bot.get_channel(CHANNEL_ID)
        message = bot_functions.get_notification_message()
        message += f"<@{USER_ID}>"
        await channel.send(message)
    else:
        print("No new update found.")

bot.run(TOKEN)
