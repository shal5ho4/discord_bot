import os
from datetime import datetime, timezone, timedelta

import dotenv
import discord
from discord.ext import commands

from server import server_thread

DEBUG = False
JST = timezone(timedelta(hours=+9), 'JST')

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)

TOKEN = os.getenv('BOT_TOKEN')

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)


CHANNEL_ID_TEST_VC = int(os.getenv('CHANNEL_ID_TEST_VC'))
CHANNEL_ID_TEST_TX = int(os.getenv('CHANNEL_ID_TEST_TX'))
CHANNEL_ID_VC_OVER_AND_RISE = int(os.getenv('CHANNEL_ID_VC_OVER_AND_RISE'))
CHANNEL_ID_TX_OVER_AND_RISE = int(os.getenv('CHANNEL_ID_TX_OVER_AND_RISE'))
CHANNEL_ID_VC_RISE = int(os.getenv('CHANNEL_ID_VC_RISE'))
CHANNEL_ID_TX_RISE = int(os.getenv('CHANNEL_ID_TX_RISE'))


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # channel = bot.get_channel(CHANNEL_ID)
    # await channel.send('Voice chat notification READY.')

active_vc_channels = []

@bot.event
async def on_voice_state_update(
    member: discord.Member,
    before: discord.VoiceState,
    after:discord.VoiceState
):
    try:
        if before.channel is None and after.channel is not None:
            voice_channel = after.channel
            if DEBUG:
                text_channel = bot.get_channel(CHANNEL_ID_TEST_TX)
            else:
                if voice_channel.id == CHANNEL_ID_VC_RISE:
                    text_channel = bot.get_channel(CHANNEL_ID_TX_RISE)
                else:
                    text_channel = bot.get_channel(CHANNEL_ID_TX_OVER_AND_RISE)

            if len(voice_channel.members) == 1:
                date = get_date_str()
                await text_channel.send(
                    f"{date}\n🎧 <@{member.id}> が **{voice_channel.name}** でボイスチャットを開始！"
                )

    except Exception as e:
        print(repr(e))
        text_channel = bot.get_channel(CHANNEL_ID_TEST_TX)
        await text_channel.send(e)


def get_date_str() -> str:
    now = datetime.now()
    return f'{now.month}月{now.day}日 {now.hour}時{now.minute}分'


if __name__ == '__main__':
    server_thread()
    bot.run(TOKEN)
