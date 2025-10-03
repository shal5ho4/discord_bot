import discord
import inspect
import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timezone, timedelta
from discord.ext import commands
from pathlib import Path

from const import *
# from modal import RegisterView
# from server import server_thread

JST = timezone(timedelta(hours=+9), 'JST')

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
@discord.app_commands.describe(role='ロールを選択！')
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

JOIN_RECORD = Path('join_record.json')  # {"member_id": "timestamp" | null}
record_start_at = ''

def load_join_record() -> dict:
    if JOIN_RECORD.exists():
        with open(JOIN_RECORD, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def update_join_record(member_id: int, date_null=False):
    join_record = load_join_record()

    if date_null:
        date = None
    else:
        date = datetime.now(JST).strftime('%Y-%m-%d')

    join_record[str(member_id)] = date
    print(join_record)

    with open(JOIN_RECORD, 'w', encoding='utf-8') as f:
        json.dump(join_record, f, ensure_ascii=False, indent=2)
    print('join record saved.')


def remove_join_record(member_id: int):
    join_record = load_join_record()
    join_record.pop(str(member_id))

    with open(JOIN_RECORD, 'w', encoding='utf-8') as f:
        json.dump(join_record, f, ensure_ascii=False, indent=2)
    print(f'member_id "{member_id}" removed.')


def get_inactive_members() -> list[tuple[int, str]]:
    join_record = load_join_record()
    inactive_members = []

    for member_id, timestamp in join_record.items():
        if timestamp:
            joined_date = datetime.strptime(timestamp, '%Y-%m-%d').replace(tzinfo=JST)
            delta = datetime.now(JST) - joined_date
            # if delta.days >= 3:
            days_ago = f'{delta.days}日前 ({timestamp})'
        else:
            days_ago = 'N/A'
        inactive_members.append((int(member_id), days_ago))
    
    return inactive_members


scheduler = AsyncIOScheduler()

@scheduler.scheduled_job(CronTrigger(minute=30, timezone='Asia/Tokyo'))
async def join_record_reminder():
    """
    send join record(weekly)
    """
    global record_start_at

    inactive_members = get_inactive_members()
    list_str = ''
    for t in inactive_members:
        member_id, days_ago = t
        list_str += f'<@{member_id}>: {days_ago}\n'

    message = f'record_start_at: {record_start_at}\nget_inactive_members():\n{list_str}'

    channel_id = CHANNEL_ID_TEST_TX if DEBUG else CHANNEL_ID_MANAGE_2
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send(message, silent=True)


active_voice_channels = {}  # {channel_id: message_id}

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
                    f'{date}\n🎧 <@{member.id}> が **<#{voice_channel.id}>** でボイスチャットを開始！'
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
        
        target_role_id = ROLE_ID_TEST if DEBUG else ROLE_ID_RISE
        has_target_role = any(role.id == target_role_id for role in member.roles)
        if has_target_role:
            update_join_record(member.id)

    except Exception as e:
        await send_error_log(e, inspect.currentframe().f_code.co_name)


def get_date_str() -> str:
    now = datetime.now(JST)
    return f'{now.month}月{now.day}日 {now.hour}時{now.minute}分'


@bot.event
async def on_member_join(member: discord.Member):
    """
    add the role to a newly joined member
    register member.id to join_record
    """
    role_id = ROLE_ID_TEST if DEBUG else ROLE_ID_RISE
    role = member.guild.get_role(role_id)

    if role:
        try:
            await member.add_roles(role, reason='bot自動登録')
        except Exception as e:
            await send_error_log(e, inspect.currentframe().f_code.co_name)

    update_join_record(member.id, date_null=True)


@bot.event
async def on_member_remove(member: discord.Member):
    """
    remove member.id from join_record
    """
    remove_join_record(member.id)


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


@bot.event
async def on_ready():
    """
    bot start-up
    """
    print(f'Logged in as {bot.user}')
    await tree.sync()

    scheduler.start()
    
    if not JOIN_RECORD.exists():
        print('creating join_record...')

        guild = bot.get_guild(SERVER_ID)
        role = discord.utils.get(guild.roles, name="RISE")
        role_members = [member for member in guild.members if role in member.roles]
        
        join_record = {}
        for member in role_members:
            join_record[str(member.id)] = None

        with open(JOIN_RECORD, 'w', encoding='utf-8') as f:
            json.dump(join_record, f)
        print(f'created join_record as : {join_record}')

    global record_start_at
    record_start_at = datetime.now(JST).strftime('%Y/%m/%d')
    print(f'join_record_start_at: {record_start_at}')



if __name__ == '__main__':
    if DEBUG:
        bot.run(TOKEN_TEST)
    else:
        bot.run(TOKEN)
