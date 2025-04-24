import os
from datetime import datetime, timezone, timedelta

import dotenv
import discord
from discord.ext import commands

# from server import server_thread


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)


TOKEN = os.getenv('BOT_TOKEN')

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree


CHANNEL_ID_TEST_TX = int(os.getenv('CHANNEL_ID_TEST_TX'))
CHANNEL_ID_TEST_VC = int(os.getenv('CHANNEL_ID_TEST_VC'))
CHANNEL_ID_TEST_VC_2 = int(os.getenv('CHANNEL_ID_TEST_VC_2'))

CHANNEL_ID_TX_OVER_AND_RISE = int(os.getenv('CHANNEL_ID_TX_OVER_AND_RISE'))
CHANNEL_ID_VC_OVER_AND_RISE = int(os.getenv('CHANNEL_ID_VC_OVER_AND_RISE'))
CHANNEL_ID_VC_CAR_MEET = int(os.getenv('CHANNEL_ID_VC_CAR_MEET'))

CHANNEL_ID_TX_RISE = int(os.getenv('CHANNEL_ID_TX_RISE'))
CHANNEL_ID_VC_RISE = int(os.getenv('CHANNEL_ID_VC_RISE'))

CHANNEL_ID_TX_OVER = int(os.getenv('CHANNEL_ID_TX_OVER'))
CHANNEL_ID_VC_OVER = int(os.getenv('CHANNEL_ID_VC_OVER'))
CHANNEL_ID_VC_OVER_2 = int(os.getenv('CHANNEL_ID_VC_OVER_2'))
CHANNEL_ID_VC_OVER_3 = int(os.getenv('CHANNEL_ID_VC_OVER_3'))

CHANNEL_ID_MANAGE = int(os.getenv('CHANNEL_ID_MANAGE'))

TX_CHANNEL_IDS = {
    # to test server
    CHANNEL_ID_TEST_VC:             CHANNEL_ID_TEST_TX,
    CHANNEL_ID_TEST_VC_2:           CHANNEL_ID_TEST_TX,

    # to over and rise channel
    CHANNEL_ID_VC_OVER_AND_RISE:    CHANNEL_ID_TX_OVER_AND_RISE,
    CHANNEL_ID_VC_CAR_MEET:         CHANNEL_ID_TX_OVER_AND_RISE,

    # to rise channel
    CHANNEL_ID_VC_RISE:             CHANNEL_ID_TX_RISE,

    # to over channel
    CHANNEL_ID_VC_OVER:             CHANNEL_ID_TX_OVER,
    CHANNEL_ID_VC_OVER_2:           CHANNEL_ID_TX_OVER,
    CHANNEL_ID_VC_OVER_3:           CHANNEL_ID_TX_OVER,
}


##### bot event functions #####
@bot.event
async def on_ready():
    await tree.sync()
    print(f'Logged in as {bot.user}')
    # channel = bot.get_channel(CHANNEL_ID)
    # await channel.send('Voice chat notification READY.')


@bot.event
async def on_voice_state_update(
    member: discord.Member,
    before: discord.VoiceState,
    after:discord.VoiceState
):
    try:
        if before.channel is None and after.channel is not None:
            voice_channel = after.channel
            text_channel_id = TX_CHANNEL_IDS.get(voice_channel.id, CHANNEL_ID_TEST_TX)
            text_channel = bot.get_channel(text_channel_id)
            
            print(f'text_channel: {text_channel.name}')

            if len(voice_channel.members) == 1 and text_channel:
                date = get_date_str()
                await text_channel.send(
                    f"{date}\n🎧 <@{member.id}> が **{voice_channel.name}** でボイスチャットを開始！"
                )

    except Exception as e:
        print(repr(e))
        text_channel = bot.get_channel(CHANNEL_ID_TEST_TX)
        await text_channel.send(e)


JST = timezone(timedelta(hours=+9), 'JST')

def get_date_str() -> str:
    now = datetime.now(JST)
    return f'{now.month}月{now.day}日 {now.hour}時{now.minute}分'


##### bot commands #####
@tree.command(name='hello', description='Say hello')
async def hello_command(interaction: discord.Interaction):
    await interaction.response.send_message(f'👋 Hello, {interaction.user.display_name}!')


@tree.command(name='no-role', description='ロールがついてない人を教えてくれます。')
async def list_no_role_members(interaction: discord.Interaction):
    await interaction.response.defer()

    if interaction.channel_id != CHANNEL_ID_MANAGE:
        await interaction.followup.send('❌ ここではつかえません')
    else:
        try:
            guild = interaction.guild
            members = [m async for m in guild.fetch_members(limit=None)]
            no_role_members = [m for m in members if len(m.roles) == 1]

            if not no_role_members:
                await interaction.followup.send("✅ 全員ロールあり！ヨシ！")
                return
            
            # names = "\n".join(member.display_name for member in no_role_members)
            names = "\n".join(m.mention for m in no_role_members)
            await interaction.followup.send(
                f'👥ロールがついてない人\n{names}'
            )
        
        except Exception as e:
            print(repr(e))
            await interaction.followup.send('なにかがおかしいよ')


if __name__ == '__main__':
    bot.run(TOKEN)
