import os

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

devman_token = os.environ['DEVMAN_TOKEN']
headers = {'Authorization': devman_token}
url = 'https://dvmn.org/api/long_polling/'
telegram_token = os.environ['TELEGRAM_TOKEN']
bot = telegram.Bot(token=telegram_token)


params = {}

while True:
    updates = bot.get_updates()
    chat_id = updates[0]['message']['chat']['id']
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        response_json = response.json()

        if 'timestamp_to_request' in response_json:
            params = {'timestamp': response_json['timestamp_to_request']}

        elif 'last_attempt_timestamp' in response_json:
            params = {'timestamp': response_json['last_attempt_timestamp']}

            if response_json['new_attempts'][0]['is_negative']:
                conclusion = 'К сожалению, в работе нашлись ошибки.'
            else:
                conclusion = '''Преподавателю всё понравилось, 
                             можно приступать к следующему уроку!'''

            bot.send_message(
                text='''У вас проверили работу "{lesson}" 
                     \n\n{link} \n\n{conclusion}'''.format(
                    lesson=response_json['new_attempts'][0]['lesson_title'],
                    link=response_json['new_attempts'][0]['lesson_url'],
                    conclusion=conclusion
                ),
                chat_id=chat_id
            )
    except (
            requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectionError
    ):
        continue
