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
        if False: self.trace("QUERY: {}".format(q))  # debug
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

    def create_party(self, user_id, user_spotify_token, party_id):
        """Create a new party table."""
        if self.check_party_exists(party_id):
            return False
        # Add a parties entry.
        self.query(
            """INSERT INTO `jukeboxdb`.`parties` 
                (`user_id`, `user_spotify_token`, `party_id`, `time_created`) 
                VALUES ('{}', '{}', '{}', '{}');
            """.format(user_id, dumps(user_spotify_token), party_id, str(time())))
        # Add a new party table.
        self.query(
            """CREATE TABLE {} (
                `unique_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
                `song_id` VARCHAR(64) NULL,
                `votes` INT NULL,
                PRIMARY KEY (`unique_id`),
                UNIQUE INDEX `row_id_UNIQUE` (`unique_id` ASC)
            )""".format(party_id))
        return True

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
            return {"meta": meta_data, "songs": song_data}
        except Exception as e:
            print("An error occurred: {}".format(e))
            return False

    def is_user_party_host(self, user_id, party_id):
        """Is the logged in user the party host?"""
        try:
            result = self.query(
                """SELECT party_id 
                    FROM parties
                    WHERE user_id='{}'
                """.format(user_id))
            return result != ()
        except:
            return False