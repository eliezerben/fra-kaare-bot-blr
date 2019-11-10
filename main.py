import os

from fra_kaare_sender import FraKaareSender

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


if __name__ == '__main__':
    config_full_path = os.path.join(SCRIPT_DIR, 'config.json')
    sender = FraKaareSender(config=config_full_path)
    sender.send_new_tracks()
