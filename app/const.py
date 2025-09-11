import os
import dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)

DEBUG = True
ENVIRONMENT = os.getenv('ENVIRONMENT')
if ENVIRONMENT and ENVIRONMENT == 'koyeb':
    DEBUG = False

print(f'DEBUG = {DEBUG}')

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
    CHANNEL_ID_TEST_TX,
)

# roles
ROLE_ID_TEST = int(os.getenv('ROLE_ID_TEST'))
ROLE_ID_OVER = int(os.getenv('ROLE_ID_OVER'))
ROLE_ID_RISE = int(os.getenv('ROLE_ID_RISE'))
