# fra-kaare-bot-blr
Python program to send Fra Kåre podcast(English) to telegram user/channel.


## Requirements
Install all requirements by running:

```
pip install -r requirements.txt
```

## Initial Configuration
Rename `config.json.example` to `config.json` and replace all dummy values with actual values.
```
{
    "bmm": {
        "username": "my-bmm-username",
        "password": "my-bmm-password"
    },
    "telegram": {
        "bot_token": "my-telegram-bot-token",
        "chat_id": "telegram-chat-id"
    }
}
```
`bot_token` is the token of the bot which sends the podcast.\
`chat_id` is the id of the user/channel to which podcasts should be sent.


## Usage
Run `main.py` to send the latest tracks from Fra Kåre to the telegram channel/user.
  - A file `database.json` is created on the first run which maintains track id of the track which was successfully sent last.
  - Each time `main.py` is run, it sends all tracks newer than the one in `database.json`(In case the program failed one day, it will try to send it again the next day)
