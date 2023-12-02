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
            response_details = response.json()

            if 'timestamp_to_request' in response_details:
                params = {'timestamp': response_details['timestamp_to_request']}

            elif 'last_attempt_timestamp' in response_details:
                params = {'timestamp': response_details['last_attempt_timestamp']}

                if response_details['new_attempts'][0]['is_negative']:
                    conclusion = 'К сожалению, в работе нашлись ошибки.'
                else:
                    conclusion = '''Преподавателю всё понравилось, 
                                 можно приступать к следующему уроку!'''

                bot.send_message(
                    text='''У вас проверили работу "{lesson}" 
                         \n\n{link} \n\n{conclusion}'''.format(
                        lesson=response_details['new_attempts'][0][
                            'lesson_title'],
                        link=response_details['new_attempts'][0]['lesson_url'],
                        conclusion=conclusion
                    ),
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
        else:
            continue
