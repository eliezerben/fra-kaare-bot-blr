import os
import sys
import json
import traceback
from datetime import datetime, timedelta
import time

from requests.exceptions import RequestException
from requests.packages.urllib3.exceptions import ReadTimeoutError

import settings
from bmmapi import MinimalBmmApi, BmmApiError
from db_manager import DatabaseManager
from telegram_bot import TelegramBot


class FraKaareSender:
    """Send new tracks from Fra Kåre podcast to Telegram channel.

    Uses MinimalBmmApi to get details of all tracks form Fra Kåre podcast.

    Id of the last track successfully sent is maintained in the database(database.json).
    This is used to find out which tracks are new.
    DatabaseManager is used to interact with the database.

    TelegramBot uploads audio/images to given chat.
    """

    def __init__(self, try_times=3):
        self.try_times = try_times

        self.bmm_api = MinimalBmmApi('https://bmm-api.brunstad.org')

        print('Authenticating user')
        for try_ind in range(self.try_times):
            self.bmm_api.authenticate(
                settings.BMM_USERNAME, settings.BMM_PASSWORD)
            if self.bmm_api.is_authenticated():
                break
            time.sleep(180)
            print(f"Authentication failed. try {try_ind+1}...", flush=True)

        self.bot = TelegramBot(settings.TELEGRAM_BOT_TOKEN)

        self.db_man = DatabaseManager(os.path.join(
            settings.SCRIPT_DIR, 'database.json'))

    def _send_new_tracks(self):
        """Look at the last sent day and send all the pending tracks"""
        last_sent_day = self.db_man.get_last_sent_day()
        print(f'Last sent day: {last_sent_day}', flush=True)
        new_tracks = self.get_new_tracks()
        if not new_tracks:
            print("No tracks to send", flush=True)
            return
        days_to_send = sorted(new_tracks.keys())
        print(f"Days to send: {', '.join(days_to_send)}", flush=True)
        for day in days_to_send:
            print(f"Sending track of: {day}", end='', flush=True)
            send_success = self.send_tracks(new_tracks[day])
            if send_success:
                print(' - Success', flush=True)
                self.db_man.set_last_sent_day(day)
            else:
                print(' - Fail', flush=True)
                break

    def _are_tracks_pending(self):
        """If the latest track was not sent, return True"""
        last_sent_day_str = self.db_man.get_last_sent_day()
        now = datetime.now()
        today_date_str = now.strftime('%Y-%m-%d')
        today_day = int(now.strftime('%w'))  # 6 - Sat, 0 - Sun
        last_weekday_str = today_date_str
        # Get last weekday
        if today_day in (6, 0):
            days_since_last_friday = (today_day + 1) % 7 + 1
            last_weekday = now - timedelta(days_since_last_friday)
            last_weekday_str = last_weekday.strftime('%Y-%m-%d')
        # today_day not in ('Sat', 'Sun') and
        if last_weekday_str != last_sent_day_str:
            return True
        else:
            return False

    def send_new_tracks(self):
        for i in range(self.try_times):
            print(f'Trying to get todays track: try {i+1}', flush=True)
            try:
                self._send_new_tracks()
            except BmmApiError:
                print(f'Got api error.', flush=True)
                traceback.print_exc()
                sys.stdout.flush()
            except Exception:
                print(f'Got unknown error.', flush=True)
                traceback.print_exc()
                sys.stdout.flush()
            if self._are_tracks_pending():
                print('Pending tracks exist.', flush=True)
            else:
                return
            print(f'Sleeping for 180 seconds...')
            time.sleep(180)

    def get_new_tracks(self):
        """Return new tracks which have not yet been sent.
        [
            '2019-25-11': {
                'en': track,
                'nb': track
            },
            ...
        ]
        """
        new_tracks = {}
        for lang in settings.LANG:
            new_tracks_lang = []
            self.bmm_api.setLanguage(lang)
            fra_kaare_tracks = self.bmm_api.podcastTracks(settings.PODCAST_ID)
            print(fra_kaare_tracks)
            last_sent_day = self.db_man.get_last_sent_day()

            if last_sent_day is None:
                new_tracks_lang.append(fra_kaare_tracks[0])
            elif last_sent_day == '':
                new_tracks_lang = fra_kaare_tracks
            else:
                for index, track in enumerate(fra_kaare_tracks):
                    if track['published_at'].startswith(last_sent_day):
                        break
                new_tracks_lang.extend(fra_kaare_tracks[:index])

            for track in new_tracks_lang:
                track_day = self.get_day_from_ts(track['published_at'])
                if track_day not in new_tracks:
                    new_tracks[track_day] = {}
                new_tracks[track_day][lang] = track

        return new_tracks

    def get_day_from_ts(self, timestamp):
        """ 2019-01-01T04:00:51+01:00 -> 2019-01-01 """
        return timestamp[:10]

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

    def get_track_caption(self, track_info, add_song_info=True):
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
        if add_song_info and song_book:
            caption_lines.append(f'<b>Song:</b> {song_book} {song_number}')

        return '\n'.join(caption_lines)

    def send_tracks(self, tracks):
        """Download and send Fra Kåre tracks of a specific day to telegram channel.
        Return:
            False on error
            True otherwise
        """
        song_book = None
        song_number = None
        song_lyrics_files = []
        for lang in settings.LANG:
            self.bmm_api.setLanguage(lang)
            if not tracks.get(lang):
                continue
            track_info = self.get_track_info(tracks[lang])
            track_url = track_info['url']
            track_title = track_info['title']
            # Remove space as telegram adds random thumbnails and album arts otherwise
            track_title_no_space = track_title.replace(' ', '_')

            # There is no url. Silently skip sending this track.
            if not track_url or not track_title:
                return False

            audio_caption = self.get_track_caption(
                track_info, add_song_info=False)

            try:
                # Send audio file
                response = self.bmm_api.get_response_object(track_url)
                raw_response_stream = response.raw
                self.bot.send_audio(
                    raw_response_stream,
                    chat_id=settings.TELEGRAM_CHAT_ID,
                    caption=audio_caption,
                    title=track_title_no_space,
                    parse_mode='HTML'
                )
            except (RequestException, ReadTimeoutError):
                traceback.print_exc()
                sys.stdout.flush()
                return False

            # Set song info
            if not song_book:
                song_book = track_info['song_book']
                song_number = track_info['song_number']

            song_lyric_file_path = os.path.join(
                settings.SCRIPT_DIR, 'song_lyrics', f"{song_book}-{lang}", f'{song_number}.png')
            # If lyric file is not found for song, continue
            if not os.path.isfile(song_lyric_file_path):
                continue
            song_lyrics_files.append(open(song_lyric_file_path, 'rb'))

        # If there is no song information for track, return
        if not song_lyrics_files:
            return True
        elif song_lyrics_files:
            self.bot.send_message(
                text=f'<b>Song:</b> {song_book} {song_number}',
                chat_id=settings.TELEGRAM_CHAT_ID,
                parse_mode='HTML'
            )

        # Send song lyrics
        if len(song_lyrics_files) > 1:
            self.bot.send_media_group(
                song_lyrics_files,
                chat_id=settings.TELEGRAM_CHAT_ID
            )
        elif song_lyrics_files:
            self.bot.send_photo(
                song_lyrics_files[0],
                chat_id=settings.TELEGRAM_CHAT_ID
            )

        return True
