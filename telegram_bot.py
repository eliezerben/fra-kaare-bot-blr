import json
import traceback

import requests


class TelegramBot:
    """Send audio as message"""

    def __init__(self, bot_token):
        self.bot_token = bot_token

    def send_message(self, text, chat_id, parse_mode=None):
        """Send a text message"""
        url = f'https://api.telegram.org/bot{self.bot_token}/sendMessage'
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
        }
        response = requests.post(
            url,
            data=data
        )
        response.raise_for_status()

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

    def send_media_group(self, media_list, chat_id):
        """Send given list of photos given chat_id"""
        url = f'https://api.telegram.org/bot{self.bot_token}/sendMediaGroup'
        files = {}
        data = {
            'chat_id': chat_id,
            'media': [],
        }
        for index, media in enumerate(media_list):
            attach_id = f'media_{index}'
            data['media'].append({
                'type': 'photo',
                'media': f'attach://{attach_id}',
            })
            files[attach_id] = media
        data['media'] = json.dumps(data['media'])
        response = requests.post(
            url,
            files=files,
            data=data
        )
        response.raise_for_status()
