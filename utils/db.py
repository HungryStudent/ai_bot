from contextlib import closing
from sqlite3 import Cursor
import sqlite3

database = "utils/database.db"


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def start():
    with closing(sqlite3.connect(database)) as connection:
        cursor = connection.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS users(user_id INT, username TEXT, first_name TEXT, tokens INT)")
        connection.commit()


def get_user(user_id):
    with closing(sqlite3.connect(database)) as connection:
        connection.row_factory = dict_factory
        cursor: Cursor = connection.cursor()
        cursor.execute("SELECT user_id, tokens FROM users WHERE user_id = ?", (user_id,))
        return cursor.fetchone()


def add_user(user_id, username, first_name):
    with closing(sqlite3.connect(database)) as connection:
        connection.row_factory = dict_factory
        cursor: Cursor = connection.cursor()
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, 10)", (user_id, username, first_name))
        connection.commit()


def remove_token(user_id):
    with closing(sqlite3.connect(database)) as connection:
        connection.row_factory = dict_factory
        cursor: Cursor = connection.cursor()
        cursor.execute("UPDATE users SET tokens = tokens - 1 WHERE user_id = ?", (user_id,))
        connection.commit()


def add_tokens(user_id):
    with closing(sqlite3.connect(database)) as connection:
        connection.row_factory = dict_factory
        cursor: Cursor = connection.cursor()
        cursor.execute("UPDATE users SET tokens = tokens + 10 WHERE user_id = ?", (user_id,))
        connection.commit()
