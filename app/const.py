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
    CREATE TABLE join_record (
        user_id BIGINT PRIMARY KEY,
        joined_date DATE
    );
'''
SQL_ADD_COLUMN_POINT = '''
    ALTER TABLE join_record
    ADD COLUMN point INTEGER NOT NULL DEFAULT 0;
'''

SQL_SELECT_RECORD = '''
    SELECT user_id, joined_date FROM join_record
'''
SQL_INSERT_WITH_DATE = '''
    INSERT INTO join_record (user_id, joined_date)
    VALUES (%s, %s)
    ON CONFLICT (user_id) DO UPDATE
    SET joined_date = EXCLUDED.joined_date;
'''
SQL_INSERT_WITHOUT_DATE = '''
    INSERT INTO join_record (user_id, joined_date)
    VALUES (%s, NULL)
    ON CONFLICT (user_id) DO UPDATE
    SET joined_date = NULL;
'''
SQL_DELETE_RECORD = '''
    DELETE FROM join_record WHERE user_id = %s
'''

SQL_SELECT_POINT = '''
    SELECT user_id, point FROM join_record
    WHERE point > 0
    ORDER BY point DESC;
'''
SQL_UPDATE_POINT = '''
    UPDATE join_record
    SET point = point + 1
    WHERE user_id = ?;
'''
SQL_UPDATE_POINT_RESET = '''
    UPDATE join_record
    SET point = 0
    WHERE user_id = ?;
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
CHANNEL_ID_VC_RISE_2 = int(os.getenv('CHANNEL_ID_VC_RISE_2'))
CHANNEL_ID_VC_RISE_3 = int(os.getenv('CHANNEL_ID_VC_RISE_3'))

CHANNEL_ID_TX_OVER = int(os.getenv('CHANNEL_ID_TX_OVER'))
CHANNEL_ID_VC_OVER = int(os.getenv('CHANNEL_ID_VC_OVER'))
CHANNEL_ID_VC_OVER_2 = int(os.getenv('CHANNEL_ID_VC_OVER_2'))
CHANNEL_ID_VC_OVER_3 = int(os.getenv('CHANNEL_ID_VC_OVER_3'))

CHANNEL_ID_MANAGE = int(os.getenv('CHANNEL_ID_MANAGE'))
CHANNEL_ID_MANAGE_2 = int(os.getenv('CHANNEL_ID_MANAGE_2'))
CHANNEL_ID_OSHIRASE = int(os.getenv('CHANNEL_ID_OSHIRASE'))
CHANNEL_ID_LOG = int(os.getenv('CHANNEL_ID_LOG'))

TX_CHANNEL_IDS = {
    # to test server
    CHANNEL_ID_TEST_VC: CHANNEL_ID_TEST_TX,
    CHANNEL_ID_TEST_VC_2: CHANNEL_ID_TEST_TX,

    # to over and rise channel
    CHANNEL_ID_VC_OVER_AND_RISE: CHANNEL_ID_TX_OVER_AND_RISE,
    CHANNEL_ID_VC_CAR_MEET: CHANNEL_ID_TX_OVER_AND_RISE,

    # to rise channel
    CHANNEL_ID_VC_RISE: CHANNEL_ID_TX_RISE,
    CHANNEL_ID_VC_RISE_2: CHANNEL_ID_TX_RISE,
    CHANNEL_ID_VC_RISE_3: CHANNEL_ID_TX_RISE,

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
# JOIN_RECORD_WHITE_LIST = ()
