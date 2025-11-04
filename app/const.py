import os
import dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)

DEBUG = True
ENVIRONMENT = os.getenv('ENVIRONMENT')
if ENVIRONMENT and ENVIRONMENT == 'koyeb':
    DEBUG = False

print(f'DEBUG = {DEBUG}')

# database
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_NAME = os.getenv('DATABASE_NAME')

SQL_CREATE_TABLE = '''
    CREATE TABLE join_records (
        user_id BIGINT PRIMARY KEY,
        joined_date DATE
    );
'''
SQL_SELECT_RECORD = '''
    SELECT user_id, joined_date FROM join_records
'''
SQL_INSERT_WITH_DATE = '''
    INSERT INTO join_records (user_id, joined_date)
    VALUES (%s, %s)
    ON CONFLICT (user_id) DO UPDATE
    SET joined_date = EXCLUDED.joined_date;
'''
SQL_INSERT_WITHOUT_DATE = '''
    INSERT INTO join_records (user_id, joined_date)
    VALUES (%s, NULL)
    ON CONFLICT (user_id) DO UPDATE
    SET joined_date = NULL;
'''
SQL_DELETE_RECORD = '''
    DELETE FROM join_records WHERE user_id = %s
'''

# token
TOKEN = os.getenv('BOT_TOKEN')
TOKEN_TEST = os.getenv('BOT_TOKEN_TEST')

# server
SERVER_ID = int(os.getenv('SERVER_ID'))
SERVER_ID_TEST = int(os.getenv('SERVER_ID_TEST'))

# channels
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
CHANNEL_ID_MANAGE_2 = int(os.getenv('CHANNEL_ID_MANAGE_2'))
CHANNEL_ID_OSHIRASE = int(os.getenv('CHANNEL_ID_OSHIRASE'))

TX_CHANNEL_IDS = {
    # to test server
    CHANNEL_ID_TEST_VC: CHANNEL_ID_TEST_TX,
    CHANNEL_ID_TEST_VC_2: CHANNEL_ID_TEST_TX,

    # to over and rise channel
    CHANNEL_ID_VC_OVER_AND_RISE: CHANNEL_ID_TX_OVER_AND_RISE,
    CHANNEL_ID_VC_CAR_MEET: CHANNEL_ID_TX_OVER_AND_RISE,

    # to rise channel
    CHANNEL_ID_VC_RISE: CHANNEL_ID_TX_RISE,

    # to over channel
    CHANNEL_ID_VC_OVER: CHANNEL_ID_TX_OVER,
    CHANNEL_ID_VC_OVER_2: CHANNEL_ID_TX_OVER,
    CHANNEL_ID_VC_OVER_3: CHANNEL_ID_TX_OVER,
}

COMMAND_WHITE_LIST = (
    CHANNEL_ID_MANAGE,
    CHANNEL_ID_MANAGE_2,
    CHANNEL_ID_TEST_TX,
)

# roles
ROLE_ID_TEST = int(os.getenv('ROLE_ID_TEST'))
ROLE_ID_OVER = int(os.getenv('ROLE_ID_OVER'))
ROLE_ID_RISE = int(os.getenv('ROLE_ID_RISE'))

# voice join record
JOIN_RECORD_WHITE_LIST = (
    981396359489929257,
    1363358365346037974,
    1363827906643628153,
    1365001405412282540,
    1083783797931253860,
    1432855520078860459,
    1432872091610386546,
    1432875321207816376
)
