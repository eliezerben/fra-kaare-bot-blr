import traceback

import requests


class TelegramBot:
    """Send audio as message"""

    def __init__(self, bot_token):
        self.bot_token = bot_token

    def send_audio(self, audio_stream, chat_id, caption=None, title=None, parse_mode=None, performer=None):
        """Send given audio byte stream to given chat_id"""
        url = f'https://api.telegram.org/bot{self.bot_token}/sendAudio'
        files = {
            'audio': audio_stream,
        }
        data = {
            'chat_id': chat_id,
            'caption': caption,
            'title': title,
            'parse_mode': parse_mode,
            'performer': performer
        }
        response = requests.post(
            url,
            files=files,
            data=data
        )
        response.raise_for_status()

    def send_photo(self, photo_stream, chat_id, caption=None, parse_mode=None):
        """Send given photo byte stream to given chat_id"""
        url = f'https://api.telegram.org/bot{self.bot_token}/sendPhoto'
        files = {
            'photo': photo_stream,
        }
        data = {
            'chat_id': chat_id,
            'caption': caption,
            'parse_mode': parse_mode,
        }
        response = requests.post(
            url,
            files=files,
            data=data
        )
        response.raise_for_status()
