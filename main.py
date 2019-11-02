from fra_kaare_sender import FraKaareSender


if __name__ == '__main__':
    sender = FraKaareSender(config='./config.json')
    sender.send_new_tracks()
