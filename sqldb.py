#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import threading

DATABASE_FILE = "{PWD}"

# DB lock for multithreaded use case
db_rlock = threading.RLock()


class IndexesSQL():
    """
    Class to interface with the db for transcoding jobs.
    """

    def __init__(self):
        """
        Connect to indexes.db and sets up an sql cursor.
        """
        print("Connecting to DB.")
        self.conn = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def create_table(self):
        """
        Creates default table for tracking search indexes.
        """
        with db_rlock:
            print("Creating Table.")
            query = 'CREATE TABLE Indexes(Id TEXT)'
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
        print("Creating Indexes DB.")
        db_setup = IndexesSQL()
        db_setup.create_table()
        db_setup.close_connection()
    else:
        print("Database file already exists.")

if __name__ == "__main__":
    main()
