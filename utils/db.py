from datetime import datetime, date, time
import asyncpg
from asyncpg import Connection
from config import DB_USER, DB_HOST, DB_DATABASE, DB_PASSWORD


async def get_conn() -> Connection:
    return await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE, host=DB_HOST)


async def start():
    conn: Connection = await get_conn()
    await conn.execute("CREATE TABLE IF NOT EXISTS users("
                       "user_id BIGINT PRIMARY KEY,"
                       "username VARCHAR(32),"
                       "first_name VARCHAR(64),"
                       "balance INT DEFAULT 0,"
                       "reg_time INT,"
                       "free_chatgpt SMALLINT DEFAULT 3,"
                       "free_image SMALLINT DEFAULT 0,"
                       "default_ai VARCHAR(10) DEFAULT 'empty',"
                       "inviter_id BIGINT,"
                       "ref_balance INT DEFAULT 0,"
                       "task_id VARCHAR(1024) DEFAULT '0')")
    await conn.execute("CREATE TABLE IF NOT EXISTS orders(id SERIAL PRIMARY KEY, user_id BIGINT, amount INT,"
                       "pay_time INT)")
    await conn.execute(
        "CREATE TABLE IF NOT EXISTS usage(id SERIAL PRIMARY KEY, user_id BIGINT, ai_type VARCHAR(10), use_time INT)")
    await conn.execute(
        "CREATE TABLE IF NOT EXISTS withdraws(id SERIAL PRIMARY KEY, user_id BIGINT, amount INT, withdraw_time INT)")
    await conn.execute("CREATE TABLE IF NOT EXISTS config(config_key VARCHAR(32), config_value VARCHAR(256))")
    row = await conn.fetchrow("SELECT config_value FROM config WHERE config_key = 'iam_token'")
    if row is None:
        await conn.execute("INSERT INTO config VALUES('iam_token', '1')")
    await conn.close()


async def get_users():
    conn: Connection = await get_conn()
    rows = await conn.fetch("SELECT user_id FROM users")
    await conn.close()
    return rows


async def get_user(user_id):
    conn: Connection = await get_conn()
    row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
    await conn.close()
    return row


async def add_user(user_id, username, first_name, inviter_id):
    conn: Connection = await get_conn()
    await conn.execute(
        "INSERT INTO users(user_id, username, first_name, reg_time, inviter_id) VALUES ($1, $2, $3, $4, $5)",
        user_id, username, first_name, int(datetime.now().timestamp()), inviter_id)
    await conn.close()


async def update_task_id(user_id, task_id):
    conn: Connection = await get_conn()
    await conn.execute("UPDATE users SET task_id = $2 WHERE user_id = $1", user_id, task_id)
    await conn.close()


async def change_default_ai(user_id, ai_type):
    conn: Connection = await get_conn()
    await conn.execute("UPDATE users SET default_ai = $2 WHERE user_id = $1", user_id, ai_type)
    await conn.close()


async def remove_chatgpt(user_id):
    conn: Connection = await get_conn()
    await conn.execute("UPDATE users SET free_chatgpt = free_chatgpt - 1 WHERE user_id = $1", user_id)
    await conn.close()


async def remove_image(user_id):
    conn: Connection = await get_conn()
    await conn.execute("UPDATE users SET free_image = free_image - 1 WHERE user_id = $1", user_id)
    await conn.close()


async def remove_balance(user_id):
    conn: Connection = await get_conn()
    await conn.execute("UPDATE users SET balance = balance - 10 WHERE user_id = $1", user_id)
    await conn.close()


async def add_balance_from_admin(user_id, amount):
    conn: Connection = await get_conn()
    await conn.execute("UPDATE users SET balance = $2 WHERE user_id = $1", user_id, amount)
    await conn.close()


async def add_balance(user_id, amount):
    conn: Connection = await get_conn()
    ref_balance = int(float(amount) * 0.15)
    await conn.execute("UPDATE users SET balance = balance + $2 WHERE user_id = $1", user_id, amount)
    await conn6.execute(
        "UPDATE users SET ref_balance = ref_balance + $2 WHERE user_id = (SELECT inviter_id FROM users WHERE user_id = $1)",
        user_id, ref_balance)

    await conn.execute("INSERT INTO orders(user_id, amount, pay_time) VALUES ($1, $2, $3)",
                       (user_id, amount, int(datetime.now().timestamp())))
    await conn.close()


