from datetime import datetime, timezone, timedelta

import discord
from discord.ext import commands

from const import *
from modal import RegisterView
# from server import server_thread


intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree


##### bot commands #####
@tree.command(name='henlo', description='Say hello')
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
                    f"{date}\n🎧 <@{member.id}> が <#{voice_channel.id}> でボイスチャットを開始！"
                )

    except Exception as e:
        print(repr(e))
        text_channel = bot.get_channel(CHANNEL_ID_TEST_TX)
        await text_channel.send(e)


JST = timezone(timedelta(hours=+9), 'JST')

def get_date_str() -> str:
    now = datetime.now(JST)
    return f'{now.month}月{now.day}日 {now.hour}時{now.minute}分'


# @bot.event
# async def on_member_join(member: discord.Member):
#     try:
#         message = MSG_WELCOME.replace('@member', member.display_name)
#         await member.send(message, view=RegisterView())

#     except discord.Forbidden:
#         print(f'on_member_join: Could not send the message to {member.display_name}')


if __name__ == '__main__':
    if DEBUG:
        bot.run(TOKEN_TEST)
    else:
        bot.run(TOKEN)
