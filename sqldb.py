#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import threading
import datetime

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

    TABLE_REGISTRATIONS = "Registrations"
    REG_URL = "url"
    REG_USERNAME = "username"
    REG_KEY = "key"
    REG_VALIDATED = "validated"
    REG_LATEST_BUY_DATE = "latestBuyDate"
    REG_ADDRESS = "address"

    def __init__(self):
        """
        Connect to indexes.db and sets up an sql cursor.
        """
        print("Connecting to DB.")
        with db_rlock:
            self.conn = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
            self.conn.row_factory = dict_factory
            self.cursor = self.conn.cursor()

    def create_tables(self):
        """
        Creates default table for tracking search indexes.
        """
        with db_rlock:
            print("Creating Tables.")

            # Create registrations table
            query = 'CREATE TABLE Registrations(url TEXT, username TEXT, key TEXT PRIMARY KEY, ' \
                    'validated INTEGER DEFAULT 0, latestBuyDate timestamp DEFAULT 0, address TEXT)'
            self.cursor.execute(query)

            query = 'CREATE TABLE Buys(buyId INTEGER PRIMARY KEY AUTOINCREMENT, regKey TEXT, campaignKey TEXT, buyDate timestamp, title TEXT, ' \
                    'description TEXT, targetUrl TEXT, imageUrl TEXT, FOREIGN KEY(regKey) REFERENCES Registrations(key))'
            self.cursor.execute(query)

    def insert_new_registration(self, url, username, key, address):
        """
        Create a new URL registration.
        """
        with db_rlock:
            query = 'INSERT INTO Registrations(url, username, key, address) VALUES(?,?,?,?)'
            self.cursor.execute(query, (url, username, key, address))
            self.conn.commit()

    def get_registration(self, key):
        """
        Returns a registration object with the specified key.
        """
        with db_rlock:
            query = 'SELECT * FROM Registrations WHERE key=?;'
            res = self.cursor.execute(query, (key,))
            return res.fetchone()

    def mark_registration_validated(self, key):
        """
        Sets the validated flag to true for specified registration.
        """
        with db_rlock:
            query = 'UPDATE Registrations SET validated=1 WHERE key=?'
            self.cursor.execute(query, (key,))
            self.conn.commit()

    def get_sites_with_no_buys_today(self):
        """
        Get all sites with no bids for today to be displayed to bidding users.
        """
        with db_rlock:
            date = datetime.date.today()
            query = 'SELECT url, key FROM Registrations WHERE latestBuyDate < ? AND validated > 0;'
            res = self.cursor.execute(query, (date,))
            return res.fetchall()

    def get_todays_buy_for_site(self, key):
        """
        Get a buy for a site that happened today if one exists.
        """
        with db_rlock:
            query = 'SELECT buyId, regKey, buyDate FROM Buys, Registrations ' \
                    'WHERE Buys.regKey = Registrations.key AND Buys.regKey=? AND Buys.buyDate > ? AND Registrations.validated > 0;'
            res = self.cursor.execute(query, (key, datetime.date.today()))
            return res.fetchall()

    def insert_new_buy(self, regKey, campaignKey, title, description, target_url, image_url, buy_time):
        """
        Create a new buy record for the specified registration.
        """
        with db_rlock:

            # Trucate strings as necessary
            t = title[:128]
            d = description[:1024]
            u = target_url[:2024]
            i = image_url[:2024]

            query = 'INSERT INTO Buys(regKey, campaignKey, buyDate, title, description, targetUrl, imageUrl) VALUES(?,?,?,?,?,?,?)'
            self.cursor.execute(query, (regKey, campaignKey, buy_time, t, d, u, i))
            self.conn.commit()

    def update_latest_buy_on_registration(self, regKey, buy_time):
        """
        Update the latestBuyDate on the specified registration.
        """
        with db_rlock:
            query = 'UPDATE Registrations SET latestBuyDate=? WHERE key=?'
            self.cursor.execute(query, (buy_time, regKey))
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
        print("Creating Ads DB.")
        db_setup = AdsSQL()
        db_setup.create_tables()
        db_setup.close_connection()
    else:
        print("Database file already exists.")

if __name__ == "__main__":
    main()
