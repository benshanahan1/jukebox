"""Wrap useful MySQL database functions.
"""

import pymysql
from datetime import datetime
from time import time
from json import loads, dumps
from threading import Lock


class Database(object):
    """Wrap useful MySQL database functions and provide a nice interface for 
    accessing database contents.

    :param str keysFile: Filepath to 'Database.keys' config file.
    :param Debugger debugger:   (*optional*) The traceback debugger to use, if
                                provided.
    """

    def __init__(self, host, user, password, dbname):
        self.lock   = Lock()
        self.host   = host
        self.user   = user
        self.db     = dbname
        self.passwd = password
        self.conn   = pymysql.connect(
            host        = self.host,
            user        = self.user,
            passwd      = self.passwd,
            db          = self.db,
            cursorclass = pymysql.cursors.DictCursor)

    def query(self, q):
        """Query database and fetchall.

        :param str q: SQL query string to execute.
        :return: Query result or None (if nothing is returned from query).
        :rtype: dict

        """
        self.lock.acquire()
        if False: print("QUERY: {}".format(q))  # debug
        self.conn.ping(True)  # refresh connection if time-out
        # Get cursor to execute SQL queries. The cursor should be a Dictionary
        # so that it's easier for us to work with.
        cur = self.conn.cursor()
        cur.execute(q)
        self.conn.commit()  # save inserted data into database
        rows = cur.fetchall()
        cur.close()
        self.lock.release()
        return rows

    def create_party(self, user_id, user_spotify_token, party_id, 
        party_name, party_description, party_starter_playlist, tracks):
        """Create a new party table."""
        if self.check_party_exists(party_id):
            return False
        # Add a parties entry.
        self.query(
            """INSERT INTO `jukeboxdb`.`parties` 
                (`party_id`, `user_spotify_token`, `user_id`, 
                `party_name`, `party_description`, `party_starter_playlist`, 
                `party_exported_playlist`, `time_created`) 
                VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', 'none');
            """.format(party_id, dumps(user_spotify_token), user_id, 
                party_name, party_description, party_starter_playlist, str(time())))
        # Add a new party table.
        self.query(
            """CREATE TABLE {} (
                `unique_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
                `song_id` VARCHAR(64) NULL,
                `name` VARCHAR(128) NULL,
                `artists` VARCHAR(256) NULL,
                `votes` INT NULL,
                PRIMARY KEY (`unique_id`),
                UNIQUE INDEX `row_id_UNIQUE` (`unique_id` ASC)
            )""".format(party_id))
        # Add starter playlist tracks to the party table.
        # First, format the query values properly.
        catstr = ""
        for track in tracks:
            song_id         = track["id"]
            name            = track["name"].replace("'","")  # TODO implement better char escaping
            artists_list    = [artist["name"].replace("'","") for artist in track["artists"]]
            artists         = ", ".join(artists_list)
            catstr += "('{}', '{}', '{}', 0),".format(song_id, name, artists)
        if tracks:
            catstr = catstr[:-1]  # remove last comma
            self.query(
                """INSERT INTO `{}` (song_id, name, artists, votes)
                    VALUES {}
                """.format(party_id, catstr))
        return True

    def update_party_exported_playlist(self, party_id, party_exported_playlist):
        """Update party_exported_playlist entry from Spotify API in database."""
        if not self.check_party_exists(party_id):
            return False
        self.query(
            """UPDATE parties
                SET party_exported_playlist='{}'
                WHERE party_id='{}'
            """.format(party_exported_playlist, party_id))
        return True

    def get_party_exported_playlist(self, party_id):
        """Retrieve party_exported_playlist entry from database."""
        if not self.check_party_exists(party_id):
            return None
        rv = self.query(
            """SELECT party_exported_playlist
                FROM parties
                WHERE party_id='{}'
            """.format(party_id))
        return rv[0]["party_exported_playlist"]

    def delete_party(self, party_id):
        # Return if the specified party doesn't exist.
        if not self.check_party_exists(party_id):
            print("Cannot delete party because it does not exist.")
            return False
        # Else, let's remove all traces of it from the database.
        try:
            self.query("DROP TABLE {}".format(party_id))
            self.query("DELETE FROM parties WHERE party_id='{}'".format(party_id))
            return True
        except Exception as e:
            print("An error occurred while deleting party: {}".format(e))
            return False

    def retrieve_spotify_token(self, party_id):
        # Retrieve the Spotify authorization token from the parties entry.
        if self.check_party_exists(party_id):
            rv = self.query(
                """SELECT user_spotify_token
                    FROM parties
                    WHERE party_id='{}'
                """.format(party_id))
            return rv[0]
        else:
            return None

    def check_party_exists(self, party_id):
        """Check if a party table and row-entry exist in database."""
        if not self._check_parties_entry_exists(party_id):
            return False
        if not self._check_party_table_exists(party_id):
            return False
        return True

    def _check_parties_entry_exists(self, party_id):
        """Check if the given party_id exists as a row in the `parties` table. """
        rv = self.query(
            """SELECT *
                FROM parties
                WHERE party_id='{}'
            """.format(party_id))
        return rv != ()

    def _check_party_table_exists(self, party_id):
        """Check if the given party_id exists (i.e. if there's a table). """
        try:
            self.query("SELECT 1 FROM `{}` LIMIT 1".format(party_id))
            return True
        except:
            return False

    def check_song_exists(self, party_id, song_id):
        if self.check_party_exists(party_id):
            rv = self.query(
                """SELECT *
                    FROM {}
                    WHERE song_id='{}'
                """.format(party_id, song_id))
            return rv != ()
        else:
            return False

    def get_party(self, party_id):
        """Retrieve information about a specific party from the database.
        """
        try:
            meta_data = self.query(
                """SELECT *
                    FROM `parties`
                    WHERE party_id='{}'
                """.format(party_id))
            song_data = self.query(
                """SELECT *
                    FROM `{}`
                """.format(party_id))
            return {"meta": meta_data[0], "songs": song_data}
        except Exception as e:
            print("An error occurred: {}".format(e))
            return False

    def is_user_party_host(self, user_id, party_id):
        """Is the logged in user the party host?"""
        if not user_id or not party_id:
            return False
        try:
            result = self.query(
                """SELECT party_id 
                    FROM parties
                    WHERE user_id='{}'
                """.format(user_id))
            return result != ()
        except:
            return False

    def get_total_votes(self, party_id, song_id):
        """ Get total vote count for specified song. """
        if self.check_song_exists(party_id, song_id):
            rv = self.query(
                """SELECT votes
                    FROM {}
                    WHERE song_id='{}'
                """.format(party_id, song_id))
            return rv[0]["votes"]
        else:
            return False

    def add_vote(self, party_id, song_id, vote_value):
        """ Add a vote to the current song. """
        if self.check_song_exists(party_id, song_id):
            self.query(
                """UPDATE {}
                    SET votes = votes + {}
                    WHERE song_id='{}'
                """.format(party_id, vote_value, song_id))
            return True
        else:
            return False