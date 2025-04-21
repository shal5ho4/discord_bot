import os

import dotenv
import discord
from discord.ext import commands


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)

CHANNEL_ID = int(os.getenv('CHANNEL_ID_DEBUG'))
TOKEN = os.getenv('BOT_TOKEN_TEST_VC')

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send('Voice chat notification READY.')


@bot.event
async def on_voice_state_update(member, before, after):
    try:
        if before.channel is None and after.channel is not None:
            voice_channel = after.channel
            text_channel = bot.get_channel(CHANNEL_ID)

            if len(voice_channel.members) == 1:
                await text_channel.send(
                    f"🎧 {member.display_name} started a voice chat in **{voice_channel.name}**!"
                )
    except Exception as e:
        print(repr(e))


bot.run(TOKEN)
