import discord
import psycopg2
import traceback
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timezone, timedelta
from datetime import date as datetime_date
from discord.ext import commands, tasks

from const import *
from log import DiscordLogger
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
logger = DiscordLogger(bot=bot, channel_id=CHANNEL_ID_LOG)

##### bot commands #####
@tree.command(name='henlo', description='Say hello')
async def hello_command(interaction: discord.Interaction):
    await interaction.response.send_message(f'👋 Hello, {interaction.user.display_name}!', ephemeral=True)


# @tree.command(name='no-role', description='ロールがついてない人を教えてくれます。')
# async def list_no_role_members(interaction: discord.Interaction):
#     await interaction.response.defer(ephemeral=True)

#     if interaction.channel_id not in COMMAND_WHITE_LIST:
#         await interaction.followup.send('❌ ここではつかえません', ephemeral=True)
#     else:
#         try:
#             guild = interaction.guild
#             members = [m async for m in guild.fetch_members(limit=None)]
#             no_role_members = [m for m in members if len(m.roles) == 1]

#             if not no_role_members:
#                 await interaction.followup.send("✅ 全員ロールあり！ヨシ！", silent=True)
#                 return
            
#             names = "\n".join(m.mention for m in no_role_members)
#             await interaction.followup.send(f'👥ロールがついてない人\n{names}')
        
#         except Exception as e:
#             await send_error_log(e, inspect.currentframe().f_code.co_name)
#             interaction.followup.send('なにかがおかしいよ')


# @tree.command(name='role-member-list', description='ロールごとのメンバーを教えてくれます。')
# @discord.app_commands.describe(role='ロールを選択！')
# async def list_role_members(
#     interaction: discord.Interaction,
#     role: discord.Role
# ):
#     await interaction.response.defer(ephemeral=True)

#     if interaction.channel_id not in COMMAND_WHITE_LIST:
#         await interaction.followup.send('❌ ここではつかえません', ephemeral=True)
#     else:
#         try:
#             members = [member for member in role.members]
#             members.sort(key=lambda m: m.display_name.lower())
#             member_list = "\n".join(member.mention for member in members)

#             if not members:
#                 await interaction.followup.send(
#                     '🤦‍♀️ 該当するメンバーがいませんでした',
#                     ephemeral=True
#                 )
#                 return
            
#             await interaction.followup.send(
#                 f'👥 {role.name} ロールのメンバーは...\n{member_list}\nです！',
#                 ephemeral=True
#             )

#         except Exception as e:
#             await send_error_log(e, inspect.currentframe().f_code.co_name)
#             await interaction.followup.send('なにかがおかしいよ')


@tree.command(name='get-join-record', description='ユーザーIDを使用して参加記録を取得します。')
@discord.app_commands.describe(member_id='ユーザーIDを入力')
async def get_join_record_command(
    interaction: discord.Interaction,
    member_id: str
):
    await interaction.response.defer(thinking=True)

    if interaction.channel_id not in COMMAND_WHITE_LIST:
        await interaction.followup.send('❌ ここではつかえません', ephemeral=True)
        return

    try:
        with get_db_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM join_record WHERE user_id = %s;', (member_id,))
                result = cursor.fetchone()
        
        if result:
            await interaction.followup.send(f'GET: {member_id}\n完了しました。\n{result}')
        else:
            await interaction.followup.send(f'GET: {member_id}\n対象レコードがありません。')
    
    except Exception as e:
        await interaction.followup.send(f'ERROR: {member_id}\n{repr(e)}')


@tree.command(name='remove-join-record', description='ユーザーIDを使用して参加記録を削除します。')
@discord.app_commands.describe(member_id='ユーザーIDを入力')
async def remove_join_record_command(
    interaction: discord.Interaction,
    member_id: str
):
    await interaction.response.defer(thinking=True)

    if interaction.channel_id not in COMMAND_WHITE_LIST:
        await interaction.followup.send('❌ ここではつかえません', ephemeral=True)
        return

    try:
        with get_db_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute('DELETE FROM join_record WHERE user_id = %s;', (member_id,))
        await interaction.followup.send(f'DELETE: {member_id}\n完了しました。')
    
    except Exception as e:
        await interaction.followup.send(f'ERROR: {member_id}\n{repr(e)}')


