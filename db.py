from typing import Optional

import sqlite3
from sqlite3 import Error

class DB:
    def __init__(self, db_file):
        self.db_file = db_file if db_file != None else ":memory:"
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.cursor = self.conn.cursor()
        except Error as e:
            print(e)

    def close(self):
        if self.conn:
            self.conn.close()

    def execute(self, sql, params=None):
        if params == None:
            self.cursor.execute(sql)
        else:
            self.cursor.execute(sql, params)
        self.conn.commit()
