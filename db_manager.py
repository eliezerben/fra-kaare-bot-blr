import os
import json


class DatabaseManager():
    """Simple JSON database to maintain track id of last sent track.

    DB fromat:
    {
        "last_sent_day": "2019-11-25"
    }
    """

    def __init__(self, db_file):
        """Open db file if exists.
        Else, initialize db
        """
        self.db_filename = db_file
        self.db_data = None

        if os.path.isfile(self.db_filename):
            with open(self.db_filename) as db_file:
                self.db_data = json.load(db_file)
        else:
            self.db_data = {}

    def get_last_sent_day(self):
        """Return 'last_sent_day'"""
        return self.db_data.get('last_sent_day')

    def set_last_sent_day(self, track_pub_day):
        """Set 'last_sent_day' and write immediately"""
        self.db_data['last_sent_day'] = track_pub_day
        with open(self.db_filename, 'w') as db_file:
            json.dump(self.db_data, db_file, indent=4)
