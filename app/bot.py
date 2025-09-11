import inspect
from datetime import datetime, timezone, timedelta

import discord
from discord import app_commands
from discord.ext import commands

from const import *
from modal import RegisterView
# from server import server_thread


intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.guild_scheduled_events = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree


##### bot commands #####
@tree.command(name='henlo', description='Say hello')
async def hello_command(interaction: discord.Interaction):
    await interaction.response.send_message(f'👋 Hello, {interaction.user.display_name}!', ephemeral=True)


@tree.command(name='no-role', description='ロールがついてない人を教えてくれます。')
async def list_no_role_members(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    if interaction.channel_id not in COMMAND_WHITE_LIST:
        await interaction.followup.send('❌ ここではつかえません', ephemeral=True)
    else:
        try:
            guild = interaction.guild
            members = [m async for m in guild.fetch_members(limit=None)]
            no_role_members = [m for m in members if len(m.roles) == 1]

            if not no_role_members:
                await interaction.followup.send("✅ 全員ロールあり！ヨシ！", silent=True)
                return
            
            names = "\n".join(m.mention for m in no_role_members)
            await interaction.followup.send(f'👥ロールがついてない人\n{names}')
        
        except Exception as e:
            await send_error_log(e, inspect.currentframe().f_code.co_name)
            interaction.followup.send('なにかがおかしいよ')


@tree.command(name='role-member-list', description='ロールごとのメンバーを教えてくれます。')
@app_commands.describe(role='ロールを選択！')
async def list_role_members(
    interaction: discord.Interaction,
    role: discord.Role
):
    await interaction.response.defer(ephemeral=True)

    if interaction.channel_id not in COMMAND_WHITE_LIST:
        await interaction.followup.send('❌ ここではつかえません', ephemeral=True)
    else:
        try:
            members = [member for member in role.members]
            members.sort(key=lambda m: m.display_name.lower())
            member_list = "\n".join(member.mention for member in members)

            if not members:
                await interaction.followup.send(
                    '🤦‍♀️ 該当するメンバーがいませんでした',
                    ephemeral=True
                )
                return
            
            await interaction.followup.send(
                f'👥 {role.name} ロールのメンバーは...\n{member_list}\nです！',
                ephemeral=True
            )

        except Exception as e:
            await send_error_log(e, inspect.currentframe().f_code.co_name)
            await interaction.followup.send('なにかがおかしいよ')


##### bot event functions #####
@bot.event
async def on_ready():
    await tree.sync()
    print(f'Logged in as {bot.user}')
    # channel = bot.get_channel(CHANNEL_ID)
    # await channel.send('Voice chat notification READY.')


# 終了メッセージ用 {channel_id: message_id}
# TODO: クラスにする？
active_voice_channels = {}

@bot.event
async def on_voice_state_update(
    member: discord.Member,
    before: discord.VoiceState,
    after:discord.VoiceState
):
    """
    send VC notifications
    """
    try:
        if before.channel is None and after.channel is not None:
            voice_channel = after.channel
            text_channel_id = TX_CHANNEL_IDS.get(voice_channel.id, CHANNEL_ID_TEST_TX)
            text_channel = bot.get_channel(text_channel_id)
            
            print(f'send notification to → {text_channel.name}')

            if len(voice_channel.members) == 1:
                # start notification
                date = get_date_str()
                message = await text_channel.send(
                    f"{date}\n🎧 <@{member.id}> が **<#{voice_channel.id}>** でボイスチャットを開始！"
                )
                active_voice_channels[voice_channel.id] = message.id
        
        elif before.channel is not None and after.channel is None:
            voice_channel = before.channel
            text_channel_id = TX_CHANNEL_IDS.get(voice_channel.id, CHANNEL_ID_TEST_TX)
            text_channel = bot.get_channel(text_channel_id)

            if len(voice_channel.members) == 0 and voice_channel.id in active_voice_channels:
                # end notification
                msg_id = active_voice_channels[voice_channel.id]
                original_message = await text_channel.fetch_message(msg_id)

                date = get_date_str()
                await original_message.reply(
                    f'{date}\nボイスチャットが終了しました。',
                    silent=True
                )
                active_voice_channels.pop(voice_channel.id)

    except Exception as e:
        await send_error_log(e, inspect.currentframe().f_code.co_name)


JST = timezone(timedelta(hours=+9), 'JST')

def get_date_str() -> str:
    now = datetime.now(JST)
    return f'{now.month}月{now.day}日 {now.hour}時{now.minute}分'


@bot.event
async def on_member_join(member: discord.Member):
    """
    add the role to a newly joined member
    """
    if DEBUG:
        role_id = ROLE_ID_TEST
        # channel_id = CHANNEL_ID_TEST_TX
    else:
        role_id = ROLE_ID_RISE
        # channel_id = CHANNEL_ID_MANAGE

    role = member.guild.get_role(role_id)
    # channel = bot.get_channel(channel_id)
    
    if role:
        try:
            await member.add_roles(role, reason='bot自動登録')
            # await channel.send(f'{member.mention} さんを {role.mention} に設定しました！')

        except Exception as e:
            await send_error_log(e, inspect.currentframe().f_code.co_name)


@bot.event
async def on_scheduled_event_create(event: discord.ScheduledEvent):
    """
    send event-created notification
    """
    if event.guild_id == SERVER_ID:
        channel_id = CHANNEL_ID_OSHIRASE
    else:
        channel_id = CHANNEL_ID_TEST_TX

    channel = bot.get_channel(channel_id)
    content = f'<@{event.creator_id}> がイベントを作成しました📝\n{event.url}'

    await channel.send(content=content)


# @bot.event
# async def on_member_join(member: discord.Member):
#     try:
#         message = MSG_WELCOME.replace('@member', member.display_name)
#         await member.send(message, view=RegisterView())

#     except discord.Forbidden:
#         print(f'on_member_join: Could not send the message to {member.display_name}')


async def send_error_log(e: Exception, func_name: str = None):
    channel = bot.get_channel(CHANNEL_ID_TEST_TX)
    message =f'Function:{func_name}\nStacktrace:\n```{(repr(e))}```'
    await channel.send(message)


if __name__ == '__main__':
    if DEBUG:
        bot.run(TOKEN_TEST)
    else:
        bot.run(TOKEN)
