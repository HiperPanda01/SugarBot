import sqlite3 as db

class DatabaseManager:
    curr = None
    def __init__(self):
        conn = db.connect("")
        self.curr = conn.cursor()






