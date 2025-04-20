import boto3
import dotenv
import os

# environment
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)

# const
TOKEN = os.getenv('BOT_TOKEN')
BOT_TOKEN_CHANNEL_MANAGE = os.getenv('BOT_TOKEN_CHANNEL_MANAGE')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
USER_ID = int(os.getenv('USER_ID'))
WEEKLY_URL = os.getenv('WEEKLY_URL')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
WEBHOOK_URL_DEBUG = os.getenv('WEBHOOK_URL_DEBUG')

isLambda = bool(os.getenv('Environment', False))


def get_previous_title() -> str | None:
    title = os.getenv('PREVIOUS_TITLE', '')
    print(f'get_previous_title: title = "{title}"')
    return title


def set_previous_title(previous_title: str):
    print(f'set_previous_title: isLambda = {isLambda}')
    if isLambda:
        client = boto3.client('lambda')
        client.update_function_configuration(
            FunctionName='GTAWeeklyNotificationForDiscord',
            Environment={
                'Variables': {
                    'TOKEN': TOKEN,
                    'CHANNEL_ID': str(CHANNEL_ID),
                    'USER_ID': str(USER_ID),
                    'WEBHOOK_URL': WEBHOOK_URL,
                    'WEBHOOK_URL_DEBUG': WEBHOOK_URL_DEBUG,
                    'WEEKLY_URL': WEEKLY_URL,
                    'PREVIOUS_TITLE': previous_title
                }
            }
        )
    get_previous_title()