##### bot event functions #####
# def get_db_connection():
#     return psycopg2.connect(
#         host=DATABASE_HOST,
#         user=DATABASE_USER,
#         password=DATABASE_PASSWORD,
#         dbname=DATABASE_NAME,
#         port=5432
#     )

def get_db_conn():
    return psycopg2.connect(
        host=DATABASE_HOST,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        dbname=DATABASE_NAME,
        port=5432
    )


def get_join_record() -> list[tuple, datetime_date|None]:
    join_record = []
    try:
        with get_db_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(SQL_SELECT_RECORD)
                result = cursor.fetchall()
        
        for member_id, date in result:
            if date:
                date: datetime_date
                date_str = date.strftime('%Y/%m/%d')
            else:
                date_str = None
            join_record.append((member_id, date_str))

    except Exception as e:
        print(repr(e))

    return join_record


def update_join_record(member_id: int, date_null=False) -> str:
    res = ''
    if date_null:
        date = None
    else:
        date = datetime.now(JST).date()

    with get_db_conn() as conn:
        with conn.cursor() as cursor:
            if date:
                cursor.execute(
                    SQL_INSERT_WITH_DATE,
                    (member_id, date)
                )
                res = f'update_join_record: {SQL_INSERT_WITH_DATE}\nmember_id: {member_id}, date: {date}'
            else:
                cursor.execute(
                    SQL_INSERT_WITHOUT_DATE,
                    (member_id,)
                )
                res = f'update_join_record: {SQL_INSERT_WITHOUT_DATE}\nmember_id: {member_id}, date: NULL'
            conn.commit()
    
    return res


def remove_join_record(member_id: int) -> str:
    with get_db_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                SQL_DELETE_RECORD,
                (member_id,)
            )
        conn.commit()
    
    return f'remove_join_record: {SQL_DELETE_RECORD}\nmember_id: {member_id}'


def sort_joined_members(members: list[tuple[int, str]]) -> list[tuple[int, str]]:
    def sort_key(item):
        _, days_info = item
        if days_info == 'N/A':
            return (0, 0)
        days = int(days_info.split('日前')[0])
        return (1, -days)

    return sorted(members, key=sort_key)


def get_inactive_members() -> list[tuple[int, str]]:
    join_record = get_join_record()
    inactive_members = []

    for member_id, date in join_record:
        if date:
            delta = datetime.now(JST) - datetime.strptime(date, '%Y/%m/%d').replace(tzinfo=JST)
            days_ago = f'{delta.days}日前 ({date})'
        else:
            days_ago = 'N/A'
        inactive_members.append((int(member_id), days_ago))
    
    return sort_joined_members(inactive_members)


scheduler = AsyncIOScheduler()

