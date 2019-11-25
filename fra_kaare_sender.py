import os
import json
import traceback

from requests.exceptions import RequestException
from requests.packages.urllib3.exceptions import ReadTimeoutError

from bmmapi import MinimalBmmApi, BmmApiError
from db_manager import DatabaseManager
from telegram_bot import TelegramBot


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


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

    def __init__(self, config):
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

        self.db_man = DatabaseManager(os.path.join(SCRIPT_DIR, 'database.json'))

    def send_new_tracks(self):
        last_sent_track_id = self.db_man.get_last_sent_track_id()
        print(f'Last sent track id: {last_sent_track_id}')
        tracks_published_order = self.get_new_tracks()
        tracks_sending_order = tracks_published_order[::-1]
        if tracks_sending_order:
            track_ids_to_send = [str(tr['id']) for tr in tracks_sending_order]
            print(f"Tracks to send: {', '.join(track_ids_to_send)}")
            for track in tracks_sending_order:
                print(f"Sending track: {track['id']}", end='', flush=True)
                send_success = self.send_track(track)
                if send_success:
                    print(' - Success')
                    self.db_man.set_last_sent_track_id(track['id'])
                else:
                    print(' - Fail')
                    break
        else:
            print("No tracks to send")

    def get_new_tracks(self):
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

    def get_track_info(self, track):
        """Get basic information about the track
        Return:
            {
                'title': 'Track title',
                'url': 'audio_url',
                'song_book': '[HV|MB]',
                'song_number': number
            }
        """
        # Initial values
        song_info = {
            'title': None,
            'url': None,
            'song_book': None,
            'song_number': None,
        }

        # Get title
        song_info['title'] = track.get('title')

        # Get audio url
        song_url = files = None
        media = track.get('media')
        if media:
            files = media[0].get('files')
        if files:
            song_url = files[0].get('url')
        song_info['url'] = song_url

        # Get song info
        song_book_long_to_short = {
            'herrens_veier': 'HV',
            'mandelblomsten': 'MB',
        }

        rel_song = {}
        if 'rel' in track and track['rel']:
            rel_song = track['rel'][0]

        song_book = rel_song.get('name')
        song_number = rel_song.get('id')
        if not (song_book and song_number):
            return song_info

        if song_book in song_book_long_to_short:
            song_book = song_book_long_to_short[song_book]
        else:
            song_book = song_book.replace('_', ' ').title()

        song_info['song_book'] = song_book
        song_info['song_number'] = song_number

        return song_info

    def get_track_caption(self, track_info):
        """Get caption for the track
        Return:
            "<b>Title:</b> Track title here
            <b>Song:</b> song_book_name song_number"
        """
        caption_lines = []

        title = track_info['title']
        if title:
            caption_lines.append(f'<b>Title:</b> {title}')

        song_book = track_info['song_book']
        song_number = track_info['song_number']
        if song_book:
            caption_lines.append(f'<b>Song:</b> {song_book} {song_number}')

        return '\n'.join(caption_lines)

    def send_track(self, track):
        """Download and send track to telegram channel.
        Return:
            False on error
            True otherwise
        """
        track_info = self.get_track_info(track)
        track_url = track_info['url']
        track_title = track_info['title']
        track_title_no_space = track_title.replace(' ', '_')  # Remove space as telegram adds random thumbnails and album arts otherwise

        # There is no url. Silently skip sending this track.
        if not track_url:
            return True

        audio_caption = self.get_track_caption(track_info)

        try:
            # Send audio file
            response = self.bmm_api.get_response_object(track_url)
            raw_response_stream = response.raw
            self.bot.send_audio(
                raw_response_stream,
                chat_id=self.telegram_config['chat_id'],
                caption=audio_caption,
                title=track_title_no_space,
                parse_mode='HTML'
            )

            # Send song lyric image file
            song_book = track_info['song_book']  
            song_number = track_info['song_number']
            # If there is no song information for track, return
            if not song_book:
                return True
            song_lyric_file_path = os.path.join(SCRIPT_DIR, 'song_lyrics', song_book, f'{song_number}.png')
            # If lyric file is not found for song, return
            if not os.path.isfile(song_lyric_file_path):
                return True
            self.bot.send_photo(
                open(song_lyric_file_path, 'rb'),
                chat_id=self.telegram_config['chat_id']
            )
        except (BmmApiError, RequestException, ReadTimeoutError):
            traceback.print_exc()
            return False
        return True
