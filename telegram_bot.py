import traceback

import requests


class TelegramBot:
    """Send audio as message"""

    def __init__(self, bot_token):
        self.bot_token = bot_token

    def send_audio(self, audio_stream, chat_id, caption=None, title=None, parse_mode=None):
        """Send given audio byte_stream to given chat_id
        Return: True on success
                False on failure
        """
        url = f'https://api.telegram.org/bot{self.bot_token}/sendAudio'
        files = {
            'audio': audio_stream,
        }
        data = {
            'chat_id': chat_id,
            'caption': caption,
            'title': title,
            'parse_mode': parse_mode,
        }
        response = requests.post(
            url,
            files=files,
            data=data
        )
        response.raise_for_status()
