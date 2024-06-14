import sqlite3
from sqlite3 import Error
import os
from config import DATABASE_PATH, DATABASE_SETUP_FILE


# Database functions

# Define global variables
global cursor
cursor = None
global connection
connection = None


# Create database if it doesn't exist
def setup_database() -> None:
    if os.path.isfile(DATABASE_PATH):
        print(f'> SQLite DB "{DATABASE_PATH}" found, skipping setup.')
        return

    print(f'> "{DATABASE_PATH}" not found, creating new empty database.')
    con = None
    try:
        con = sqlite3.connect(DATABASE_PATH)
        print(f'> Created database "{DATABASE_PATH}", version {sqlite3.version}.')
        print(f'> Setting up database with schema.')

        with open(DATABASE_SETUP_FILE, 'r') as sql_file:
            sql_script = sql_file.read()

        cursor = con.cursor()
        cursor.executescript(sql_script)
        con.commit()

        print(f'> Creation and setup of database completed.')

    except FileNotFoundError:
        print(f'> ERROR: File "{DATABASE_SETUP_FILE}" not found')
        con.close()
        os.remove(DATABASE_PATH)
    except Error as e:
        print(f'> ERROR: {e}')
        con.close()
        os.remove(DATABASE_PATH)


# Create connection to database
def create_connection() -> None:
    try:
        if os.path.isfile(DATABASE_PATH):
            global connection
            connection = sqlite3.connect(DATABASE_PATH)
            global cursor
            cursor = connection.cursor()
            print('> Connection to DB established')
        else:
            raise FileNotFoundError
    except Error as e:
        print(f'> ERROR: {e}')


# Write to database
def write_sql(query, params=()) -> None:
    cursor.execute(query, params)
    connection.commit()


# Read from database
def read_sql(query, params=()) -> list:
    cursor.execute(query, params)
    return cursor.fetchall()


# Write user information to database
def write_user(discord_id, first_seen: str) -> None:
    if first_seen:
        query = 'INSERT INTO user (discord_id, joined_at) VALUES (?, ?)'
        params = (discord_id, str(first_seen))
    else:
        query = 'INSERT INTO user (discord_id) VALUES (?)'
        params = (discord_id,)
    write_sql(query, params)


# Check if user exists in database
def user_exists(discord_id):
    query = 'SELECT COUNT(1) FROM user WHERE user.discord_id = ?'
    params = (discord_id,)
    result = read_sql(query, params)
    return result[0][0]


# Write support case information to database
def write_support_case(discord_id, type, title, description, rating=None) -> int:
    query = 'INSERT INTO support_case (discord_id, type, title, description, rating) VALUES (?, ?, ?, ?, ?)'
    params = (discord_id, type, title, description, rating)
    write_sql(query, params)
    return cursor.lastrowid


# Write support case supporter information to database
def write_support_case_supporter(support_case_id, is_primary, supporter_id=None) -> None:
    query = 'INSERT INTO support_case_supporter (support_case_id, supporter_id, is_primary) VALUES (?, ?, ?)'
    params = (support_case_id, supporter_id, is_primary)
    write_sql(query, params)


# Update support case entries in specified column
def update_support_case(support_case_id, column, value) -> None:
    query = f'UPDATE support_case SET {column} = ? WHERE id = ?'
    params = (value, support_case_id)
    write_sql(query, params)


# Update support case supporter entries in specified column
def update_support_case_supporter(support_case_id, column, value) -> None:
    query = f'UPDATE support_case_supporter SET {column} = ? WHERE support_case_id = ?'
    params = (value, support_case_id)
    write_sql(query, params)


# Write a new support case
def write_case(discord_id, user_first_seen, type_id, supporter_id=None, supporter_first_seen=None, title=None, is_primary=False, transcript=None) -> int:
    if not user_exists(discord_id=discord_id):
        write_user(discord_id=discord_id, first_seen=user_first_seen)
    if supporter_id and not user_exists(supporter_id):
        write_user(discord_id=supporter_id, first_seen=supporter_first_seen)
    support_case_id = write_support_case(discord_id=discord_id, type=type_id, title=title, description=transcript)
    write_support_case_supporter(support_case_id=support_case_id, is_primary=is_primary, supporter_id=supporter_id)
    return support_case_id


# Get specified support case
def get_support_case(support_case_id) -> list:
    query = 'SELECT * FROM support_case WHERE id = ?'
    params = (support_case_id,)
    return read_sql(query, params)


# Get all support cases for a specified user
def get_user_cases(discord_id) -> list:
    query = 'SELECT * FROM support_case WHERE discord_id = ?'
    params = (discord_id,)
    return read_sql(query, params)


# Get count of support cases for a user
def get_user_cases_count(discord_id) -> int:
    query = 'SELECT COUNT(1) FROM support_case WHERE discord_id = ?'
    params = (discord_id,)
    result = read_sql(query, params)
    return result[0][0]