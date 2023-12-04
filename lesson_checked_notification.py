import os
import time

import requests
import telegram
from dotenv import load_dotenv


if __name__ == '__main__':
    load_dotenv()

    devman_token = os.environ['DEVMAN_TOKEN']
    headers = {'Authorization': devman_token}
    url = 'https://dvmn.org/api/long_polling/'
    telegram_token = os.environ['TELEGRAM_TOKEN']
    bot = telegram.Bot(token=telegram_token)

    params = {}
    reconnection_tries = 0
    while True:
        updates = bot.get_updates()
        chat_id = updates[0]['message']['chat']['id']
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            response_lesson = response.json()

            if 'timestamp_to_request' in response_lesson:
                params = {'timestamp': response_lesson['timestamp_to_request']}

            elif 'last_attempt_timestamp' in response_lesson:
                params = {'timestamp': response_lesson['last_attempt_timestamp']}

                if response_lesson['new_attempts'][0]['is_negative']:
                    conclusion = 'К сожалению, в работе нашлись ошибки.'
                else:
                    conclusion = '''Преподавателю всё понравилось, 
                                 можно приступать к следующему уроку!'''

                bot.send_message(
                    text=f'''У вас проверили работу 
                    \n\n"{response_lesson['new_attempts'][0]['lesson_title']}" 
                    \n\n{response_lesson['new_attempts'][0]['lesson_url']} 
                    \n\n{conclusion}'''
                    ,
                    chat_id=chat_id
                )
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError as e:
            print(f'A connection error occurred: {e}')
            reconnection_tries += 1
            if reconnection_tries <= 1:
                print('Retrying...')
            else:
                print('Retry after 5 seconds...')
                time.sleep(5)