async def add_balance_from_ref(user_id):
    conn: Connection = await get_conn()
    await conn.execute("UPDATE users SET balance = balance + ref_balance, ref_balance = 0 WHERE user_id = $1",
                       user_id)
    await conn.close()


async def get_ref_stat(user_id):
    conn: Connection = await get_conn()
    row = await conn.fetchrow("SELECT (SELECT CAST(sum(amount) * 0.15 as int) FROM orders WHERE "
                              "EXISTS(SELECT * FROM users "
                              "WHERE inviter_id = $1 AND users.user_id = orders.user_id)) as all_income,"
                              "(SELECT ref_balance FROM users WHERE user_id = $1) as available_for_withdrawal,"
                              "(SELECT COUNT(user_id) FROM users WHERE inviter_id = $1) as count_refs,"
                              "(SELECT COUNT(id) FROM orders JOIN users u ON orders.user_id = u.user_id WHERE u.inviter_id = $1) as orders_count",
                              user_id)
    await conn.close()
    print(row)
    return row


async def get_all_inviters():
    conn: Connection = await get_conn()
    rows = await conn.fetch('select distinct inviter_id from users where inviter_id != 0')
    await conn.close()
    return rows


async def add_action(user_id, ai_type):
    conn: Connection = await get_conn()
    await conn.execute("INSERT INTO usage(user_id, ai_type, use_time) VALUES ($1, $2, $3)",
                       user_id, ai_type, int(datetime.now().timestamp()))
    await conn.close()


async def get_stat():
    end = int(datetime.now().timestamp())
    start = int(datetime.combine(date.today(), time()).timestamp())

    conn: Connection = await get_conn()
    row = await conn.fetchrow("SELECT (SELECT COUNT() FROM users) as users_count,"
                              "(SELECT COUNT() FROM users where reg_time between $1 and $2) as today_users_count,"
                              "(SELECT COUNT() FROM usage WHERE ai_type = 'chatgpt') as chatgpt_count,"
                              "(SELECT COUNT() FROM usage WHERE ai_type = 'image') as image_count,"
                              "(SELECT COUNT() FROM usage WHERE ai_type = 'chatgpt' and use_time between $1 and $2) "
                              "as today_chatgpt_count,"
                              "(SELECT COUNT() FROM usage WHERE ai_type = 'image' and use_time between $1 and $2) "
                              "as today_image_count,"
                              "(SELECT COUNT() FROM orders) as orders_count,"
                              "(SELECT SUM(amount) FROM orders) as orders_sum,"
                              "(SELECT count(id) - count(DISTINCT user_id) FROM orders) as repeated_orders_count,"
                              "(SELECT COUNT() FROM orders WHERE pay_time between $1 and $2) as today_orders_count,"
                              "(SELECT SUM(amount) FROM orders WHERE pay_time between $1 and $2) as today_orders_sum",
                              start, end)
    await conn.close()
    return row


async def get_iam_token():
    conn: Connection = await get_conn()
    row = await conn.fetchrow("SELECT config_value FROM config WHERE config_key = 'iam_token'")
    await conn.close()
    return row['config_value']


async def change_iam_token(iam_token):
    conn: Connection = await get_conn()
    await conn.execute(
        "UPDATE config SET config_value = $1 WHERE config_key = 'iam_token'", iam_token)
    await conn.close()


async def add_withdraw(user_id, amount):
    conn: Connection = await get_conn()
    await conn.execute("INSERT INTO withdraws(user_id, amount, withdraw_time) VALUES ($1, $2, $3)",
                       user_id, amount, int(datetime.now().timestamp()))
    await conn.close()


async def reset_ref_balance(user_id):
    conn: Connection = await get_conn()
    await conn.execute(
        "UPDATE users SET ref_balance = 0 WHERE user_id = $1", user_id)
    await conn.close()
