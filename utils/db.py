from contextlib import closing
from datetime import datetime, date, time
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
            "CREATE TABLE IF NOT EXISTS users(user_id INT, username TEXT, first_name TEXT, balance INT, reg_time INT, free_chatgpt INT, free_image INT, default_ai TEXT, inviter_id INT, ref_balance INT)")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INT, amount INT, pay_time INT)")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS usage(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INT, ai_type TEXT, use_time INT)")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS withdraws(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INT, amount TEXT, withdraw_time INT)")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS config(config_key TEXT, config_value TEXT)")
        cursor.execute("SELECT config_value FROM config WHERE config_key = 'iam_token'")
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO config VALUES('iam_token', '1')")
        connection.commit()


def get_users():
    with closing(sqlite3.connect(database)) as connection:
        connection.row_factory = dict_factory
        cursor: Cursor = connection.cursor()
        cursor.execute("SELECT user_id FROM users")
        return cursor.fetchall()


def get_user(user_id):
    with closing(sqlite3.connect(database)) as connection:
        connection.row_factory = dict_factory
        cursor: Cursor = connection.cursor()
        cursor.execute(
            "SELECT user_id, balance, ref_balance, free_chatgpt, free_image, default_ai FROM users WHERE user_id = ?",
            (user_id,))
        return cursor.fetchone()


def add_user(user_id, username, first_name, inviter_id):
    with closing(sqlite3.connect(database)) as connection:
        connection.row_factory = dict_factory
        cursor: Cursor = connection.cursor()
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, 0, ?, 3, 0, 'empty', ?, 0)",
                       (user_id, username, first_name, int(datetime.now().timestamp()), inviter_id))
        connection.commit()


def change_default_ai(user_id, ai_type):
    with closing(sqlite3.connect(database)) as connection:
        connection.row_factory = dict_factory
        cursor: Cursor = connection.cursor()
        cursor.execute("UPDATE users SET default_ai = ? WHERE user_id = ?", (ai_type, user_id,))
        connection.commit()


def remove_chatgpt(user_id):
    with closing(sqlite3.connect(database)) as connection:
        connection.row_factory = dict_factory
        cursor: Cursor = connection.cursor()
        cursor.execute("UPDATE users SET free_chatgpt = free_chatgpt - 1 WHERE user_id = ?", (user_id,))
        connection.commit()


def remove_image(user_id):
    with closing(sqlite3.connect(database)) as connection:
        connection.row_factory = dict_factory
        cursor: Cursor = connection.cursor()
        cursor.execute("UPDATE users SET free_image = free_image - 1 WHERE user_id = ?", (user_id,))
        connection.commit()


def remove_balance(user_id):
    with closing(sqlite3.connect(database)) as connection:
        connection.row_factory = dict_factory
        cursor: Cursor = connection.cursor()
        cursor.execute("UPDATE users SET balance = balance - 10 WHERE user_id = ?", (user_id,))
        connection.commit()


def add_balance_from_admin(user_id, amount):
    with closing(sqlite3.connect(database)) as connection:
        connection.row_factory = dict_factory
        cursor: Cursor = connection.cursor()
        cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (amount, user_id))
        connection.commit()


def add_balance(user_id, amount):
    with closing(sqlite3.connect(database)) as connection:
        connection.row_factory = dict_factory
        cursor: Cursor = connection.cursor()
        ref_balance = int(float(amount) * 0.2)
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        cursor.execute(
            "UPDATE users SET ref_balance = ref_balance + ? WHERE user_id = (SELECT inviter_id FROM users WHERE user_id = ?)",
            (ref_balance, user_id))

        cursor.execute("INSERT INTO orders(user_id, amount, pay_time) VALUES (?, ?, ?)",
                       (user_id, amount, int(datetime.now().timestamp())))
        connection.commit()


def add_balance_from_ref(user_id):
    with closing(sqlite3.connect(database)) as connection:
        connection.row_factory = dict_factory
        cursor: Cursor = connection.cursor()
        cursor.execute("UPDATE users SET balance = balance + ref_balance, ref_balance = 0 WHERE user_id = ?",
                       (user_id,))
        connection.commit()


def get_ref_stat(user_id):
    with closing(sqlite3.connect(database)) as connection:
        connection.row_factory = dict_factory
        cursor: Cursor = connection.cursor()
        cursor.execute("SELECT (SELECT sum(amount) FROM orders WHERE "
                       "EXISTS(SELECT * FROM users "
                       "WHERE inviter_id = ? AND users.user_id = orders.user_id)) as all_income,"
                       "(SELECT ref_balance FROM users WHERE user_id = ?) as available_for_withdrawal,"
                       "(SELECT SUM(user_id) FROM users WHERE inviter_id = ?) as count_refs",
                       (user_id, user_id, user_id))
        return cursor.fetchone()


def add_action(user_id, ai_type):
    with closing(sqlite3.connect(database)) as connection:
        connection.row_factory = dict_factory
        cursor: Cursor = connection.cursor()
        cursor.execute("INSERT INTO usage(user_id, ai_type, use_time) VALUES (?, ?, ?)",
                       (user_id, ai_type, int(datetime.now().timestamp())))
        connection.commit()


def get_stat():
    end = int(datetime.now().timestamp())
    start = int(datetime.combine(date.today(), time()).timestamp())
    with closing(sqlite3.connect(database)) as connection:
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        cursor.execute("SELECT (SELECT COUNT() FROM users) as users_count,"
                       "(SELECT COUNT() FROM users where reg_time between ? and ?) as today_users_count,"
                       "(SELECT COUNT() FROM usage WHERE ai_type = 'chatgpt') as chatgpt_count,"
                       "(SELECT COUNT() FROM usage WHERE ai_type = 'image') as image_count,"
                       "(SELECT COUNT() FROM usage WHERE ai_type = 'chatgpt' and use_time between ? and ?) "
                       "as today_chatgpt_count,"
                       "(SELECT COUNT() FROM usage WHERE ai_type = 'image' and use_time between ? and ?) "
                       "as today_image_count,"
                       "(SELECT COUNT() FROM orders) as orders_count,"
                       "(SELECT SUM(amount) FROM orders) as orders_sum,"
                       "(SELECT COUNT() FROM orders WHERE pay_time between ? and ?) as today_orders_count,"
                       "(SELECT SUM(amount) FROM orders WHERE pay_time between ? and ?) as today_orders_sum",
                       (start, end, start, end, start, end, start, end, start, end))
        return cursor.fetchone()


def get_iam_token():
    with closing(sqlite3.connect(database)) as connection:
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        cursor.execute("SELECT config_value FROM config WHERE config_key = 'iam_token'")
        return cursor.fetchone()['config_value']


def change_iam_token(iam_token):
    with closing(sqlite3.connect(database)) as connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE config SET config_value = ? WHERE config_key = 'iam_token'", (iam_token,))
        connection.commit()


def add_withdraw(user_id, amount):
    with closing(sqlite3.connect(database)) as connection:
        connection.row_factory = dict_factory
        cursor: Cursor = connection.cursor()
        cursor.execute("INSERT INTO withdraws(user_id, amount, withdraw_time) VALUES (?, ?, ?)",
                       (user_id, amount, int(datetime.now().timestamp())))
        connection.commit()


def reset_ref_balance(user_id):
    with closing(sqlite3.connect(database)) as connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE users SET ref_balance = 0 WHERE user_id = ?", (user_id,))
        connection.commit()
