import os
import argparse

import settings
from fra_kaare_sender import FraKaareSender


def validate_settings():
    required = [
        'BMM_USERNAME',
        'BMM_PASSWORD',
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID',
        'LANG',
    ]

    required_not_found = []

    for key in required:
        if key not in settings.__dict__:
            required_not_found.append(key)

    if required_not_found:
        raise Exception(f"Required settings {', '.join(required_not_found)} not found.")


if __name__ == '__main__':
    settings.SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
    sender = FraKaareSender()
    sender.send_new_tracks(try_times=18)
