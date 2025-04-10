import boto3
import dotenv
import os

# environment
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)

# const
TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
USER_ID = int(os.getenv('USER_ID'))
WEBHOOK_URL = os.getenv('WEBHOOK_URL')


def get_previous_title():
    title = os.getenv('PREVIOUS_TITLE', '')
    print(f'get_previous_title: title = "{title}"')
    return title

def set_previous_title(previous_title: str):
    client = boto3.client('lambda')
    client.update_function_configuration(
        FunctionName='GTAWeeklyNotificationForDiscord',
        Environment={
            'Variables': {
                'TOKEN': TOKEN,
                'CHANNEL_ID': str(CHANNEL_ID),
                'USER_ID': str(USER_ID),
                'WEBHOOK_URL': WEBHOOK_URL,
                'PREVIOUS_TITLE': previous_title
            }
        }
    )
    get_previous_title()
