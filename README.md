# fra-kaare-bot-blr
Python program to send Fra Kåre podcast(English) to telegram user/channel.


## Requirements
Install all requirements by running:

```
pip install -r requirements.txt
```

## Initial Configuration
Rename `settings.example.py` to `settings.py` and replace all dummy values with actual values.
```
# Bmm Settings
BMM_USERNAME = "my-bmm-username"
BMM_PASSWORD = "my-bmm-password"

# Telegram Settings
TELEGRAM_BOT_TOKEN = "my-telegram-bot-token"
TELEGRAM_CHAT_ID = "telegram-chat-id-to-which-to-send"

# Which all languages should Fra Kåre be sent in
# Supported values: 'de', 'en', 'es', 'fi', 'fr', 'hu', 'it', 'nb', 'nl', 'pl', 'pt', 'ro', 'ru', 'sl', 'ta', 'tr'
LANG = [
    'en',
    'no',
]
```
`TELEGRAM_BOT_TOKEN` is the token of the bot which sends the podcast.\
`TELEGRAM_CHAT_ID` is the id of the user/channel to which podcasts should be sent.


## Usage
Run `main.py` to send the latest tracks from Fra Kåre to the telegram channel/user.
  - A file `database.json` is created on the first run which maintains track id of the track which was successfully sent last.
  - Each time `main.py` is run, it sends all tracks newer than the one in `database.json`(In case the program failed one day, it will try to send it again the next day)
