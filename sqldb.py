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


class IndexesSQL():
    """
    Class to interface with the db for transcoding jobs.
    """

    ID = 'id'
    EXPIRE = 'expire'
    DELETED = 'deleted'

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
            query = 'CREATE TABLE Indexes(id TEXT, expire REAL, deleted INTEGER DEFAULT 0, deletedByIP TEXT)'
            self.cursor.execute(query)

    def insert_new_index(self, index_name, expire_time):
        """
        Create a new index in the db.
        """
        with db_rlock:
            query = 'INSERT INTO Indexes(id, expire) VALUES(?,?)'
            self.cursor.execute(query, (index_name, expire_time))
            self.conn.commit()

    def get_index(self, index_name):
        """
        Get the index specified by index_name.
        """
        with db_rlock:
            query = 'SELECT * FROM Indexes WHERE id=?;'
            res = self.cursor.execute(query, (index_name,))
            return res.fetchone()

    def update_expire(self, index_name, expire_time):
        """
        Update the exprire time for the specified index.
        """
        with db_rlock:
            query = 'UPDATE Indexes SET expire=? WHERE id=?'
            self.cursor.execute(query, (index_name, expire_time))
            self.conn.commit()

    def delete_index(self, index_name, remote_addr):
        """
        Marks the index as deleted in the db and records the IP of the client.
        """
        with db_rlock:
            query = 'UPDATE Indexes SET deleted=?, deletedByIP=? WHERE id=?'
            self.cursor.execute(query, (1, remote_addr, index_name))
            self.conn.commit()

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
