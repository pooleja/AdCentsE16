#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import threading

DATABASE_FILE = "{PWD}"

# DB lock for multithreaded use case
db_rlock = threading.RLock()


def dict_factory(cursor, row):
    """
    Dictionary factory for parsing tuple results.
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class AdsSQL():
    """
    Class to interface with the db for transcoding jobs.
    """

    ID = 'id'

    def __init__(self):
        """
        Connect to indexes.db and sets up an sql cursor.
        """
        print("Connecting to DB.")
        with db_rlock:
            self.conn = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
            self.conn.row_factory = dict_factory
            self.cursor = self.conn.cursor()

    def create_table(self):
        """
        Creates default table for tracking search indexes.
        """
        with db_rlock:
            print("Creating Table.")
            query = 'CREATE TABLE Ads(id TEXT)'
            self.cursor.execute(query)

    def close_connection(self):
        """
        Close the sqlite3 handle.
        """
        print("Closing connection to DB.")
        self.conn.close()


def main():
    """
    Main function to set up the DB.
    """
    db_already_exists = os.path.exists(DATABASE_FILE)
    if db_already_exists is False:
        print("Creating Ads DB.")
        db_setup = AdsSQL()
        db_setup.create_table()
        db_setup.close_connection()
    else:
        print("Database file already exists.")

if __name__ == "__main__":
    main()