@scheduler.scheduled_job(CronTrigger(hour=18, timezone='Asia/Tokyo'))
async def join_record_reminder():
    """
    send join record(daily)
    """
    inactive_members = get_inactive_members()
    await logger.info(f'join_record_reminder:\n{inactive_members}')
    list_str = ''
    for t in inactive_members:
        member_id, days_ago = t
        list_str += f'<@{member_id}>: {days_ago}\n'

    message = f'2026/04/28からのVC参加記録だゾ～📊\n{list_str}'

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
        await logger.info(
            f'on_voice_state_update:\n  member = {member}\n  before.channel = {before.channel}\n  after.channel = {after.channel}'
        )
        if before.channel is None and after.channel is not None:
            voice_channel = after.channel
            text_channel_id = TX_CHANNEL_IDS.get(voice_channel.id, CHANNEL_ID_TEST_TX)
            text_channel = bot.get_channel(text_channel_id)

            if len(voice_channel.members) == 1:
                await logger.info(f'on_voice_state_update:\nsend start notification to → {text_channel.name}')
                date = get_date_str()
                message = await text_channel.send(
                    f'{date}\n🎧 <@{member.id}> が **<#{voice_channel.id}>** でボイスチャットを開始しました。'
                )
                active_voice_channels[voice_channel.id] = message.id
        
        elif before.channel is not None and after.channel is None:
            voice_channel = before.channel
            text_channel_id = TX_CHANNEL_IDS.get(voice_channel.id, CHANNEL_ID_TEST_TX)
            text_channel = bot.get_channel(text_channel_id)

            if len(voice_channel.members) == 0 and voice_channel.id in active_voice_channels:
                await logger.info(f'on_voice_state_update:\nsend end notification to → {text_channel.name}')
                msg_id = active_voice_channels[voice_channel.id]
                original_message = await text_channel.fetch_message(msg_id)

                date = get_date_str()
                await original_message.reply(
                    f'{date}\nボイスチャットが終了しました。',
                    silent=True
                )
                active_voice_channels.pop(voice_channel.id)
        
        # target_role_id = ROLE_ID_TEST if DEBUG else ROLE_ID_RISE
        # has_target_role = any(role.id == target_role_id for role in member.roles)
        # if has_target_role and member.id not in JOIN_RECORD_WHITE_LIST:
        res = update_join_record(member.id)
        await logger.info(f'on_voice_state_update:\nupdate member.id = {member.id}')

    except Exception:
        await logger.error(f'on_voice_state_update\n{traceback.format_exc()}')


def get_date_str() -> str:
    now = datetime.now(JST)
    return f'{now.month}月{now.day}日 {now.hour}時{now.minute}分'


@bot.event
async def on_member_join(member: discord.Member):
    # role_id = ROLE_ID_TEST if DEBUG else ROLE_ID_RISE
    # role = member.guild.get_role(role_id)

    # if role and member.id not in JOIN_RECORD_WHITE_LIST:
    try:
        # await member.add_roles(role, reason='bot自動登録')
        res = update_join_record(member.id, date_null=True)
        await logger.info(f'on_member_join:\n{res}')
    except Exception:
        await logger.error(f'on_member_join\n{traceback.format_exc()}')


@bot.event
async def on_member_remove(member: discord.Member):
    try:
        res = remove_join_record(member.id)
        await logger.info(f'on_member_remove:\n{res}')
    except Exception:
        await logger.error(f'on_member_remove:\n{traceback.format_exc()}')


@bot.event
async def on_scheduled_event_create(event: discord.ScheduledEvent):
    if event.guild_id == SERVER_ID:
        channel_id = CHANNEL_ID_OSHIRASE
    else:
        channel_id = CHANNEL_ID_TEST_TX

    channel = bot.get_channel(channel_id)
    content = f'<@{event.creator_id}> がイベントを作成しました📝\n{event.url}'

    await channel.send(content)


# @bot.event
# async def on_member_join(member: discord.Member):
#     try:
#         message = MSG_WELCOME.replace('@member', member.display_name)
#         await member.send(message, view=RegisterView())

#     except discord.Forbidden:
#         print(f'on_member_join: Could not send the message to {member.display_name}')


# async def send_error_log(e: Exception, func_name: str = None):
#     channel = bot.get_channel(CHANNEL_ID_LOG)
#     message =f'Function:{func_name}\nStacktrace:\n```{traceback.format_tb(e.__traceback__)}```'
#     await channel.send(message)


@tasks.loop(minutes=30)
async def health_check():
    await logger.system()


@bot.event
async def on_ready():
    await tree.sync()

    scheduler.start()
    health_check.start()
    
    # print(f'on_ready: Logged in as {bot.user}')
    await logger.info(f'on_ready: Logged in as {bot.user}')


if __name__ == '__main__':
    if DEBUG:
        bot.run(TOKEN_TEST)
    else:
        bot.run(TOKEN)
