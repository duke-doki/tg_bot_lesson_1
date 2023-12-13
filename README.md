# Lesson check notificator

A simple script that sends you notification if your lesson is checked.

## Environment


### Requirements

Python3 should be already installed. 
Then use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
```bash
pip install -r requirements.txt
```

### Environment variables

- TELEGRAM_TOKEN
- DEVMAN_TOKEN
- MASTER_ID

1. Put `.env` file near `main.py`.
2. `.env` contains text data without quotes.

For example, if you print `.env` content, you will see:

```bash
$ cat .env
TELEGRAM_TOKEN=6400824160:AAH...
DEVMAN_TOKEN=Token 0aee...
MASTER_ID=421...
```

#### How to get

Create a chatbot to get its token with [BotFather](https://telegram.me/BotFather). Find your Devman token
[here](https://dvmn.org/api/docs/).


### Run

Launch on Linux(Python 3) or Windows:
```bash
python lesson_checked_notification.py
```

## Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).