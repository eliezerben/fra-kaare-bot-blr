import os
import json
import traceback

from requests.exceptions import RequestException
from requests.packages.urllib3.exceptions import ReadTimeoutError

from bmmapi import MinimalBmmApi, BmmApiError
from db_manager import DatabaseManager
from telegram_bot import TelegramBot


class ConfigFileException(Exception):
    pass


class FraKaareSender:
    """Send new tracks from Fra Kåre podcast to Telegram channel.

    Uses MinimalBmmApi to get details of all tracks form Fra Kåre podcast.

    Id of the last track successfully sent is maintained in the database(database.json).
    This is used to find out which tracks are new.
    DatabaseManager is used to interact with the database.

    TelegramBot uploads the audio to the channel.
    """

    def __init__(self, config='./config.json'):
        self.fra_kaare_podcast_id = 1

        if not os.path.isfile(config):
            raise ConfigFileException(f"Config file '{config}' could not be found.")

        config_data = json.load(open(config))
        self.bmm_config = config_data['bmm']
        self.telegram_config = config_data['telegram']

        self.bmm_api = MinimalBmmApi('https://bmm-api.brunstad.org')
        self.bmm_api.authenticate(self.bmm_config['username'], self.bmm_config['password'])
        self.bmm_api.setLanguage('en')
        self.bot = TelegramBot(self.telegram_config['bot_token'])

        self.db_man = DatabaseManager()

    def send_new_tracks(self):
        last_sent_track_id = self.db_man.get_last_sent_track_id()
        print(f'Last sent track id: {last_sent_track_id}')
        tracks_published_order = self._get_new_tracks()
        tracks_sending_order = tracks_published_order[::-1]
        if tracks_sending_order:
            track_ids_to_send = [str(tr['id']) for tr in tracks_sending_order]
            print(f"Tracks to send: {', '.join(track_ids_to_send)}")
            for track in tracks_sending_order:
                print(f"Sending track: {track['id']}", end='', flush=True)
                send_success = self._send_track(track)
                if send_success:
                    print(' - Success')
                    self.db_man.set_last_sent_track_id(track['id'])
                else:
                    print(' - Fail')
                    break
        else:
            print("No tracks to send")

    def _get_new_tracks(self):
        """Return new tracks which have been published after the last track was sent"""
        new_tracks = []
        fra_kaare_tracks = self.bmm_api.podcastTracks(self.fra_kaare_podcast_id)
        last_sent_track_id = self.db_man.get_last_sent_track_id()

        if not last_sent_track_id:
            new_tracks.append(fra_kaare_tracks[0])
        else:
            for index, track in enumerate(fra_kaare_tracks):
                if track['id'] == last_sent_track_id:
                    break
            new_tracks.extend(fra_kaare_tracks[:index])
        return new_tracks

    def _get_song_info(self, track):
        """Get information of song played in the track to be sent as caption"""
        title = track['_meta'].get('title')
        caption = f'<b>Title:</b> {title}'

        long_to_short = {
            'herrens_veier': 'HV',
            'mandelblomsten': 'MB',
        }

        rel = None
        if track['rel']:
            rel = track['rel'][0]
        else:
            return caption

        rel_name = rel.get('name')
        rel_id = rel.get('id')
        if not rel_name or not rel_id:
            return caption

        if rel_name in long_to_short:
            rel_name = long_to_short[rel_name]
        else:
            rel_name = rel_name.replace('_', ' ').title()
        caption = f'{caption}\n<b>Song:</b> {rel_name} {rel_id}'

        return caption

    def _send_track(self, track):
        """Download and send track to telegram channel.
        Return: True on success
                False on failure
        """
        track_url = track['media'][0]['files'][0]['url']
        track_title = track['_meta'].get('title')

        caption = self._get_song_info(track)

        try:
            response = self.bmm_api.get_response_object(track_url)
            raw_response_stream = response.raw
            self.bot.send_audio(
                raw_response_stream,
                chat_id=self.telegram_config['chat_id'],
                caption=caption,
                title=track_title,
                parse_mode='HTML'
            )
        except (BmmApiError, RequestException, ReadTimeoutError):
            traceback.print_exc()
            return False
        return True
