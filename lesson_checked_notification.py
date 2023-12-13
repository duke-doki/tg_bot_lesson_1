import os
import time
import logging
import requests
import telegram
from dotenv import load_dotenv

logger = logging.getLogger('notification_bot_logger')


class LogsHandler(logging.Handler):
    def __init__(self, bot, master_id):
        super().__init__()
        self.bot = bot
        self.master_id = master_id

    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(text=log_entry, chat_id=self.master_id)


if __name__ == '__main__':
    load_dotenv()
    devman_token = os.environ['DEVMAN_TOKEN']
    telegram_token = os.environ['TELEGRAM_TOKEN']
    master_id = os.environ['MASTER_ID']
    headers = {'Authorization': devman_token}
    url = 'https://dvmn.org/api/long_polling/'
    bot = telegram.Bot(token=telegram_token)
    logger.setLevel(logging.INFO)
    logger.addHandler(LogsHandler(bot, master_id))
    logger.info("Бот запущен!")

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
                    \n\n{conclusion}''',
                    chat_id=chat_id
                )
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError as e:
            logger.info('A connection error occurred:')
            logger.exception(e)
            reconnection_tries += 1
            if reconnection_tries <= 1:
                logger.info('Retrying...')
            else:
                logger.info('Retry after 5 seconds...')
                time.sleep(5)
